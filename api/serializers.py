from rest_framework import serializers
from django.contrib.auth import get_user_model
from main.models import Post, Category, Comment, Tag
from .models import APIKey, Webhook, APIVersion, APIEndpoint

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """مُسلسل المستخدم"""
    full_name = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'is_verified', 'date_joined',
            'posts_count'
        ]
        read_only_fields = ['id', 'date_joined', 'is_verified']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CategorySerializer(serializers.ModelSerializer):
    """مُسلسل الفئة"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'icon', 'color',
            'is_active', 'created_at', 'posts_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """مُسلسل العلامة"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'slug', 'color', 'created_at', 'posts_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class PostSerializer(serializers.ModelSerializer):
    """مُسلسل المنشور"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'author', 'category', 'tags', 'featured_image',
            'status', 'is_featured', 'views_count', 'comments_count',
            'likes_count', 'reading_time', 'published_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'views_count', 'comments_count',
            'likes_count', 'published_at', 'created_at', 'updated_at'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()
    
    def get_likes_count(self, obj):
        return obj.likes_count
    
    def get_reading_time(self, obj):
        # تقدير وقت القراءة (كلمة واحدة في الثانية)
        word_count = len(obj.content.split())
        return max(1, word_count // 200)  # 200 كلمة في الدقيقة
    
    def create(self, validated_data):
        # إنشاء المنشور
        post = Post.objects.create(**validated_data)
        return post


class CommentSerializer(serializers.ModelSerializer):
    """مُسلسل التعليق"""
    author = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'post', 'parent',
            'is_approved', 'likes_count', 'replies_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'is_approved', 'likes_count',
            'created_at', 'updated_at'
        ]
    
    def get_replies_count(self, obj):
        return obj.replies.filter(is_approved=True).count()
    
    def create(self, validated_data):
        # إنشاء التعليق
        comment = Comment.objects.create(**validated_data)
        return comment


class APIKeySerializer(serializers.ModelSerializer):
    """مُسلسل مفتاح API"""
    key_display = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_display', 'is_active',
            'permissions', 'last_used', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'key_display', 'last_used',
            'created_at', 'updated_at'
        ]
    
    def get_key_display(self, obj):
        # إظهار جزء من المفتاح فقط للأمان
        return f"{obj.key[:8]}...{obj.key[-4:]}" if obj.key else None
    
    def create(self, validated_data):
        # إنشاء مفتاح API
        api_key = APIKey.objects.create(**validated_data)
        return api_key


class WebhookSerializer(serializers.ModelSerializer):
    """مُسلسل Webhook"""
    deliveries_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'status',
            'is_active', 'last_triggered', 'failure_count',
            'deliveries_count', 'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_triggered', 'failure_count',
            'deliveries_count', 'success_rate', 'created_at', 'updated_at'
        ]
    
    def get_deliveries_count(self, obj):
        return obj.deliveries.count()
    
    def get_success_rate(self, obj):
        total_deliveries = obj.deliveries.count()
        if total_deliveries == 0:
            return 0
        
        successful_deliveries = obj.deliveries.filter(status='delivered').count()
        return (successful_deliveries / total_deliveries) * 100
    
    def create(self, validated_data):
        # إنشاء Webhook
        webhook = Webhook.objects.create(**validated_data)
        return webhook


class APIVersionSerializer(serializers.ModelSerializer):
    """مُسلسل إصدار API"""
    endpoints_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIVersion
        fields = [
            'id', 'version', 'is_active', 'is_deprecated',
            'deprecation_date', 'changelog', 'documentation_url',
            'endpoints_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_endpoints_count(self, obj):
        return obj.endpoints.filter(is_active=True).count()


class APIEndpointSerializer(serializers.ModelSerializer):
    """مُسلسل نقطة نهاية API"""
    version = APIVersionSerializer(read_only=True)
    
    class Meta:
        model = APIEndpoint
        fields = [
            'id', 'name', 'path', 'method', 'description',
            'version', 'is_public', 'requires_auth', 'rate_limit',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PostCreateSerializer(serializers.ModelSerializer):
    """مُسلسل إنشاء المنشور"""
    category_id = serializers.IntegerField(write_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category_id',
            'tag_ids', 'featured_image', 'status', 'is_featured'
        ]
    
    def create(self, validated_data):
        # استخراج البيانات
        category_id = validated_data.pop('category_id')
        tag_ids = validated_data.pop('tag_ids', [])
        
        # إنشاء المنشور
        post = Post.objects.create(**validated_data)
        
        # ربط الفئة
        if category_id:
            try:
                from main.models import Category
                category = Category.objects.get(id=category_id)
                post.category = category
                post.save()
            except Category.DoesNotExist:
                pass
        
        # ربط العلامات
        if tag_ids:
            try:
                from main.models import Tag
                tags = Tag.objects.filter(id__in=tag_ids)
                post.tags.set(tags)
            except Tag.DoesNotExist:
                pass
        
        return post


class CommentCreateSerializer(serializers.ModelSerializer):
    """مُسلسل إنشاء التعليق"""
    post_id = serializers.IntegerField(write_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['content', 'post_id', 'parent_id']
    
    def create(self, validated_data):
        # استخراج البيانات
        post_id = validated_data.pop('post_id')
        parent_id = validated_data.pop('parent_id', None)
        
        # الحصول على المنشور
        try:
            from main.models import Post
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError("المنشور غير موجود")
        
        # الحصول على التعليق الأب
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                raise serializers.ValidationError("التعليق الأب غير موجود")
        
        # إنشاء التعليق
        comment = Comment.objects.create(
            post=post,
            parent=parent,
            **validated_data
        )
        
        return comment

