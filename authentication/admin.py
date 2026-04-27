from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, UserProfile, EmailVerification, PasswordReset, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إدارة المستخدمين"""
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_verified', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_verified', 'is_staff', 'is_superuser', 
        'date_joined', 'last_login'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('معلومات شخصية', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('معلومات إضافية', {
            'fields': ('birth_date', 'address')
        }),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تواريخ مهمة', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """إدارة ملفات المستخدمين"""
    list_display = ['user', 'clearance_badge', 'bio_preview', 'website']
    list_filter = ['clearance_level']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = []
    
    fieldsets = (
        (None, {'fields': ('user', 'clearance_level')}),
        ('معلومات إضافية', {
            'fields': ('bio', 'organization', 'website')
        }),
        ('وسائل التواصل الاجتماعي', {
            'fields': ('social_media',),
            'classes': ('collapse',)
        }),
        ('التفضيلات', {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
    )
    
    def bio_preview(self, obj):
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '-'
    bio_preview.short_description = 'نبذة مختصرة'

    def clearance_badge(self, obj):
        colors = {
            'L1': '#6c757d',
            'L2': '#17a2b8',
            'L3': '#ffc107',
            'L4': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            colors.get(obj.clearance_level, '#000'),
            obj.get_clearance_level_display()
        )
    clearance_badge.short_description = 'مستوى التصريح'


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """إدارة تحقق البريد الإلكتروني"""
    list_display = [
        'user', 'token_preview', 'is_used', 'is_expired', 
        'created_at', 'expires_at'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'token')}),
        ('الحالة', {'fields': ('is_used',)}),
        ('التواريخ', {'fields': ('created_at', 'expires_at')}),
    )
    
    def token_preview(self, obj):
        return f"{obj.token[:8]}...{obj.token[-4:]}"
    token_preview.short_description = 'رمز التحقق'
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'منتهي الصلاحية'


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    """إدارة إعادة تعيين كلمة المرور"""
    list_display = [
        'user', 'token_preview', 'is_used', 'is_expired',
        'created_at', 'expires_at'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'token')}),
        ('الحالة', {'fields': ('is_used',)}),
        ('التواريخ', {'fields': ('created_at', 'expires_at')}),
    )
    
    def token_preview(self, obj):
        return f"{obj.token[:8]}...{obj.token[-4:]}"
    token_preview.short_description = 'رمز إعادة التعيين'
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'منتهي الصلاحية'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """إدارة محاولات تسجيل الدخول"""
    list_display = [
        'user', 'email', 'ip_address', 'success', 'created_at'
    ]
    list_filter = ['success', 'created_at']
    search_fields = ['user__username', 'email', 'ip_address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'email')}),
        ('معلومات الشبكة', {'fields': ('ip_address', 'user_agent')}),
        ('النتيجة', {'fields': ('success',)}),
        ('التاريخ', {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')