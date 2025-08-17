"""
Signals for External APIs Integration

This module handles Django signals for the external APIs integration,
including automatic data cleanup, monitoring, and event handling.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
import logging

from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WeatherData)
def weather_data_saved(sender, instance, created, **kwargs):
    """Handle weather data save events."""
    if created:
        logger.info(f"New weather data created for {instance.location}")
        # Cache the weather data for quick access
        cache_key = f"weather_data_{instance.location}_{instance.weather_type}"
        cache.set(cache_key, instance.weather_data, timeout=3600)  # 1 hour cache
    else:
        logger.info(f"Weather data updated for {instance.location}")
        # Update cache
        cache_key = f"weather_data_{instance.location}_{instance.weather_type}"
        cache.set(cache_key, instance.weather_data, timeout=3600)


@receiver(post_save, sender=WeatherImpactAnalysis)
def weather_impact_analysis_saved(sender, instance, created, **kwargs):
    """Handle weather impact analysis save events."""
    if created:
        logger.info(f"New weather impact analysis created for project {instance.project_id}")
        # Trigger any follow-up actions if needed
        pass
    else:
        logger.info(f"Weather impact analysis updated for project {instance.project_id}")


@receiver(post_save, sender=DataQualityRecord)
def data_quality_record_saved(sender, instance, created, **kwargs):
    """Handle data quality record save events."""
    if created:
        logger.info(f"New data quality record created for {instance.system_name}")
        # Check if quality score is below threshold
        if instance.overall_score < 75.0:
            logger.warning(f"Low data quality detected for {instance.system_name}: {instance.overall_score}")
    else:
        logger.info(f"Data quality record updated for {instance.system_name}")


@receiver(post_save, sender=DataBackupRecord)
def data_backup_record_saved(sender, instance, created, **kwargs):
    """Handle data backup record save events."""
    if created:
        logger.info(f"New backup record created: {instance.backup_id}")
        # Clean up old backups if retention policy is exceeded
        if instance.retention_date and instance.retention_date < timezone.now():
            logger.info(f"Backup {instance.backup_id} has exceeded retention period")
    else:
        logger.info(f"Backup record updated: {instance.backup_id}")


@receiver(post_save, sender=DataFlowExecution)
def data_flow_execution_saved(sender, instance, created, **kwargs):
    """Handle data flow execution save events."""
    if created:
        logger.info(f"New data flow execution started: {instance.execution_id}")
    else:
        if instance.status == 'completed':
            logger.info(f"Data flow execution completed: {instance.execution_id}")
        elif instance.status == 'failed':
            logger.error(f"Data flow execution failed: {instance.execution_id}")


@receiver(post_save, sender=ExternalAPIConfig)
def external_api_config_saved(sender, instance, created, **kwargs):
    """Handle external API configuration save events."""
    if created:
        logger.info(f"New API configuration created: {instance.api_name}")
    else:
        logger.info(f"API configuration updated: {instance.api_name}")
        # Update health status in cache
        cache_key = f"api_health_{instance.api_name}"
        cache.set(cache_key, instance.health_status, timeout=300)  # 5 minutes cache


@receiver(post_save, sender=APIUsageLog)
def api_usage_log_saved(sender, instance, created, **kwargs):
    """Handle API usage log save events."""
    if created:
        logger.info(f"API usage logged: {instance.api_config.api_name} - {instance.endpoint}")
        # Track API usage metrics
        cache_key = f"api_usage_{instance.api_config.api_name}"
        current_usage = cache.get(cache_key, 0)
        cache.set(cache_key, current_usage + 1, timeout=3600)  # 1 hour cache


@receiver(post_delete, sender=WeatherData)
def weather_data_deleted(sender, instance, **kwargs):
    """Handle weather data deletion events."""
    logger.info(f"Weather data deleted for {instance.location}")
    # Clean up cache
    cache_key = f"weather_data_{instance.location}_{instance.weather_type}"
    cache.delete(cache_key)


@receiver(post_delete, sender=DataBackupRecord)
def data_backup_record_deleted(sender, instance, **kwargs):
    """Handle data backup record deletion events."""
    logger.info(f"Backup record deleted: {instance.backup_id}")
    # Clean up associated files if they exist
    # Note: This would require additional file system operations


@receiver(pre_save, sender=WeatherData)
def weather_data_pre_save(sender, instance, **kwargs):
    """Handle weather data pre-save events."""
    # Validate weather data before saving
    if instance.weather_data and isinstance(instance.weather_data, dict):
        if 'temp' in instance.weather_data:
            temp = instance.weather_data['temp']
            if not isinstance(temp, (int, float)) or temp < -100 or temp > 150:
                logger.warning(f"Invalid temperature value: {temp}")
    
    # Set expiration if not provided
    if not instance.expires_at:
        instance.expires_at = timezone.now() + timezone.timedelta(hours=1)


@receiver(pre_save, sender=DataQualityRecord)
def data_quality_record_pre_save(sender, instance, **kwargs):
    """Handle data quality record pre-save events."""
    # Ensure overall score is within valid range
    if instance.overall_score is not None:
        if instance.overall_score < 0:
            instance.overall_score = 0
        elif instance.overall_score > 100:
            instance.overall_score = 100
    
    # Set timestamp if not provided
    if not instance.timestamp:
        instance.timestamp = timezone.now()
