import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from osint_tools.models import (
    OSINTTool,
    OSINTSession,
    OSINTReport,
    OSINTActivityLog,
)
from osint_tools.tasks import run_osint_tool, generate_osint_report

User = get_user_model()


class OSINTViewsTests(TestCase):
    """اختبارات لواجهات تشغيل الأدوات وإنشاء التقارير"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='strong-pass-123',
            is_verified=True,
        )
        self.client.force_login(self.user)

        self.tool = OSINTTool.objects.create(
            name='Sherlock',
            slug='sherlock',
            description='Test tool',
            tool_type='username',
            status='active',
            icon='fas fa-search',
            color='#00ff00',
            requires_auth=False,
            api_key_required=False,
            rate_limit=10,
            timeout=30,
            tool_path='tools/sherlock',
            executable_name='sherlock.py',
            command_template='python {executable} {target}',
        )

    @patch('osint_tools.views.run_osint_tool.delay')
    def test_run_tool_view_schedules_celery_task(self, mock_delay):
        mock_delay.return_value.id = 'task-123'

        response = self.client.post(
            reverse('osint_tools:run_tool', args=[self.tool.slug]),
            data=json.dumps({'target': 'example', 'options': {'verbose': True}}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('session_id', payload)
        self.assertEqual(payload['task_id'], 'task-123')

        session = OSINTSession.objects.get(id=payload['session_id'])
        mock_delay.assert_called_once_with(session.id)
        self.assertEqual(session.status, 'pending')
        self.assertEqual(session.tool, self.tool)

    @patch('osint_tools.views.generate_osint_report.delay')
    def test_generate_report_view_schedules_celery_task(self, mock_delay):
        mock_delay.return_value.id = 'task-report-1'
        session = OSINTSession.objects.create(
            user=self.user,
            tool=self.tool,
            target='example',
            status='completed',
            progress=100,
        )

        response = self.client.post(
            reverse('osint_tools:generate_report', args=[session.id]),
            data=json.dumps({'report_type': 'summary', 'format': 'html'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('report_id', payload)
        self.assertEqual(payload['task_id'], 'task-report-1')

        report = OSINTReport.objects.get(id=payload['report_id'])
        mock_delay.assert_called_once_with(report.id)
        self.assertEqual(report.status, 'pending')
        self.assertEqual(report.session, session)


class OSINTTasksTests(TestCase):
    """اختبارات لمهام Celery الخاصة بأدوات OSINT"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user2@example.com',
            username='taskuser',
            password='strong-pass-123',
            is_verified=True,
        )

        self.tool = OSINTTool.objects.create(
            name='Infoga',
            slug='infoga',
            description='Email enumeration tool',
            tool_type='email',
            status='active',
            icon='fas fa-envelope',
            color='#ff9900',
            requires_auth=False,
            api_key_required=False,
            rate_limit=20,
            timeout=60,
            tool_path='tools/infoga',
            executable_name='infoga.py',
            command_template='python {executable} {target}',
        )

    @patch('osint_tools.tasks.OSINTToolRunner.run', autospec=True)
    def test_run_osint_tool_task_completes_session(self, mock_runner):
        session = OSINTSession.objects.create(
            user=self.user,
            tool=self.tool,
            target='target@example.com',
            status='pending',
        )

        result = run_osint_tool.apply(args=[session.id]).get()

        session.refresh_from_db()
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(session.status, 'completed')
        self.assertEqual(session.progress, 100)
        self.assertIsNotNone(session.celery_task_id)
        self.assertTrue(
            OSINTActivityLog.objects.filter(session=session, action='session_completed').exists()
        )

    @patch('osint_tools.tasks.ReportGenerator.generate', autospec=True)
    def test_generate_osint_report_task_marks_report_completed(self, mock_generator):
        session = OSINTSession.objects.create(
            user=self.user,
            tool=self.tool,
            target='target@example.com',
            status='completed',
            progress=100,
        )
        report = OSINTReport.objects.create(
            user=self.user,
            session=session,
            title='تقرير تجريبي',
            report_type='summary',
            format='html',
        )

        result = generate_osint_report.apply(args=[report.id]).get()

        report.refresh_from_db()
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(report.status, 'completed')
        self.assertIsNotNone(report.celery_task_id)
        self.assertTrue(
            OSINTActivityLog.objects.filter(session=session, action='report_generated').exists()
        )
