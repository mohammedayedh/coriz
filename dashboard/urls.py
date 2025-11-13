from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard main
    path('', views.dashboard_index, name='index'),
    
    # Posts management
    path('posts/', views.posts_management, name='posts_management'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # OSINT Tools
    path('osint/', include('osint_tools.urls')),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Activity log
    path('activity-log/', views.activity_log_view, name='activity_log'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('profile/', views.profile_view, name='profile'),
    
    # Security
    path('security/', views.security_view, name='security'),
    path('security/session/<int:session_id>/terminate/', views.terminate_session, name='terminate_session'),
    path('security/terminate-all-sessions/', views.terminate_all_sessions, name='terminate_all_sessions'),
]

