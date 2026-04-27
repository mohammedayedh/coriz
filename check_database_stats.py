#!/usr/bin/env python3
"""
سكريبت للتحقق من البيانات في قاعدة البيانات
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
django.setup()

from osint_tools.models import OSINTTool, OSINTSession, OSINTResult
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         📊 فحص البيانات في قاعدة البيانات                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # 1. الأدوات
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🛠️  الأدوات (OSINTTool)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    total_tools = OSINTTool.objects.count()
    active_tools = OSINTTool.objects.filter(status='active').count()
    web_sources = OSINTTool.objects.filter(
        status='active',
        source_type='open',
        api_key_required=False
    ).count()
    
    print(f"إجمالي الأدوات: {total_tools}")
    print(f"الأدوات النشطة: {active_tools}")
    print(f"مصادر الويب (بدون API): {web_sources}")
    print()
    
    # عرض الأدوات النشطة
    if active_tools > 0:
        print("الأدوات النشطة:")
        for tool in OSINTTool.objects.filter(status='active')[:10]:
            api_status = "❌ يحتاج API" if tool.api_key_required else "✅ بدون API"
            print(f"  • {tool.name} ({tool.slug}) - {api_status}")
        if active_tools > 10:
            print(f"  ... و {active_tools - 10} أداة أخرى")
    else:
        print("⚠️  لا توجد أدوات نشطة!")
        print("💡 قم بتشغيل: python3 manage.py add_web_sources")
    print()
    
    # 2. المستخدمين
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("👥 المستخدمين")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    total_users = User.objects.count()
    print(f"إجمالي المستخدمين: {total_users}")
    
    if total_users > 0:
        print("\nالمستخدمين:")
        for user in User.objects.all()[:5]:
            sessions_count = OSINTSession.objects.filter(user=user).count()
            results_count = OSINTResult.objects.filter(session__user=user).count()
            print(f"  • {user.username}")
            print(f"    - الجلسات: {sessions_count}")
            print(f"    - النتائج: {results_count}")
    else:
        print("⚠️  لا يوجد مستخدمين!")
    print()
    
    # 3. الجلسات
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔄 الجلسات (OSINTSession)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    total_sessions = OSINTSession.objects.count()
    completed_sessions = OSINTSession.objects.filter(status='completed').count()
    running_sessions = OSINTSession.objects.filter(status='running').count()
    failed_sessions = OSINTSession.objects.filter(status='failed').count()
    
    print(f"إجمالي الجلسات: {total_sessions}")
    print(f"  • مكتملة: {completed_sessions}")
    print(f"  • قيد التشغيل: {running_sessions}")
    print(f"  • فاشلة: {failed_sessions}")
    
    if total_sessions > 0:
        print("\nآخر 5 جلسات:")
        for session in OSINTSession.objects.order_by('-created_at')[:5]:
            status_icon = {
                'completed': '✅',
                'running': '🔄',
                'failed': '❌',
                'pending': '⏳'
            }.get(session.status, '❓')
            print(f"  {status_icon} {session.tool.name} - {session.target} ({session.status})")
    print()
    
    # 4. النتائج
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 النتائج (OSINTResult)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    total_results = OSINTResult.objects.count()
    high_confidence = OSINTResult.objects.filter(confidence='high').count()
    medium_confidence = OSINTResult.objects.filter(confidence='medium').count()
    low_confidence = OSINTResult.objects.filter(confidence='low').count()
    
    print(f"إجمالي النتائج: {total_results}")
    print(f"  • ثقة عالية: {high_confidence}")
    print(f"  • ثقة متوسطة: {medium_confidence}")
    print(f"  • ثقة منخفضة: {low_confidence}")
    print()
    
    # 5. التوصيات
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💡 التوصيات")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if active_tools == 0:
        print("⚠️  لا توجد أدوات نشطة!")
        print("   قم بتشغيل: python3 manage.py add_web_sources")
        print()
    
    if total_users == 0:
        print("⚠️  لا يوجد مستخدمين!")
        print("   قم بإنشاء مستخدم: python3 manage.py createsuperuser")
        print()
    
    if total_sessions == 0 and active_tools > 0:
        print("💡 لم يتم تشغيل أي جلسات بعد")
        print("   جرب البحث على: http://127.0.0.1:8000/osint/search/")
        print()
    
    if active_tools > 0 and total_users > 0:
        print("✅ قاعدة البيانات جاهزة!")
        print("   يمكنك البدء بالبحث على: http://127.0.0.1:8000/osint/search/")
        print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)
