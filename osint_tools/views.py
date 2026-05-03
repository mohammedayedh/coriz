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
    InvestigationCase, OSINTTool, OSINTSession, OSINTResult, OSINTReport, 
    OSINTConfiguration, OSINTActivityLog
)
from .serializers import (
    OSINTToolSerializer, OSINTSessionSerializer, OSINTResultSerializer,
    OSINTReportSerializer, OSINTConfigurationSerializer
)
from .utils import OSINTToolRunner, ReportGenerator
from .tasks import run_osint_tool, generate_osint_report

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
def cases_list(request):
    """قائمة القضايا"""
    cases = InvestigationCase.objects.filter(user=request.user).order_by('-created_at')
    
    # التعامل مع طلب إنشاء قضية جديدة (مبسط)
    if request.method == 'POST' and 'title' in request.POST:
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        if title:
            InvestigationCase.objects.create(
                user=request.user,
                title=title,
                description=description
            )
            return redirect('osint_tools:cases_list')
            
    paginator = Paginator(cases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'osint_tools/cases_list.html', {'page_obj': page_obj})


@login_required
def case_detail(request, case_id):
    """تفاصيل القضية المتقدمة"""
    from .models import OSINTResult
    from django.db.models import Count, Q
    
    case = get_object_or_404(InvestigationCase, id=case_id, user=request.user)
    sessions = case.sessions.all().order_by('-created_at')
    
    # حساب الإحصائيات للقضية
    stats = OSINTResult.objects.filter(session__investigation_case=case).aggregate(
        total_results=Count('id'),
        high_confidence=Count('id', filter=Q(confidence='high')),
        sources_count=Count('source', distinct=True)
    )
    
    # جلب آخر النتائج المكتشفة في هذه القضية
    recent_results = OSINTResult.objects.filter(session__investigation_case=case).order_by('-discovered_at')[:10]
    
    context = {
        'case': case, 
        'sessions': sessions,
        'stats': stats,
        'recent_results': recent_results
    }
    
    return render(request, 'osint_tools/case_detail.html', context)


@login_required
@require_http_methods(["POST"])
def update_case_notes(request, case_id):
    """تحديث ملاحظات القضية عبر AJAX"""
    case = get_object_or_404(InvestigationCase, id=case_id, user=request.user)
    try:
        data = json.loads(request.body)
        case.notes = data.get('notes', '')
        case.save()
        return JsonResponse({'success': True, 'message': 'تم حفظ الملاحظات بنجاح'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
def tools_list(request):
    """قائمة أدوات OSINT"""
    try:
        user_clearance = request.user.profile.clearance_level
    except Exception:
        user_clearance = 'L1'
        
    # فلترة الأدوات حسب مستوى تصريح المستخدم
    tools = OSINTTool.objects.filter(
        status='active',
        required_clearance__lte=user_clearance
    ).order_by('name')
    
    # فلترة حسب النوع
    tool_type = request.GET.get('type', '')
    if tool_type:
        tools = tools.filter(tool_type=tool_type)
    
    # البحث
    search_query = request.GET.get('search', '')
    if search_query:
        tools = tools.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(tools, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tool_type': tool_type if tool_type else None,
        'search_query': search_query if search_query else None,
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
    
    # القضايا المفتوحة للمستخدم
    user_cases = InvestigationCase.objects.filter(
        user=request.user,
        status__in=['open', 'in_progress']
    ).order_by('-created_at')
    
    context = {
        'tool': tool,
        'user_sessions': user_sessions,
        'user_stats': user_stats,
        'user_configs': user_configs,
        'user_cases': user_cases,
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


@login_required
def export_all_results(request):
    """تصدير جميع النتائج (مع الفلترة الاختيارية)"""
    format_type = request.GET.get('format', 'json')
    
    # الحصول على جميع النتائج للمستخدم الحالي
    results = OSINTResult.objects.filter(session__user=request.user)
    
    # تطبيق الفلاتر إذا وجدت
    tool_filter = request.GET.get('tool')
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if tool_filter:
        results = results.filter(session__tool__slug=tool_filter)
    if status_filter:
        results = results.filter(session__status=status_filter)
    if date_from:
        results = results.filter(discovered_at__gte=date_from)
    if date_to:
        results = results.filter(discovered_at__lte=date_to)
    
    if format_type == 'json':
        data = {
            'export_info': {
                'exported_at': timezone.now().isoformat(),
                'total_results': results.count(),
                'user': request.user.username,
            },
            'results': [
                {
                    'session_id': result.session.id,
                    'tool': result.session.tool.name,
                    'target': result.session.target,
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
        response['Content-Disposition'] = f'attachment; filename="osint_all_results_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
    elif format_type == 'csv':
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="osint_all_results_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['رقم الجلسة', 'الأداة', 'الهدف', 'العنوان', 'النوع', 'الوصف', 'الرابط', 'الثقة', 'المصدر', 'تاريخ الاكتشاف'])
        
        for result in results:
            writer.writerow([
                result.session.id,
                result.session.tool.name,
                result.session.target,
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
@require_http_methods(["GET"])
def api_stats(request):
    """
    إحصائيات API
    
    إصلاح المشكلة الحرجة #4: إزالة csrf_exempt غير الضروري
    هذا endpoint هو GET فقط ولا يحتاج csrf_exempt أصلاً
    GET requests لا تحتاج CSRF protection
    """
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


# ─── test_tool: تعريف واحد موحّد ──────────────────────────────────────────────


@login_required
def run_tool(request, tool_slug):
    """تشغيل أداة OSINT"""
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')
    
    try:
        data = json.loads(request.body)
        target = data.get('target', '').strip()
        config_id = data.get('config_id')
        case_id = data.get('case_id')
        options = data.get('options', {})
        
        if not target:
            return JsonResponse({
                'success': False, 
                'message': 'الهدف مطلوب'
            })
        
        # التحقق من وجود جلسة نشطة لنفس الأداة والهدف
        active_session = OSINTSession.objects.filter(
            user=request.user,
            tool=tool,
            target=target,
            status__in=['pending', 'running']
        ).first()
        
        if active_session:
            return JsonResponse({
                'success': False,
                'message': f'يوجد جلسة نشطة بالفعل لهذا الهدف (جلسة #{active_session.id}). يرجى الانتظار حتى تكتمل أو إلغاؤها.',
                'session_id': active_session.id
            })
            
        case = None
        if case_id:
            case = InvestigationCase.objects.filter(id=case_id, user=request.user).first()
        
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
            investigation_case=case,
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
        
        # تشغيل الأداة مباشرة (synchronous) - موثوق على السيرفر
        from .utils import OSINTToolRunner
        runner = OSINTToolRunner(session)
        runner.run()

        return JsonResponse({
            'success': True,
            'message': 'تم تشغيل الأداة بنجاح',
            'session_id': session.id,
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
            include_charts=include_charts,
            status='pending'
        )
        
        # جدولة إنشاء التقرير عبر Celery
        task = generate_osint_report.delay(report.id)
        report.celery_task_id = task.id
        report.save(update_fields=['celery_task_id', 'updated_at'])

        return JsonResponse({
            'success': True,
            'message': 'تم جدولة إنشاء التقرير بنجاح',
            'report_id': report.id,
            'task_id': task.id
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
@require_http_methods(["POST"])
def generate_session_report(request, session_id):
    """إنشاء تقرير للجلسة من صفحة النتائج"""
    return generate_report(request, session_id)


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
def generate_case_report(request, case_id):
    """توليد تقرير استخباراتي شامل للقضية"""
    case = get_object_or_404(InvestigationCase, id=case_id, user=request.user)
    sessions = case.sessions.all().prefetch_related('results')
    
    # حساب الإحصائيات
    total_results = 0
    high_confidence = 0
    all_results = []
    
    for session in sessions:
        res_list = session.results.all()
        total_results += res_list.count()
        high_confidence += res_list.filter(confidence='high').count()
        all_results.extend(res_list)

    context = {
        'case': case,
        'sessions': sessions,
        'total_results': total_results,
        'high_confidence': high_confidence,
        'all_results': all_results[:100], # الحد من النتائج للتقرير
        'generated_at': timezone.now()
    }
    
    return render(request, 'osint_tools/case_report_template.html', context)


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
    """صفحة التحليلات المتقدمة"""
    user = request.user
    from django.db.models import Count, Q, Avg
    from django.db.models.functions import TruncMonth, TruncDate
    from datetime import timedelta
    
    # 1. إحصائيات الجلسات العامة
    sessions_stats = OSINTSession.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed')),
        running=Count('id', filter=Q(status='running'))
    )
    
    # 2. إحصائيات النتائج والجودة
    results_stats = OSINTResult.objects.filter(session__user=user).aggregate(
        total=Count('id'),
        high_confidence=Count('id', filter=Q(confidence='high')),
        medium_confidence=Count('id', filter=Q(confidence='medium')),
        low_confidence=Count('id', filter=Q(confidence='low')),
        avg_confidence=Avg('confidence_score')
    )
    
    # 3. توزيع أنواع الأدوات (Tool Type Distribution)
    type_distribution = OSINTSession.objects.filter(user=user).values('tool__tool_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 4. أداء الأدوات (Tool Performance)
    tools_performance_raw = OSINTTool.objects.filter(sessions__user=user).annotate(
        total_runs=Count('sessions', filter=Q(sessions__user=user)),
        success_runs=Count('sessions', filter=Q(sessions__user=user, sessions__status='completed')),
        found_results=Count('sessions__results', filter=Q(sessions__user=user))
    ).order_by('-total_runs')[:10]
    
    tools_performance = []
    for tool in tools_performance_raw:
        success_rate = (tool.success_runs / tool.total_runs * 100) if tool.total_runs > 0 else 0
        tools_performance.append({
            'name': tool.name,
            'total_runs': tool.total_runs,
            'success_runs': tool.success_runs,
            'found_results': tool.found_results,
            'success_rate': round(success_rate, 1)
        })
    
    # 5. النشاط اليومي لآخر 14 يوم
    two_weeks_ago = timezone.now() - timedelta(days=14)
    daily_activity = OSINTSession.objects.filter(
        user=user,
        created_at__gte=two_weeks_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # 6. توزيع النتائج حسب النوع (Result Type Distribution)
    results_by_type = OSINTResult.objects.filter(session__user=user).values('result_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # 7. متوسط النتائج لكل جلسة
    avg_results = 0
    if sessions_stats['total'] > 0:
        avg_results = results_stats['total'] / sessions_stats['total']
        
    # 8. أفضل المصادر (Top Sources)
    top_sources = OSINTResult.objects.filter(session__user=user).values('source').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'sessions_stats': sessions_stats,
        'results_stats': results_stats,
        'type_distribution': type_distribution,
        'tools_performance': tools_performance,
        'daily_activity': daily_activity,
        'results_by_type': results_by_type,
        'avg_results_per_session': round(avg_results, 1),
        'top_sources': top_sources,
    }
    
    return render(request, 'osint_tools/analytics.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def test_tool(request, tool_slug):
    """
    اختبار أداة OSINT للتحقق من وجودها وقابليتها للتشغيل.
    GET  → يُعيد معلومات الأداة
    POST → يُشغّل اختبارًا فعليًا
    """
    tool = get_object_or_404(OSINTTool, slug=tool_slug, status='active')

    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'tool': tool.name,
            'tool_type': tool.tool_type,
            'status': tool.status,
        })

    # ── POST: اختبار فعلي ──────────────────────────────────────────────────────
    try:
        data = json.loads(request.body) if request.body else {}
        test_target = data.get('target', 'test@example.com').strip() or 'test@example.com'

        # إنشاء جلسة مؤقتة للاختبار (لا تُربط بقضية)
        session = OSINTSession.objects.create(
            user=request.user,
            tool=tool,
            target=test_target,
            config={},
            options={},
        )

        runner = OSINTToolRunner(session)
        test_result = runner.test()

        # تحديث حالة الجلسة باستخدام الدوال الرسمية
        if test_result['success']:
            session.mark_completed(step_label='Tool test passed')
        else:
            session.mark_failed(test_result.get('error') or 'Tool test failed')

        return JsonResponse({
            'success': test_result['success'],
            'message': test_result.get('message', 'تم الاختبار'),
            'error': test_result.get('error'),
            'session_id': session.id,
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'بيانات JSON غير صحيحة'}, status=400)
    except Exception as e:
        logger.error('خطأ في اختبار الأداة %s: %s', tool_slug, e)
        return JsonResponse({'success': False, 'error': 'حدث خطأ في الخادم'}, status=500)


# ---------------------------------------------------------
# Utilities Views (Client-Side OSINT Utilities)
# ---------------------------------------------------------

@login_required
def utilities_dashboard(request):
    """لوحة الأدوات المساعدة"""
    return render(request, 'osint_tools/utilities/dashboard.html')

@login_required
def hash_generator(request):
    """مُولّد الهاش المتقدم"""
    return render(request, 'osint_tools/utilities/hash_generator.html')

@login_required
def coder_decoder(request):
    """تشفير وفك تشفير البيانات"""
    return render(request, 'osint_tools/utilities/coder_decoder.html')

@login_required
def timestamp_converter(request):
    """محول الطوابع الزمنية"""
    return render(request, 'osint_tools/utilities/timestamp_converter.html')

@login_required
def json_formatter(request):
    """منسق ومدقق JSON"""
    return render(request, 'osint_tools/utilities/json_formatter.html')

@login_required
def text_diff(request):
    """مقارن النصوص"""
    return render(request, 'osint_tools/utilities/text_diff.html')

@login_required
def cybersecurity_resources(request):
    """مصادر الأمن السيبراني"""
    return render(request, 'osint_tools/cybersecurity_resources.html')

@login_required
def simple_search_interface(request):
    """واجهة البحث المبسطة الموحدة"""
    # إحصائيات حقيقية من قاعدة البيانات
    total_tools = OSINTTool.objects.filter(status='active').count()
    
    # حساب عدد المصادر الفعلية (الأدوات التي تعمل بدون API)
    web_sources = OSINTTool.objects.filter(
        status='active',
        source_type='open',
        api_key_required=False
    ).count()
    
    # إجمالي الجلسات للمستخدم
    total_searches = OSINTSession.objects.filter(user=request.user).count()
    
    # إحصائيات إضافية
    completed_searches = OSINTSession.objects.filter(
        user=request.user,
        status='completed'
    ).count()
    
    total_results = OSINTResult.objects.filter(
        session__user=request.user
    ).count()
    
    context = {
        'total_tools': total_tools,
        'total_sources': web_sources if web_sources > 0 else total_tools,
        'total_searches': total_searches,
        'completed_searches': completed_searches,
        'total_results': total_results,
    }
    
    return render(request, 'osint_tools/simple_search_interface.html', context)


@login_required
def ajax_session_results(request, session_id):
    """الحصول على نتائج الجلسة عبر AJAX"""
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    results = OSINTResult.objects.filter(session=session).order_by('-discovered_at')
    
    results_data = [
        {
            'id': result.id,
            'title': result.title,
            'description': result.description,
            'url': result.url,
            'result_type': result.get_result_type_display(),
            'confidence': result.get_confidence_display(),
            'source': result.source,
            'raw_data': result.raw_data,
            'metadata': result.metadata,
            'discovered_at': result.discovered_at.isoformat(),
        }
        for result in results
    ]
    
    return JsonResponse({
        'success': True,
        'results': results_data,
        'count': len(results_data)
    })


@login_required
def password_generator(request):
    """مُولّد كلمات المرور الآمنة"""
    return render(request, 'osint_tools/utilities/password_generator.html')

@login_required
def jwt_inspector(request):
    """مُفتش توكن المصادقة JWT"""
    return render(request, 'osint_tools/utilities/jwt_inspector.html')


# ---------------------------------------------------------
# Server-Side OSINT Intelligence Tool Views
# ---------------------------------------------------------
import urllib.request
import urllib.parse
import socket
import ssl
import re

def _fetch_json(url, timeout=10, headers=None):
    """Helper: fetch and parse JSON from a URL"""
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Coriza-OSINT/1.0')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


@login_required
def ip_lookup(request):
    """صفحة أداة IP Lookup"""
    return render(request, 'osint_tools/intel/ip_lookup.html')


@login_required
def domain_recon(request):
    """صفحة أداة Domain Recon"""
    return render(request, 'osint_tools/intel/domain_recon.html')


@login_required
def email_scanner(request):
    """صفحة أداة Email Scanner"""
    return render(request, 'osint_tools/intel/email_scanner.html')


@login_required
def virustotal_scan(request):
    """صفحة أداة VirusTotal Scan"""
    return render(request, 'osint_tools/intel/virustotal_scan.html')


@login_required
def threat_intel(request):
    """صفحة استخبارات التهديدات"""
    return render(request, 'osint_tools/intel/threat_intel.html')


@login_required
def phone_analyzer(request):
    """صفحة محلل أرقام الهواتف"""
    return render(request, 'osint_tools/intel/phone_analyzer.html')


@login_required
def subdomain_enum(request):
    """صفحة استخراج النطاقات الفرعية"""
    return render(request, 'osint_tools/intel/subdomain_enum.html')


# --- JSON API Endpoints (called by frontend JS) ---

@login_required
@require_http_methods(["POST"])
def api_ip_lookup(request):
    """استعلام معلومات عنوان IP"""
    try:
        data = json.loads(request.body)
        ip_address = data.get('ip', '').strip()
        if not ip_address:
            return JsonResponse({'success': False, 'error': 'يرجى إدخال عنوان IP'}, status=400)

        # Validate basic IP / hostname format
        if not re.match(r'^[a-zA-Z0-9.:\-_]+$', ip_address):
            return JsonResponse({'success': False, 'error': 'عنوان IP غير صالح'}, status=400)

        result = _fetch_json(f'http://ip-api.com/json/{urllib.parse.quote(ip_address)}?fields=66846719')

        if result.get('status') == 'fail':
            return JsonResponse({'success': False, 'error': result.get('message', 'فشل الاستعلام')})

        return JsonResponse({'success': True, 'data': result})

    except Exception as e:
        logger.error(f'IP Lookup error: {e}')
        return JsonResponse({'success': False, 'error': 'فشل الاتصال بخدمة الاستعلام. تحقق من الاتصال.'}, status=500)


@login_required
@require_http_methods(["POST"])
def api_domain_recon(request):
    """استطلاع معلومات النطاق (Domain Recon)"""
    try:
        data = json.loads(request.body)
        domain = data.get('domain', '').strip().lower()
        if not domain:
            return JsonResponse({'success': False, 'error': 'يرجى إدخال اسم نطاق'}, status=400)

        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain).split('/')[0]

        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]{1,253}[a-zA-Z0-9]$', domain):
            return JsonResponse({'success': False, 'error': 'اسم النطاق غير صالح'}, status=400)

        results = {'domain': domain}

        # --- WHOIS via hackertarget (free, no key required) ---
        try:
            whois_raw = urllib.request.urlopen(
                f'https://api.hackertarget.com/whois/?q={urllib.parse.quote(domain)}',
                timeout=12
            ).read().decode('utf-8', errors='replace')
            results['whois'] = whois_raw[:3000]  # limit size
        except Exception:
            results['whois'] = 'تعذّر جلب بيانات WHOIS'

        # --- DNS Records via hackertarget ---
        dns_types = {'A': 'dnslookup', 'MX': 'mxlookup'}
        results['dns'] = {}
        for record_type, endpoint in dns_types.items():
            try:
                dns_raw = urllib.request.urlopen(
                    f'https://api.hackertarget.com/{endpoint}/?q={urllib.parse.quote(domain)}',
                    timeout=10
                ).read().decode('utf-8', errors='replace')
                results['dns'][record_type] = dns_raw[:2000]
            except Exception:
                results['dns'][record_type] = 'تعذّر الاستعلام'

        # --- IP resolution ---
        try:
            resolved_ip = socket.gethostbyname(domain)
            results['resolved_ip'] = resolved_ip
        except Exception:
            results['resolved_ip'] = 'تعذّر الحل'

        return JsonResponse({'success': True, 'data': results})

    except Exception as e:
        logger.error(f'Domain Recon error: {e}')
        return JsonResponse({'success': False, 'error': 'حدث خطأ في الاستطلاع'}, status=500)


@login_required
@require_http_methods(["POST"])
def api_email_scanner(request):
    """فحص صحة وسمعة عنوان البريد الإلكتروني"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()

        if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return JsonResponse({'success': False, 'error': 'بريد إلكتروني غير صالح'}, status=400)

        domain = email.split('@')[1]
        results = {'email': email, 'domain': domain, 'checks': {}}

        # Check MX records (domain validity)
        try:
            mx_raw = urllib.request.urlopen(
                f'https://api.hackertarget.com/mxlookup/?q={urllib.parse.quote(domain)}',
                timeout=10
            ).read().decode('utf-8', errors='replace')
            has_mx = 'error' not in mx_raw.lower() and len(mx_raw.strip()) > 0
            results['checks']['mx_records'] = {
                'status': 'valid' if has_mx else 'invalid',
                'details': mx_raw[:500] if has_mx else 'لا توجد سجلات MX - البريد غير قابل للتسليم'
            }
        except Exception:
            results['checks']['mx_records'] = {'status': 'error', 'details': 'فشل الفحص'}

        # Validate email syntax more thoroughly
        syntax_valid = bool(re.match(
            r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email
        ))
        results['checks']['syntax'] = {
            'status': 'valid' if syntax_valid else 'invalid',
            'details': 'الصياغة صحيحة' if syntax_valid else 'صياغة البريد غير صحيحة'
        }

        # Domain reputation via IP resolution
        try:
            ip = socket.gethostbyname(domain)
            results['checks']['domain_resolution'] = {
                'status': 'valid',
                'details': f'النطاق يُحل إلى IP: {ip}'
            }
        except Exception:
            results['checks']['domain_resolution'] = {
                'status': 'invalid',
                'details': 'لا يمكن حل النطاق - قد يكون البريد وهمياً'
            }

        return JsonResponse({'success': True, 'data': results})

    except Exception as e:
        logger.error(f'Email Scanner error: {e}')
        return JsonResponse({'success': False, 'error': 'حدث خطأ في الفحص'}, status=500)


@login_required
@require_http_methods(["POST"])
def api_virustotal_scan(request):
    """فحص الروابط والملفات عبر VirusTotal"""
    try:
        from django.conf import settings
        vt_api_key = getattr(settings, 'VIRUSTOTAL_API_KEY', '')

        data = json.loads(request.body)
        target = data.get('target', '').strip()
        scan_type = data.get('scan_type', 'url')  # url or hash

        if not target:
            return JsonResponse({'success': False, 'error': 'يرجى إدخال هدف الفحص'}, status=400)

        if not vt_api_key:
            # Return a demo/simulation result when no API key is configured
            return JsonResponse({
                'success': True,
                'demo': True,
                'message': 'نمط العرض التوضيحي - أضف VIRUSTOTAL_API_KEY في الإعدادات للحصول على نتائج حقيقية',
                'data': {
                    'target': target,
                    'scan_type': scan_type,
                    'stats': {'malicious': 0, 'suspicious': 2, 'undetected': 68, 'harmless': 5, 'total': 75},
                    'threat_names': [],
                    'permalink': f'https://www.virustotal.com/gui/{scan_type}/{target}',
                }
            })

        # Real VirusTotal API call
        if scan_type == 'url':
            endpoint = 'https://www.virustotal.com/api/v3/urls'
            post_data = urllib.parse.urlencode({'url': target}).encode()
            req = urllib.request.Request(endpoint, data=post_data, method='POST')
        else:
            # hash lookup
            endpoint = f'https://www.virustotal.com/api/v3/files/{urllib.parse.quote(target)}'
            req = urllib.request.Request(endpoint, method='GET')

        req.add_header('x-apikey', vt_api_key)
        req.add_header('User-Agent', 'Coriza-OSINT/1.0')

        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            vt_data = json.loads(resp.read().decode())

        # Parse VT response
        attributes = vt_data.get('data', {}).get('attributes', {})
        last_stats = attributes.get('last_analysis_stats', {})
        results_map = attributes.get('last_analysis_results', {})

        malicious_engines = [
            {'engine': k, 'result': v.get('result'), 'category': v.get('category')}
            for k, v in results_map.items()
            if v.get('category') in ('malicious', 'suspicious')
        ]

        return JsonResponse({
            'success': True,
            'demo': False,
            'data': {
                'target': target,
                'scan_type': scan_type,
                'stats': last_stats,
                'threat_names': list(set(v.get('result') for v in results_map.values() if v.get('result'))),
                'malicious_engines': malicious_engines[:20],
                'permalink': attributes.get('url', f'https://www.virustotal.com')
            }
        })

    except Exception as e:
        logger.error(f'VirusTotal error: {e}')
        return JsonResponse({'success': False, 'error': 'فشل الاتصال بـ VirusTotal'}, status=500)


@login_required
@require_http_methods(["GET"])
def api_threat_feed(request):
    """جلب تغذية استخبارات التهديدات (Threat Intelligence Feed)"""
    try:
        # AlienVault OTX free pulses - no key needed for public feed
        feed_url = 'https://otx.alienvault.com/api/v1/pulses/subscribed?modified_since=2024-01-01&limit=20'
        otx_key = getattr(__import__('django.conf', fromlist=['settings']).settings, 'OTX_API_KEY', '')

        if not otx_key:
            # Return simulated threat intel data
            simulated = [
                {'name': 'APT28 - Fancy Bear Campaign', 'description': 'نشاط مجموعة APT28 الروسية المرتبطة بهجمات التصيد الاحتيالي', 'tlp': 'WHITE', 'severity': 'high', 'tags': ['APT28', 'phishing', 'russia'], 'created': '2026-04-10'},
                {'name': 'Log4Shell Exploitation Wave', 'description': 'استغلال ثغرة Log4Shell في بيئات Java المشغلة على الإنترنت', 'tlp': 'GREEN', 'severity': 'critical', 'tags': ['log4j', 'RCE', 'java'], 'created': '2026-04-09'},
                {'name': 'Ransomware - LockBit 3.0 IOCs', 'description': 'مؤشرات الاختراق الخاصة بمجموعة LockBit 3.0 الفدية', 'tlp': 'WHITE', 'severity': 'critical', 'tags': ['ransomware', 'lockbit', 'IOC'], 'created': '2026-04-08'},
                {'name': 'Credential Stuffing via Leaked Databases', 'description': 'هجمات حشو بيانات الاعتماد باستخدام قواعد بيانات مسربة', 'tlp': 'GREEN', 'severity': 'medium', 'tags': ['credential-stuffing', 'breach'], 'created': '2026-04-07'},
                {'name': 'Malicious npm Package Supply Chain', 'description': 'اكتشاف حزمة npm خبيثة تستهدف سلسلة torii المعروفة', 'tlp': 'WHITE', 'severity': 'high', 'tags': ['supply-chain', 'npm', 'malware'], 'created': '2026-04-06'},
            ]
            return JsonResponse({'success': True, 'demo': True, 'data': simulated})

        req = urllib.request.Request(feed_url)
        req.add_header('X-OTX-API-KEY', otx_key)
        req.add_header('User-Agent', 'Coriza-OSINT/1.0')
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            feed_data = json.loads(resp.read().decode())

        pulses = [
            {
                'name': p.get('name'),
                'description': p.get('description', '')[:200],
                'tlp': p.get('tlp', 'WHITE'),
                'severity': 'high' if p.get('adversary') else 'medium',
                'tags': p.get('tags', [])[:5],
                'created': p.get('created', '')[:10],
            }
            for p in feed_data.get('results', [])[:20]
        ]

        return JsonResponse({'success': True, 'demo': False, 'data': pulses})

    except Exception as e:
        logger.error(f'Threat Feed error: {e}')
        return JsonResponse({'success': False, 'error': 'فشل جلب بيانات تغذية التهديدات'}, status=500)


import phonenumbers
from phonenumbers import geocoder, carrier, timezone as ph_timezone

@login_required
@require_http_methods(["POST"])
def api_phone_analyzer(request):
    """تحليل رقم الهاتف"""
    try:
        data = json.loads(request.body)
        phone = data.get('target', '').strip()
        if not phone:
            return JsonResponse({'success': False, 'error': 'يرجى إدخال رقم هاتف'}, status=400)
            
        if not phone.startswith('+'):
            phone = '+' + phone
            
        parsed_number = phonenumbers.parse(phone, None)
        
        if not phonenumbers.is_valid_number(parsed_number):
            return JsonResponse({'success': False, 'error': 'رقم غير صالح للتنسيق الدولي'})

        country = geocoder.description_for_number(parsed_number, "ar") or geocoder.description_for_number(parsed_number, "en")
        carrier_name = carrier.name_for_number(parsed_number, "ar") or carrier.name_for_number(parsed_number, "en")
        time_zones = ph_timezone.time_zones_for_number(parsed_number)

        results = {
            'target': phone,
            'is_valid': True,
            'country': country or 'غير معروف',
            'carrier': carrier_name or 'غير معروف',
            'timezones': list(time_zones),
            'formatted': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        }
        
        return JsonResponse({'success': True, 'demo': False, 'data': results})
        
    except phonenumbers.phonenumberutil.NumberParseException:
         return JsonResponse({'success': False, 'error': 'الرقم يبدو غير صالح للتحليل'})
    except Exception as e:
        logger.error(f'Phone Analyzer error: {e}')
        return JsonResponse({'success': False, 'error': 'فشل تحليل الهاتف'}, status=500)


@login_required
@require_http_methods(["POST"])
def api_subdomain_enum(request):
    """استخراج النطاقات الفرعية عبر crt.sh"""
    try:
        data = json.loads(request.body)
        domain = data.get('target', '').strip().lower()
        if not domain:
            return JsonResponse({'success': False, 'error': 'يرجى إدخال اسم نطاق'}, status=400)

        domain = re.sub(r'^https?://', '', domain).split('/')[0]

        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]{1,253}[a-zA-Z0-9]$', domain):
             return JsonResponse({'success': False, 'error': 'اسم النطاق غير صالح'})
             
        results = {'domain': domain, 'subdomains': []}
        
        try:
            req = urllib.request.Request(f'https://crt.sh/?q=%.{urllib.parse.quote(domain)}&output=json')
            req.add_header('User-Agent', 'Coriza-OSINT/1.0')
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                crt_data = json.loads(resp.read().decode())
                
            seen = set()
            for entry in crt_data:
                name = entry.get('name_value', '').lower()
                if '*' not in name and name.endswith(domain):
                    for sub in name.split('\\n'):
                        if sub not in seen:
                            seen.add(sub)
                            
            results['subdomains'] = list(seen)[:500]
            
        except Exception as e:
            logger.error(f'crt.sh error: {e}')
            return JsonResponse({'success': False, 'error': 'فشل جلب النطاقات من المصدر.'}, status=500)

        return JsonResponse({'success': True, 'demo': False, 'data': results})

    except Exception as e:
        logger.error(f'Subdomain Enum error: {e}')
        return JsonResponse({'success': False, 'error': 'حدث خطأ في عملية البحث'}, status=500)



@login_required
@require_http_methods(["GET"])
def ajax_completed_sessions(request):
    """الحصول على قائمة الجلسات المكتملة للمستخدم (لإنشاء التقارير)"""
    try:
        # جلب الجلسات المكتملة فقط
        sessions = OSINTSession.objects.filter(
            user=request.user,
            status='completed'
        ).select_related('tool').order_by('-completed_at')[:50]
        
        sessions_data = [
            {
                'id': session.id,
                'tool_name': session.tool.name,
                'target': session.target,
                'results_count': session.results_count,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'created_at': session.created_at.isoformat(),
            }
            for session in sessions
        ]
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data,
            'count': len(sessions_data)
        })
        
    except Exception as e:
        logger.error(f'Error fetching completed sessions: {e}')
        return JsonResponse({
            'success': False,
            'error': 'حدث خطأ في جلب الجلسات',
            'sessions': []
        }, status=500)

@csrf_exempt
@login_required
def ajax_run_tool(request):
    """تشغيل أداة OSINT عبر AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        tool_slug = data.get('tool_slug')
        target = data.get('target')
        
        if not tool_slug or not target:
            return JsonResponse({'success': False, 'error': 'Missing tool_slug or target'}, status=400)
            
        tool = get_object_or_404(OSINTTool, slug=tool_slug)
        
        # التحقق من وجود جلسة نشطة لنفس الهدف والأداة (لمنع التكرار)
        active_session = OSINTSession.objects.filter(
            user=request.user,
            tool=tool,
            target=target,
            status='running'
        ).first()
        
        if active_session:
            return JsonResponse({
                'success': False, 
                'error': f'يوجد جلسة نشطة بالفعل لهذا الهدف (جلسة #{active_session.id})',
                'session_id': active_session.id
            })

        # إنشاء جلسة جديدة
        session = OSINTSession.objects.create(
            user=request.user,
            tool=tool,
            target=target,
            status='pending',
            progress=0,
            current_step='جاري التحضير...'
        )
        
        # تشغيل الأداة (إذا كان Celery مفعلاً سيعمل في الخلفية، وإذا لم يكن سيعمل الآن)
        from .tasks import run_osint_tool_task
        if hasattr(run_osint_tool_task, 'delay'):
            run_osint_tool_task.delay(session.id)
        else:
            run_osint_tool_task(session.id)
            
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'message': 'بدأت عملية الفحص بنجاح'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
