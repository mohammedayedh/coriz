from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from .models import DashboardWidget, UserDashboard, ActivityLog, Notification, UserSession, SystemMetrics
from osint_tools.models import InvestigationCase, OSINTSession, OSINTResult, OSINTReport
from authentication.models import User, LoginAttempt

logger = logging.getLogger(__name__)


@login_required
def dashboard_index(request):
    """لوحة التحكم الرئيسية (مركز الاستخبارات)"""
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    
    # إحصائيات استخباراتية
    stats = {
        'total_cases': InvestigationCase.objects.filter(user=request.user).count(),
        'open_cases': InvestigationCase.objects.filter(user=request.user, status__in=['open', 'in_progress']).count(),
        'total_sessions': OSINTSession.objects.filter(user=request.user).count(),
        'total_results': OSINTResult.objects.filter(session__user=request.user).count(),
        'total_reports': OSINTReport.objects.filter(user=request.user).count(),
    }
    
    # الجلسات الحديثة
    recent_sessions = OSINTSession.objects.filter(user=request.user).select_related('tool', 'investigation_case').order_by('-created_at')[:5]
    
    # القضايا النشطة
    recent_cases = InvestigationCase.objects.filter(
        user=request.user, 
        status__in=['open', 'in_progress']
    ).order_by('-updated_at')[:5]
    
    # الإشعارات غير المقروءة
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_sessions': recent_sessions,
        'recent_cases': recent_cases,
        'unread_notifications': unread_notifications,
        'user_dashboard': user_dashboard,
    }
    
    return render(request, 'dashboard/index.html', context)





@login_required
def notifications_view(request):
    """صفحة الإشعارات"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # فلترة الإشعارات
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    is_read_filter = request.GET.get('read')
    if is_read_filter == 'false':
        notifications = notifications.filter(is_read=False)
    elif is_read_filter == 'true':
        notifications = notifications.filter(is_read=True)
    
    context = {
        'notifications': notifications,
        'notification_type': notification_type,
        'is_read_filter': is_read_filter,
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """تحديد الإشعار كمقروء"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'الإشعار غير موجود'})
    except Exception as e:
        logger.error(f"خطأ في تحديد الإشعار كمقروء: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'})


@login_required
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    try:
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"خطأ في تحديد جميع الإشعارات كمقروءة: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'})


@login_required
def activity_log_view(request):
    """سجل الأنشطة"""
    activities = ActivityLog.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # فلترة الأنشطة
    action_filter = request.GET.get('action')
    if action_filter:
        activities = activities.filter(action=action_filter)
    
    object_type_filter = request.GET.get('object_type')
    if object_type_filter:
        activities = activities.filter(object_type=object_type_filter)
    
    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            activities = activities.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to')
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            activities = activities.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    context = {
        'activities': activities,
        'action_filter': action_filter,
        'object_type_filter': object_type_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/activity_log.html', context)


@login_required
def settings_view(request):
    """إعدادات المستخدم"""
    if request.method == 'POST':
        # تحديث إعدادات لوحة التحكم
        user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
        
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            user_dashboard.theme = theme
            user_dashboard.save()
        
        messages.success(request, 'تم حفظ الإعدادات بنجاح.')
        return redirect('dashboard:settings')
    
    # الحصول على إعدادات المستخدم
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    
    context = {
        'user_dashboard': user_dashboard,
    }
    
    return render(request, 'dashboard/settings.html', context)


@login_required
def profile_view(request):
    """ملف المستخدم الشخصي"""
    from authentication.forms import ProfileUpdateForm
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('dashboard:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'dashboard/profile.html', {'form': form})


@login_required
def security_view(request):
    """صفحة الأمان"""
    # الحصول على جلسات المستخدم النشطة
    active_sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')
    
    # الحصول على محاولات تسجيل الدخول الأخيرة
    recent_login_attempts = LoginAttempt.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'active_sessions': active_sessions,
        'recent_login_attempts': recent_login_attempts,
    }
    
    return render(request, 'dashboard/security.html', context)


@login_required
def terminate_session(request, session_id):
    """إنهاء جلسة معينة"""
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user
        )
        session.is_active = False
        session.save()
        
        # إذا كانت الجلسة الحالية
        if session.session_key == request.session.session_key:
            logout(request)
            return redirect('authentication:login')
        
        return JsonResponse({'success': True})
    except UserSession.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'الجلسة غير موجودة'})
    except Exception as e:
        logger.error(f"خطأ في إنهاء الجلسة: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'})


@login_required
def terminate_all_sessions(request):
    """إنهاء جميع الجلسات"""
    try:
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(
            session_key=request.session.session_key
        ).update(is_active=False)
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"خطأ في إنهاء جميع الجلسات: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'})