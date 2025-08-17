"""
Serializers for unified project models.

Provides serialization and deserialization for all unified project
models, supporting both read and write operations with proper
validation and data transformation.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class IntegrationSystemSerializer(serializers.ModelSerializer):
    """Serializer for integration systems."""
    
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    connection_status_display = serializers.CharField(source='get_connection_status_display', read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = IntegrationSystem
        fields = [
            'id', 'name', 'system_type', 'system_type_display', 'status', 'status_display',
            'base_url', 'api_version', 'credentials', 'last_connection', 'connection_status',
            'connection_status_display', 'error_message', 'avg_response_time', 'total_requests',
            'failed_requests', 'success_rate', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'success_rate', 'total_requests', 'failed_requests'
        ]


class ProjectSystemMappingSerializer(serializers.ModelSerializer):
    """Serializer for project system mappings."""
    
    system_name = serializers.CharField(source='system.name', read_only=True)
    system_type = serializers.CharField(source='system.system_type', read_only=True)
    
    class Meta:
        model = ProjectSystemMapping
        fields = [
            'id', 'project', 'system', 'system_name', 'system_type', 'external_project_id',
            'external_project_number', 'external_project_name', 'last_sync', 'sync_status',
            'sync_error', 'field_mappings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UnifiedProjectSerializer(serializers.ModelSerializer):
    """Serializer for unified projects."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    budget_variance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    
    # Related fields
    project_manager = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    integration_systems = IntegrationSystemSerializer(many=True, read_only=True)
    system_mappings = ProjectSystemMappingSerializer(many=True, read_only=True)
    
    class Meta:
        model = UnifiedProject
        fields = [
            'id', 'name', 'description', 'project_number', 'status', 'status_display',
            'project_type', 'project_type_display', 'address', 'city', 'state', 'country',
            'postal_code', 'start_date', 'end_date', 'estimated_duration_days', 'budget',
            'actual_cost', 'currency', 'project_manager', 'client', 'architect', 'contractor',
            'progress_percentage', 'budget_variance', 'days_remaining', 'is_over_budget',
            'integration_systems', 'system_mappings', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'progress_percentage', 'budget_variance',
            'days_remaining', 'is_over_budget'
        ]


class UnifiedProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating unified projects."""
    
    class Meta:
        model = UnifiedProject
        fields = [
            'name', 'description', 'project_number', 'status', 'project_type', 'address',
            'city', 'state', 'country', 'postal_code', 'start_date', 'end_date',
            'estimated_duration_days', 'budget', 'actual_cost', 'currency', 'project_manager',
            'client', 'architect', 'contractor', 'integration_systems'
        ]


class UnifiedProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating unified projects."""
    
    class Meta:
        model = UnifiedProject
        fields = [
            'name', 'description', 'status', 'project_type', 'address', 'city', 'state',
            'country', 'postal_code', 'start_date', 'end_date', 'estimated_duration_days',
            'budget', 'actual_cost', 'currency', 'project_manager', 'client', 'architect',
            'contractor', 'integration_systems'
        ]


class ProjectDocumentSerializer(serializers.ModelSerializer):
    """Serializer for project documents."""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Related fields
    project = UnifiedProjectSerializer(read_only=True)
    system_mapping = ProjectSystemMappingSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'title', 'description', 'document_type', 'document_type_display', 'status',
            'status_display', 'file_name', 'file_size', 'file_type', 'file_url', 'version',
            'revision', 'project', 'system_mapping', 'external_document_id', 'external_metadata',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectDocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project documents."""
    
    class Meta:
        model = ProjectDocument
        fields = [
            'title', 'description', 'document_type', 'status', 'file_name', 'file_size',
            'file_type', 'file_url', 'version', 'revision', 'project', 'system_mapping',
            'external_document_id', 'external_metadata'
        ]


class ProjectScheduleSerializer(serializers.ModelSerializer):
    """Serializer for project schedules."""
    
    # Related fields
    project = UnifiedProjectSerializer(read_only=True)
    system_mapping = ProjectSystemMappingSerializer(read_only=True)
    
    class Meta:
        model = ProjectSchedule
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'total_duration_days',
            'critical_path_length', 'completion_percentage', 'project', 'system_mapping',
            'external_schedule_id', 'external_metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project schedules."""
    
    class Meta:
        model = ProjectSchedule
        fields = [
            'name', 'description', 'start_date', 'end_date', 'total_duration_days',
            'critical_path_length', 'completion_percentage', 'project', 'system_mapping',
            'external_schedule_id', 'external_metadata'
        ]


class ProjectFinancialSerializer(serializers.ModelSerializer):
    """Serializer for project financials."""
    
    financial_type_display = serializers.CharField(source='get_financial_type_display', read_only=True)
    
    # Related fields
    project = UnifiedProjectSerializer(read_only=True)
    system_mapping = ProjectSystemMappingSerializer(read_only=True)
    
    class Meta:
        model = ProjectFinancial
        fields = [
            'id', 'financial_type', 'financial_type_display', 'amount', 'currency',
            'labor_cost', 'material_cost', 'equipment_cost', 'subcontractor_cost',
            'overhead_cost', 'effective_date', 'period_start', 'period_end', 'project',
            'system_mapping', 'external_financial_id', 'external_metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectFinancialCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project financials."""
    
    class Meta:
        model = ProjectFinancial
        fields = [
            'financial_type', 'amount', 'currency', 'labor_cost', 'material_cost',
            'equipment_cost', 'subcontractor_cost', 'overhead_cost', 'effective_date',
            'period_start', 'period_end', 'project', 'system_mapping',
            'external_financial_id', 'external_metadata'
        ]


class ProjectChangeOrderSerializer(serializers.ModelSerializer):
    """Serializer for project change orders."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Related fields
    project = UnifiedProjectSerializer(read_only=True)
    system_mapping = ProjectSystemMappingSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectChangeOrder
        fields = [
            'id', 'change_order_number', 'title', 'description', 'status', 'status_display',
            'original_contract_value', 'change_order_value', 'new_total_value',
            'original_completion_date', 'new_completion_date', 'schedule_impact_days',
            'project', 'system_mapping', 'external_change_order_id', 'external_metadata',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectChangeOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project change orders."""
    
    class Meta:
        model = ProjectChangeOrder
        fields = [
            'change_order_number', 'title', 'description', 'status',
            'original_contract_value', 'change_order_value', 'new_total_value',
            'original_completion_date', 'new_completion_date', 'schedule_impact_days',
            'project', 'system_mapping', 'external_change_order_id', 'external_metadata'
        ]


class ProjectRFISerializer(serializers.ModelSerializer):
    """Serializer for project RFIs."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    
    # Related fields
    project = UnifiedProjectSerializer(read_only=True)
    system_mapping = ProjectSystemMappingSerializer(read_only=True)
    submitted_by = UserSerializer(read_only=True)
    answered_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectRFI
        fields = [
            'id', 'rfi_number', 'subject', 'question', 'answer', 'status', 'status_display',
            'priority', 'priority_display', 'date_submitted', 'date_answered', 'date_closed',
            'days_open', 'project', 'system_mapping', 'submitted_by', 'answered_by',
            'external_rfi_id', 'external_metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_open']


class ProjectRFICreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project RFIs."""
    
    class Meta:
        model = ProjectRFI
        fields = [
            'rfi_number', 'subject', 'question', 'answer', 'status', 'priority',
            'date_submitted', 'date_answered', 'date_closed', 'project', 'system_mapping',
            'submitted_by', 'answered_by', 'external_rfi_id', 'external_metadata'
        ]


# Summary and Analytics Serializers
class ProjectSummarySerializer(serializers.Serializer):
    """Serializer for project summary information."""
    
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_actual_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_progress = serializers.FloatField()
    projects_over_budget = serializers.IntegerField()
    projects_behind_schedule = serializers.IntegerField()


class ProjectAnalyticsSerializer(serializers.Serializer):
    """Serializer for project analytics data."""
    
    project_id = serializers.UUIDField()
    project_name = serializers.CharField()
    progress_percentage = serializers.FloatField()
    budget_variance = serializers.DecimalField(max_digits=15, decimal_places=2)
    days_remaining = serializers.IntegerField()
    risk_score = serializers.FloatField()
    integration_status = serializers.DictField()
    last_updated = serializers.DateTimeField()


class IntegrationStatusSerializer(serializers.Serializer):
    """Serializer for integration system status."""
    
    system_name = serializers.CharField()
    system_type = serializers.CharField()
    status = serializers.CharField()
    last_sync = serializers.DateTimeField()
    sync_status = serializers.CharField()
    error_count = serializers.IntegerField()
    success_rate = serializers.FloatField()
