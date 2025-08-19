"""
Admin configuration for integrations app.

Provides administrative interface for managing integration systems,
unified projects, and related data across all platforms.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    IntegrationSystem,
    UnifiedProject,
    ProjectSystemMapping,
    ProjectDocument,
    ProjectSchedule,
    ProjectFinancial,
    ProjectChangeOrder,
    ProjectRFI,
)


@admin.register(IntegrationSystem)
class IntegrationSystemAdmin(admin.ModelAdmin):
    """Admin interface for integration systems."""
    
    list_display = [
        'name', 'system_type', 'status', 'connection_status',
        'last_connection', 'success_rate', 'avg_response_time'
    ]
    
    list_filter = ['system_type', 'status', 'connection_status']
    search_fields = ['name', 'base_url']
    readonly_fields = ['created_at', 'updated_at', 'success_rate']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'system_type', 'status')
        }),
        ('Configuration', {
            'fields': ('base_url', 'api_version', 'credentials')
        }),
        ('Connection Status', {
            'fields': ('connection_status', 'last_connection', 'error_message')
        }),
        ('Performance Metrics', {
            'fields': ('avg_response_time', 'total_requests', 'failed_requests')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def success_rate(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 75:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate.short_description = 'Success Rate'


@admin.register(UnifiedProject)
class UnifiedProjectAdmin(admin.ModelAdmin):
    """Admin interface for unified projects."""
    
    list_display = [
        'name', 'project_number', 'status', 'project_type',
        'start_date', 'end_date', 'progress_percentage',
        'budget', 'actual_cost', 'is_over_budget'
    ]
    
    list_filter = ['status', 'project_type', 'start_date', 'end_date']
    search_fields = ['name', 'project_number', 'description', 'client']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'budget_variance', 'days_remaining']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'project_number', 'status', 'project_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'estimated_duration_days')
        }),
        ('Financial', {
            'fields': ('budget', 'actual_cost', 'currency')
        }),
        ('Team', {
            'fields': ('project_manager', 'client', 'architect', 'contractor')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    # Remove filter_horizontal since integration_systems uses a custom through model
    
    def progress_percentage(self, obj):
        """Display progress percentage with color coding."""
        progress = obj.progress_percentage
        if progress >= 80:
            color = 'green'
        elif progress >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, progress
        )
    progress_percentage.short_description = 'Progress'
    
    def is_over_budget(self, obj):
        """Display budget status."""
        if obj.is_over_budget:
            return format_html('<span style="color: red;">Over Budget</span>')
        return format_html('<span style="color: green;">Within Budget</span>')
    is_over_budget.short_description = 'Budget Status'


@admin.register(ProjectSystemMapping)
class ProjectSystemMappingAdmin(admin.ModelAdmin):
    """Admin interface for project system mappings."""
    
    list_display = [
        'project', 'system', 'external_project_id',
        'sync_status', 'last_sync'
    ]
    
    list_filter = ['system', 'sync_status', 'last_sync']
    search_fields = ['project__name', 'external_project_id', 'external_project_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Mapping', {
            'fields': ('project', 'system', 'external_project_id')
        }),
        ('External Data', {
            'fields': ('external_project_number', 'external_project_name')
        }),
        ('Synchronization', {
            'fields': ('sync_status', 'last_sync', 'sync_error')
        }),
        ('Configuration', {
            'fields': ('field_mappings',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    """Admin interface for project documents."""
    
    list_display = [
        'title', 'project', 'document_type', 'status',
        'version', 'file_size', 'created_at'
    ]
    
    list_filter = ['document_type', 'status', 'created_at']
    search_fields = ['title', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description', 'document_type', 'status')
        }),
        ('File Details', {
            'fields': ('file_name', 'file_size', 'file_type', 'file_url')
        }),
        ('Version Control', {
            'fields': ('version', 'revision')
        }),
        ('Relationships', {
            'fields': ('project', 'system_mapping')
        }),
        ('External Data', {
            'fields': ('external_document_id', 'external_metadata')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProjectSchedule)
class ProjectScheduleAdmin(admin.ModelAdmin):
    """Admin interface for project schedules."""
    
    list_display = [
        'name', 'project', 'start_date', 'end_date',
        'total_duration_days', 'completion_percentage'
    ]
    
    list_filter = ['start_date', 'end_date']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('name', 'description', 'start_date', 'end_date')
        }),
        ('Duration', {
            'fields': ('total_duration_days', 'critical_path_length', 'completion_percentage')
        }),
        ('Relationships', {
            'fields': ('project', 'system_mapping')
        }),
        ('External Data', {
            'fields': ('external_schedule_id', 'external_metadata')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProjectFinancial)
class ProjectFinancialAdmin(admin.ModelAdmin):
    """Admin interface for project financials."""
    
    list_display = [
        'project', 'financial_type', 'amount', 'currency',
        'effective_date', 'labor_cost', 'material_cost'
    ]
    
    list_filter = ['financial_type', 'currency', 'effective_date']
    search_fields = ['project__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Financial Information', {
            'fields': ('financial_type', 'amount', 'currency')
        }),
        ('Cost Breakdown', {
            'fields': ('labor_cost', 'material_cost', 'equipment_cost', 'subcontractor_cost', 'overhead_cost')
        }),
        ('Timing', {
            'fields': ('effective_date', 'period_start', 'period_end')
        }),
        ('Relationships', {
            'fields': ('project', 'system_mapping')
        }),
        ('External Data', {
            'fields': ('external_financial_id', 'external_metadata')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProjectChangeOrder)
class ProjectChangeOrderAdmin(admin.ModelAdmin):
    """Admin interface for project change orders."""
    
    list_display = [
        'change_order_number', 'project', 'title', 'status',
        'change_order_value', 'schedule_impact_days'
    ]
    
    list_filter = ['status', 'created_at']
    search_fields = ['change_order_number', 'title', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Change Order Information', {
            'fields': ('change_order_number', 'title', 'description', 'status')
        }),
        ('Financial Impact', {
            'fields': ('original_contract_value', 'change_order_value', 'new_total_value')
        }),
        ('Schedule Impact', {
            'fields': ('original_completion_date', 'new_completion_date', 'schedule_impact_days')
        }),
        ('Relationships', {
            'fields': ('project', 'system_mapping')
        }),
        ('External Data', {
            'fields': ('external_change_order_id', 'external_metadata')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProjectRFI)
class ProjectRFIAdmin(admin.ModelAdmin):
    """Admin interface for project RFIs."""
    
    list_display = [
        'rfi_number', 'project', 'subject', 'status',
        'priority', 'date_submitted', 'days_open'
    ]
    
    list_filter = ['status', 'priority', 'date_submitted']
    search_fields = ['rfi_number', 'subject', 'question', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'days_open']
    
    fieldsets = (
        ('RFI Information', {
            'fields': ('rfi_number', 'subject', 'question', 'answer', 'status', 'priority')
        }),
        ('Timeline', {
            'fields': ('date_submitted', 'date_answered', 'date_closed')
        }),
        ('Relationships', {
            'fields': ('project', 'system_mapping', 'submitted_by', 'answered_by')
        }),
        ('External Data', {
            'fields': ('external_rfi_id', 'external_metadata')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def days_open(self, obj):
        """Display days open with color coding."""
        days = obj.days_open
        if days <= 7:
            color = 'green'
        elif days <= 14:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} days</span>',
            color, days
        )
    days_open.short_description = 'Days Open'
