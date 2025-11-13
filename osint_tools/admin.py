from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    OSINTTool, OSINTSession, OSINTResult, OSINTReport, 
    OSINTConfiguration, OSINTActivityLog
)


@admin.register(OSINTTool)
class OSINTToolAdmin(admin.ModelAdmin):
    """إدارة أدوات OSINT"""
    list_display = [
        'name', 'tool_type', 'status', 'usage_count', 
        'success_rate', 'created_at'
    ]
    list_filter = ['tool_type', 'status', 'requires_auth', 'api_key_required']
    search_fields = ['name', 'description', 'tool_path']
    readonly_fields = ['usage_count', 'success_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'slug', 'description', 'tool_type', 'status')
        }),
        ('المظهر', {
            'fields': ('icon', 'color')
        }),
        ('إعدادات الأداة', {
            'fields': ('requires_auth', 'api_key_required', 'rate_limit', 'timeout')
        }),
        ('مسار الأداة', {
            'fields': ('tool_path', 'executable_name', 'command_template')
        }),
        ('إعدادات متقدمة', {
            'fields': ('config_schema', 'supported_formats')
        }),
        ('إحصائيات', {
            'fields': ('usage_count', 'success_rate'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('sessions')


@admin.register(OSINTSession)
class OSINTSessionAdmin(admin.ModelAdmin):
    """إدارة جلسات OSINT"""
    list_display = [
        'id', 'user', 'tool', 'target', 'status', 
        'progress', 'results_count', 'created_at'
    ]
    list_filter = ['status', 'tool__tool_type', 'created_at']
    search_fields = ['target', 'user__username', 'tool__name']
    readonly_fields = [
        'progress', 'results_count', 'started_at', 
        'completed_at', 'duration', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('معلومات الجلسة', {
            'fields': ('user', 'tool', 'target', 'status')
        }),
        ('إعدادات الجلسة', {
            'fields': ('config', 'options')
        }),
        ('معلومات التقدم', {
            'fields': ('progress', 'current_step', 'results_count', 'results_summary')
        }),
        ('معلومات التوقيت', {
            'fields': ('started_at', 'completed_at', 'duration')
        }),
        ('معلومات إضافية', {
            'fields': ('error_message', 'log_file'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tool')


@admin.register(OSINTResult)
class OSINTResultAdmin(admin.ModelAdmin):
    """إدارة نتائج OSINT"""
    list_display = [
        'title', 'session', 'result_type', 'confidence', 
        'confidence_score', 'source', 'discovered_at'
    ]
    list_filter = ['result_type', 'confidence', 'session__tool__tool_type']
    search_fields = ['title', 'description', 'source', 'session__target']
    readonly_fields = ['discovered_at', 'updated_at']
    
    fieldsets = (
        ('معلومات النتيجة', {
            'fields': ('session', 'result_type', 'title', 'description', 'url')
        }),
        ('مستوى الثقة', {
            'fields': ('confidence', 'confidence_score')
        }),
        ('معلومات إضافية', {
            'fields': ('source', 'tags', 'metadata')
        }),
        ('البيانات الخام', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('discovered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session__tool', 'session__user')


@admin.register(OSINTReport)
class OSINTReportAdmin(admin.ModelAdmin):
    """إدارة تقارير OSINT"""
    list_display = [
        'title', 'user', 'session', 'report_type', 
        'format', 'file_size', 'downloaded_count', 'generated_at'
    ]
    list_filter = ['report_type', 'format', 'generated_at']
    search_fields = ['title', 'user__username', 'session__target']
    readonly_fields = ['file_size', 'downloaded_count', 'generated_at']
    
    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('user', 'session', 'title', 'report_type', 'format')
        }),
        ('محتوى التقرير', {
            'fields': ('content', 'summary', 'recommendations')
        }),
        ('ملف التقرير', {
            'fields': ('file', 'file_size')
        }),
        ('إعدادات التقرير', {
            'fields': ('include_raw_data', 'include_metadata', 'include_charts')
        }),
        ('إحصائيات', {
            'fields': ('downloaded_count', 'generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'session__tool')


@admin.register(OSINTConfiguration)
class OSINTConfigurationAdmin(admin.ModelAdmin):
    """إدارة إعدادات OSINT"""
    list_display = [
        'user', 'tool', 'config_name', 'is_active', 
        'timeout', 'retry_count', 'updated_at'
    ]
    list_filter = ['is_active', 'tool__tool_type', 'updated_at']
    search_fields = ['user__username', 'tool__name', 'config_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الإعداد', {
            'fields': ('user', 'tool', 'config_name', 'is_active')
        }),
        ('إعدادات الأداة', {
            'fields': ('config_data',)
        }),
        ('إعدادات API', {
            'fields': ('api_keys', 'proxy_settings'),
            'classes': ('collapse',)
        }),
        ('إعدادات الأداء', {
            'fields': ('timeout', 'retry_count', 'concurrent_requests')
        }),
        ('إعدادات الخصوصية', {
            'fields': ('anonymize_results', 'store_results')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tool')


@admin.register(OSINTActivityLog)
class OSINTActivityLogAdmin(admin.ModelAdmin):
    """إدارة سجل أنشطة OSINT"""
    list_display = [
        'user', 'action', 'session', 'ip_address', 'created_at'
    ]
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'description', 'session__target']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('معلومات النشاط', {
            'fields': ('user', 'session', 'action', 'description')
        }),
        ('تفاصيل إضافية', {
            'fields': ('details', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'session__tool')
    
    def has_add_permission(self, request):
        return False  # منع إضافة سجلات نشاط يدوياً


# تخصيص عنوان لوحة الإدارة
admin.site.site_header = "إدارة أدوات OSINT - كوريزا"
admin.site.site_title = "كوريزا OSINT"
admin.site.index_title = "لوحة تحكم أدوات OSINT"