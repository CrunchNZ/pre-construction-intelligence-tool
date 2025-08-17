"""
Django REST Framework Serializers for External APIs Integration

This module provides serializers for all models in the external APIs integration,
enabling REST API functionality with proper data validation and transformation.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from rest_framework import serializers
from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)


class WeatherDataSerializer(serializers.ModelSerializer):
    """Serializer for WeatherData model."""
    
    class Meta:
        model = WeatherData
        fields = [
            'id', 'location', 'weather_data', 'weather_type', 'units',
            'timestamp', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def validate_weather_data(self, value):
        """Validate weather data JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Weather data must be a dictionary")
        return value
    
    def validate_expires_at(self, value):
        """Validate expiration timestamp."""
        from django.utils import timezone
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration time must be in the future")
        return value


class WeatherImpactAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for WeatherImpactAnalysis model."""
    
    weather_data = WeatherDataSerializer(read_only=True)
    
    class Meta:
        model = WeatherImpactAnalysis
        fields = [
            'id', 'project_id', 'location', 'project_type', 'impact_score',
            'risk_factors', 'recommendations', 'cost_impact', 'analysis_date',
            'weather_data'
        ]
        read_only_fields = ['id', 'analysis_date']
    
    def validate_impact_score(self, value):
        """Validate impact score range."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Impact score must be between 0 and 100")
        return value
    
    def validate_risk_factors(self, value):
        """Validate risk factors JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Risk factors must be a dictionary")
        return value
    
    def validate_recommendations(self, value):
        """Validate recommendations JSON field."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Recommendations must be a list")
        return value
    
    def validate_cost_impact(self, value):
        """Validate cost impact JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Cost impact must be a dictionary")
        return value


class DataQualityRecordSerializer(serializers.ModelSerializer):
    """Serializer for DataQualityRecord model."""
    
    class Meta:
        model = DataQualityRecord
        fields = [
            'id', 'system_name', 'quality_metrics', 'overall_score',
            'issues', 'recommendations', 'assessment_date', 'data_sample_size'
        ]
        read_only_fields = ['id', 'assessment_date']
    
    def validate_overall_score(self, value):
        """Validate overall quality score range."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Overall score must be between 0 and 100")
        return value
    
    def validate_quality_metrics(self, value):
        """Validate quality metrics JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Quality metrics must be a dictionary")
        return value
    
    def validate_issues(self, value):
        """Validate issues JSON field."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Issues must be a list")
        return value
    
    def validate_recommendations(self, value):
        """Validate recommendations JSON field."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Recommendations must be a list")
        return value
    
    def validate_data_sample_size(self, value):
        """Validate data sample size."""
        if value < 0:
            raise serializers.ValidationError("Data sample size cannot be negative")
        return value


class DataBackupRecordSerializer(serializers.ModelSerializer):
    """Serializer for DataBackupRecord model."""
    
    class Meta:
        model = DataBackupRecord
        fields = [
            'id', 'backup_id', 'system_name', 'backup_type', 'file_path',
            'file_size_bytes', 'checksum', 'compression_enabled',
            'encryption_enabled', 'backup_date', 'retention_date', 'is_active'
        ]
        read_only_fields = ['id', 'backup_date', 'file_size_bytes', 'checksum']
    
    def validate_backup_id(self, value):
        """Validate backup ID format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Backup ID cannot be empty")
        return value.strip()
    
    def validate_file_size_bytes(self, value):
        """Validate file size."""
        if value < 0:
            raise serializers.ValidationError("File size cannot be negative")
        return value
    
    def validate_checksum(self, value):
        """Validate checksum format."""
        if value and len(value) != 64:
            raise serializers.ValidationError("Checksum must be 64 characters long")
        return value
    
    def validate_retention_date(self, value):
        """Validate retention date."""
        from django.utils import timezone
        if value and value <= timezone.now():
            raise serializers.ValidationError("Retention date must be in the future")
        return value


class DataRecoveryRecordSerializer(serializers.ModelSerializer):
    """Serializer for DataRecoveryRecord model."""
    
    backup_record = DataBackupRecordSerializer(read_only=True)
    
    class Meta:
        model = DataRecoveryRecord
        fields = [
            'id', 'recovery_id', 'backup_record', 'target_system',
            'restore_options', 'recovery_date', 'status', 'error_message',
            'restored_data_size'
        ]
        read_only_fields = ['id', 'recovery_date', 'restored_data_size']
    
    def validate_recovery_id(self, value):
        """Validate recovery ID format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Recovery ID cannot be empty")
        return value.strip()
    
    def validate_target_system(self, value):
        """Validate target system name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Target system cannot be empty")
        return value.strip()
    
    def validate_restore_options(self, value):
        """Validate restore options JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Restore options must be a dictionary")
        return value
    
    def validate_status(self, value):
        """Validate status field."""
        valid_statuses = ['in_progress', 'completed', 'failed']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {valid_statuses}")
        return value
    
    def validate_restored_data_size(self, value):
        """Validate restored data size."""
        if value < 0:
            raise serializers.ValidationError("Restored data size cannot be negative")
        return value


class DataFlowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for DataFlowExecution model."""
    
    class Meta:
        model = DataFlowExecution
        fields = [
            'id', 'execution_id', 'flow_name', 'status', 'start_time',
            'end_time', 'input_data', 'output_data', 'errors',
            'performance_metrics', 'steps'
        ]
        read_only_fields = ['id', 'start_time', 'end_time']
    
    def validate_execution_id(self, value):
        """Validate execution ID format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Execution ID cannot be empty")
        return value.strip()
    
    def validate_flow_name(self, value):
        """Validate flow name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Flow name cannot be empty")
        return value.strip()
    
    def validate_status(self, value):
        """Validate status field."""
        valid_statuses = ['running', 'completed', 'failed', 'started_async']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {valid_statuses}")
        return value
    
    def validate_input_data(self, value):
        """Validate input data JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Input data must be a dictionary")
        return value
    
    def validate_output_data(self, value):
        """Validate output data JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Output data must be a dictionary")
        return value
    
    def validate_errors(self, value):
        """Validate errors JSON field."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Errors must be a list")
        return value
    
    def validate_performance_metrics(self, value):
        """Validate performance metrics JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Performance metrics must be a dictionary")
        return value
    
    def validate_steps(self, value):
        """Validate steps JSON field."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Steps must be a list")
        return value


class ExternalAPIConfigSerializer(serializers.ModelSerializer):
    """Serializer for ExternalAPIConfig model."""
    
    class Meta:
        model = ExternalAPIConfig
        fields = [
            'id', 'api_name', 'api_type', 'base_url', 'api_key',
            'rate_limit_per_minute', 'rate_limit_per_day', 'timeout_seconds',
            'is_active', 'last_health_check', 'health_status',
            'configuration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_health_check']
        extra_kwargs = {
            'api_key': {'write_only': True}  # Hide API key in responses
        }
    
    def validate_api_name(self, value):
        """Validate API name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("API name cannot be empty")
        return value.strip()
    
    def validate_base_url(self, value):
        """Validate base URL format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Base URL cannot be empty")
        return value.strip()
    
    def validate_api_type(self, value):
        """Validate API type."""
        valid_types = ['weather', 'geocoding', 'financial', 'other']
        if value not in valid_types:
            raise serializers.ValidationError(f"API type must be one of: {valid_types}")
        return value
    
    def validate_rate_limit_per_minute(self, value):
        """Validate rate limit per minute."""
        if value <= 0:
            raise serializers.ValidationError("Rate limit per minute must be positive")
        return value
    
    def validate_rate_limit_per_day(self, value):
        """Validate rate limit per day."""
        if value <= 0:
            raise serializers.ValidationError("Rate limit per day must be positive")
        return value
    
    def validate_timeout_seconds(self, value):
        """Validate timeout seconds."""
        if value <= 0:
            raise serializers.ValidationError("Timeout must be positive")
        return value
    
    def validate_health_status(self, value):
        """Validate health status."""
        valid_statuses = ['healthy', 'degraded', 'unhealthy', 'unknown']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Health status must be one of: {valid_statuses}")
        return value
    
    def validate_configuration(self, value):
        """Validate configuration JSON field."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Configuration must be a dictionary")
        return value


class APIUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for APIUsageLog model."""
    
    api_config = ExternalAPIConfigSerializer(read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = [
            'id', 'api_config', 'endpoint', 'method', 'request_timestamp',
            'response_timestamp', 'status_code', 'response_time_ms',
            'success', 'error_message', 'request_size_bytes',
            'response_size_bytes', 'user'
        ]
        read_only_fields = ['id', 'request_timestamp', 'response_timestamp', 'response_time_ms']
    
    def validate_endpoint(self, value):
        """Validate endpoint."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Endpoint cannot be empty")
        return value.strip()
    
    def validate_method(self, value):
        """Validate HTTP method."""
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if value not in valid_methods:
            raise serializers.ValidationError(f"Method must be one of: {valid_methods}")
        return value
    
    def validate_status_code(self, value):
        """Validate status code."""
        if value and (value < 100 or value > 599):
            raise serializers.ValidationError("Status code must be between 100 and 599")
        return value
    
    def validate_response_time_ms(self, value):
        """Validate response time."""
        if value and value < 0:
            raise serializers.ValidationError("Response time cannot be negative")
        return value
    
    def validate_request_size_bytes(self, value):
        """Validate request size."""
        if value < 0:
            raise serializers.ValidationError("Request size cannot be negative")
        return value
    
    def validate_response_size_bytes(self, value):
        """Validate response size."""
        if value < 0:
            raise serializers.ValidationError("Response size cannot be negative")
        return value


# Nested serializers for detailed views
class WeatherDataDetailSerializer(WeatherDataSerializer):
    """Detailed serializer for WeatherData with additional computed fields."""
    
    is_expired = serializers.ReadOnlyField()
    
    class Meta(WeatherDataSerializer.Meta):
        fields = WeatherDataSerializer.Meta.fields + ['is_expired']


class WeatherImpactAnalysisDetailSerializer(WeatherImpactAnalysisSerializer):
    """Detailed serializer for WeatherImpactAnalysis."""
    
    weather_data = WeatherDataDetailSerializer(read_only=True)
    
    class Meta(WeatherImpactAnalysisSerializer.Meta):
        pass


class DataBackupRecordDetailSerializer(DataBackupRecordSerializer):
    """Detailed serializer for DataBackupRecord with computed fields."""
    
    file_size_mb = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta(DataBackupRecordSerializer.Meta):
        fields = DataBackupRecordSerializer.Meta.fields + ['file_size_mb', 'is_expired']


class DataFlowExecutionDetailSerializer(DataFlowExecutionSerializer):
    """Detailed serializer for DataFlowExecution with computed fields."""
    
    duration_seconds = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta(DataFlowExecutionSerializer.Meta):
        fields = DataFlowExecutionSerializer.Meta.fields + ['duration_seconds', 'is_completed']


class APIUsageLogDetailSerializer(APIUsageLogSerializer):
    """Detailed serializer for APIUsageLog with computed fields."""
    
    response_time_seconds = serializers.ReadOnlyField()
    
    class Meta(APIUsageLogSerializer.Meta):
        fields = APIUsageLogSerializer.Meta.fields + ['response_time_seconds']


# Summary serializers for list views
class WeatherDataSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for WeatherData in list views."""
    
    class Meta:
        model = WeatherData
        fields = ['id', 'location', 'weather_type', 'units', 'timestamp', 'is_active']


class WeatherImpactAnalysisSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for WeatherImpactAnalysis in list views."""
    
    class Meta:
        model = WeatherImpactAnalysis
        fields = ['id', 'project_id', 'location', 'project_type', 'impact_score', 'analysis_date']


class DataQualityRecordSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for DataQualityRecord in list views."""
    
    class Meta:
        model = DataQualityRecord
        fields = ['id', 'system_name', 'overall_score', 'assessment_date', 'data_sample_size']


class DataBackupRecordSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for DataBackupRecord in list views."""
    
    class Meta:
        model = DataBackupRecord
        fields = ['id', 'backup_id', 'system_name', 'backup_type', 'backup_date', 'is_active']


class DataFlowExecutionSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for DataFlowExecution in list views."""
    
    class Meta:
        model = DataFlowExecution
        fields = ['id', 'execution_id', 'flow_name', 'status', 'start_time', 'end_time']


class ExternalAPIConfigSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for ExternalAPIConfig in list views."""
    
    class Meta:
        model = ExternalAPIConfig
        fields = ['id', 'api_name', 'api_type', 'base_url', 'is_active', 'health_status']


class APIUsageLogSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for APIUsageLog in list views."""
    
    class Meta:
        model = APIUsageLog
        fields = ['id', 'api_config', 'endpoint', 'method', 'status_code', 'success', 'request_timestamp']
