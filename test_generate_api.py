import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from osint_tools.models import OSINTSession

User = get_user_model()
user = User.objects.first()
session = OSINTSession.objects.filter(user=user, status='completed').last()

client = Client()
client.force_login(user)

response = client.post(f'/osint/sessions/{session.id}/report/', 
    data='{"report_type":"summary","format":"pdf"}',
    content_type='application/json')

print("Status:", response.status_code)
print("Content:", response.content.decode())
