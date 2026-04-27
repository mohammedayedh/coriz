from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging

from .models import Post, Category, Comment, Tag, ContactMessage, Newsletter, SiteSettings
from .forms import ContactForm, NewsletterForm
from authentication.models import User
from osint_tools.models import OSINTTool

logger = logging.getLogger(__name__)


def home_view(request):
    """الصفحة الرئيسية"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    context = {
        'site_settings': site_settings,
    }
    
    return render(request, 'main/home.html', context)


def custom_page_not_found(request, exception=None):
    """عرض الصفحة المخصصة عند حدوث خطأ 404."""
    context = {
        'request_path': getattr(request, 'path', '/'),
    }
    return render(request, 'errors/404.html', context, status=404)





@require_http_methods(["GET", "POST"])
def contact_view(request):
    """صفحة التواصل"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact_message = ContactMessage.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
                return redirect('main:contact')
                
            except Exception as e:
                logger.error(f"خطأ في إرسال رسالة التواصل: {e}")
                messages.error(request, 'حدث خطأ أثناء إرسال الرسالة. يرجى المحاولة مرة أخرى.')
    else:
        form = ContactForm()
    
    return render(request, 'main/contact.html', {'form': form})


@require_http_methods(["POST"])
def newsletter_subscribe_view(request):
    """
    الاشتراك في النشرة الإخبارية
    
    إصلاح المشكلة الحرجة #4: إزالة csrf_exempt
    هذا endpoint يستقبل POST requests ويجب أن يكون محمياً بـ CSRF
    إذا كان يُستدعى من JavaScript، يجب إرسال CSRF token في الـ headers
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'البريد الإلكتروني مطلوب'})
        
        form = NewsletterForm({'email': email})
        if not form.is_valid():
            return JsonResponse({'success': False, 'message': form.errors['email'][0]})
        
        # إصلاح إضافي: معالجة race condition في get_or_create
        from django.db import IntegrityError
        try:
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
        except IntegrityError:
            # حدث تزامن - نحاول الحصول على السجل الموجود
            newsletter = Newsletter.objects.get(email=email)
            created = False
        
        if not created and not newsletter.is_active:
            newsletter.is_active = True
            newsletter.unsubscribed_at = None
            newsletter.save(update_fields=['is_active', 'unsubscribed_at'])
        
        return JsonResponse({
            'success': True,
            'message': 'تم الاشتراك في النشرة الإخبارية بنجاح'
        })
        
    except json.JSONDecodeError:
        logger.error("خطأ في تحليل JSON في الاشتراك بالنشرة الإخبارية")
        return JsonResponse({'success': False, 'message': 'بيانات غير صحيحة'}, status=400)
    except Newsletter.DoesNotExist:
        logger.error("خطأ غير متوقع: Newsletter.DoesNotExist بعد get_or_create")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'}, status=500)
    except Exception as e:
        logger.exception(f"خطأ غير متوقع في الاشتراك في النشرة الإخبارية: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'}, status=500)


def about_view(request):
    """صفحة من نحن"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    return render(request, 'main/about.html', {'site_settings': site_settings})


def privacy_policy_view(request):
    """صفحة سياسة الخصوصية"""
    return render(request, 'main/privacy_policy.html')


def terms_of_service_view(request):
    """صفحة شروط الخدمة"""
    return render(request, 'main/terms_of_service.html')


def search_view(request):
    """صفحة البحث"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        results = OSINTTool.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).order_by('-created_at')
        
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'results_count': len(results) if query else 0,
    }
    
    return render(request, 'main/search.html', context)


