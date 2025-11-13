from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.db import transaction
from django.core.cache import cache
import secrets
import json
import logging

from .models import User, UserProfile, EmailVerification, PasswordReset, LoginAttempt
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, PasswordResetForm,
    PasswordResetConfirmForm, ProfileUpdateForm
)

logger = logging.getLogger(__name__)


RATE_LIMITS = {
    'login': {'limit': 5, 'window': 15 * 60},
    'password_reset': {'limit': 5, 'window': 15 * 60},
    'resend_verification': {'limit': 5, 'window': 15 * 60},
    'availability': {'limit': 30, 'window': 5 * 60},
}


def _rl_key(kind: str, ident: str) -> str:
    return f"auth:{kind}:{ident}"


def is_rate_limited(kind: str, ident: str) -> bool:
    conf = RATE_LIMITS[kind]
    count = cache.get(_rl_key(kind, ident), 0)
    return count >= conf['limit']


def incr_rate(kind: str, ident: str):
    conf = RATE_LIMITS[kind]
    key = _rl_key(kind, ident)
    val = cache.get(key, 0)
    if val == 0:
        cache.set(key, 1, timeout=conf['window'])
        messages.success(request, 'إن كانت البيانات صحيحة ستصل رسالة إعادة التعيين إن أمكن.')
        incr_rate('password_reset', rl_ident)
        return redirect('authentication:login')
    else:
        try:
            cache.incr(key)
        except Exception:
            cache.set(key, val + 1, timeout=conf['window'])


def reset_rate(kind: str, ident: str):
    cache.delete(_rl_key(kind, ident))

def get_client_ip(request):
    """الحصول على عنوان IP للمستخدم"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def register_view(request):
    """عرض تسجيل مستخدم جديد"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    UserProfile.objects.create(user=user)
                    send_verification_email(user, request)

                    messages.success(
                        request,
                        'تم إنشاء حسابك بنجاح! يمكنك تسجيل الدخول الآن، وتم إرسال بريد للتحقق من بريدك الإلكتروني.'
                    )
                    return redirect('authentication:login')
            except Exception as e:
                logger.error(f"خطأ في إنشاء المستخدم: {e}")
                messages.error(request, 'حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """عرض تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)

            rl_ident = f"{get_client_ip(request)}:{email}"
            if is_rate_limited('login', rl_ident):
                messages.error(request, 'محاولات تسجيل الدخول تجاوزت الحد مؤقتاً. حاول لاحقاً.')
                return render(request, 'authentication/login.html', {'form': form})

            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active and getattr(user, 'is_verified', False):
                    LoginAttempt.objects.create(
                        user=user,
                        email=email,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=True
                    )
                    
                    login(request, user)
                    reset_rate('login', rl_ident)
                    
                    if not remember_me:
                        request.session.set_expiry(0)
                    else:
                        request.session.set_expiry(1209600)
                    
                    next_url = request.GET.get('next', 'dashboard:index')
                    return redirect(next_url)
                else:
                    messages.error(request, 'حسابك غير مفعل. يرجى التحقق من بريدك الإلكتروني.')
            else:
                LoginAttempt.objects.create(
                    email=email,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=False
                )
                incr_rate('login', rl_ident)
                messages.error(request, 'بيانات تسجيل الدخول غير صحيحة.')
        else:
            messages.error(request, 'بيانات تسجيل الدخول غير صحيحة.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'authentication/login.html', {'form': form})


@require_http_methods(["POST"])
def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('main:home')


@login_required
def profile_view(request):
    """عرض وتحديث الملف الشخصي"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('authentication:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'authentication/profile.html', {'form': form})


def send_verification_email(user, request):
    """إرسال بريد التحقق من البريد الإلكتروني"""
    try:
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        verification_url = request.build_absolute_uri(
            reverse('authentication:verify_email', kwargs={'token': token})
        )
        
        subject = 'تفعيل حسابك في كوريزا'
        message = render_to_string('authentication/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f"تم إرسال بريد التحقق للمستخدم: {user.email}")
        
    except Exception as e:
        logger.error(f"خطأ في إرسال بريد التحقق: {e}")


def verify_email_view(request, token):
    """التحقق من البريد الإلكتروني"""
    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False
        )
        
        if verification.is_expired():
            messages.error(request, 'انتهت صلاحية رابط التحقق.')
            return redirect('authentication:login')
        
        verification.user.is_active = True
        verification.user.is_verified = True
        verification.user.save()
        
        verification.is_used = True
        verification.save()
        
        messages.success(request, 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
        return redirect('authentication:login')
        
    except EmailVerification.DoesNotExist:
        messages.error(request, 'رابط التحقق غير صحيح أو منتهي الصلاحية.')
        return redirect('authentication:login')


def password_reset_view(request):
    """عرض إعادة تعيين كلمة المرور"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            rl_ident = f"{get_client_ip(request)}:{email}"
            if is_rate_limited('password_reset', rl_ident):
                messages.error(request, 'تم تجاوز الحد المسموح لطلبات إعادة التعيين مؤقتاً. حاول لاحقاً.')
                return render(request, 'authentication/password_reset.html', {'form': form})
            try:
                user = User.objects.get(email=email, is_active=True)
                send_password_reset_email(user, request)
                messages.success(
                    request,
                    'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.'
                )
                return redirect('authentication:login')
            except User.DoesNotExist:
                messages.error(request, 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'authentication/password_reset.html', {'form': form})


def send_password_reset_email(user, request):
    """إرسال بريد إعادة تعيين كلمة المرور"""
    try:
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timezone.timedelta(hours=1)
        
        PasswordReset.objects.filter(user=user, is_used=False).update(is_used=True)
        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        reset_url = request.build_absolute_uri(
            reverse('authentication:password_reset_confirm', kwargs={'token': token})
        )
        
        subject = 'إعادة تعيين كلمة المرور - كوريزا'
        message = render_to_string('authentication/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        
        logger.info(f"تم إرسال بريد إعادة تعيين كلمة المرور للمستخدم: {user.email}")
        
    except Exception as e:
        logger.error(f"خطأ في إرسال بريد إعادة تعيين كلمة المرور: {e}")


def password_reset_confirm_view(request, token):
    """تأكيد إعادة تعيين كلمة المرور"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    try:
        reset = PasswordReset.objects.get(
            token=token,
            is_used=False
        )
        
        if reset.is_expired():
            messages.error(request, 'انتهت صلاحية رابط إعادة تعيين كلمة المرور.')
            return redirect('authentication:password_reset')
        
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password1')
                reset.user.set_password(new_password)
                reset.user.save()
                
                reset.is_used = True
                reset.save()
                
                messages.success(request, 'تم تحديث كلمة المرور بنجاح! يمكنك الآن تسجيل الدخول.')
                return redirect('authentication:login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'authentication/password_reset_confirm.html', {
            'form': form,
            'token': token
        })
        
    except PasswordReset.DoesNotExist:
        messages.error(request, 'رابط إعادة تعيين كلمة المرور غير صحيح أو منتهي الصلاحية.')
        return redirect('authentication:password_reset')


@require_http_methods(["POST"])
def check_email_availability(request):
    """فحص توفر البريد الإلكتروني (AJAX)"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'available': False, 'message': 'البريد الإلكتروني مطلوب'})
        
        # Throttle availability checks
        rl_ident = f"{get_client_ip(request)}:email_avail"
        if is_rate_limited('availability', rl_ident):
            return JsonResponse({'available': False, 'message': 'محاولات متكررة، حاول لاحقاً.'}, status=429)
        incr_rate('availability', rl_ident)

        is_available = not User.objects.filter(email=email).exists()
        
        return JsonResponse({
            'available': is_available,
            'message': 'البريد الإلكتروني متاح' if is_available else 'البريد الإلكتروني مستخدم بالفعل'
        })
        
    except Exception as e:
        logger.error(f"خطأ في فحص البريد الإلكتروني: {e}")
        return JsonResponse({'available': False, 'message': 'حدث خطأ في الخادم'})


@require_http_methods(["POST"])
def check_username_availability(request):
    """فحص توفر اسم المستخدم (AJAX)"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'available': False, 'message': 'اسم المستخدم مطلوب'})
        
        # Throttle availability checks
        rl_ident = f"{get_client_ip(request)}:username_avail"
        if is_rate_limited('availability', rl_ident):
            return JsonResponse({'available': False, 'message': 'محاولات متكررة، حاول لاحقاً.'}, status=429)
        incr_rate('availability', rl_ident)

        is_available = not User.objects.filter(username=username).exists()
        
        return JsonResponse({
            'available': is_available,
            'message': 'اسم المستخدم متاح' if is_available else 'اسم المستخدم مستخدم بالفعل'
        })
        
    except Exception as e:
        logger.error(f"خطأ في فحص اسم المستخدم: {e}")
        return JsonResponse({'available': False, 'message': 'حدث خطأ في الخادم'})


@login_required
def resend_verification_email(request):
    """إعادة إرسال بريد التحقق"""
    if request.user.is_verified:
        messages.info(request, 'حسابك مفعل بالفعل.')
        return redirect('dashboard:index')
    
    try:
        send_verification_email(request.user, request)
        messages.success(request, 'تم إرسال بريد التحقق مرة أخرى.')
    except Exception as e:
        logger.error(f"خطأ في إعادة إرسال بريد التحقق: {e}")
        messages.error(request, 'حدث خطأ أثناء إرسال بريد التحقق.')
    
    return redirect('authentication:profile')


@require_http_methods(["POST"])
def resend_verification_email_public(request):
    """إعادة إرسال رسالة التحقق لغير المسجلين (بريد فقط)."""
    try:
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except Exception:
            email = request.POST.get('email')

        if not email:
            return JsonResponse({'success': False, 'message': 'البريد الإلكتروني مطلوب.'}, status=400)

        rl_ident = f"{get_client_ip(request)}:{email}:resend"
        if is_rate_limited('resend_verification', rl_ident):
            return JsonResponse({'success': False, 'message': 'محاولات متكررة، حاول لاحقاً.'}, status=429)

        try:
            user = User.objects.get(email=email)
            if not getattr(user, 'is_verified', False):
                send_verification_email(user, request)
        except User.DoesNotExist:
            pass

        incr_rate('resend_verification', rl_ident)
        return JsonResponse({'success': True, 'message': 'إن كان البريد غير موثق فستصلك رسالة تحقق.'})
    except Exception as e:
        logger.error(f"Error in public resend verification: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ غير متوقع.'}, status=500)

