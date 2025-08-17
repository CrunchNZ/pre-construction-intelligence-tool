"""
Django Admin Interface for External APIs Integration

This module provides the admin interface for managing external API integrations,
weather data, data quality monitoring, and backup/recovery operations.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    """Admin interface for WeatherData model."""
    
    list_display = ('location', 'weather_type', 'units', 'timestamp', 'expires_at', 'is_active', 'status_indicator')
    list_filter = ('weather_type', 'units', 'is_active', 'timestamp')
    search_fields = ('location',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Location Information', {
            'fields': ('location', 'weather_type', 'units')
        }),
        ('Weather Data', {
            'fields': ('weather_data',)
        }),
        ('Timing', {
            'fields': ('timestamp', 'expires_at', 'is_active')
        })
    )
    
    def status_indicator(self, obj):
        """Display status indicator for weather data."""
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">EXPIRED</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">INACTIVE</span>'
            )
    
    status_indicator.short_description = 'Status'


@admin.register(WeatherImpactAnalysis)
class WeatherImpactAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for WeatherImpactAnalysis model."""
    
    list_display = ('project_id', 'location', 'project_type', 'impact_score', 'analysis_date', 'score_indicator')
    list_filter = ('project_type', 'location', 'analysis_date')
    search_fields = ('project_id', 'location')
    readonly_fields = ('analysis_date',)
    date_hierarchy = 'analysis_date'
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project_id', 'location', 'project_type')
        }),
        ('Analysis Results', {
            'fields': ('impact_score', 'risk_factors', 'recommendations', 'cost_impact')
        }),
        ('Metadata', {
            'fields': ('analysis_date', 'weather_data')
        })
    )
    
    def score_indicator(self, obj):
        """Display impact score with color coding."""
        if obj.impact_score >= 70:
            color = 'red'
            label = 'HIGH'
        elif obj.impact_score >= 40:
            color = 'orange'
            label = 'MEDIUM'
        else:
            color = 'green'
            label = 'LOW'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.1f})</span>',
            color, label, obj.impact_score
        )
    
    score_indicator.short_description = 'Impact Level'


@admin.register(DataQualityRecord)
class DataQualityRecordAdmin(admin.ModelAdmin):
    """Admin interface for DataQualityRecord model."""
    
    list_display = ('system_name', 'overall_score', 'assessment_date', 'data_sample_size', 'quality_indicator')
    list_filter = ('system_name', 'assessment_date')
    search_fields = ('system_name',)
    readonly_fields = ('assessment_date',)
    date_hierarchy = 'assessment_date'
    
    fieldsets = (
        ('System Information', {
            'fields': ('system_name', 'data_sample_size')
        }),
        ('Quality Assessment', {
            'fields': ('quality_metrics', 'overall_score', 'issues', 'recommendations')
        }),
        ('Timing', {
            'fields': ('assessment_date',)
        })
    )
    
    def quality_indicator(self, obj):
        """Display quality score with color coding."""
        if obj.overall_score >= 80:
            color = 'green'
            label = 'EXCELLENT'
        elif obj.overall_score >= 70:
            color = 'orange'
            label = 'GOOD'
        elif obj.overall_score >= 60:
            color = 'red'
            label = 'FAIR'
        else:
            color = 'darkred'
            label = 'POOR'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.1f})</span>',
            color, label, obj.overall_score
        )
    
    quality_indicator.short_description = 'Quality Level'


@admin.register(DataBackupRecord)
class DataBackupRecordAdmin(admin.ModelAdmin):
    """Admin interface for DataBackupRecord model."""
    
    list_display = ('backup_id', 'system_name', 'backup_type', 'backup_date', 'file_size_mb', 'status_indicator')
    list_filter = ('system_name', 'backup_type', 'backup_date', 'is_active')
    search_fields = ('backup_id', 'system_name')
    readonly_fields = ('backup_date', 'file_size_bytes', 'checksum')
    date_hierarchy = 'backup_date'
    
    fieldsets = (
        ('Backup Information', {
            'fields': ('backup_id', 'system_name', 'backup_type')
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size_bytes', 'checksum')
        }),
        ('Configuration', {
            'fields': ('compression_enabled', 'encryption_enabled')
        }),
        ('Timing', {
            'fields': ('backup_date', 'retention_date', 'is_active')
        })
    )
    
    def status_indicator(self, obj):
        """Display backup status indicator."""
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">EXPIRED</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">INACTIVE</span>'
            )
    
    status_indicator.short_description = 'Status'
    
    def file_size_mb(self, obj):
        """Display file size in MB."""
        return f"{obj.file_size_mb:.2f} MB"
    
    file_size_mb.short_description = 'File Size'


@admin.register(DataRecoveryRecord)
class DataRecoveryRecordAdmin(admin.ModelAdmin):
    """Admin interface for DataRecoveryRecord model."""
    
    list_display = ('recovery_id', 'backup_record', 'target_system', 'recovery_date', 'status', 'status_indicator')
    list_filter = ('status', 'target_system', 'recovery_date')
    search_fields = ('recovery_id', 'target_system')
    readonly_fields = ('recovery_date', 'restored_data_size')
    date_hierarchy = 'recovery_date'
    
    fieldsets = (
        ('Recovery Information', {
            'fields': ('recovery_id', 'backup_record', 'target_system')
        }),
        ('Recovery Details', {
            'fields': ('restore_options', 'restored_data_size')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timing', {
            'fields': ('recovery_date',)
        })
    )
    
    def status_indicator(self, obj):
        """Display recovery status indicator."""
        if obj.status == 'completed':
            color = 'green'
        elif obj.status == 'failed':
            color = 'red'
        elif obj.status == 'in_progress':
            color = 'orange'
        else:
            color = 'gray'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )
    
    status_indicator.short_description = 'Status'


@admin.register(DataFlowExecution)
class DataFlowExecutionAdmin(admin.ModelAdmin):
    """Admin interface for DataFlowExecution model."""
    
    list_display = ('execution_id', 'flow_name', 'status', 'start_time', 'end_time', 'duration_display', 'status_indicator')
    list_filter = ('status', 'flow_name', 'start_time')
    search_fields = ('execution_id', 'flow_name')
    readonly_fields = ('start_time', 'end_time', 'duration_seconds')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('execution_id', 'flow_name', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_seconds')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data')
        }),
        ('Results', {
            'fields': ('errors', 'performance_metrics', 'steps')
        })
    )
    
    def duration_display(self, obj):
        """Display execution duration in a readable format."""
        duration = obj.duration_seconds
        if duration is None:
            return 'Running...'
        
        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            minutes = duration / 60
            return f"{minutes:.1f}m"
        else:
            hours = duration / 3600
            return f"{hours:.1f}h"
    
    duration_display.short_description = 'Duration'
    
    def status_indicator(self, obj):
        """Display execution status indicator."""
        if obj.status == 'completed':
            color = 'green'
        elif obj.status == 'failed':
            color = 'red'
        elif obj.status == 'running':
            color = 'orange'
        else:
            color = 'blue'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )
    
    status_indicator.short_description = 'Status'


@admin.register(ExternalAPIConfig)
class ExternalAPIConfigAdmin(admin.ModelAdmin):
    """Admin interface for ExternalAPIConfig model."""
    
    list_display = ('api_name', 'api_type', 'base_url', 'is_active', 'health_status', 'health_indicator')
    list_filter = ('api_type', 'is_active', 'health_status')
    search_fields = ('api_name', 'base_url')
    readonly_fields = ('created_at', 'updated_at', 'last_health_check')
    
    fieldsets = (
        ('API Information', {
            'fields': ('api_name', 'api_type', 'base_url')
        }),
        ('Authentication', {
            'fields': ('api_key',)
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_day', 'timeout_seconds')
        }),
        ('Status', {
            'fields': ('is_active', 'health_status', 'last_health_check')
        }),
        ('Configuration', {
            'fields': ('configuration',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def health_indicator(self, obj):
        """Display health status indicator."""
        if obj.health_status == 'healthy':
            color = 'green'
        elif obj.health_status == 'degraded':
            color = 'orange'
        elif obj.health_status == 'unhealthy':
            color = 'red'
        else:
            color = 'gray'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.health_status.upper()
        )
    
    health_indicator.short_description = 'Health'


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """Admin interface for APIUsageLog model."""
    
    list_display = ('api_config', 'endpoint', 'method', 'status_code', 'success', 'response_time_ms', 'request_timestamp', 'success_indicator')
    list_filter = ('api_config', 'method', 'success', 'status_code', 'request_timestamp')
    search_fields = ('endpoint', 'api_config__api_name')
    readonly_fields = ('request_timestamp', 'response_timestamp', 'response_time_ms')
    date_hierarchy = 'request_timestamp'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('api_config', 'endpoint', 'method')
        }),
        ('Timing', {
            'fields': ('request_timestamp', 'response_timestamp', 'response_time_ms')
        }),
        ('Response', {
            'fields': ('status_code', 'success', 'error_message')
        }),
        ('Data Sizes', {
            'fields': ('request_size_bytes', 'response_size_bytes')
        }),
        ('User', {
            'fields': ('user',)
        })
    )
    
    def success_indicator(self, obj):
        """Display success indicator."""
        if obj.success:
            color = 'green'
            label = 'SUCCESS'
        else:
            color = 'red'
            label = 'FAILED'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, label
        )
    
    success_indicator.short_description = 'Result'
