import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from osint_tools.models import OSINTReport
failed = OSINTReport.objects.filter(status='failed')
for r in failed:
    print(f"Report ID: {r.id}, Type: {r.report_type}, Error: {r.error_message}")
