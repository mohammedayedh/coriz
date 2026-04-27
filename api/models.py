from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class APIKey(models.Model):
    """نموذج مفاتيح API"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys', verbose_name="المستخدم")
    name = models.CharField(max_length=100, verbose_name="اسم المفتاح")
    key = models.CharField(max_length=64, unique=True, verbose_name="المفتاح")
    secret = models.CharField(max_length=64, verbose_name="السر")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    permissions = models.JSONField(default=list, blank=True, verbose_name="الصلاحيات")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="آخر استخدام")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "مفتاح API"
        verbose_name_plural = "مفاتيح API"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = str(uuid.uuid4()).replace('-', '')
        if not self.secret:
            self.secret = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
    
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class APIRequest(models.Model):
    """نموذج طلبات API"""
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='requests', verbose_name="مفتاح API")
    endpoint = models.CharField(max_length=200, verbose_name="النقطة النهائية")
    method = models.CharField(max_length=10, verbose_name="الطريقة")
    status_code = models.PositiveIntegerField(verbose_name="رمز الحالة")
    response_time = models.FloatField(verbose_name="وقت الاستجابة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    request_data = models.JSONField(default=dict, blank=True, verbose_name="بيانات الطلب")
    response_data = models.JSONField(default=dict, blank=True, verbose_name="بيانات الاستجابة")
    error_message = models.TextField(blank=True, null=True, verbose_name="رسالة الخطأ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "طلب API"
        verbose_name_plural = "طلبات API"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class APIRateLimit(models.Model):
    """نموذج حدود معدل API"""
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name='rate_limits', verbose_name="مفتاح API")
    endpoint = models.CharField(max_length=200, verbose_name="النقطة النهائية")
    requests_count = models.PositiveIntegerField(default=0, verbose_name="عدد الطلبات")
    window_start = models.DateTimeField(verbose_name="بداية النافذة")
    window_end = models.DateTimeField(verbose_name="نهاية النافذة")
    is_blocked = models.BooleanField(default=False, verbose_name="محظور")
    blocked_until = models.DateTimeField(null=True, blank=True, verbose_name="محظور حتى")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "حد معدل API"
        verbose_name_plural = "حدود معدل API"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint}"


class Webhook(models.Model):
    """نموذج Webhooks"""
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('error', 'خطأ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks', verbose_name="المستخدم")
    name = models.CharField(max_length=100, verbose_name="اسم الـ Webhook")
    url = models.URLField(verbose_name="الرابط")
    events = models.JSONField(default=list, verbose_name="الأحداث")
    secret = models.CharField(max_length=64, verbose_name="السر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_triggered = models.DateTimeField(null=True, blank=True, verbose_name="آخر تشغيل")
    failure_count = models.PositiveIntegerField(default=0, verbose_name="عدد الفشل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)


class WebhookDelivery(models.Model):
    """نموذج تسليم Webhooks"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('delivered', 'تم التسليم'),
        ('failed', 'فشل'),
        ('retrying', 'إعادة المحاولة'),
    ]
    
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries', verbose_name="الـ Webhook")
    event = models.CharField(max_length=100, verbose_name="الحدث")
    payload = models.JSONField(verbose_name="البيانات")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    status_code = models.PositiveIntegerField(null=True, blank=True, verbose_name="رمز الحالة")
    response_body = models.TextField(blank=True, null=True, verbose_name="نص الاستجابة")
    error_message = models.TextField(blank=True, null=True, verbose_name="رسالة الخطأ")
    attempts = models.PositiveIntegerField(default=0, verbose_name="عدد المحاولات")
    max_attempts = models.PositiveIntegerField(default=3, verbose_name="الحد الأقصى للمحاولات")
    next_retry_at = models.DateTimeField(null=True, blank=True, verbose_name="موعد المحاولة التالية")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التسليم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تسليم Webhook"
        verbose_name_plural = "تسليمات Webhooks"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.webhook.name} - {self.event}"


class APIVersion(models.Model):
    """نموذج إصدارات API"""
    version = models.CharField(max_length=20, unique=True, verbose_name="الإصدار")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_deprecated = models.BooleanField(default=False, verbose_name="مهجور")
    deprecation_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الهجر")
    changelog = models.TextField(blank=True, null=True, verbose_name="سجل التغييرات")
    documentation_url = models.URLField(blank=True, null=True, verbose_name="رابط التوثيق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إصدار API"
        verbose_name_plural = "إصدارات API"
        ordering = ['-version']
    
    def __str__(self):
        return f"API v{self.version}"


class APIEndpoint(models.Model):
    """نموذج نقاط نهاية API"""
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم النقطة")
    path = models.CharField(max_length=200, verbose_name="المسار")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="الطريقة")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    version = models.ForeignKey(APIVersion, on_delete=models.CASCADE, related_name='endpoints', verbose_name="الإصدار")
    is_public = models.BooleanField(default=False, verbose_name="عام")
    requires_auth = models.BooleanField(default=True, verbose_name="يتطلب مصادقة")
    rate_limit = models.PositiveIntegerField(default=100, verbose_name="حد المعدل")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "نقطة نهاية API"
        verbose_name_plural = "نقاط نهاية API"
        ordering = ['path', 'method']
        unique_together = ['path', 'method', 'version']
    
    def __str__(self):
        return f"{self.method} {self.path} - v{self.version.version}"