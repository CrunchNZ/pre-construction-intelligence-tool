"""
Django Models for External APIs Integration

This module defines the database models for external API integrations,
weather data, data quality monitoring, and backup/recovery operations.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json


class WeatherData(models.Model):
    """Model for storing weather data from OpenWeatherMap API."""
    
    location = models.CharField(max_length=255, help_text="Location name or coordinates")
    weather_data = models.JSONField(help_text="Raw weather data from API")
    weather_type = models.CharField(max_length=50, choices=[
        ('current', 'Current Weather'),
        ('forecast', 'Weather Forecast'),
        ('alerts', 'Weather Alerts'),
        ('historical', 'Historical Weather')
    ])
    units = models.CharField(max_length=20, default='metric', choices=[
        ('metric', 'Metric'),
        ('imperial', 'Imperial'),
        ('kelvin', 'Kelvin')
    ])
    timestamp = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(help_text="When this weather data expires")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'external_apis_weather_data'
        indexes = [
            models.Index(fields=['location', 'weather_type', 'timestamp']),
            models.Index(fields=['expires_at', 'is_active'])
        ]
    
    def __str__(self):
        return f"Weather data for {self.location} ({self.weather_type}) at {self.timestamp}"
    
    @property
    def is_expired(self):
        """Check if weather data has expired."""
        return timezone.now() > self.expires_at


class WeatherImpactAnalysis(models.Model):
    """Model for storing weather impact analysis results."""
    
    project_id = models.CharField(max_length=100, help_text="Project identifier")
    location = models.CharField(max_length=255, help_text="Project location")
    project_type = models.CharField(max_length=100, default='construction', choices=[
        ('construction', 'General Construction'),
        ('excavation', 'Excavation'),
        ('concrete', 'Concrete Work'),
        ('roofing', 'Roofing'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('steel_erection', 'Steel Erection'),
        ('interior_finishing', 'Interior Finishing')
    ])
    impact_score = models.FloatField(help_text="Weather impact score (0-100)")
    risk_factors = models.JSONField(default=dict, help_text="Risk factor analysis")
    recommendations = models.JSONField(default=list, help_text="Weather-based recommendations")
    cost_impact = models.JSONField(default=dict, help_text="Cost impact analysis")
    analysis_date = models.DateTimeField(default=timezone.now)
    weather_data = models.ForeignKey(WeatherData, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'external_apis_weather_impact'
        indexes = [
            models.Index(fields=['project_id', 'location']),
            models.Index(fields=['impact_score', 'analysis_date']),
            models.Index(fields=['project_type', 'location'])
        ]
    
    def __str__(self):
        return f"Weather impact analysis for {self.project_id} at {self.location}"


class DataQualityRecord(models.Model):
    """Model for storing data quality assessment records."""
    
    system_name = models.CharField(max_length=100, help_text="Name of the system being monitored")
    quality_metrics = models.JSONField(help_text="Quality assessment results")
    overall_score = models.FloatField(help_text="Overall quality score (0-100)")
    issues = models.JSONField(default=list, help_text="Quality issues identified")
    recommendations = models.JSONField(default=list, help_text="Quality improvement recommendations")
    assessment_date = models.DateTimeField(default=timezone.now)
    data_sample_size = models.IntegerField(default=0, help_text="Number of records assessed")
    
    class Meta:
        db_table = 'external_apis_data_quality'
        indexes = [
            models.Index(fields=['system_name', 'assessment_date']),
            models.Index(fields=['overall_score', 'assessment_date'])
        ]
    
    def __str__(self):
        return f"Data quality record for {self.system_name} - Score: {self.overall_score}"


class DataBackupRecord(models.Model):
    """Model for storing data backup records."""
    
    backup_id = models.CharField(max_length=100, unique=True, help_text="Unique backup identifier")
    system_name = models.CharField(max_length=100, help_text="System being backed up")
    backup_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Backup'),
        ('incremental', 'Incremental Backup')
    ])
    file_path = models.CharField(max_length=500, help_text="Path to backup file")
    file_size_bytes = models.BigIntegerField(help_text="Size of backup file in bytes")
    checksum = models.CharField(max_length=64, help_text="SHA-256 checksum of backup file")
    compression_enabled = models.BooleanField(default=True, help_text="Whether backup is compressed")
    encryption_enabled = models.BooleanField(default=False, help_text="Whether backup is encrypted")
    backup_date = models.DateTimeField(default=timezone.now)
    retention_date = models.DateTimeField(help_text="Date when backup should be deleted")
    is_active = models.BooleanField(default=True, help_text="Whether backup is still available")
    
    class Meta:
        db_table = 'external_apis_data_backups'
        indexes = [
            models.Index(fields=['system_name', 'backup_type']),
            models.Index(fields=['backup_date', 'retention_date']),
            models.Index(fields=['is_active', 'retention_date'])
        ]
    
    def __str__(self):
        return f"Backup {self.backup_id} for {self.system_name} ({self.backup_type})"
    
    @property
    def file_size_mb(self):
        """Get file size in megabytes."""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def is_expired(self):
        """Check if backup has expired and should be deleted."""
        return timezone.now() > self.retention_date


class DataRecoveryRecord(models.Model):
    """Model for storing data recovery records."""
    
    recovery_id = models.CharField(max_length=100, unique=True, help_text="Unique recovery identifier")
    backup_record = models.ForeignKey(DataBackupRecord, on_delete=models.CASCADE, help_text="Backup being recovered")
    target_system = models.CharField(max_length=100, help_text="System where data is being restored")
    restore_options = models.JSONField(default=dict, help_text="Options used for restoration")
    recovery_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='in_progress')
    error_message = models.TextField(blank=True, help_text="Error message if recovery failed")
    restored_data_size = models.IntegerField(default=0, help_text="Size of restored data")
    
    class Meta:
        db_table = 'external_apis_data_recovery'
        indexes = [
            models.Index(fields=['recovery_id', 'status']),
            models.Index(fields=['backup_record', 'recovery_date']),
            models.Index(fields=['target_system', 'status'])
        ]
    
    def __str__(self):
        return f"Recovery {self.recovery_id} from backup {self.backup_record.backup_id}"


class DataFlowExecution(models.Model):
    """Model for storing data flow execution records."""
    
    execution_id = models.CharField(max_length=100, unique=True, help_text="Unique execution identifier")
    flow_name = models.CharField(max_length=100, help_text="Name of the data flow")
    status = models.CharField(max_length=20, choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('started_async', 'Started Asynchronously')
    ], default='running')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True, help_text="When execution completed")
    input_data = models.JSONField(default=dict, help_text="Input data for the flow")
    output_data = models.JSONField(default=dict, help_text="Output data from the flow")
    errors = models.JSONField(default=list, help_text="Errors encountered during execution")
    performance_metrics = models.JSONField(default=dict, help_text="Performance metrics")
    steps = models.JSONField(default=list, help_text="Individual step execution details")
    
    class Meta:
        db_table = 'external_apis_data_flow_execution'
        indexes = [
            models.Index(fields=['execution_id', 'status']),
            models.Index(fields=['flow_name', 'start_time']),
            models.Index(fields=['status', 'start_time'])
        ]
    
    def __str__(self):
        return f"Data flow execution {self.execution_id} ({self.flow_name})"
    
    @property
    def duration_seconds(self):
        """Get execution duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_completed(self):
        """Check if execution is completed."""
        return self.status in ['completed', 'failed']


class ExternalAPIConfig(models.Model):
    """Model for storing external API configuration."""
    
    api_name = models.CharField(max_length=100, unique=True, help_text="Name of the external API")
    api_type = models.CharField(max_length=50, choices=[
        ('weather', 'Weather API'),
        ('geocoding', 'Geocoding API'),
        ('financial', 'Financial API'),
        ('other', 'Other API')
    ])
    base_url = models.URLField(help_text="Base URL for the API")
    api_key = models.CharField(max_length=255, blank=True, help_text="API key (encrypted in production)")
    rate_limit_per_minute = models.IntegerField(default=60, help_text="API calls per minute limit")
    rate_limit_per_day = models.IntegerField(default=1000, help_text="API calls per day limit")
    timeout_seconds = models.IntegerField(default=30, help_text="Request timeout in seconds")
    is_active = models.BooleanField(default=True, help_text="Whether API integration is active")
    last_health_check = models.DateTimeField(null=True, blank=True, help_text="Last health check timestamp")
    health_status = models.CharField(max_length=20, choices=[
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
        ('unknown', 'Unknown')
    ], default='unknown')
    configuration = models.JSONField(default=dict, help_text="Additional API configuration")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'external_apis_config'
        indexes = [
            models.Index(fields=['api_name', 'is_active']),
            models.Index(fields=['api_type', 'health_status']),
            models.Index(fields=['last_health_check', 'health_status'])
        ]
    
    def __str__(self):
        return f"External API config for {self.api_name} ({self.api_type})"


class APIUsageLog(models.Model):
    """Model for logging API usage and performance."""
    
    api_config = models.ForeignKey(ExternalAPIConfig, on_delete=models.CASCADE, help_text="API configuration used")
    endpoint = models.CharField(max_length=255, help_text="API endpoint called")
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ], default='GET')
    request_timestamp = models.DateTimeField(default=timezone.now)
    response_timestamp = models.DateTimeField(null=True, blank=True, help_text="When response was received")
    status_code = models.IntegerField(null=True, blank=True, help_text="HTTP status code")
    response_time_ms = models.IntegerField(null=True, blank=True, help_text="Response time in milliseconds")
    success = models.BooleanField(default=True, help_text="Whether the API call was successful")
    error_message = models.TextField(blank=True, help_text="Error message if call failed")
    request_size_bytes = models.IntegerField(default=0, help_text="Size of request in bytes")
    response_size_bytes = models.IntegerField(default=0, help_text="Size of response in bytes")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who made the request")
    
    class Meta:
        db_table = 'external_apis_usage_log'
        indexes = [
            models.Index(fields=['api_config', 'request_timestamp']),
            models.Index(fields=['endpoint', 'success']),
            models.Index(fields=['status_code', 'request_timestamp']),
            models.Index(fields=['user', 'request_timestamp'])
        ]
    
    def __str__(self):
        return f"API call to {self.api_config.api_name} - {self.endpoint} at {self.request_timestamp}"
    
    @property
    def response_time_seconds(self):
        """Get response time in seconds."""
        if self.response_time_ms:
            return self.response_time_ms / 1000
        return None
