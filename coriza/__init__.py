# إصلاح المشكلة الحرجة #1: Celery غير مثبت
# نستورد Celery بشكل آمن لتجنب فشل التطبيق إذا لم يكن مثبتاً
try:
    from .celery import app as celery_app
    __all__ = ("celery_app",)
except ImportError:
    # Celery غير مثبت - التطبيق سيعمل بدون دعم المهام اللاحقة
    celery_app = None
    __all__ = ()
    import warnings
    warnings.warn(
        "Celery is not installed. Background tasks will not be available. "
        "Install celery with: pip install celery redis",
        ImportWarning
    )
