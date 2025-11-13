from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
import json
import logging
import subprocess
import os
import time

from .models import (
    OSINTTool, OSINTSession, OSINTResult, OSINTReport, 
    OSINTConfiguration, OSINTActivityLog
)
from .serializers import (
    OSINTToolSerializer, OSINTSessionSerializer, OSINTResultSerializer,
    OSINTReportSerializer, OSINTConfigurationSerializer
)
from .utils import OSINTToolRunner, ReportGenerator

logger = logging.getLogger(__name__)


# Dashboard Views
@login_required
def osint_dashboard(request):
    """لوحة تحكم أدوات OSINT الرئيسية"""
    # إحصائيات عامة
    user_sessions = OSINTSession.objects.filter(user=request.user)
    user_results = OSINTResult.objects.filter(session__user=request.user)
    user_reports = OSINTReport.objects.filter(user=request.user)
    
    stats = {
        'total_tools': OSINTTool.objects.filter(status='active').count(),
        'total_sessions': user_sessions.count(),
        'active_sessions': user_sessions.filter(status='running').count(),
        'completed_sessions': user_sessions.filter(status='completed').count(),
        'total_results': user_results.count(),
        'total_reports': user_reports.count(),
        'success_rate': user_sessions.filter(status='completed').count() / max(user_sessions.count(), 1) * 100,
    }
    
    # أحدث الجلسات
    recent_sessions = user_sessions.order_by('-created_at')[:5]
    
    # أحدث النتائج
    recent_results = user_results.order_by('-discovered_at')[:5]
    
    # أحدث التقارير
    recent_reports = user_reports.order_by('-generated_at')[:5]
    
    # الأدوات الأكثر استخداماً
    popular_tools = OSINTTool.objects.annotate(
        user_usage_count=Count('sessions', filter=Q(sessions__user=request.user))
    ).order_by('-user_usage_count')[:5]
    
    context = {
        'stats': stats,
        'recent_sessions': recent_sessions,
        'recent_results': recent_results,
        'recent_reports': recent_reports,
        'popular_tools': popular_tools,
    }
    
    return render(request, 'osint_tools/dashboard.html', context)


@login_required
def tools_list(request):
    """قائمة أدوات OSINT"""
    tools = OSINTTool.objects.filter(status='active').order_by('name')
    
    # فلترة حسب النوع
    tool_type = request.GET.get('type')
    if tool_type:
        tools = tools.filter(tool_type=tool_type)
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        tools = tools.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(tools, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tool_type': tool_type,
        'search_query': search_query,
        'tool_types': OSINTTool.TOOL_TYPES,
    }
    
    return render(request, 'osint_tools/tools_list.html', context)


@login_required
def tool_detail(request, tool_slug):
    """تفاصيل أداة OSINT"""
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')
    
    # جلسات المستخدم لهذه الأداة
    user_sessions_query = OSINTSession.objects.filter(
        user=request.user, 
        tool=tool
    ).order_by('-created_at')
    
    # إحصائيات الأداة للمستخدم
    user_stats = {
        'sessions_count': user_sessions_query.count(),
        'completed_sessions': user_sessions_query.filter(status='completed').count(),
        'total_results': OSINTResult.objects.filter(session__user=request.user, session__tool=tool).count(),
        'success_rate': user_sessions_query.filter(status='completed').count() / max(user_sessions_query.count(), 1) * 100,
    }
    
    # جلسات المستخدم للعرض (مقطوعة)
    user_sessions = user_sessions_query[:10]
    
    # إعدادات المستخدم للأداة
    user_configs = OSINTConfiguration.objects.filter(
        user=request.user, 
        tool=tool, 
        is_active=True
    )
    
    context = {
        'tool': tool,
        'user_sessions': user_sessions,
        'user_stats': user_stats,
        'user_configs': user_configs,
    }
    
    return render(request, 'osint_tools/tool_detail.html', context)


# API ViewSets
class OSINTToolViewSet(viewsets.ReadOnlyModelViewSet):
    """API للأدوات"""
    queryset = OSINTTool.objects.filter(status='active')
    serializer_class = OSINTToolSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'


class OSINTSessionViewSet(viewsets.ModelViewSet):
    """API للجلسات"""
    serializer_class = OSINTSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OSINTSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OSINTResultViewSet(viewsets.ReadOnlyModelViewSet):
    """API للنتائج"""
    serializer_class = OSINTResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OSINTResult.objects.filter(session__user=self.request.user)


class OSINTReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API للتقارير"""
    serializer_class = OSINTReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OSINTReport.objects.filter(user=self.request.user)


class OSINTConfigurationViewSet(viewsets.ModelViewSet):
    """API للإعدادات"""
    serializer_class = OSINTConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OSINTConfiguration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def sessions_list(request):
    """قائمة جلسات OSINT"""
    sessions = OSINTSession.objects.filter(user=request.user).order_by('-created_at')
    
    # فلترة حسب الحالة
    status_filter = request.GET.get('status')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    # فلترة حسب الأداة
    tool_filter = request.GET.get('tool')
    if tool_filter:
        sessions = sessions.filter(tool_id=tool_filter)
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(
            Q(target__icontains=search_query) |
            Q(tool__name__icontains=search_query)
        )
    
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'tool_filter': tool_filter,
        'search_query': search_query,
        'status_choices': OSINTSession.STATUS_CHOICES,
        'tools': OSINTTool.objects.filter(status='active'),
    }
    
    return render(request, 'osint_tools/sessions_list.html', context)


@login_required
def session_detail(request, session_id):
    """تفاصيل جلسة OSINT"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    
    # النتائج
    results = OSINTResult.objects.filter(session=session).order_by('-discovered_at')
    
    # التقارير
    reports = OSINTReport.objects.filter(session=session).order_by('-generated_at')
    
    # سجل الأنشطة
    activities = OSINTActivityLog.objects.filter(session=session).order_by('-created_at')
    
    context = {
        'session': session,
        'results': results,
        'reports': reports,
        'activities': activities,
    }
    
    return render(request, 'osint_tools/session_detail.html', context)


# AJAX Views
@login_required
def get_session_status(request, session_id):
    """الحصول على حالة الجلسة"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    
    return JsonResponse({
        'status': session.status,
        'progress': session.progress,
        'current_step': session.current_step,
        'results_count': session.results_count,
        'error_message': session.error_message,
        'started_at': session.started_at.isoformat() if session.started_at else None,
        'completed_at': session.completed_at.isoformat() if session.completed_at else None,
    })


@login_required
def get_tool_progress(request, session_id):
    """الحصول على تقدم الأداة"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    
    return JsonResponse({
        'progress': session.progress,
        'current_step': session.current_step,
        'status': session.status,
    })


@login_required
def export_results(request, session_id):
    """تصدير نتائج الجلسة"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    format_type = request.GET.get('format', 'json')
    
    results = OSINTResult.objects.filter(session=session)
    
    if format_type == 'json':
        data = {
            'session': {
                'id': session.id,
                'tool': session.tool.name,
                'target': session.target,
                'created_at': session.created_at.isoformat(),
                'status': session.status,
            },
            'results': [
                {
                    'title': result.title,
                    'type': result.result_type,
                    'description': result.description,
                    'url': result.url,
                    'confidence': result.confidence,
                    'source': result.source,
                    'discovered_at': result.discovered_at.isoformat(),
                    'raw_data': result.raw_data,
                }
                for result in results
            ]
        }
        
        response = HttpResponse(
            json.dumps(data, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="osint_results_{session_id}.json"'
        
    elif format_type == 'csv':
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="osint_results_{session_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['العنوان', 'النوع', 'الوصف', 'الرابط', 'الثقة', 'المصدر', 'تاريخ الاكتشاف'])
        
        for result in results:
            writer.writerow([
                result.title,
                result.result_type,
                result.description,
                result.url,
                result.confidence,
                result.source,
                result.discovered_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    else:
        raise Http404("صيغة غير مدعومة")
    
    return response


# API Endpoints
@csrf_exempt
@require_http_methods(["GET"])
def api_stats(request):
    """إحصائيات API"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'غير مصرح'}, status=401)
    
    user = request.user
    
    # إحصائيات الجلسات
    sessions_stats = OSINTSession.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed')),
        running=Count('id', filter=Q(status='running'))
    )
    
    # إحصائيات النتائج
    results_stats = OSINTResult.objects.filter(session__user=user).aggregate(
        total=Count('id'),
        high_confidence=Count('id', filter=Q(confidence='high')),
        medium_confidence=Count('id', filter=Q(confidence='medium')),
        low_confidence=Count('id', filter=Q(confidence='low'))
    )
    
    # إحصائيات التقارير
    reports_stats = OSINTReport.objects.filter(user=user).aggregate(
        total=Count('id'),
        total_downloads=Count('downloaded_count')
    )
    
    stats = {
        'sessions': sessions_stats,
        'results': results_stats,
        'reports': reports_stats,
        'success_rate': (sessions_stats['completed'] / max(sessions_stats['total'], 1)) * 100,
    }
    
    return JsonResponse(stats)


@login_required
def test_tool(request, tool_slug):
    """اختبار أداة OSINT"""
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')
    
    try:
        # إنشاء جلسة مؤقتة للاختبار
        session = OSINTSession.objects.create(
            user=request.user,
            tool=tool,
            target='test@example.com',  # هدف اختبار
            config={},
            options={},
            status='testing'
        )
        
        # اختبار الأداة
        runner = OSINTToolRunner(session)
        test_result = runner.test()
        
        # حذف الجلسة المؤقتة
        session.delete()
        
        return JsonResponse({
            'success': test_result['success'],
            'message': test_result['message'],
            'error': test_result['error']
        })
        
    except Exception as e:
        logger.error(f"خطأ في اختبار الأداة: {e}")
        return JsonResponse({
            'success': False,
            'message': 'حدث خطأ في اختبار الأداة',
            'error': str(e)
        })


@login_required
def run_tool(request, tool_slug):
    """تشغيل أداة OSINT"""
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')
    
    try:
        data = json.loads(request.body)
        target = data.get('target', '').strip()
        config_id = data.get('config_id')
        options = data.get('options', {})
        
        if not target:
            return JsonResponse({
                'success': False, 
                'message': 'الهدف مطلوب'
            })
        
        # الحصول على الإعدادات
        config = None
        if config_id:
            try:
                config = OSINTConfiguration.objects.get(
                    id=config_id, 
                    user=request.user, 
                    tool=tool, 
                    is_active=True
                )
            except OSINTConfiguration.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'الإعداد غير موجود'
                })
        
        # إنشاء جلسة جديدة
        session = OSINTSession.objects.create(
            user=request.user,
            tool=tool,
            target=target,
            config=config.config_data if config else {},
            options=options,
            status='pending'
        )
        
        # تسجيل النشاط
        OSINTActivityLog.objects.create(
            user=request.user,
            session=session,
            action='tool_run',
            description=f'تم تشغيل أداة {tool.name} للهدف: {target}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # تشغيل الأداة مباشرة (بدون threading)
        try:
            runner = OSINTToolRunner(session)
            runner.run()
        except Exception as e:
            logger.error(f"خطأ في تشغيل الأداة: {e}")
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم بدء تشغيل الأداة بنجاح',
            'session_id': session.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'بيانات غير صحيحة'
        })
    except Exception as e:
        logger.error(f"خطأ في تشغيل الأداة: {e}")
        return JsonResponse({
            'success': False, 
            'message': 'حدث خطأ في الخادم'
        })


@login_required
def generate_report(request, session_id):
    """إنشاء تقرير للجلسة"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type', 'summary')
        format_type = data.get('format', 'html')
        include_raw_data = data.get('include_raw_data', False)
        include_metadata = data.get('include_metadata', True)
        include_charts = data.get('include_charts', True)
        
        # إنشاء التقرير
        report = OSINTReport.objects.create(
            user=request.user,
            session=session,
            title=f"تقرير {session.tool.name} - {session.target}",
            report_type=report_type,
            format=format_type,
            include_raw_data=include_raw_data,
            include_metadata=include_metadata,
            include_charts=include_charts
        )
        
        # إنشاء محتوى التقرير
        generator = ReportGenerator(report)
        generator.generate()
        
        # تسجيل النشاط
        OSINTActivityLog.objects.create(
            user=request.user,
            session=session,
            action='report_generated',
            description=f'تم إنشاء تقرير {report_type} بصيغة {format_type}',
            details={
                'report_id': report.id,
                'report_type': report_type,
                'format': format_type
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء التقرير بنجاح',
            'report_id': report.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'بيانات غير صحيحة'
        })
    except Exception as e:
        logger.error(f"خطأ في إنشاء التقرير: {e}")
        return JsonResponse({
            'success': False, 
            'message': 'حدث خطأ في الخادم'
        })


@login_required
def session_results(request, session_id):
    """نتائج جلسة OSINT"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    results = OSINTResult.objects.filter(session=session).order_by('-discovered_at')
    
    # فلترة حسب نوع النتيجة
    result_type = request.GET.get('type')
    if result_type:
        results = results.filter(result_type=result_type)
    
    # فلترة حسب مستوى الثقة
    confidence = request.GET.get('confidence')
    if confidence:
        results = results.filter(confidence=confidence)
    
    paginator = Paginator(results, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'session': session,
        'page_obj': page_obj,
        'result_type': result_type,
        'confidence': confidence,
        'result_types': OSINTResult.RESULT_TYPES,
        'confidence_levels': OSINTResult.CONFIDENCE_LEVELS,
    }
    
    return render(request, 'osint_tools/session_results.html', context)


@login_required
def results_list(request):
    """قائمة النتائج"""
    results = OSINTResult.objects.filter(session__user=request.user).order_by('-discovered_at')
    
    # فلترة حسب نوع النتيجة
    result_type = request.GET.get('type')
    if result_type:
        results = results.filter(result_type=result_type)
    
    # فلترة حسب مستوى الثقة
    confidence = request.GET.get('confidence')
    if confidence:
        results = results.filter(confidence=confidence)
    
    # البحث
    search_query = request.GET.get('search')
    if search_query:
        results = results.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(source__icontains=search_query)
        )
    
    paginator = Paginator(results, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'result_type': result_type,
        'confidence': confidence,
        'search_query': search_query,
        'result_types': OSINTResult.RESULT_TYPES,
        'confidence_levels': OSINTResult.CONFIDENCE_LEVELS,
    }
    
    return render(request, 'osint_tools/results_list.html', context)


@login_required
def result_detail(request, result_id):
    """تفاصيل النتيجة"""
    result = get_object_or_404(OSINTResult, id=result_id, session__user=request.user)
    
    context = {
        'result': result,
    }
    
    return render(request, 'osint_tools/result_detail.html', context)


@login_required
def reports_list(request):
    """قائمة التقارير"""
    reports = OSINTReport.objects.filter(user=request.user).order_by('-generated_at')
    
    # فلترة حسب نوع التقرير
    report_type = request.GET.get('type')
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    # فلترة حسب الصيغة
    format_type = request.GET.get('format')
    if format_type:
        reports = reports.filter(format=format_type)
    
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'report_type': report_type,
        'format_type': format_type,
        'report_types': OSINTReport.REPORT_TYPES,
        'format_choices': OSINTReport.FORMAT_CHOICES,
    }
    
    return render(request, 'osint_tools/reports_list.html', context)


@login_required
def report_detail(request, report_id):
    """تفاصيل التقرير"""
    report = get_object_or_404(OSINTReport, id=report_id, user=request.user)
    
    context = {
        'report': report,
    }
    
    return render(request, 'osint_tools/report_detail.html', context)


@login_required
def download_report(request, report_id):
    """تحميل التقرير"""
    report = get_object_or_404(OSINTReport, id=report_id, user=request.user)
    
    if not report.file:
        raise Http404("ملف التقرير غير موجود")
    
    # زيادة عدد التحميلات
    report.downloaded_count += 1
    report.save(update_fields=['downloaded_count'])
    
    response = HttpResponse(report.file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{report.file.name}"'
    
    return response


@login_required
def configurations_list(request):
    """قائمة الإعدادات"""
    configs = OSINTConfiguration.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    
    # فلترة حسب الأداة
    tool_filter = request.GET.get('tool')
    if tool_filter:
        configs = configs.filter(tool_id=tool_filter)
    
    context = {
        'configs': configs,
        'tool_filter': tool_filter,
        'tools': OSINTTool.objects.filter(status='active'),
    }
    
    return render(request, 'osint_tools/configurations_list.html', context)


@login_required
def configuration_detail(request, config_id):
    """تفاصيل الإعداد"""
    config = get_object_or_404(OSINTConfiguration, id=config_id, user=request.user)
    
    context = {
        'config': config,
    }
    
    return render(request, 'osint_tools/configuration_detail.html', context)


@login_required
def osint_analytics(request):
    """صفحة التحليلات"""
    user = request.user
    
    # إحصائيات الجلسات
    sessions_stats = OSINTSession.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed')),
        running=Count('id', filter=Q(status='running'))
    )
    
    # إحصائيات النتائج
    results_stats = OSINTResult.objects.filter(session__user=user).aggregate(
        total=Count('id'),
        high_confidence=Count('id', filter=Q(confidence='high')),
        medium_confidence=Count('id', filter=Q(confidence='medium')),
        low_confidence=Count('id', filter=Q(confidence='low'))
    )
    
    # إحصائيات الأدوات
    tools_stats = OSINTTool.objects.annotate(
        user_usage_count=Count('sessions', filter=Q(sessions__user=user))
    ).filter(user_usage_count__gt=0).order_by('-user_usage_count')[:10]
    
    # إحصائيات شهرية
    from datetime import datetime, timedelta
    last_month = timezone.now() - timedelta(days=30)
    monthly_stats = OSINTSession.objects.filter(
        user=user,
        created_at__gte=last_month
    ).extra(select={'month': "strftime('%%Y-%%m', created_at)"}).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'sessions_stats': sessions_stats,
        'results_stats': results_stats,
        'tools_stats': tools_stats,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'osint_tools/analytics.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def test_tool(request, tool_slug):
    """اختبار أداة OSINT"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'غير مصرح'}, status=401)
    
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')
    
    try:
        data = json.loads(request.body)
        test_target = data.get('target', 'test@example.com')
        
        # إنشاء جلسة اختبار
        session = OSINTSession.objects.create(
            user=request.user,
            tool=tool,
            target=test_target,
            status='running'
        )
        
        # تشغيل اختبار سريع
        runner = OSINTToolRunner(session)
        test_result = runner.test()
        
        session.status = 'completed' if test_result['success'] else 'failed'
        session.error_message = test_result.get('error', '')
        session.save()
        
        return JsonResponse({
            'success': test_result['success'],
            'message': test_result.get('message', 'تم الاختبار'),
            'session_id': session.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'بيانات غير صحيحة'}, status=400)
    except Exception as e:
        logger.error(f"خطأ في اختبار الأداة: {e}")
        return JsonResponse({'error': 'حدث خطأ في الخادم'}, status=500)
