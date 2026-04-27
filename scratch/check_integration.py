import os
import sys
import json
import subprocess
from django.core.management import BaseCommand

# إضافة مسار المشروع لتشغيل السكريبت بشكل مستقل إذا لزم الأمر
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
import django
django.setup()

from osint_tools.models import OSINTTool

def check_tools_integration():
    print("🧪 بدء فحص الربط البرمجي الشامل...")
    print("-" * 60)
    
    tools = OSINTTool.objects.filter(status='active')
    results = []
    
    for tool in tools:
        print(f"🔎 فحص الأداة: {tool.name} ({tool.slug})")
        
        # 1. التحقق من وجود الملف
        file_path = os.path.join(os.getcwd(), tool.tool_path, tool.executable_name)
        file_exists = os.path.exists(file_path)
        
        # 2. التحقق من قالب الأمر
        # نختبر تشغيل الأداة مع هدف وهمي للتحقق من المخرجات
        test_target = "test.com" if tool.tool_type in ['domain', 'general'] else "test@example.com"
        if tool.tool_type == 'username': test_target = "testuser"
        if tool.tool_type == 'ip': test_target = "8.8.8.8"
        
        cmd = tool.command_template.format(
            tool_path=tool.tool_path,
            executable_name=tool.executable_name,
            target=test_target
        ).split()
        
        json_valid = False
        output = ""
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = process.stdout
            json.loads(output) # محاولة تحليل المخرجات كـ JSON
            json_valid = True
        except Exception as e:
            error = str(e)
        
        status = {
            'name': tool.name,
            'file_exists': file_exists,
            'file_path': file_path,
            'json_valid': json_valid,
            'cmd': ' '.join(cmd)
        }
        results.append(status)
        
        if file_exists and json_valid:
            print(f"   ✅ الربط سليم 100%")
        else:
            print(f"   ❌ يوجد خلل:")
            if not file_exists: print(f"      - الملف غير موجود في المسار: {file_path}")
            if not json_valid: print(f"      - المخرجات ليست JSON صالح. المخرجات المستلمة: {output[:100]}...")

    print("-" * 60)
    return results

if __name__ == "__main__":
    check_tools_integration()
