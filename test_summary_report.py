import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from osint_tools.models import OSINTSession, OSINTReport
from osint_tools.utils import ReportGenerator
from django.contrib.auth import get_user_model
import json

User = get_user_model()
user = User.objects.first()
session = OSINTSession.objects.filter(user=user, status='completed').last()

report = OSINTReport.objects.create(
    user=user,
    session=session,
    report_type='summary',
    format='json',
    title="Test Summary Report"
)

try:
    generator = ReportGenerator(report)
    generator.generate()
    print("SUCCESS: Report generated!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

