from django.apps import AppConfig


class OsintToolsConfig(AppConfig):
    """تكوين تطبيق أدوات OSINT"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'osint_tools'
    verbose_name = 'أدوات OSINT المتقدمة'
    
    def ready(self):
        """تهيئة التطبيق عند البدء"""
        # استيراد الإشارات هنا لتجنب مشاكل الاستيراد الدائري
        try:
            import osint_tools.signals
        except ImportError:
            pass
