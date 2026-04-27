from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="الصورة الشخصية")
    birth_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الميلاد")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    is_verified = models.BooleanField(default=False, verbose_name="مُتحقق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username


class UserProfile(models.Model):
    """ملف المستخدم الشخصي"""
    CLEARANCE_LEVELS = [
        ('L1', 'Level 1 - Public OSINT (مصادر مفتوحة)'),
        ('L2', 'Level 2 - Commercial APIs (تجارية)'),
        ('L3', 'Level 3 - Private & Leaked (خاصة وتسريبات)'),
        ('L4', 'Level 4 - Agency / Admin (جهات عليا)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="المستخدم")
    bio = models.TextField(blank=True, null=True, verbose_name="نبذة شخصية")
    organization = models.CharField(max_length=150, blank=True, null=True, verbose_name="المؤسسة / الجهة")
    clearance_level = models.CharField(max_length=2, choices=CLEARANCE_LEVELS, default='L1', verbose_name="مستوى التصريح الأمني")
    website = models.URLField(blank=True, null=True, verbose_name="الموقع الإلكتروني")
    social_media = models.JSONField(default=dict, blank=True, verbose_name="وسائل التواصل الاجتماعي")
    preferences = models.JSONField(default=dict, blank=True, verbose_name="التفضيلات")
    
    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
    
    def __str__(self):
        return f"ملف {self.user.username} - {self.get_clearance_level_display()}"


class EmailVerification(models.Model):
    """نموذج التحقق من البريد الإلكتروني"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    token = models.CharField(max_length=100, unique=True, verbose_name="رمز التحقق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    expires_at = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    is_used = models.BooleanField(default=False, verbose_name="مُستخدم")
    
    class Meta:
        verbose_name = "تحقق البريد الإلكتروني"
        verbose_name_plural = "تحقق البريد الإلكتروني"
    
    def __str__(self):
        return f"تحقق {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordReset(models.Model):
    """نموذج إعادة تعيين كلمة المرور"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    token = models.CharField(max_length=100, unique=True, verbose_name="رمز إعادة التعيين")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    expires_at = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    is_used = models.BooleanField(default=False, verbose_name="مُستخدم")
    
    class Meta:
        verbose_name = "إعادة تعيين كلمة المرور"
        verbose_name_plural = "إعادة تعيين كلمة المرور"
    
    def __str__(self):
        return f"إعادة تعيين {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class LoginAttempt(models.Model):
    """نموذج محاولات تسجيل الدخول"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="المستخدم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP")
    user_agent = models.TextField(verbose_name="متصفح المستخدم")
    success = models.BooleanField(verbose_name="نجح")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المحاولة")
    
    class Meta:
        verbose_name = "محاولة تسجيل دخول"
        verbose_name_plural = "محاولات تسجيل الدخول"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "نجح" if self.success else "فشل"
        return f"{status} - {self.email}"