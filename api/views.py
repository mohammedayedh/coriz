from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import APIKey, APIRequest, APIRateLimit, Webhook, WebhookDelivery, APIVersion, APIEndpoint
from .serializers import (
    UserSerializer, PostSerializer, CategorySerializer, CommentSerializer,
    APIKeySerializer, WebhookSerializer, APIVersionSerializer, APIEndpointSerializer
)
from main.models import Post, Category, Comment
from authentication.models import User

logger = logging.getLogger(__name__)


class UserListAPIView(generics.ListAPIView):
    """قائمة المستخدمين"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDetailAPIView(generics.RetrieveAPIView):
    """تفاصيل المستخدم"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'


class PostListAPIView(generics.ListCreateAPIView):
    """قائمة المنشورات"""
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # البحث
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        # الفلترة حسب الفئة
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # الفلترة حسب العلامة
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # الفلترة حسب المؤلف
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        return queryset.order_by('-published_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل المنشور"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # زيادة عدد المشاهدات
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryListAPIView(generics.ListAPIView):
    """قائمة الفئات"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """تفاصيل الفئة"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class CommentListAPIView(generics.ListCreateAPIView):
    """قائمة التعليقات"""
    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # الفلترة حسب المنشور
        post_slug = self.request.query_params.get('post')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل التعليق"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class APIKeyListAPIView(generics.ListCreateAPIView):
    """قائمة مفاتيح API"""
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class APIKeyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل مفتاح API"""
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)


class WebhookListAPIView(generics.ListCreateAPIView):
    """قائمة Webhooks"""
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WebhookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل Webhook"""
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user)


class APIVersionListAPIView(generics.ListAPIView):
    """قائمة إصدارات API"""
    queryset = APIVersion.objects.filter(is_active=True)
    serializer_class = APIVersionSerializer
    permission_classes = [permissions.AllowAny]


class APIEndpointListAPIView(generics.ListAPIView):
    """قائمة نقاط نهاية API"""
    queryset = APIEndpoint.objects.filter(is_active=True)
    serializer_class = APIEndpointSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # الفلترة حسب الإصدار
        version = self.request.query_params.get('version')
        if version:
            queryset = queryset.filter(version__version=version)
        
        return queryset.order_by('path', 'method')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_stats(request):
    """إحصائيات API"""
    user = request.user
    
    # إحصائيات مفاتيح API
    api_keys_count = APIKey.objects.filter(user=user, is_active=True).count()
    
    # إحصائيات الطلبات
    total_requests = APIRequest.objects.filter(api_key__user=user).count()
    successful_requests = APIRequest.objects.filter(
        api_key__user=user,
        status_code__lt=400
    ).count()
    failed_requests = total_requests - successful_requests
    
    # إحصائيات Webhooks
    webhooks_count = Webhook.objects.filter(user=user, is_active=True).count()
    webhook_deliveries = WebhookDelivery.objects.filter(webhook__user=user).count()
    
    # الطلبات الأخيرة
    recent_requests = APIRequest.objects.filter(
        api_key__user=user
    ).order_by('-created_at')[:10]
    
    stats = {
        'api_keys_count': api_keys_count,
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        'webhooks_count': webhooks_count,
        'webhook_deliveries': webhook_deliveries,
        'recent_requests': [
            {
                'endpoint': req.endpoint,
                'method': req.method,
                'status_code': req.status_code,
                'response_time': req.response_time,
                'created_at': req.created_at
            }
            for req in recent_requests
        ]
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_webhook(request, webhook_id):
    """اختبار Webhook"""
    try:
        webhook = Webhook.objects.get(id=webhook_id, user=request.user)
        
        # إنشاء تسليم تجريبي
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event='test',
            payload={'message': 'Test webhook delivery'},
            status='pending'
        )
        
        # محاولة إرسال Webhook
        # هنا يمكن إضافة منطق إرسال Webhook الفعلي
        
        delivery.status = 'delivered'
        delivery.status_code = 200
        delivery.delivered_at = timezone.now()
        delivery.save()
        
        return Response({
            'success': True,
            'message': 'تم إرسال Webhook بنجاح',
            'delivery_id': delivery.id
        })
        
    except Webhook.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Webhook غير موجود'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"خطأ في اختبار Webhook: {e}")
        return Response({
            'success': False,
            'message': 'حدث خطأ في الخادم'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_documentation(request):
    """توثيق API"""
    endpoints = APIEndpoint.objects.filter(is_active=True).order_by('path', 'method')
    
    documentation = {
        'title': 'كوريزا API',
        'version': '1.0.0',
        'description': 'واجهة برمجة التطبيقات لمنصة كوريزا',
        'base_url': request.build_absolute_uri('/api/v1/'),
        'endpoints': [
            {
                'path': endpoint.path,
                'method': endpoint.method,
                'description': endpoint.description,
                'requires_auth': endpoint.requires_auth,
                'rate_limit': endpoint.rate_limit,
                'version': endpoint.version.version
            }
            for endpoint in endpoints
        ]
    }
    
    return Response(documentation)