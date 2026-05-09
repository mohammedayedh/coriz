import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from osint_tools.models import OSINTSession, OSINTReport
from osint_tools.utils import ReportGenerator
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
session = OSINTSession.objects.filter(user=user, status='completed').last()

report = OSINTReport(
    user=user,
    session=session,
    report_type='summary',
    format='json',
    title="Test Summary Report"
)

try:
    generator = ReportGenerator(report)
    print("Results:", list(generator.results))
except Exception as e:
    print(f"ERROR: {e}")

