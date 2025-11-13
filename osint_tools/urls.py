from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'osint_tools'

# API Router
router = DefaultRouter()
router.register(r'tools', views.OSINTToolViewSet, basename='osint-tool')
router.register(r'sessions', views.OSINTSessionViewSet, basename='osint-session')
router.register(r'results', views.OSINTResultViewSet, basename='osint-result')
router.register(r'reports', views.OSINTReportViewSet, basename='osint-report')
router.register(r'configurations', views.OSINTConfigurationViewSet, basename='osint-configuration')

urlpatterns = [
    # Dashboard URLs
    path('', views.osint_dashboard, name='dashboard'),
    path('tools/', views.tools_list, name='tools_list'),
    path('tools/<slug:tool_slug>/', views.tool_detail, name='tool_detail'),
    path('tools/<slug:tool_slug>/run/', views.run_tool, name='run_tool'),
    path('tools/<slug:tool_slug>/test/', views.test_tool, name='test_tool'),
    path('sessions/', views.sessions_list, name='sessions_list'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/results/', views.session_results, name='session_results'),
    path('sessions/<int:session_id>/report/', views.generate_report, name='generate_report'),
    path('results/', views.results_list, name='results_list'),
    path('results/<int:result_id>/', views.result_detail, name='result_detail'),
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
    path('configurations/', views.configurations_list, name='configurations_list'),
    path('configurations/<int:config_id>/', views.configuration_detail, name='configuration_detail'),
    path('analytics/', views.osint_analytics, name='analytics'),
    
    # AJAX URLs
    path('ajax/session-status/<int:session_id>/', views.get_session_status, name='get_session_status'),
    path('ajax/tool-progress/<int:session_id>/', views.get_tool_progress, name='get_tool_progress'),
    path('ajax/export-results/<int:session_id>/', views.export_results, name='export_results'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/tools/<slug:tool_slug>/test/', views.test_tool, name='test_tool'),
]
