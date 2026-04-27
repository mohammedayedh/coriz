import logging
import uuid

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Define a dummy decorator when Celery is not available
    def shared_task(bind=False, **kwargs):
        def decorator(func):
            return func
        return decorator

from .models import OSINTSession, OSINTReport, OSINTActivityLog
from .utils import OSINTToolRunner, ReportGenerator

logger = logging.getLogger(__name__)

# الحالات التي تعني أن الأداة لا تزال قيد التشغيل
_RUNNING_STATUSES = {'pending', 'running'}


@shared_task(bind=True)
def run_osint_tool(self, session_id):
    """تشغيل أداة OSINT ضمن مهمة Celery."""
    try:
        session = OSINTSession.objects.select_related('tool', 'user').get(pk=session_id)
    except OSINTSession.DoesNotExist:
        logger.error("OSINT session not found with id %s", session_id)
        return {'status': 'missing', 'session_id': session_id}

    task_id = getattr(self.request, 'id', None) or f'local-{session_id}-{uuid.uuid4()}'
    session.mark_running(task_id)

    runner = OSINTToolRunner(session)

    try:
        runner.run()
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to run OSINT tool for session %s", session_id)
        session.mark_failed(str(exc))

        OSINTActivityLog.objects.create(
            user=session.user,
            session=session,
            action='error_occurred',
            description=f'Failed to run tool {session.tool.name}',
            details={'session_id': session.id, 'error': str(exc)},
        )
        raise

    # ✅ إصلاح حرج: نُكمل الجلسة فقط إذا كانت لا تزال في حالة تشغيل
    # الشرط السابق != 'completed' كان يُكمل الجلسات الفاشلة أيضًا!
    session.refresh_from_db()
    if session.status in _RUNNING_STATUSES:
        session.mark_completed()

    OSINTActivityLog.objects.create(
        user=session.user,
        session=session,
        action='session_completed',
        description=f'Tool {session.tool.name} finished with status: {session.status}',
        details={'session_id': session.id, 'final_status': session.status},
    )

    return {'status': session.status, 'session_id': session.id}


@shared_task(bind=True)
def generate_osint_report(self, report_id):
    """توليد تقرير OSINT ضمن مهمة Celery."""
    try:
        report = OSINTReport.objects.select_related('session', 'user').get(pk=report_id)
    except OSINTReport.DoesNotExist:
        logger.error("OSINT report not found with id %s", report_id)
        return {'status': 'missing', 'report_id': report_id}

    task_id = getattr(self.request, 'id', None) or f'local-report-{report_id}-{uuid.uuid4()}'
    report.mark_running(task_id)

    try:
        generator = ReportGenerator(report)
        generator.generate()
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to generate OSINT report %s", report_id)
        report.refresh_from_db()
        report.mark_failed(str(exc))

        OSINTActivityLog.objects.create(
            user=report.user,
            session=report.session,
            action='error_occurred',
            description=f'Failed to generate report for tool {report.session.tool.name}',
            details={'report_id': report.id, 'error': str(exc)},
        )
        raise

    # ✅ نُكمل التقرير فقط إذا كان لا يزال في حالة تشغيل
    report.refresh_from_db()
    if report.status in _RUNNING_STATUSES:
        report.mark_completed()

    OSINTActivityLog.objects.create(
        user=report.user,
        session=report.session,
        action='report_generated',
        description=f'Report {report.report_type} generated in format {report.format}',
        details={
            'report_id': report.id,
            'report_type': report.report_type,
            'format': report.format,
            'final_status': report.status,
        },
    )

    return {'status': report.status, 'report_id': report.id}
