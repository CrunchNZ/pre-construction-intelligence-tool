"""
URL configuration for Jobpac integration.

Provides routing for Jobpac-specific API endpoints including
project data synchronization, analytics, and monitoring.
"""

from django.urls import path
from . import views

app_name = 'jobpac'

urlpatterns = [
    # Health and status endpoints
    path('health/', views.health_check, name='health_check'),
    path('status/', views.integration_status, name='integration_status'),
    
    # Project management endpoints
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/contacts/', views.project_contacts, name='project_contacts'),
    
    # Financial management endpoints
    path('projects/<int:project_id>/financials/', views.project_financials, name='project_financials'),
    path('projects/<int:project_id>/cost-centres/', views.cost_centres, name='cost_centres'),
    path('projects/<int:project_id>/purchase-orders/', views.purchase_orders, name='purchase_orders'),
    path('projects/<int:project_id>/purchase-orders/<int:po_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    
    # Time and attendance endpoints
    path('projects/<int:project_id>/timesheets/', views.timesheets, name='timesheets'),
    path('projects/<int:project_id>/timesheets/<int:timesheet_id>/', views.timesheet_detail, name='timesheet_detail'),
    
    # Equipment and resources endpoints
    path('projects/<int:project_id>/equipment/', views.equipment, name='equipment'),
    path('projects/<int:project_id>/equipment/<int:equipment_id>/usage/', views.equipment_usage, name='equipment_usage'),
    
    # Subcontractor management endpoints
    path('projects/<int:project_id>/subcontractors/', views.subcontractors, name='subcontractors'),
    path('projects/<int:project_id>/subcontractors/<int:subcontractor_id>/', views.subcontractor_detail, name='subcontractor_detail'),
    
    # Company and user endpoints
    path('company/info/', views.company_info, name='company_info'),
    path('users/', views.users, name='users'),
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
