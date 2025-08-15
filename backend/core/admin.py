"""
Admin configuration for core models.

This module configures the Django admin interface for
managing projects, suppliers, and related data.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Project, Supplier, ProjectSupplier, HistoricalData, RiskAssessment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    
    list_display = [
        'name', 'project_type', 'status', 'location', 'start_date', 
        'estimated_budget', 'cost_variance_display', 'created_by'
    ]
    list_filter = [
        'project_type', 'status', 'start_date', 'created_at',
        ('created_by', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['name', 'description', 'location', 'external_id']
    readonly_fields = ['cost_variance', 'cost_variance_percentage', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'project_type', 'status')
        }),
        ('Location & Timing', {
            'fields': ('location', 'start_date', 'end_date', 'estimated_duration_days')
        }),
        ('Financial Information', {
            'fields': ('estimated_budget', 'actual_budget', 'cost_variance', 'cost_variance_percentage')
        }),
        ('Project Details', {
            'fields': ('square_footage', 'floors', 'complexity_score')
        }),
        ('External Systems', {
            'fields': ('external_id', 'source_system'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def cost_variance_display(self, obj):
        """Display cost variance with color coding."""
        if obj.cost_variance is None:
            return '-'
        
        if obj.cost_variance > 0:
            color = 'red'
            icon = '🔴'
        elif obj.cost_variance < 0:
            color = 'green'
            icon = '🟢'
        else:
            color = 'black'
            icon = '⚫'
        
        return format_html(
            '<span style="color: {};">{} ${:,.2f}</span>',
            color, icon, abs(obj.cost_variance)
        )
    cost_variance_display.short_description = 'Cost Variance'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('created_by')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin configuration for Supplier model."""
    
    list_display = [
        'name', 'company_type', 'contact_person', 'overall_score_display',
        'reliability_score', 'quality_score', 'cost_score', 'is_active'
    ]
    list_filter = [
        'company_type', 'is_active', 'created_at',
        'overall_score'
    ]
    search_fields = ['name', 'contact_person', 'email', 'external_id']
    readonly_fields = ['overall_score', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_type', 'contact_person', 'email', 'phone')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('tax_id', 'insurance_info', 'certifications'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('reliability_score', 'quality_score', 'cost_score', 'overall_score')
        }),
        ('External Systems', {
            'fields': ('external_id', 'source_system'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def overall_score_display(self, obj):
        """Display overall score with color coding."""
        if obj.overall_score is None:
            return '-'
        
        if obj.overall_score >= 80:
            color = 'green'
        elif obj.overall_score >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
            color, obj.overall_score
        )
    overall_score_display.short_description = 'Overall Score'
    
    actions = ['recalculate_scores']
    
    def recalculate_scores(self, request, queryset):
        """Recalculate overall scores for selected suppliers."""
        updated = 0
        for supplier in queryset:
            supplier.calculate_overall_score()
            updated += 1
        
        self.message_user(
            request,
            f'Successfully recalculated scores for {updated} suppliers.'
        )
    recalculate_scores.short_description = 'Recalculate overall scores'


@admin.register(ProjectSupplier)
class ProjectSupplierAdmin(admin.ModelAdmin):
    """Admin configuration for ProjectSupplier model."""
    
    list_display = [
        'project', 'supplier', 'relationship_type', 'contract_value',
        'quality_rating_display', 'cost_variance_display', 'on_time_delivery'
    ]
    list_filter = [
        'relationship_type', 'on_time_delivery', 'created_at',
        ('project', admin.RelatedOnlyFieldListFilter),
        ('supplier', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['project__name', 'supplier__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('project', 'supplier', 'relationship_type')
        }),
        ('Contract Details', {
            'fields': ('contract_value', 'contract_start_date', 'contract_end_date')
        }),
        ('Performance', {
            'fields': ('on_time_delivery', 'quality_rating', 'cost_variance')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def quality_rating_display(self, obj):
        """Display quality rating with stars."""
        if obj.quality_rating is None:
            return '-'
        
        stars = '⭐' * obj.quality_rating
        return format_html('<span title="{}">{}</span>', obj.quality_rating, stars)
    quality_rating_display.short_description = 'Quality Rating'
    
    def cost_variance_display(self, obj):
        """Display cost variance with color coding."""
        if obj.cost_variance is None:
            return '-'
        
        if obj.cost_variance > 0:
            color = 'red'
            icon = '🔴'
        elif obj.cost_variance < 0:
            color = 'green'
            icon = '🟢'
        else:
            color = 'black'
            icon = '⚫'
        
        return format_html(
            '<span style="color: {};">{} ${:,.2f}</span>',
            color, icon, abs(obj.cost_variance)
        )
    cost_variance_display.short_description = 'Cost Variance'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('project', 'supplier')


@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    """Admin configuration for HistoricalData model."""
    
    list_display = [
        'project', 'data_type', 'source_system', 'data_date',
        'is_processed', 'external_record_id', 'created_at'
    ]
    list_filter = [
        'data_type', 'source_system', 'is_processed', 'data_date', 'created_at',
        ('project', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['project__name', 'external_record_id', 'source_system']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'data_date'
    
    fieldsets = (
        ('Data Identification', {
            'fields': ('project', 'data_type', 'source_system', 'external_record_id')
        }),
        ('Data Content', {
            'fields': ('data', 'data_date')
        }),
        ('Processing', {
            'fields': ('is_processed', 'processing_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('project')
    
    actions = ['mark_as_processed']
    
    def mark_as_processed(self, request, queryset):
        """Mark selected historical data as processed."""
        updated = queryset.update(is_processed=True)
        self.message_user(
            request,
            f'Successfully marked {updated} records as processed.'
        )
    mark_as_processed.short_description = 'Mark as processed'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for RiskAssessment model."""
    
    list_display = [
        'project', 'title', 'risk_category', 'risk_level_display',
        'probability', 'impact_score', 'risk_score_display',
        'is_active', 'is_mitigated', 'assigned_to'
    ]
    list_filter = [
        'risk_category', 'risk_level', 'is_active', 'is_mitigated',
        'created_at',         ('project', admin.RelatedOnlyFieldListFilter),
        ('assigned_to', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['project__name', 'title', 'description']
    readonly_fields = ['risk_score', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Risk Information', {
            'fields': ('project', 'risk_category', 'risk_level', 'title', 'description')
        }),
        ('Risk Metrics', {
            'fields': ('probability', 'impact_score', 'risk_score')
        }),
        ('AI Model', {
            'fields': ('ai_model_version', 'confidence_score', 'factors'),
            'classes': ('collapse',)
        }),
        ('Mitigation', {
            'fields': ('mitigation_strategy', 'assigned_to', 'is_mitigated', 'mitigation_date')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def risk_level_display(self, obj):
        """Display risk level with color coding."""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        
        color = colors.get(obj.risk_level, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.risk_level.upper()
        )
    risk_level_display.short_description = 'Risk Level'
    
    def risk_score_display(self, obj):
        """Display risk score with color coding."""
        if obj.risk_score is None:
            return '-'
        
        if obj.risk_score >= 7:
            color = 'red'
        elif obj.risk_score >= 4:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
            color, obj.risk_score
        )
    risk_score_display.short_description = 'Risk Score'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('project', 'assigned_to')
    
    actions = ['activate_risks', 'deactivate_risks']
    
    def activate_risks(self, request, queryset):
        """Activate selected risk assessments."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Successfully activated {updated} risk assessments.'
        )
    activate_risks.short_description = 'Activate selected risks'
    
    def deactivate_risks(self, request, queryset):
        """Deactivate selected risk assessments."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Successfully deactivated {updated} risk assessments.'
        )
    deactivate_risks.short_description = 'Deactivate selected risks'
