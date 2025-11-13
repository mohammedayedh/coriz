from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('posts/', views.posts_list_view, name='posts_list'),
    path('post/<slug:slug>/', views.post_detail_view, name='post_detail'),
    
    # Contact and newsletter
    path('contact/', views.contact_view, name='contact'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    
    # Static pages
    path('about/', views.about_view, name='about'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    
    # Search
    path('search/', views.search_view, name='search'),
    
    # Category and tag pages
    path('category/<slug:slug>/', views.category_posts_view, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts_view, name='tag_posts'),
    path('author/<str:username>/', views.author_posts_view, name='author_posts'),
    
    # Comments
    path('post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
]

