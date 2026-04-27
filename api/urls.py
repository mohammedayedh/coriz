from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# API Router
router = DefaultRouter()

urlpatterns = [
    # API v1
    path('v1/', include([
        # Users
        path('users/', views.UserListAPIView.as_view(), name='user_list'),
        path('users/<str:username>/', views.UserDetailAPIView.as_view(), name='user_detail'),
        
        # Posts
        path('posts/', views.PostListAPIView.as_view(), name='post_list'),
        path('posts/<slug:slug>/', views.PostDetailAPIView.as_view(), name='post_detail'),
        
        # Categories
        path('categories/', views.CategoryListAPIView.as_view(), name='category_list'),
        path('categories/<slug:slug>/', views.CategoryDetailAPIView.as_view(), name='category_detail'),
        
        # Comments
        path('comments/', views.CommentListAPIView.as_view(), name='comment_list'),
        path('comments/<int:pk>/', views.CommentDetailAPIView.as_view(), name='comment_detail'),
        
        # API Management
        path('keys/', views.APIKeyListAPIView.as_view(), name='api_key_list'),
        path('keys/<int:pk>/', views.APIKeyDetailAPIView.as_view(), name='api_key_detail'),
        
        # Webhooks
        path('webhooks/', views.WebhookListAPIView.as_view(), name='webhook_list'),
        path('webhooks/<int:pk>/', views.WebhookDetailAPIView.as_view(), name='webhook_detail'),
        path('webhooks/<int:webhook_id>/test/', views.test_webhook, name='test_webhook'),
        
        # API Info
        path('versions/', views.APIVersionListAPIView.as_view(), name='api_version_list'),
        path('endpoints/', views.APIEndpointListAPIView.as_view(), name='api_endpoint_list'),
        path('stats/', views.api_stats, name='api_stats'),
        path('documentation/', views.api_documentation, name='api_documentation'),
    ])),
    
    # API Root
    path('', views.api_documentation, name='api_root'),
]

