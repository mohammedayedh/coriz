import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coriza.settings")
django.setup()

from osint_tools.models import OSINTTool, OSINTSession
from osint_tools.utils import OSINTToolRunner
from django.contrib.auth import get_user_model
import json

User = get_user_model()

try:
    tool = OSINTTool.objects.get(slug='emailrep-pro')
    print(f"✓ تم العثور على الأداة: {tool.name}")
except OSINTTool.DoesNotExist:
    print("❌ لم يتم العثور على أداة emailrep-pro")
    exit()

user = User.objects.first()
print(f"✓ المستخدم: {user.username}")

session = OSINTSession.objects.create(
    user=user,
    tool=tool,
    target='test@gmail.com',
    config={},
    options={}
)
print(f"✓ تم إنشاء الجلسة #{session.id}")

runner = OSINTToolRunner(session)
print("⏳ جاري تشغيل EmailRep...")
runner.run()

session.refresh_from_db()
print(f"\n📊 النتيجة:")
print(f"   الحالة: {session.status}")
print(f"   التقدم: {session.progress}%")
print(f"   عدد النتائج: {session.results_count}")
print(f"   الأخطاء: {session.error_message}")

for result in session.results.all():
    print(f"   نتيجة: {result.title} - {result.raw_data}")

