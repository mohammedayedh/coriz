import logging
import uuid

from celery import shared_task
from django.utils import timezone

from .models import OSINTSession, OSINTReport, OSINTActivityLog
from .utils import OSINTToolRunner, ReportGenerator

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_osint_tool(self, session_id):
    """Execute an OSINT tool within a Celery task."""
    try:
        session = OSINTSession.objects.select_related('tool', 'user').get(pk=session_id)
    except OSINTSession.DoesNotExist:
        logger.error("OSINT session not found with id %s", session_id)
        return {'status': 'missing', 'session_id': session_id}

    request_id = getattr(self.request, 'id', None) or f'local-session-{session_id}-{uuid.uuid4()}'
    session.mark_running(request_id)

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
            details={'session_id': session.id, 'error': str(exc)}
        )
        raise

    session.refresh_from_db()

    if session.status != 'completed':
        session.mark_completed()

    return {'status': session.status, 'session_id': session.id}


@shared_task(bind=True)
def generate_osint_report(self, report_id):
    """Generate an OSINT report within a Celery task."""
    try:
        report = OSINTReport.objects.select_related('session', 'user').get(pk=report_id)
    except OSINTReport.DoesNotExist:
        logger.error("OSINT report not found with id %s", report_id)
        return {'status': 'missing', 'report_id': report_id}

    request_id = getattr(self.request, 'id', None) or f'local-report-{report_id}-{uuid.uuid4()}'
    report.mark_running(request_id)

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
            details={'report_id': report.id, 'error': str(exc)}
        )
        raise

    report.refresh_from_db()
    report.mark_completed()

    OSINTActivityLog.objects.create(
        user=report.user,
        session=report.session,
        action='report_generated',
        description=f'Report {report.report_type} generated in format {report.format}',
        details={'report_id': report.id, 'report_type': report.report_type, 'format': report.format}
    )

    return {'status': report.status, 'report_id': report.id}
