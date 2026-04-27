from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class DashboardWidget(models.Model):
    """نموذج عناصر لوحة التحكم"""
    WIDGET_TYPES = [
        ('chart', 'رسم بياني'),
        ('table', 'جدول'),
        ('metric', 'مقياس'),
        ('list', 'قائمة'),
        ('card', 'بطاقة'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم العنصر")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name="نوع العنصر")
    position_x = models.PositiveIntegerField(default=0, verbose_name="الموضع X")
    position_y = models.PositiveIntegerField(default=0, verbose_name="الموضع Y")
    width = models.PositiveIntegerField(default=4, verbose_name="العرض")
    height = models.PositiveIntegerField(default=3, verbose_name="الارتفاع")
    config = models.JSONField(default=dict, blank=True, verbose_name="الإعدادات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "عنصر لوحة التحكم"
        verbose_name_plural = "عناصر لوحة التحكم"
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return self.name


class UserDashboard(models.Model):
    """نموذج لوحة تحكم المستخدم"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard', verbose_name="المستخدم")
    widgets = models.ManyToManyField(DashboardWidget, blank=True, verbose_name="العناصر")
    layout_config = models.JSONField(default=dict, blank=True, verbose_name="إعدادات التخطيط")
    theme = models.CharField(max_length=20, default='light', verbose_name="المظهر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "لوحة تحكم المستخدم"
        verbose_name_plural = "لوحات تحكم المستخدمين"
    
    def __str__(self):
        return f"لوحة تحكم {self.user.username}"


class ActivityLog(models.Model):
    """نموذج سجل الأنشطة"""
    ACTION_TYPES = [
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('create', 'إنشاء'),
        ('update', 'تحديث'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
        ('download', 'تحميل'),
        ('upload', 'رفع'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name="المستخدم")
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name="الإجراء")
    object_type = models.CharField(max_length=50, verbose_name="نوع الكائن")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="معرف الكائن")
    description = models.TextField(verbose_name="الوصف")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="بيانات إضافية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "سجل نشاط"
        verbose_name_plural = "سجلات الأنشطة"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class Notification(models.Model):
    """نموذج الإشعارات"""
    NOTIFICATION_TYPES = [
        ('info', 'معلومات'),
        ('success', 'نجح'),
        ('warning', 'تحذير'),
        ('error', 'خطأ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="المستخدم")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name="نوع الإشعار")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    action_url = models.URLField(blank=True, null=True, verbose_name="رابط الإجراء")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="بيانات إضافية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القراءة")
    
    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class UserSession(models.Model):
    """نموذج جلسات المستخدم"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name="المستخدم")
    session_key = models.CharField(max_length=40, unique=True, verbose_name="مفتاح الجلسة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="آخر نشاط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "جلسة مستخدم"
        verbose_name_plural = "جلسات المستخدمين"
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:8]}..."


class SystemMetrics(models.Model):
    """نموذج مقاييس النظام"""
    metric_name = models.CharField(max_length=100, verbose_name="اسم المقياس")
    metric_value = models.FloatField(verbose_name="قيمة المقياس")
    metric_unit = models.CharField(max_length=20, blank=True, null=True, verbose_name="وحدة القياس")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="بيانات إضافية")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    
    class Meta:
        verbose_name = "مقياس نظام"
        verbose_name_plural = "مقاييس النظام"
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value}"


class BackupLog(models.Model):
    """نموذج سجل النسخ الاحتياطية"""
    STATUS_CHOICES = [
        ('started', 'بدأ'),
        ('completed', 'اكتمل'),
        ('failed', 'فشل'),
    ]
    
    backup_name = models.CharField(max_length=200, verbose_name="اسم النسخة")
    backup_type = models.CharField(max_length=50, verbose_name="نوع النسخة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="الحالة")
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="مسار الملف")
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="حجم الملف")
    error_message = models.TextField(blank=True, null=True, verbose_name="رسالة الخطأ")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ البداية")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاكتمال")
    
    class Meta:
        verbose_name = "سجل نسخة احتياطية"
        verbose_name_plural = "سجلات النسخ الاحتياطية"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.backup_name} - {self.get_status_display()}"