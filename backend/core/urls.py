"""
URL configuration for core app.

This module defines the URL patterns for the core functionality
of the Pre-Construction Intelligence Tool.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'suppliers', views.SupplierViewSet, basename='supplier')
router.register(r'project-suppliers', views.ProjectSupplierViewSet, basename='project-supplier')
router.register(r'historical-data', views.HistoricalDataViewSet, basename='historical-data')
router.register(r'risk-assessments', views.RiskAssessmentViewSet, basename='risk-assessment')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('projects/<int:pk>/cost-variance/', views.ProjectCostVarianceView.as_view(), name='project-cost-variance'),
    path('suppliers/<int:pk>/score/', views.SupplierScoreView.as_view(), name='supplier-score'),
    path('risk-analysis/', views.RiskAnalysisView.as_view(), name='risk-analysis'),
]
