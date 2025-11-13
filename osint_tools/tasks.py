import logging

from celery import shared_task
from django.utils import timezone

from .models import OSINTSession, OSINTReport, OSINTActivityLog
from .utils import OSINTToolRunner, ReportGenerator

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_osint_tool(self, session_id):
    """تنفيذ أداة OSINT داخل مهمة Celery"""
    try:
        session = OSINTSession.objects.select_related('tool', 'user').get(pk=session_id)
    except OSINTSession.DoesNotExist:
        logger.error("لم يتم العثور على جلسة OSINT بالمعرف %s", session_id)
        return {'status': 'missing', 'session_id': session_id}

    session.celery_task_id = self.request.id
    session.status = 'running'
    session.progress = 5
    session.current_step = 'جاري تهيئة الأداة...'
    session.started_at = session.started_at or timezone.now()
    session.save(update_fields=['celery_task_id', 'status', 'progress', 'current_step', 'started_at', 'updated_at'])

    runner = OSINTToolRunner(session)

    try:
        runner.run()
    except Exception as exc:  # pragma: no cover - يتم تسجيل الاستثناء وإعادة رفعه
        logger.exception("فشل تشغيل أداة OSINT للجلسة %s", session_id)
        session.refresh_from_db()
        session.status = 'failed'
        session.error_message = str(exc)
        session.current_step = f'فشل التنفيذ: {exc}'
        session.save(update_fields=['status', 'error_message', 'current_step', 'updated_at'])

        OSINTActivityLog.objects.create(
            user=session.user,
            session=session,
            action='error_occurred',
            description=f'فشل تشغيل الأداة {session.tool.name}',
            details={'session_id': session.id, 'error': str(exc)}
        )
        raise

    session.refresh_from_db()

    if session.status != 'completed':
        session.status = 'completed'
        session.progress = 100
        session.current_step = 'تم الانتهاء بنجاح!'
        session.completed_at = session.completed_at or timezone.now()
        if session.started_at and session.completed_at:
            session.duration = session.completed_at - session.started_at
        session.save(update_fields=['status', 'progress', 'current_step', 'completed_at', 'duration', 'updated_at'])

    return {'status': session.status, 'session_id': session.id}


@shared_task(bind=True)
def generate_osint_report(self, report_id):
    """إنشاء تقرير OSINT داخل مهمة Celery"""
    try:
        report = OSINTReport.objects.select_related('session', 'user').get(pk=report_id)
    except OSINTReport.DoesNotExist:
        logger.error("لم يتم العثور على تقرير OSINT بالمعرف %s", report_id)
        return {'status': 'missing', 'report_id': report_id}

    report.celery_task_id = self.request.id
    report.status = 'running'
    report.error_message = ''
    report.save(update_fields=['status', 'error_message'])

    try:
        generator = ReportGenerator(report)
        generator.generate()
    except Exception as exc:  # pragma: no cover - يتم تسجيل الاستثناء وإعادة رفعه
        logger.exception("فشل إنشاء تقرير OSINT %s", report_id)
        report.refresh_from_db()
        report.status = 'failed'
        report.error_message = str(exc)
        report.save(update_fields=['status', 'error_message'])

        OSINTActivityLog.objects.create(
            user=report.user,
            session=report.session,
            action='error_occurred',
            description=f'فشل إنشاء تقرير للأداة {report.session.tool.name}',
            details={'report_id': report.id, 'error': str(exc)}
        )
        raise

    report.refresh_from_db()
    report.status = 'completed'
    report.error_message = ''
    report.save(update_fields=['status', 'error_message'])

    OSINTActivityLog.objects.create(
        user=report.user,
        session=report.session,
        action='report_generated',
        description=f'تم إنشاء تقرير {report.report_type} بصيغة {report.format}',
        details={'report_id': report.id, 'report_type': report.report_type, 'format': report.format}
    )

    return {'status': report.status, 'report_id': report.id}
