from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """نموذج الفئات"""
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="الرابط")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="الأيقونة")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="اللون")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """نموذج المنشورات"""
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="العنوان")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="الرابط")
    content = models.TextField(verbose_name="المحتوى")
    excerpt = models.TextField(max_length=300, blank=True, null=True, verbose_name="الملخص")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="المؤلف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="الفئة")
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="الصورة المميزة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="عدد الإعجابات")
    comments_count = models.PositiveIntegerField(default=0, verbose_name="عدد التعليقات")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "منشور"
        verbose_name_plural = "المنشورات"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Comment(models.Model):
    """نموذج التعليقات"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="المنشور")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="المؤلف")
    content = models.TextField(verbose_name="المحتوى")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="التعليق الأب")
    is_approved = models.BooleanField(default=True, verbose_name="موافق عليه")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="عدد الإعجابات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"تعليق على {self.post.title}"


class Tag(models.Model):
    """نموذج العلامات"""
    name = models.CharField(max_length=50, unique=True, verbose_name="اسم العلامة")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="الرابط")
    color = models.CharField(max_length=7, default="#6c757d", verbose_name="اللون")
    posts = models.ManyToManyField(Post, related_name='tags', blank=True, verbose_name="المنشورات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "علامة"
        verbose_name_plural = "العلامات"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    """نموذج رسائل التواصل"""
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('read', 'مقروء'),
        ('replied', 'تم الرد'),
        ('closed', 'مغلق'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="الاسم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    message = models.TextField(verbose_name="الرسالة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="الحالة")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="متصفح المستخدم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Newsletter(models.Model):
    """نموذج النشرة الإخبارية"""
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاشتراك")
    unsubscribed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ إلغاء الاشتراك")
    
    class Meta:
        verbose_name = "مشترك في النشرة"
        verbose_name_plural = "مشتركو النشرة الإخبارية"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    """نموذج إعدادات الموقع"""
    site_name = models.CharField(max_length=100, default="كوريزا", verbose_name="اسم الموقع")
    site_description = models.TextField(blank=True, null=True, verbose_name="وصف الموقع")
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name="شعار الموقع")
    site_favicon = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name="أيقونة الموقع")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="بريد التواصل")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="هاتف التواصل")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    social_media = models.JSONField(default=dict, blank=True, verbose_name="وسائل التواصل الاجتماعي")
    analytics_code = models.TextField(blank=True, null=True, verbose_name="كود التحليلات")
    maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            # إذا كان هناك إعدادات موجودة، لا تنشئ جديدة
            return
        super().save(*args, **kwargs)