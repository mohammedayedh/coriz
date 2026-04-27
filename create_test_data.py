#!/usr/bin/env python3
"""
سكريبت لإنشاء بيانات تجريبية للاختبار
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
django.setup()

from osint_tools.models import OSINTTool, OSINTSession, OSINTResult
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def create_test_data():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         🧪 إنشاء بيانات تجريبية للاختبار                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # 1. التحقق من وجود مستخدم
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("👤 التحقق من المستخدمين")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    user = User.objects.first()
    if not user:
        print("⚠️  لا يوجد مستخدمين!")
        print("💡 قم بإنشاء مستخدم أولاً:")
        print("   python3 manage.py createsuperuser")
        return
    
    print(f"✅ المستخدم: {user.username}")
    print()
    
    # 2. التحقق من الأدوات
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🛠️  التحقق من الأدوات")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    tools = OSINTTool.objects.filter(status='active')
    if not tools.exists():
        print("⚠️  لا توجد أدوات نشطة!")
        print("💡 قم بإضافة الأدوات أولاً:")
        print("   python3 manage.py add_web_sources")
        return
    
    print(f"✅ عدد الأدوات النشطة: {tools.count()}")
    print()
    
    # 3. إنشاء جلسات تجريبية
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔄 إنشاء جلسات تجريبية")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # أهداف تجريبية
    test_targets = [
        'test@example.com',
        'user@gmail.com',
        'example.com',
        'github.com',
        '8.8.8.8',
        '1.1.1.1',
        'john_doe',
        'test_user',
        'https://example.com/image.jpg',
        'admin@test.com'
    ]
    
    statuses = ['completed', 'running', 'failed', 'pending']
    created_count = 0
    
    for i in range(15):  # إنشاء 15 جلسة
        tool = random.choice(tools)
        target = random.choice(test_targets)
        status = random.choice(statuses)
        
        # تاريخ عشوائي في آخر 30 يوم
        days_ago = random.randint(0, 30)
        created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        session = OSINTSession.objects.create(
            user=user,
            tool=tool,
            target=target,
            status=status,
            progress=random.randint(0, 100) if status == 'running' else (100 if status == 'completed' else 0),
            created_at=created_at,
            started_at=created_at if status != 'pending' else None,
            completed_at=created_at + timedelta(minutes=random.randint(1, 30)) if status == 'completed' else None
        )
        
        # إضافة نتائج للجلسات المكتملة
        if status == 'completed':
            results_count = random.randint(1, 10)
            for j in range(results_count):
                OSINTResult.objects.create(
                    session=session,
                    title=f'نتيجة {j+1} من {tool.name}',
                    description=f'وصف تجريبي للنتيجة {j+1}',
                    result_type=random.choice(['profile', 'email', 'phone', 'domain', 'ip', 'other']),
                    confidence=random.choice(['high', 'medium', 'low']),
                    source=tool.name,
                    url=f'https://example.com/result/{j+1}',
                    discovered_at=created_at + timedelta(minutes=random.randint(1, 20))
                )
        
        created_count += 1
        print(f"  ✅ جلسة {created_count}: {tool.name} - {target} ({status})")
    
    print()
    print(f"✨ تم إنشاء {created_count} جلسة تجريبية بنجاح!")
    print()
    
    # 4. عرض الإحصائيات
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 الإحصائيات النهائية")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    total_sessions = OSINTSession.objects.filter(user=user).count()
    completed = OSINTSession.objects.filter(user=user, status='completed').count()
    running = OSINTSession.objects.filter(user=user, status='running').count()
    failed = OSINTSession.objects.filter(user=user, status='failed').count()
    total_results = OSINTResult.objects.filter(session__user=user).count()
    
    print(f"إجمالي الجلسات: {total_sessions}")
    print(f"  • مكتملة: {completed}")
    print(f"  • قيد التشغيل: {running}")
    print(f"  • فاشلة: {failed}")
    print(f"إجمالي النتائج: {total_results}")
    print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ تم إنشاء البيانات التجريبية بنجاح!")
    print()
    print("🌐 يمكنك الآن زيارة:")
    print("   • قائمة الجلسات: http://127.0.0.1:8000/osint/sessions/")
    print("   • واجهة البحث: http://127.0.0.1:8000/osint/search/")
    print("   • التحليلات: http://127.0.0.1:8000/osint/analytics/")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
