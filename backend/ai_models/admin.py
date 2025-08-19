from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    """Admin interface for ML Models"""
    
    list_display = [
        'name', 'model_type', 'version', 'status', 'algorithm', 'accuracy',
        'created_by', 'created_at', 'last_trained'
    ]
    
    list_filter = [
        'model_type', 'status', 'algorithm', 'created_at', 'last_trained'
    ]
    
    search_fields = ['name', 'description', 'algorithm']
    
    readonly_fields = [
        'created_at', 'updated_at', 'is_active', 'performance_summary_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'model_type', 'version', 'description', 'status')
        }),
        ('Model Configuration', {
            'fields': ('algorithm', 'hyperparameters', 'feature_columns', 'target_column')
        }),
        ('Model Files', {
            'fields': ('model_file_path', 'scaler_file_path', 'encoder_file_path'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('accuracy', 'precision', 'recall', 'f1_score', 'mae', 'rmse'),
            'classes': ('collapse',)
        }),
        ('Training Information', {
            'fields': ('training_data_size', 'validation_data_size', 'training_duration', 'last_trained'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def performance_summary_display(self, obj):
        """Display performance summary in a readable format"""
        if not obj.performance_summary:
            return "No performance data available"
        
        summary = obj.performance_summary
        html = "<div style='font-family: monospace;'>"
        for metric, value in summary.items():
            if value is not None:
                html += f"<div><strong>{metric.replace('_', ' ').title()}:</strong> {value:.4f}</div>"
        html += "</div>"
        return mark_safe(html)
    
    performance_summary_display.short_description = 'Performance Summary'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new model
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModelTrainingHistory)
class ModelTrainingHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Model Training History"""
    
    list_display = [
        'training_run_id', 'model', 'status', 'training_accuracy', 'validation_accuracy',
        'started_at', 'duration', 'data_size'
    ]
    
    list_filter = [
        'status', 'started_at', 'model__model_type', 'model__algorithm'
    ]
    
    search_fields = ['training_run_id', 'model__name']
    
    readonly_fields = [
        'training_time_minutes', 'started_at', 'completed_at', 'duration'
    ]
    
    fieldsets = (
        ('Training Information', {
            'fields': ('model', 'training_run_id', 'status')
        }),
        ('Training Results', {
            'fields': ('training_accuracy', 'validation_accuracy', 'training_loss', 'validation_loss')
        }),
        ('Performance Metrics', {
            'fields': ('precision', 'recall', 'f1_score'),
            'classes': ('collapse',)
        }),
        ('Training Configuration', {
            'fields': ('epochs', 'batch_size', 'learning_rate', 'hyperparameters'),
            'classes': ('collapse',)
        }),
        ('Timing Information', {
            'fields': ('started_at', 'completed_at', 'duration', 'training_time_minutes'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('data_size', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('model')
    
    def has_add_permission(self, request):
        """Only allow adding through the API or training process"""
        return False


@admin.register(FeatureEngineering)
class FeatureEngineeringAdmin(admin.ModelAdmin):
    """Admin interface for Feature Engineering"""
    
    list_display = [
        'name', 'scaling_method', 'encoding_method', 'created_by', 'created_at', 'is_active'
    ]
    
    list_filter = [
        'scaling_method', 'encoding_method', 'is_active', 'created_at'
    ]
    
    search_fields = ['name', 'description']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Feature Configuration', {
            'fields': ('input_features', 'output_features', 'transformations')
        }),
        ('Processing Methods', {
            'fields': ('scaling_method', 'encoding_method')
        }),
        ('Validation', {
            'fields': ('validation_rules', 'data_quality_checks'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new feature engineering
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModelPrediction)
class ModelPredictionAdmin(admin.ModelAdmin):
    """Admin interface for Model Predictions"""
    
    list_display = [
        'id', 'model', 'prediction_value', 'prediction_confidence', 'project_id',
        'created_at', 'is_accurate_display'
    ]
    
    list_filter = [
        'created_at', 'model__model_type', 'project_id', 'user_id'
    ]
    
    search_fields = ['model__name', 'project_id', 'user_id']
    
    readonly_fields = [
        'input_data_hash', 'created_at', 'is_accurate', 'prediction_error'
    ]
    
    fieldsets = (
        ('Prediction Information', {
            'fields': ('model', 'prediction_value', 'prediction_confidence')
        }),
        ('Input Data', {
            'fields': ('input_features', 'input_data_hash'),
            'classes': ('collapse',)
        }),
        ('Prediction Intervals', {
            'fields': ('prediction_interval_lower', 'prediction_interval_upper'),
            'classes': ('collapse',)
        }),
        ('Ground Truth', {
            'fields': ('actual_value', 'prediction_error', 'is_accurate'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('project_id', 'user_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('model')
    
    def has_add_permission(self, request):
        """Only allow adding through the API or prediction process"""
        return False
    
    def is_accurate_display(self, obj):
        """Display accuracy status with color coding"""
        if obj.is_accurate is None:
            return format_html('<span style="color: gray;">Unknown</span>')
        elif obj.is_accurate:
            return format_html('<span style="color: green;">✓ Accurate</span>')
        else:
            return format_html('<span style="color: red;">✗ Inaccurate</span>')
    
    is_accurate_display.short_description = 'Accuracy Status'
