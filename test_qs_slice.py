import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from osint_tools.models import OSINTResult

try:
    qs = OSINTResult.objects.all()[:15]
    print("Exists?", qs.exists())
except Exception as e:
    print("ERROR:", e.__class__.__name__, e)
