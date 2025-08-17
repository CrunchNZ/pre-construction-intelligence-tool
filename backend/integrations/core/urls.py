"""
Core integrations URL configuration.

Provides overview and status endpoints for all integrations.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Integration overview
    path('', views.IntegrationsOverviewView.as_view(), name='integrations-overview'),
    
    # Integration status
    path('status/', views.IntegrationsStatusView.as_view(), name='integrations-status'),
    
    # Integration health
    path('health/', views.IntegrationsHealthView.as_view(), name='integrations-health'),
    
    # Integration configuration
    path('config/', views.IntegrationsConfigView.as_view(), name='integrations-config'),
]

