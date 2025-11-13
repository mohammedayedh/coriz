from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    APIKey, APIRequest, APIRateLimit, Webhook, WebhookDelivery,
    APIVersion, APIEndpoint
)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """إدارة مفاتيح API"""
    list_display = [
        'name', 'user', 'key_display', 'is_active', 'last_used', 'expires_at'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'secret', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'name')}),
        ('المفتاح', {'fields': ('key', 'secret')}),
        ('الحالة', {'fields': ('is_active',)}),
        ('الصلاحيات', {'fields': ('permissions',)}),
        ('الاستخدام', {'fields': ('last_used', 'expires_at')}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def key_display(self, obj):
        if obj.key:
            return format_html(
                '<code>{}</code>',
                f"{obj.key[:8]}...{obj.key[-4:]}"
            )
        return '-'
    key_display.short_description = 'المفتاح'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    """إدارة طلبات API"""
    list_display = [
        'api_key', 'endpoint', 'method', 'status_code', 'response_time',
        'ip_address', 'created_at'
    ]
    list_filter = ['method', 'status_code', 'created_at']
    search_fields = ['endpoint', 'ip_address', 'api_key__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {'fields': ('api_key', 'endpoint', 'method')}),
        ('الاستجابة', {'fields': ('status_code', 'response_time')}),
        ('معلومات الشبكة', {'fields': ('ip_address', 'user_agent')}),
        ('البيانات', {
            'fields': ('request_data', 'response_data'),
            'classes': ('collapse',)
        }),
        ('الخطأ', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('التاريخ', {'fields': ('created_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('api_key').order_by('-created_at')


@admin.register(APIRateLimit)
class APIRateLimitAdmin(admin.ModelAdmin):
    """إدارة حدود معدل API"""
    list_display = [
        'api_key', 'endpoint', 'requests_count', 'is_blocked',
        'window_start', 'window_end'
    ]
    list_filter = ['is_blocked', 'window_start', 'window_end']
    search_fields = ['endpoint', 'api_key__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('api_key', 'endpoint')}),
        ('الحدود', {'fields': ('requests_count', 'window_start', 'window_end')}),
        ('الحظر', {'fields': ('is_blocked', 'blocked_until')}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('api_key').order_by('-updated_at')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """إدارة Webhooks"""
    list_display = [
        'name', 'user', 'url', 'status', 'is_active',
        'last_triggered', 'failure_count'
    ]
    list_filter = ['status', 'is_active', 'created_at']
    search_fields = ['name', 'url', 'user__username']
    readonly_fields = ['secret', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'name', 'url')}),
        ('الأحداث', {'fields': ('events',)}),
        ('الحالة', {'fields': ('status', 'is_active')}),
        ('السر', {'fields': ('secret',)}),
        ('الإحصائيات', {'fields': ('last_triggered', 'failure_count')}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    """إدارة تسليم Webhooks"""
    list_display = [
        'webhook', 'event', 'status', 'status_code', 'attempts',
        'created_at', 'delivered_at'
    ]
    list_filter = ['status', 'created_at', 'delivered_at']
    search_fields = ['webhook__name', 'event']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('webhook', 'event')}),
        ('البيانات', {'fields': ('payload',)}),
        ('الحالة', {'fields': ('status', 'status_code', 'response_body')}),
        ('المحاولات', {'fields': ('attempts', 'max_attempts', 'next_retry_at')}),
        ('الخطأ', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {'fields': ('created_at', 'delivered_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('webhook').order_by('-created_at')


@admin.register(APIVersion)
class APIVersionAdmin(admin.ModelAdmin):
    """إدارة إصدارات API"""
    list_display = [
        'version', 'is_active', 'is_deprecated', 'deprecation_date',
        'endpoints_count', 'created_at'
    ]
    list_filter = ['is_active', 'is_deprecated', 'created_at']
    search_fields = ['version']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('version',)}),
        ('الحالة', {'fields': ('is_active', 'is_deprecated', 'deprecation_date')}),
        ('المعلومات', {'fields': ('changelog', 'documentation_url')}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def endpoints_count(self, obj):
        return obj.endpoints.filter(is_active=True).count()
    endpoints_count.short_description = 'عدد النقاط النهائية'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('endpoints')


@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    """إدارة نقاط نهاية API"""
    list_display = [
        'name', 'path', 'method', 'version', 'is_public',
        'requires_auth', 'rate_limit', 'is_active'
    ]
    list_filter = ['method', 'is_public', 'requires_auth', 'is_active', 'version']
    search_fields = ['name', 'path', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'path', 'method', 'version')}),
        ('الوصف', {'fields': ('description',)}),
        ('الصلاحيات', {'fields': ('is_public', 'requires_auth')}),
        ('الحدود', {'fields': ('rate_limit',)}),
        ('الحالة', {'fields': ('is_active',)}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('version').order_by('path', 'method')