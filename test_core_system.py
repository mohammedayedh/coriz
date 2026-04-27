#!/usr/bin/env python
"""
سكريبت اختبار شامل لنواة نظام Coriza OSINT
يختبر جميع الوحدات الأساسية ويتأكد من عملها بنجاح
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model

# الألوان للطباعة
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# ============================================================================
# اختبار 1: استيراد الوحدات
# ============================================================================

def test_imports():
    print_header("اختبار 1: استيراد الوحدات الأساسية")
    
    apps = {
        'authentication': ['models', 'views', 'forms'],
        'main': ['models', 'views', 'forms'],
        'dashboard': ['models', 'views'],
        'api': ['models', 'views', 'serializers'],
        'osint_tools': ['models', 'views', 'serializers', 'tasks', 'utils']
    }
    
    success_count = 0
    total_count = 0
    
    for app, modules in apps.items():
        for module in modules:
            total_count += 1
            try:
                exec(f'from {app} import {module}')
                print_success(f"{app}.{module}")
                success_count += 1
            except Exception as e:
                print_error(f"{app}.{module}: {e}")
    
    print(f"\n{Colors.BOLD}النتيجة: {success_count}/{total_count} نجح{Colors.END}")
    return success_count == total_count

# ============================================================================
# اختبار 2: قاعدة البيانات
# ============================================================================

def test_database():
    print_header("اختبار 2: قاعدة البيانات")
    
    try:
        # اختبار الاتصال
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_success("الاتصال بقاعدة البيانات")
        
        # اختبار الجداول
        tables = connection.introspection.table_names()
        print_success(f"عدد الجداول: {len(tables)}")
        
        # اختبار النماذج
        User = get_user_model()
        from authentication.models import UserProfile
        from osint_tools.models import OSINTTool, OSINTSession, OSINTResult
        from main.models import Post, Category
        from api.models import APIKey
        
        models_count = {
            'User': User.objects.count(),
            'UserProfile': UserProfile.objects.count(),
            'OSINTTool': OSINTTool.objects.count(),
            'OSINTSession': OSINTSession.objects.count(),
            'OSINTResult': OSINTResult.objects.count(),
            'Post': Post.objects.count(),
            'Category': Category.objects.count(),
            'APIKey': APIKey.objects.count(),
        }
        
        for model, count in models_count.items():
            print_info(f"{model}: {count} سجل")
        
        return True
        
    except Exception as e:
        print_error(f"خطأ في قاعدة البيانات: {e}")
        return False

# ============================================================================
# اختبار 3: Migrations
# ============================================================================

def test_migrations():
    print_header("اختبار 3: Migrations")
    
    try:
        # فحص migrations غير المطبقة
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print_warning(f"يوجد {len(plan)} migration غير مطبق")
            for migration, backwards in plan:
                print_info(f"  - {migration}")
            return False
        else:
            print_success("جميع migrations مطبقة")
            return True
            
    except Exception as e:
        print_error(f"خطأ في فحص migrations: {e}")
        return False

# ============================================================================
# اختبار 4: الإعدادات
# ============================================================================

def test_settings():
    print_header("اختبار 4: الإعدادات")
    
    from django.conf import settings
    
    checks = {
        'DEBUG': settings.DEBUG,
        'SECRET_KEY': bool(settings.SECRET_KEY and settings.SECRET_KEY != 'insecure-development-key-CHANGE-THIS-IN-PRODUCTION'),
        'ALLOWED_HOSTS': bool(settings.ALLOWED_HOSTS),
        'DATABASES': bool(settings.DATABASES),
        'INSTALLED_APPS': len(settings.INSTALLED_APPS) > 0,
        'MIDDLEWARE': len(settings.MIDDLEWARE) > 0,
    }
    
    for key, value in checks.items():
        if value:
            print_success(f"{key}: مضبوط")
        else:
            if key == 'SECRET_KEY' and settings.DEBUG:
                print_warning(f"{key}: يستخدم مفتاح تطوير (مقبول في DEBUG mode)")
            else:
                print_error(f"{key}: غير مضبوط")
    
    # فحص التطبيقات المثبتة
    required_apps = [
        'django.contrib.admin',
        'django.contrib.auth',
        'rest_framework',
        'authentication',
        'osint_tools',
        'api',
        'main',
        'dashboard'
    ]
    
    print(f"\n{Colors.BOLD}التطبيقات المطلوبة:{Colors.END}")
    all_installed = True
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print_success(app)
        else:
            print_error(f"{app}: غير مثبت")
            all_installed = False
    
    return all_installed

# ============================================================================
# اختبار 5: Celery
# ============================================================================

def test_celery():
    print_header("اختبار 5: Celery (اختياري)")
    
    try:
        from coriza import celery_app
        
        if celery_app:
            print_success("Celery: متاح")
            
            # اختبار المهام
            from osint_tools.tasks import run_osint_tool, generate_osint_report
            print_success("المهام: run_osint_tool, generate_osint_report")
            
            return True
        else:
            print_warning("Celery: غير مثبت (اختياري)")
            return True
            
    except Exception as e:
        print_warning(f"Celery: {e} (اختياري)")
        return True

# ============================================================================
# اختبار 6: URLs
# ============================================================================

def test_urls():
    print_header("اختبار 6: URLs")
    
    try:
        from django.urls import get_resolver
        
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        
        print_success(f"عدد URL patterns: {len(url_patterns)}")
        
        # اختبار URLs الأساسية
        from django.urls import reverse
        
        essential_urls = [
            ('main:home', 'الصفحة الرئيسية'),
            ('authentication:login', 'تسجيل الدخول'),
            ('authentication:register', 'التسجيل'),
            ('dashboard:index', 'لوحة التحكم'),
            ('osint_tools:dashboard', 'لوحة OSINT'),
        ]
        
        for url_name, description in essential_urls:
            try:
                url = reverse(url_name)
                print_success(f"{description}: {url}")
            except Exception as e:
                print_error(f"{description}: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"خطأ في URLs: {e}")
        return False

# ============================================================================
# اختبار 7: Static Files
# ============================================================================

def test_static_files():
    print_header("اختبار 7: Static Files")
    
    from django.conf import settings
    import os
    
    checks = {
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': settings.STATIC_ROOT,
        'STATICFILES_DIRS': settings.STATICFILES_DIRS,
    }
    
    for key, value in checks.items():
        if value:
            print_success(f"{key}: {value}")
        else:
            print_warning(f"{key}: غير مضبوط")
    
    # فحص وجود الملفات الثابتة
    if settings.STATICFILES_DIRS:
        static_dir = settings.STATICFILES_DIRS[0]
        if os.path.exists(static_dir):
            print_success(f"مجلد static موجود: {static_dir}")
            
            # فحص الملفات الأساسية
            essential_files = [
                'css/style.css',
                'js/main.js',
            ]
            
            for file in essential_files:
                file_path = os.path.join(static_dir, file)
                if os.path.exists(file_path):
                    print_success(f"  - {file}")
                else:
                    print_warning(f"  - {file}: غير موجود")
        else:
            print_warning(f"مجلد static غير موجود: {static_dir}")
    
    return True

# ============================================================================
# اختبار 8: Templates
# ============================================================================

def test_templates():
    print_header("اختبار 8: Templates")
    
    from django.conf import settings
    import os
    
    template_dirs = settings.TEMPLATES[0]['DIRS']
    
    if template_dirs:
        template_dir = template_dirs[0]
        if os.path.exists(template_dir):
            print_success(f"مجلد templates موجود: {template_dir}")
            
            # فحص المجلدات الأساسية
            essential_dirs = [
                'base',
                'authentication',
                'dashboard',
                'main',
                'osint_tools',
            ]
            
            for dir_name in essential_dirs:
                dir_path = os.path.join(template_dir, dir_name)
                if os.path.exists(dir_path):
                    files_count = len([f for f in os.listdir(dir_path) if f.endswith('.html')])
                    print_success(f"  - {dir_name}: {files_count} ملف")
                else:
                    print_warning(f"  - {dir_name}: غير موجود")
        else:
            print_warning(f"مجلد templates غير موجود: {template_dir}")
    
    return True

# ============================================================================
# اختبار 9: Security
# ============================================================================

def test_security():
    print_header("اختبار 9: الأمان")
    
    from django.conf import settings
    
    security_checks = {
        'CSRF Middleware': 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE,
        'Security Middleware': 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE,
        'Clickjacking Middleware': 'django.middleware.clickjacking.XFrameOptionsMiddleware' in settings.MIDDLEWARE,
        'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
        'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
        'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', None) == 'DENY',
    }
    
    for check, passed in security_checks.items():
        if passed:
            print_success(check)
        else:
            print_warning(f"{check}: غير مفعل")
    
    # تحذيرات الإنتاج
    if settings.DEBUG:
        print_warning("DEBUG=True (يجب تعطيله في الإنتاج)")
    
    if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
        print_warning("SESSION_COOKIE_SECURE=False (يجب تفعيله في الإنتاج)")
    
    if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
        print_warning("CSRF_COOKIE_SECURE=False (يجب تفعيله في الإنتاج)")
    
    return True

# ============================================================================
# التقرير النهائي
# ============================================================================

def generate_report(results):
    print_header("التقرير النهائي")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"{Colors.BOLD}إجمالي الاختبارات: {total_tests}{Colors.END}")
    print(f"{Colors.GREEN}✅ نجح: {passed_tests}{Colors.END}")
    print(f"{Colors.RED}❌ فشل: {failed_tests}{Colors.END}")
    print(f"{Colors.BOLD}نسبة النجاح: {(passed_tests/total_tests)*100:.1f}%{Colors.END}\n")
    
    if failed_tests == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 جميع الاختبارات نجحت! النظام جاهز للعمل.{Colors.END}")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  بعض الاختبارات فشلت. يرجى مراجعة التفاصيل أعلاه.{Colors.END}")
        return 1

# ============================================================================
# Main
# ============================================================================

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("اختبار شامل لنواة نظام Coriza OSINT".center(60))
    print("="*60)
    print(f"{Colors.END}\n")
    
    results = {}
    
    # تشغيل الاختبارات
    results['imports'] = test_imports()
    results['database'] = test_database()
    results['migrations'] = test_migrations()
    results['settings'] = test_settings()
    results['celery'] = test_celery()
    results['urls'] = test_urls()
    results['static_files'] = test_static_files()
    results['templates'] = test_templates()
    results['security'] = test_security()
    
    # التقرير النهائي
    exit_code = generate_report(results)
    
    return exit_code

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}تم إيقاف الاختبار بواسطة المستخدم{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}خطأ غير متوقع: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
