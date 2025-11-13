from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class OSINTTool(models.Model):
    """نموذج أدوات OSINT"""
    TOOL_TYPES = [
        ('email', 'البريد الإلكتروني'),
        ('username', 'اسم المستخدم'),
        ('domain', 'النطاق'),
        ('ip', 'عنوان IP'),
        ('phone', 'رقم الهاتف'),
        ('social', 'وسائل التواصل الاجتماعي'),
        ('google', 'Google'),
        ('general', 'عام'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('maintenance', 'صيانة'),
        ('deprecated', 'مهمل'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم الأداة")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="الرابط")
    description = models.TextField(verbose_name="الوصف")
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPES, verbose_name="نوع الأداة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة")
    icon = models.CharField(max_length=50, default='fas fa-search', verbose_name="الأيقونة")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="اللون")
    
    # إعدادات الأداة
    requires_auth = models.BooleanField(default=False, verbose_name="يتطلب مصادقة")
    api_key_required = models.BooleanField(default=False, verbose_name="يتطلب مفتاح API")
    rate_limit = models.PositiveIntegerField(default=100, verbose_name="حد المعدل")
    timeout = models.PositiveIntegerField(default=30, verbose_name="المهلة الزمنية")
    
    # مسار الأداة
    tool_path = models.CharField(max_length=200, verbose_name="مسار الأداة")
    executable_name = models.CharField(max_length=100, verbose_name="اسم الملف التنفيذي")
    command_template = models.TextField(verbose_name="قالب الأمر")
    
    # إعدادات إضافية
    config_schema = models.JSONField(default=dict, blank=True, verbose_name="مخطط الإعدادات")
    supported_formats = models.JSONField(default=list, blank=True, verbose_name="الصيغ المدعومة")
    
    # إحصائيات
    usage_count = models.PositiveIntegerField(default=0, verbose_name="عدد الاستخدامات")
    success_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], verbose_name="معدل النجاح")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "أداة OSINT"
        verbose_name_plural = "أدوات OSINT"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class OSINTSession(models.Model):
    """نموذج جلسات OSINT"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('running', 'قيد التشغيل'),
        ('completed', 'مكتملة'),
        ('failed', 'فشلت'),
        ('cancelled', 'ملغية'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='osint_sessions', verbose_name="المستخدم")
    tool = models.ForeignKey(OSINTTool, on_delete=models.CASCADE, related_name='sessions', verbose_name="الأداة")
    target = models.CharField(max_length=500, verbose_name="الهدف")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    
    # إعدادات الجلسة
    config = models.JSONField(default=dict, blank=True, verbose_name="الإعدادات")
    options = models.JSONField(default=dict, blank=True, verbose_name="الخيارات")
    celery_task_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="معرف مهمة Celery")
    
    # معلومات التقدم
    progress = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="التقدم")
    current_step = models.CharField(max_length=200, blank=True, verbose_name="الخطوة الحالية")
    
    # النتائج
    results_count = models.PositiveIntegerField(default=0, verbose_name="عدد النتائج")
    results_summary = models.JSONField(default=dict, blank=True, verbose_name="ملخص النتائج")
    
    # معلومات التوقيت
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت البدء")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الإكمال")
    duration = models.DurationField(null=True, blank=True, verbose_name="المدة")
    
    # معلومات إضافية
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    log_file = models.FileField(upload_to='osint_logs/', blank=True, null=True, verbose_name="ملف السجل")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "جلسة OSINT"
        verbose_name_plural = "جلسات OSINT"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tool.name} - {self.target}"
    
    def save(self, *args, **kwargs):
        if self.status == 'running' and not self.started_at:
            self.started_at = timezone.now()
        elif self.status in ['completed', 'failed', 'cancelled'] and self.started_at and not self.completed_at:
            self.completed_at = timezone.now()
            self.duration = self.completed_at - self.started_at
        super().save(*args, **kwargs)


class OSINTResult(models.Model):
    """نموذج نتائج OSINT"""
    RESULT_TYPES = [
        ('email', 'بريد إلكتروني'),
        ('username', 'اسم مستخدم'),
        ('profile', 'ملف شخصي'),
        ('domain', 'نطاق'),
        ('ip', 'عنوان IP'),
        ('phone', 'رقم هاتف'),
        ('social_media', 'وسائل التواصل'),
        ('website', 'موقع ويب'),
        ('image', 'صورة'),
        ('document', 'مستند'),
        ('other', 'أخرى'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('high', 'عالي'),
        ('medium', 'متوسط'),
        ('low', 'منخفض'),
        ('unknown', 'غير معروف'),
    ]
    
    session = models.ForeignKey(OSINTSession, on_delete=models.CASCADE, related_name='results', verbose_name="الجلسة")
    result_type = models.CharField(max_length=20, choices=RESULT_TYPES, verbose_name="نوع النتيجة")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(blank=True, verbose_name="الوصف")
    url = models.URLField(blank=True, verbose_name="الرابط")
    
    # البيانات الخام
    raw_data = models.JSONField(default=dict, blank=True, verbose_name="البيانات الخام")
    
    # مستوى الثقة
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS, default='unknown', verbose_name="مستوى الثقة")
    confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], verbose_name="درجة الثقة")
    
    # معلومات إضافية
    source = models.CharField(max_length=100, blank=True, verbose_name="المصدر")
    tags = models.JSONField(default=list, blank=True, verbose_name="العلامات")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="البيانات الوصفية")
    
    # التواريخ
    discovered_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاكتشاف")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "نتيجة OSINT"
        verbose_name_plural = "نتائج OSINT"
        ordering = ['-discovered_at']
    
    def __str__(self):
        return f"{self.title} - {self.session.tool.name}"


class OSINTReport(models.Model):
    """نموذج تقارير OSINT"""
    REPORT_TYPES = [
        ('summary', 'ملخص'),
        ('detailed', 'مفصل'),
        ('executive', 'تنفيذي'),
        ('technical', 'تقني'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('xml', 'XML'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='osint_reports', verbose_name="المستخدم")
    session = models.ForeignKey(OSINTSession, on_delete=models.CASCADE, related_name='reports', verbose_name="الجلسة")
    title = models.CharField(max_length=200, verbose_name="عنوان التقرير")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="نوع التقرير")
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, verbose_name="الصيغة")
    
    # محتوى التقرير
    content = models.TextField(blank=True, verbose_name="المحتوى")
    summary = models.TextField(blank=True, verbose_name="الملخص")
    recommendations = models.TextField(blank=True, verbose_name="التوصيات")
    
    # ملف التقرير
    file = models.FileField(upload_to='osint_reports/', blank=True, null=True, verbose_name="ملف التقرير")
    file_size = models.PositiveIntegerField(default=0, verbose_name="حجم الملف")
    
    # إعدادات التقرير
    include_raw_data = models.BooleanField(default=False, verbose_name="تضمين البيانات الخام")
    include_metadata = models.BooleanField(default=True, verbose_name="تضمين البيانات الوصفية")
    include_charts = models.BooleanField(default=True, verbose_name="تضمين الرسوم البيانية")
    
    # حالة إنشاء التقرير
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'قيد الانتظار'),
            ('running', 'قيد الإنشاء'),
            ('completed', 'مكتمل'),
            ('failed', 'فشل')
        ],
        default='pending',
        verbose_name="الحالة"
    )
    error_message = models.TextField(blank=True, verbose_name="رسالة الخطأ")
    celery_task_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="معرف مهمة Celery")

    # التواريخ
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    downloaded_count = models.PositiveIntegerField(default=0, verbose_name="عدد التحميلات")
    
    class Meta:
        verbose_name = "تقرير OSINT"
        verbose_name_plural = "تقارير OSINT"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.session.tool.name}"


class OSINTConfiguration(models.Model):
    """نموذج إعدادات OSINT"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='osint_configs', verbose_name="المستخدم")
    tool = models.ForeignKey(OSINTTool, on_delete=models.CASCADE, related_name='configurations', verbose_name="الأداة")
    
    # إعدادات الأداة
    config_name = models.CharField(max_length=100, verbose_name="اسم الإعداد")
    config_data = models.JSONField(default=dict, verbose_name="بيانات الإعداد")
    
    # إعدادات API
    api_keys = models.JSONField(default=dict, blank=True, verbose_name="مفاتيح API")
    proxy_settings = models.JSONField(default=dict, blank=True, verbose_name="إعدادات البروكسي")
    
    # إعدادات الأداء
    timeout = models.PositiveIntegerField(default=30, verbose_name="المهلة الزمنية")
    retry_count = models.PositiveIntegerField(default=3, verbose_name="عدد المحاولات")
    concurrent_requests = models.PositiveIntegerField(default=5, verbose_name="الطلبات المتزامنة")
    
    # إعدادات الخصوصية
    anonymize_results = models.BooleanField(default=False, verbose_name="إخفاء هوية النتائج")
    store_results = models.BooleanField(default=True, verbose_name="حفظ النتائج")
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "إعداد OSINT"
        verbose_name_plural = "إعدادات OSINT"
        unique_together = ['user', 'tool', 'config_name']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.tool.name} - {self.config_name}"


class OSINTActivityLog(models.Model):
    """نموذج سجل أنشطة OSINT"""
    ACTION_TYPES = [
        ('tool_run', 'تشغيل أداة'),
        ('report_generated', 'إنشاء تقرير'),
        ('config_updated', 'تحديث إعداد'),
        ('session_started', 'بدء جلسة'),
        ('session_completed', 'إكمال جلسة'),
        ('result_exported', 'تصدير نتيجة'),
        ('error_occurred', 'حدث خطأ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='osint_activities', verbose_name="المستخدم")
    session = models.ForeignKey(OSINTSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities', verbose_name="الجلسة")
    action = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name="الإجراء")
    description = models.TextField(verbose_name="الوصف")
    
    # تفاصيل إضافية
    details = models.JSONField(default=dict, blank=True, verbose_name="التفاصيل")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="متصفح المستخدم")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "سجل نشاط OSINT"
        verbose_name_plural = "سجلات أنشطة OSINT"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
