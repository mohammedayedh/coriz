from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Category, Post, Comment, Tag, ContactMessage, 
    Newsletter, SiteSettings
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إدارة الفئات"""
    list_display = ['name', 'icon', 'color_preview', 'is_active', 'posts_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        ('المظهر', {'fields': ('icon', 'color')}),
        ('الحالة', {'fields': ('is_active',)}),
    )
    
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></span> {}',
                obj.color, obj.color
            )
        return '-'
    color_preview.short_description = 'اللون'
    
    def posts_count(self, obj):
        return obj.posts.filter(status='published').count()
    posts_count.short_description = 'عدد المنشورات'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """إدارة المنشورات"""
    list_display = [
        'title', 'author', 'category', 'status', 'is_featured',
        'views_count', 'comments_count', 'published_at'
    ]
    list_filter = ['status', 'is_featured', 'category', 'author', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'comments_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'content', 'excerpt')}),
        ('المعلومات', {'fields': ('author', 'category', 'tags')}),
        ('المظهر', {'fields': ('featured_image',)}),
        ('الحالة', {'fields': ('status', 'is_featured')}),
        ('الإحصائيات', {
            'fields': ('views_count', 'comments_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')
    
    def save_model(self, request, obj, form, change):
        if not change:  # إنشاء جديد
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """إدارة التعليقات"""
    list_display = [
        'content_preview', 'author', 'post', 'is_approved',
        'likes_count', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['likes_count', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('content',)}),
        ('المعلومات', {'fields': ('author', 'post', 'parent')}),
        ('الحالة', {'fields': ('is_approved',)}),
        ('الإحصائيات', {'fields': ('likes_count',)}),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'محتوى التعليق'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """إدارة العلامات"""
    list_display = ['name', 'slug', 'color_preview', 'posts_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {'fields': ('name', 'slug')}),
        ('المظهر', {'fields': ('color',)}),
    )
    
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></span> {}',
                obj.color, obj.color
            )
        return '-'
    color_preview.short_description = 'اللون'
    
    def posts_count(self, obj):
        return obj.posts.filter(status='published').count()
    posts_count.short_description = 'عدد المنشورات'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """إدارة رسائل التواصل"""
    list_display = [
        'name', 'email', 'subject', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'email', 'subject', 'message')}),
        ('الحالة', {'fields': ('status',)}),
        ('معلومات الشبكة', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """إدارة النشرة الإخبارية"""
    list_display = ['email', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('الحالة', {'fields': ('is_active',)}),
        ('التواريخ', {'fields': ('subscribed_at', 'unsubscribed_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-subscribed_at')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """إدارة إعدادات الموقع"""
    list_display = ['site_name', 'contact_email', 'maintenance_mode', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الموقع', {
            'fields': ('site_name', 'site_description', 'site_logo', 'site_favicon')
        }),
        ('معلومات التواصل', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('وسائل التواصل الاجتماعي', {
            'fields': ('social_media',),
            'classes': ('collapse',)
        }),
        ('الإعدادات التقنية', {
            'fields': ('analytics_code', 'maintenance_mode'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # منع إضافة أكثر من إعداد واحد
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # منع حذف الإعدادات
        return False