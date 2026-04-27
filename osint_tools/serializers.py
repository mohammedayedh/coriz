from rest_framework import serializers
from .models import (
    OSINTTool, OSINTSession, OSINTResult, OSINTReport, 
    OSINTConfiguration, OSINTActivityLog
)


class OSINTToolSerializer(serializers.ModelSerializer):
    """Serializer لأدوات OSINT"""
    class Meta:
        model = OSINTTool
        fields = [
            'id', 'name', 'slug', 'description', 'tool_type', 'status',
            'icon', 'color', 'requires_auth', 'api_key_required',
            'rate_limit', 'timeout', 'usage_count', 'success_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'usage_count', 'success_rate', 'created_at', 'updated_at']


class OSINTSessionSerializer(serializers.ModelSerializer):
    """Serializer لجلسات OSINT"""
    tool_name = serializers.CharField(source='tool.name', read_only=True)
    tool_icon = serializers.CharField(source='tool.icon', read_only=True)
    tool_color = serializers.CharField(source='tool.color', read_only=True)
    
    class Meta:
        model = OSINTSession
        fields = [
            'id', 'tool', 'tool_name', 'tool_icon', 'tool_color',
            'target', 'status', 'config', 'options', 'celery_task_id', 'progress',
            'current_step', 'results_count', 'results_summary',
            'started_at', 'completed_at', 'duration', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tool_name', 'tool_icon', 'tool_color', 'celery_task_id', 'progress',
            'current_step', 'results_count', 'results_summary',
            'started_at', 'completed_at', 'duration', 'error_message',
            'created_at', 'updated_at'
        ]


class OSINTResultSerializer(serializers.ModelSerializer):
    """Serializer لنتائج OSINT"""
    session_tool = serializers.CharField(source='session.tool.name', read_only=True)
    session_target = serializers.CharField(source='session.target', read_only=True)
    
    class Meta:
        model = OSINTResult
        fields = [
            'id', 'session', 'session_tool', 'session_target',
            'result_type', 'title', 'description', 'url', 'raw_data',
            'confidence', 'confidence_score', 'source', 'tags',
            'metadata', 'discovered_at', 'updated_at'
        ]
        read_only_fields = ['id', 'session_tool', 'session_target', 'discovered_at', 'updated_at']


class OSINTReportSerializer(serializers.ModelSerializer):
    """Serializer لتقارير OSINT"""
    session_tool = serializers.CharField(source='session.tool.name', read_only=True)
    session_target = serializers.CharField(source='session.target', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OSINTReport
        fields = [
            'id', 'session', 'session_tool', 'session_target',
            'title', 'report_type', 'format', 'content', 'summary',
            'recommendations', 'file', 'file_url', 'file_size',
            'include_raw_data', 'include_metadata', 'include_charts',
            'status', 'error_message', 'celery_task_id',
            'generated_at', 'downloaded_count'
        ]
        read_only_fields = [
            'id', 'session_tool', 'session_target', 'file_url',
            'file_size', 'status', 'error_message', 'celery_task_id',
            'generated_at', 'downloaded_count'
        ]
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class OSINTConfigurationSerializer(serializers.ModelSerializer):
    """Serializer لإعدادات OSINT"""
    tool_name = serializers.CharField(source='tool.name', read_only=True)
    tool_slug = serializers.CharField(source='tool.slug', read_only=True)
    
    class Meta:
        model = OSINTConfiguration
        fields = [
            'id', 'tool', 'tool_name', 'tool_slug', 'config_name',
            'config_data', 'api_keys', 'proxy_settings', 'timeout',
            'retry_count', 'concurrent_requests', 'anonymize_results',
            'store_results', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tool_name', 'tool_slug', 'created_at', 'updated_at']


class OSINTActivityLogSerializer(serializers.ModelSerializer):
    """Serializer لسجل أنشطة OSINT"""
    session_tool = serializers.CharField(source='session.tool.name', read_only=True)
    session_target = serializers.CharField(source='session.target', read_only=True)
    
    class Meta:
        model = OSINTActivityLog
        fields = [
            'id', 'session', 'session_tool', 'session_target',
            'action', 'description', 'details', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'session_tool', 'session_target', 'created_at']


# Serializers للاستخدام في النماذج
class OSINTToolFormSerializer(serializers.ModelSerializer):
    """Serializer لاستخدام أدوات OSINT في النماذج"""
    class Meta:
        model = OSINTTool
        fields = ['id', 'name', 'slug', 'description', 'tool_type', 'icon', 'color']


class OSINTSessionFormSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء جلسات OSINT"""
    class Meta:
        model = OSINTSession
        fields = ['tool', 'target', 'config', 'options']
    
    def validate_target(self, value):
        """التحقق من صحة الهدف"""
        if not value or not value.strip():
            raise serializers.ValidationError("الهدف مطلوب")
        
        # يمكن إضافة المزيد من التحقق هنا حسب نوع الأداة
        return value.strip()


class OSINTResultFormSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء نتائج OSINT"""
    class Meta:
        model = OSINTResult
        fields = [
            'session', 'result_type', 'title', 'description', 'url',
            'raw_data', 'confidence', 'confidence_score', 'source', 'tags', 'metadata'
        ]
    
    def validate_confidence_score(self, value):
        """التحقق من درجة الثقة"""
        if value < 0.0 or value > 1.0:
            raise serializers.ValidationError("درجة الثقة يجب أن تكون بين 0.0 و 1.0")
        return value


class OSINTReportFormSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء تقارير OSINT"""
    class Meta:
        model = OSINTReport
        fields = [
            'session', 'title', 'report_type', 'format', 'content',
            'summary', 'recommendations', 'include_raw_data',
            'include_metadata', 'include_charts'
        ]
    
    def validate_report_type(self, value):
        """التحقق من نوع التقرير"""
        valid_types = [choice[0] for choice in OSINTReport.REPORT_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(f"نوع التقرير غير صحيح. الأنواع المتاحة: {valid_types}")
        return value
    
    def validate_format(self, value):
        """التحقق من صيغة التقرير"""
        valid_formats = [choice[0] for choice in OSINTReport.FORMAT_CHOICES]
        if value not in valid_formats:
            raise serializers.ValidationError(f"صيغة التقرير غير صحيحة. الصيغ المتاحة: {valid_formats}")
        return value
