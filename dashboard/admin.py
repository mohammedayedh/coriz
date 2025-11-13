from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    DashboardWidget, UserDashboard, ActivityLog, Notification,
    UserSession, SystemMetrics, BackupLog
)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """إدارة عناصر لوحة التحكم"""
    list_display = [
        'name', 'widget_type', 'position_display', 'size_display',
        'is_active', 'created_at'
    ]
    list_filter = ['widget_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'widget_type')}),
        ('الموضع والحجم', {'fields': ('position_x', 'position_y', 'width', 'height')}),
        ('الإعدادات', {'fields': ('config',)}),
        ('الحالة', {'fields': ('is_active',)}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def position_display(self, obj):
        return f"({obj.position_x}, {obj.position_y})"
    position_display.short_description = 'الموضع'
    
    def size_display(self, obj):
        return f"{obj.width} × {obj.height}"
    size_display.short_description = 'الحجم'


@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    """إدارة لوحات تحكم المستخدمين"""
    list_display = ['user', 'theme', 'widgets_count', 'updated_at']
    list_filter = ['theme', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('العناصر', {'fields': ('widgets',)}),
        ('الإعدادات', {'fields': ('layout_config', 'theme')}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def widgets_count(self, obj):
        return obj.widgets.count()
    widgets_count.short_description = 'عدد العناصر'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('widgets')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """إدارة سجل الأنشطة"""
    list_display = [
        'user', 'action', 'object_type', 'description_preview',
        'ip_address', 'created_at'
    ]
    list_filter = ['action', 'object_type', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'action', 'object_type', 'object_id')}),
        ('الوصف', {'fields': ('description',)}),
        ('معلومات الشبكة', {'fields': ('ip_address', 'user_agent')}),
        ('بيانات إضافية', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('التاريخ', {'fields': ('created_at',)}),
    )
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'الوصف'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').order_by('-created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات"""
    list_display = [
        'user', 'title', 'notification_type', 'is_read',
        'created_at', 'read_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'title', 'message')}),
        ('النوع والحالة', {'fields': ('notification_type', 'is_read')}),
        ('الإجراء', {'fields': ('action_url',)}),
        ('بيانات إضافية', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {'fields': ('created_at', 'read_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').order_by('-created_at')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """إدارة جلسات المستخدمين"""
    list_display = [
        'user', 'session_key_preview', 'ip_address', 'is_active',
        'last_activity', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__username', 'session_key', 'ip_address']
    readonly_fields = ['session_key', 'created_at', 'last_activity']
    
    fieldsets = (
        (None, {'fields': ('user', 'session_key')}),
        ('معلومات الشبكة', {'fields': ('ip_address', 'user_agent')}),
        ('الحالة', {'fields': ('is_active',)}),
        ('التواريخ', {'fields': ('created_at', 'last_activity')}),
    )
    
    def session_key_preview(self, obj):
        return f"{obj.session_key[:8]}...{obj.session_key[-4:]}"
    session_key_preview.short_description = 'مفتاح الجلسة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').order_by('-last_activity')


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    """إدارة مقاييس النظام"""
    list_display = [
        'metric_name', 'metric_value', 'metric_unit', 'recorded_at'
    ]
    list_filter = ['metric_name', 'recorded_at']
    search_fields = ['metric_name']
    readonly_fields = ['recorded_at']
    
    fieldsets = (
        (None, {'fields': ('metric_name', 'metric_value', 'metric_unit')}),
        ('بيانات إضافية', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('التاريخ', {'fields': ('recorded_at',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-recorded_at')


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    """إدارة سجل النسخ الاحتياطية"""
    list_display = [
        'backup_name', 'backup_type', 'status', 'file_size_display',
        'started_at', 'completed_at'
    ]
    list_filter = ['backup_type', 'status', 'started_at']
    search_fields = ['backup_name', 'file_path']
    readonly_fields = ['started_at']
    
    fieldsets = (
        (None, {'fields': ('backup_name', 'backup_type', 'status')}),
        ('الملف', {'fields': ('file_path', 'file_size')}),
        ('الخطأ', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('التواريخ', {'fields': ('started_at', 'completed_at')}),
    )
    
    def file_size_display(self, obj):
        if obj.file_size:
            # تحويل الحجم إلى وحدات مناسبة
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return '-'
    file_size_display.short_description = 'حجم الملف'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-started_at')