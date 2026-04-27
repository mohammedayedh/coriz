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
    path('search/', views.simple_search_interface, name='simple_search'),  # الواجهة المبسطة الجديدة
    path('tools/', views.tools_list, name='tools_list'),
    path('tools/<slug:tool_slug>/', views.tool_detail, name='tool_detail'),
    path('tools/<slug:tool_slug>/run/', views.run_tool, name='run_tool'),
    path('tools/<slug:tool_slug>/test/', views.test_tool, name='test_tool'),
    path('cases/', views.cases_list, name='cases_list'),
    path('cases/<int:case_id>/', views.case_detail, name='case_detail'),
    path('cases/<int:case_id>/update-notes/', views.update_case_notes, name='update_case_notes'),
    path('cases/<int:case_id>/report/', views.generate_case_report, name='generate_case_report'),
    path('sessions/', views.sessions_list, name='sessions_list'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/results/', views.session_results, name='session_results'),
    path('sessions/<int:session_id>/report/', views.generate_report, name='generate_report'),
    path('sessions/<int:session_id>/generate-report/', views.generate_session_report, name='generate_session_report'),
    path('results/', views.results_list, name='results_list'),
    path('results/<int:result_id>/', views.result_detail, name='result_detail'),
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/download/', views.download_report, name='download_report'),
    path('configurations/', views.configurations_list, name='configurations_list'),
    path('configurations/<int:config_id>/', views.configuration_detail, name='configuration_detail'),
    path('analytics/', views.osint_analytics, name='analytics'),
    
    # Utilities URLs
    path('utilities/', views.utilities_dashboard, name='utilities_dashboard'),
    path('utilities/hash-generator/', views.hash_generator, name='hash_generator'),
    path('utilities/coder-decoder/', views.coder_decoder, name='coder_decoder'),
    path('utilities/password-generator/', views.password_generator, name='password_generator'),
    path('utilities/jwt-inspector/', views.jwt_inspector, name='jwt_inspector'),
    path('utilities/timestamp-converter/', views.timestamp_converter, name='timestamp_converter'),
    path('utilities/json-formatter/', views.json_formatter, name='json_formatter'),
    path('utilities/text-diff/', views.text_diff, name='text_diff'),
    
    # Cybersecurity Resources
    path('cybersecurity-resources/', views.cybersecurity_resources, name='cybersecurity_resources'),
    
    # Server-Side OSINT Intelligence Tools
    path('intel/ip-lookup/', views.ip_lookup, name='ip_lookup'),
    path('intel/domain-recon/', views.domain_recon, name='domain_recon'),
    path('intel/email-scanner/', views.email_scanner, name='email_scanner'),
    path('intel/virustotal/', views.virustotal_scan, name='virustotal_scan'),
    path('intel/threat-intel/', views.threat_intel, name='threat_intel'),
    path('intel/phone-analyzer/', views.phone_analyzer, name='phone_analyzer'),
    path('intel/subdomain-enum/', views.subdomain_enum, name='subdomain_enum'),
    
    # AJAX API endpoints for intel tools
    path('api/intel/ip-lookup/', views.api_ip_lookup, name='api_ip_lookup'),
    path('api/intel/domain-recon/', views.api_domain_recon, name='api_domain_recon'),
    path('api/intel/email-scanner/', views.api_email_scanner, name='api_email_scanner'),
    path('api/intel/virustotal/', views.api_virustotal_scan, name='api_virustotal_scan'),
    path('api/intel/threat-feed/', views.api_threat_feed, name='api_threat_feed'),
    path('api/intel/phone-analyzer/', views.api_phone_analyzer, name='api_phone_analyzer'),
    path('api/intel/subdomain-enum/', views.api_subdomain_enum, name='api_subdomain_enum'),
    
    # AJAX URLs
    path('ajax/session-status/<int:session_id>/', views.get_session_status, name='get_session_status'),
    path('ajax/session-results/<int:session_id>/', views.ajax_session_results, name='ajax_session_results'),  # جديد
    path('ajax/tool-progress/<int:session_id>/', views.get_tool_progress, name='get_tool_progress'),
    path('ajax/export-results/<int:session_id>/', views.export_results, name='export_results'),
    path('ajax/completed-sessions/', views.ajax_completed_sessions, name='ajax_completed_sessions'),  # جديد
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/tools/<slug:tool_slug>/test/', views.test_tool, name='api_test_tool'),
]
