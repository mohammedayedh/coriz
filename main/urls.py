from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    
    # Contact and newsletter
    path('contact/', views.contact_view, name='contact'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    
    # Static pages
    path('about/', views.about_view, name='about'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    
    # Search
    path('search/', views.search_view, name='search'),
]

