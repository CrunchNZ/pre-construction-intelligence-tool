"""
URL Configuration for External APIs Integration

This module defines the URL patterns for external API integrations,
weather services, data quality monitoring, and backup/recovery operations.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API viewsets
router = DefaultRouter()
router.register(r'weather', views.WeatherViewSet, basename='weather')
router.register(r'weather-impact', views.WeatherImpactViewSet, basename='weather-impact')
router.register(r'data-quality', views.DataQualityViewSet, basename='data-quality')
router.register(r'backups', views.DataBackupViewSet, basename='backups')
router.register(r'recovery', views.DataRecoveryViewSet, basename='recovery')
router.register(r'data-flows', views.DataFlowViewSet, basename='data-flows')
router.register(r'api-config', views.ExternalAPIConfigViewSet, basename='api-config')
router.register(r'api-usage', views.APIUsageViewSet, basename='api-usage')

app_name = 'external_apis'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Weather services
    path('weather/current/<str:location>/', views.current_weather, name='current_weather'),
    path('weather/forecast/<str:location>/', views.weather_forecast, name='weather_forecast'),
    path('weather/alerts/<str:location>/', views.weather_alerts, name='weather_alerts'),
    path('weather/impact-analysis/', views.weather_impact_analysis, name='weather_impact_analysis'),
    path('weather/portfolio-analysis/', views.portfolio_weather_analysis, name='portfolio_weather_analysis'),
    
    # Data quality monitoring
    path('data-quality/check/<str:system_name>/', views.check_data_quality, name='check_data_quality'),
    path('data-quality/report/<str:system_name>/', views.get_quality_report, name='get_quality_report'),
    path('data-quality/trends/<str:system_name>/', views.get_quality_trends, name='get_quality_trends'),
    
    # Data backup and recovery
    path('backups/create/<str:system_name>/', views.create_backup, name='create_backup'),
    path('backups/restore/<str:backup_id>/', views.restore_backup, name='restore_backup'),
    path('backups/list/<str:system_name>/', views.list_backups, name='list_backups'),
    path('backups/delete/<str:backup_id>/', views.delete_backup, name='delete_backup'),
    
    # Data flow orchestration
    path('data-flows/register/', views.register_data_flow, name='register_data_flow'),
    path('data-flows/execute/<str:flow_name>/', views.execute_data_flow, name='execute_data_flow'),
    path('data-flows/status/<str:execution_id>/', views.get_flow_status, name='get_flow_status'),
    path('data-flows/performance/<str:flow_name>/', views.get_flow_performance, name='get_flow_performance'),
    
    # External API management
    path('api-config/health-check/<str:api_name>/', views.check_api_health, name='check_api_health'),
    path('api-config/configure/<str:api_name>/', views.configure_api, name='configure_api'),
    path('api-config/usage-stats/<str:api_name>/', views.get_api_usage_stats, name='get_api_usage_stats'),
    
    # Utility endpoints
    path('health/', views.health_check, name='health_check'),
    path('status/', views.system_status, name='system_status'),
    path('metrics/', views.get_metrics, name='get_metrics'),
]
