"""
URL configuration for Procore integration.

Provides routing for Procore-specific API endpoints including
project data synchronization, analytics, and monitoring.
"""

from django.urls import path
from . import views

app_name = 'procore'

urlpatterns = [
    # Health and status endpoints
    path('health/', views.health_check, name='health_check'),
    path('status/', views.integration_status, name='integration_status'),
    
    # Project management endpoints
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/contacts/', views.project_contacts, name='project_contacts'),
    
    # Document management endpoints
    path('projects/<int:project_id>/documents/', views.project_documents, name='project_documents'),
    path('projects/<int:project_id>/documents/<int:document_id>/', views.document_detail, name='document_detail'),
    
    # Schedule management endpoints
    path('projects/<int:project_id>/schedule/', views.project_schedule, name='project_schedule'),
    path('projects/<int:project_id>/schedule-items/', views.schedule_items, name='schedule_items'),
    
    # Financial management endpoints
    path('projects/<int:project_id>/budget/', views.project_budget, name='project_budget'),
    path('projects/<int:project_id>/cost-codes/', views.cost_codes, name='cost_codes'),
    
    # Change management endpoints
    path('projects/<int:project_id>/change-orders/', views.change_orders, name='change_orders'),
    path('projects/<int:project_id>/change-orders/<int:change_order_id>/', views.change_order_detail, name='change_order_detail'),
    
    # Submittal management endpoints
    path('projects/<int:project_id>/submittals/', views.submittals, name='submittals'),
    path('projects/<int:project_id>/submittals/<int:submittal_id>/', views.submittal_detail, name='submittal_detail'),
    
    # RFI management endpoints
    path('projects/<int:project_id>/rfis/', views.rfis, name='rfis'),
    path('projects/<int:project_id>/rfis/<int:rfi_id>/', views.rfi_detail, name='rfi_detail'),
    
    # Company and user endpoints
    path('company/users/', views.company_users, name='company_users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Synchronization endpoints
    path('sync/projects/', views.sync_projects, name='sync_projects'),
    path('sync/projects/<int:project_id>/', views.sync_project, name='sync_project'),
    path('sync/status/', views.sync_status, name='sync_status'),
    
    # Analytics endpoints
    path('analytics/projects/', views.projects_analytics, name='projects_analytics'),
    path('analytics/projects/<int:project_id>/', views.project_analytics, name='project_analytics'),
    path('analytics/company/', views.company_analytics, name='company_analytics'),
]
