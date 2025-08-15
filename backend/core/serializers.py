"""
Serializers for the core models.

This module contains Django REST Framework serializers for
converting model instances to JSON and vice versa.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Supplier, ProjectSupplier, HistoricalData, RiskAssessment
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    
    created_by = UserSerializer(read_only=True)
    cost_variance_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'project_type', 'status',
            'location', 'start_date', 'end_date', 'estimated_duration_days',
            'estimated_budget', 'actual_budget', 'cost_variance', 'cost_variance_percentage',
            'square_footage', 'floors', 'complexity_score',
            'external_id', 'source_system', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'cost_variance', 'cost_variance_percentage', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate project data."""
        # Ensure end_date is after start_date if both are provided
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError("End date must be after start date.")
        
        # Ensure estimated_duration_days is positive
        if data.get('estimated_duration_days') and data['estimated_duration_days'] <= 0:
            raise serializers.ValidationError("Estimated duration must be positive.")
        
        # Ensure complexity_score is within valid range
        if data.get('complexity_score') and (data['complexity_score'] < 1 or data['complexity_score'] > 10):
            raise serializers.ValidationError("Complexity score must be between 1 and 10.")
        
        return data


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'company_type', 'contact_person', 'email', 'phone',
            'address', 'city', 'state', 'country', 'postal_code',
            'tax_id', 'insurance_info', 'certifications',
            'overall_score', 'reliability_score', 'quality_score', 'cost_score',
            'external_id', 'source_system', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'overall_score', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate supplier data."""
        # Ensure scores are within valid range
        for score_field in ['reliability_score', 'quality_score', 'cost_score']:
            if data.get(score_field) and (data[score_field] < 0 or data[score_field] > 100):
                raise serializers.ValidationError(f"{score_field.replace('_', ' ').title()} must be between 0 and 100.")
        
        return data


class ProjectSupplierSerializer(serializers.ModelSerializer):
    """Serializer for ProjectSupplier model."""
    
    project = ProjectSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectSupplier
        fields = [
            'id', 'project', 'supplier', 'project_id', 'supplier_id',
            'relationship_type', 'contract_value', 'contract_start_date', 'contract_end_date',
            'on_time_delivery', 'quality_rating', 'cost_variance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate project-supplier relationship data."""
        # Ensure contract_end_date is after contract_start_date if both are provided
        if data.get('contract_start_date') and data.get('contract_end_date'):
            if data['contract_end_date'] <= data['contract_start_date']:
                raise serializers.ValidationError("Contract end date must be after start date.")
        
        # Ensure quality_rating is within valid range
        if data.get('quality_rating') and (data['quality_rating'] < 1 or data['quality_rating'] > 5):
            raise serializers.ValidationError("Quality rating must be between 1 and 5.")
        
        return data


class HistoricalDataSerializer(serializers.ModelSerializer):
    """Serializer for HistoricalData model."""
    
    project = ProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = HistoricalData
        fields = [
            'id', 'project', 'project_id', 'data_type', 'source_system',
            'external_record_id', 'data', 'data_date', 'is_processed',
            'processing_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate historical data."""
        # Ensure data_date is not in the future
        if data.get('data_date') and data['data_date'] > timezone.now().date():
            raise serializers.ValidationError("Data date cannot be in the future.")
        
        # Ensure data is valid JSON
        if data.get('data') and not isinstance(data['data'], dict):
            raise serializers.ValidationError("Data must be a valid JSON object.")
        
        return data


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for RiskAssessment model."""
    
    project = ProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(write_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    risk_score = serializers.ReadOnlyField()
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'project', 'project_id', 'risk_category', 'risk_level',
            'title', 'description', 'probability', 'impact_score',
            'ai_model_version', 'confidence_score', 'factors',
            'mitigation_strategy', 'assigned_to', 'assigned_to_id',
            'is_active', 'is_mitigated', 'mitigation_date',
            'risk_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'risk_score', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate risk assessment data."""
        # Ensure probability is within valid range
        if data.get('probability') and (data['probability'] < 0 or data['probability'] > 100):
            raise serializers.ValidationError("Probability must be between 0 and 100.")
        
        # Ensure impact_score is within valid range
        if data.get('impact_score') and (data['impact_score'] < 1 or data['impact_score'] > 10):
            raise serializers.ValidationError("Impact score must be between 1 and 10.")
        
        # Ensure confidence_score is within valid range if provided
        if data.get('confidence_score') and (data['confidence_score'] < 0 or data['confidence_score'] > 100):
            raise serializers.ValidationError("Confidence score must be between 0 and 100.")
        
        # Ensure factors is a list if provided
        if data.get('factors') and not isinstance(data['factors'], list):
            raise serializers.ValidationError("Factors must be a list.")
        
        return data


class ProjectAnalyticsSerializer(serializers.Serializer):
    """Serializer for project analytics data."""
    
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    cost_variance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    cost_variance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    supplier_performance = serializers.DictField()
    risk_summary = serializers.DictField()


class SupplierPerformanceSerializer(serializers.Serializer):
    """Serializer for supplier performance data."""
    
    supplier_id = serializers.IntegerField()
    supplier_name = serializers.CharField()
    total_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_quality_rating = serializers.FloatField(allow_null=True)
    average_cost_variance = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    on_time_delivery_rate = serializers.FloatField()
    overall_score = serializers.FloatField(allow_null=True)
    recent_projects = serializers.ListField()


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data."""
    
    recent_projects = serializers.ListField()
    risk_summary = serializers.DictField()
    supplier_summary = serializers.DictField()
    cost_analysis = serializers.DictField()


class RiskAnalysisSerializer(serializers.Serializer):
    """Serializer for risk analysis data."""
    
    risk_distribution = serializers.ListField()
    high_risk_projects = serializers.ListField()
    recent_risks = serializers.IntegerField()
    total_active_risks = serializers.IntegerField()
