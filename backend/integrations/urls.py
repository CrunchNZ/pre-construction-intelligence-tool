"""
URL configuration for integrations app.

Provides routing for all external system integrations including
ProcurePro, Procore, Jobpac, Greentree, and BIM systems.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    IntegrationSystemViewSet,
    UnifiedProjectViewSet,
    ProjectSystemMappingViewSet,
    ProjectDocumentViewSet,
    ProjectScheduleViewSet,
    ProjectFinancialViewSet,
    ProjectChangeOrderViewSet,
    ProjectRFIViewSet,
)
from .analytics_views import (
    AnalyticsViewSet,
    portfolio_summary_view,
    project_analytics_view,
    system_analytics_view,
    comparative_analytics_view,
    trend_analytics_view,
    risk_assessment_view,
    performance_metrics_view,
    clear_analytics_cache_view,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'integration-systems', IntegrationSystemViewSet)
router.register(r'unified-projects', UnifiedProjectViewSet)
router.register(r'project-system-mappings', ProjectSystemMappingViewSet)
router.register(r'project-documents', ProjectDocumentViewSet)
router.register(r'project-schedules', ProjectScheduleViewSet)
router.register(r'project-financials', ProjectFinancialViewSet)
router.register(r'project-change-orders', ProjectChangeOrderViewSet)
router.register(r'project-rfis', ProjectRFIViewSet)

# Analytics router
analytics_router = DefaultRouter()
analytics_router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # ProcurePro Integration
    path('procurepro/', include('integrations.procurepro.urls')),
    
    # Procore Integration
    path('procore/', include('integrations.procore.urls')),
    
    # Jobpac Integration
    path('jobpac/', include('integrations.jobpac.urls')),
    
    # Unified Project Management API
    path('api/', include(router.urls)),
    
    # Analytics API
    path('api/analytics/', include(analytics_router.urls)),
    
    # Individual analytics endpoints
    path('api/analytics/portfolio-summary/', portfolio_summary_view, name='portfolio_summary'),
    path('api/analytics/project/<str:project_id>/', project_analytics_view, name='project_analytics'),
    path('api/analytics/system/<str:system_type>/', system_analytics_view, name='system_analytics'),
    path('api/analytics/comparative/', comparative_analytics_view, name='comparative_analytics'),
    path('api/analytics/trends/', trend_analytics_view, name='trend_analytics'),
    path('api/analytics/risk-assessment/', risk_assessment_view, name='risk_assessment'),
    path('api/analytics/performance-metrics/', performance_metrics_view, name='performance_metrics'),
    path('api/analytics/clear-cache/', clear_analytics_cache_view, name='clear_analytics_cache'),
    
    # Integration overview and status
    path('', include('integrations.core.urls')),
]
