from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Email verification
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('resend-verification/public/', views.resend_verification_email_public, name='resend_verification_public'),
    
    # Password reset
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # AJAX endpoints
    path('check-email/', views.check_email_availability, name='check_email'),
    path('check-username/', views.check_username_availability, name='check_username'),
]

