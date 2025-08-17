"""
Background Tasks for External APIs Integration

This module handles background tasks for the external APIs integration,
including scheduled data updates, cleanup operations, and monitoring tasks.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
import logging
from datetime import timedelta

from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)
from .weather_client import OpenWeatherMapClient
from .weather_impact_service import WeatherImpactService
from .data_quality_monitor import DataQualityMonitor
from .data_backup_recovery import DataBackupRecovery
from .data_flow_orchestrator import DataFlowOrchestrator

logger = logging.getLogger(__name__)


@shared_task
def update_weather_data():
    """Update weather data for all active locations."""
    try:
        logger.info("Starting weather data update task")
        
        # Get all active weather data records
        active_weather = WeatherData.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        if not active_weather.exists():
            logger.info("No expired weather data to update")
            return
        
        # Get API configuration
        api_config = ExternalAPIConfig.objects.filter(
            api_type='weather',
            is_active=True,
            health_status='healthy'
        ).first()
        
        if not api_config:
            logger.error("No active weather API configuration found")
            return
        
        # Initialize weather client
        weather_client = OpenWeatherMapClient(api_key=api_config.api_key)
        
        updated_count = 0
        for weather_record in active_weather:
            try:
                # Get fresh weather data
                new_weather_data = weather_client.get_current_weather(weather_record.location)
                
                # Update the record
                weather_record.weather_data = new_weather_data
                weather_record.expires_at = timezone.now() + timedelta(hours=1)
                weather_record.last_updated = timezone.now()
                weather_record.save()
                
                updated_count += 1
                logger.info(f"Updated weather data for {weather_record.location}")
                
            except Exception as e:
                logger.error(f"Failed to update weather data for {weather_record.location}: {e}")
                continue
        
        logger.info(f"Weather data update task completed. Updated {updated_count} records")
        
    except Exception as e:
        logger.error(f"Weather data update task failed: {e}")
        raise


@shared_task
def cleanup_expired_data():
    """Clean up expired data records."""
    try:
        logger.info("Starting data cleanup task")
        
        # Clean up expired weather data
        expired_weather = WeatherData.objects.filter(
            expires_at__lt=timezone.now() - timedelta(days=1)
        )
        weather_deleted = expired_weather.count()
        expired_weather.delete()
        
        # Clean up old API usage logs
        old_usage_logs = APIUsageLog.objects.filter(
            request_timestamp__lt=timezone.now() - timedelta(days=90)
        )
        logs_deleted = old_usage_logs.count()
        old_usage_logs.delete()
        
        # Clean up old data quality records
        old_quality_records = DataQualityRecord.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=180)
        )
        quality_deleted = old_quality_records.count()
        old_quality_records.delete()
        
        logger.info(f"Data cleanup completed. Deleted: {weather_deleted} weather, {logs_deleted} logs, {quality_deleted} quality records")
        
    except Exception as e:
        logger.error(f"Data cleanup task failed: {e}")
        raise


@shared_task
def monitor_data_quality():
    """Monitor data quality across all systems."""
    try:
        logger.info("Starting data quality monitoring task")
        
        # Initialize quality monitor
        quality_monitor = DataQualityMonitor()
        
        # Get all systems that need monitoring
        systems_to_monitor = [
            'weather_api',
            'construction_data',
            'supplier_data',
            'project_data'
        ]
        
        for system in systems_to_monitor:
            try:
                # Get sample data for quality check
                # This would typically fetch from the actual data source
                sample_data = {'test': 'data'}  # Placeholder
                
                # Check data quality
                quality_result = quality_monitor.check_data_quality(system, sample_data)
                
                # Create quality record
                DataQualityRecord.objects.create(
                    system_name=system,
                    quality_metrics=quality_result,
                    overall_score=quality_result.get('overall_score', 0.0),
                    issues=quality_result.get('issues', []),
                    recommendations=quality_result.get('recommendations', []),
                    data_sample_size=100  # Placeholder
                )
                
                logger.info(f"Data quality monitored for {system}: {quality_result.get('overall_score', 0.0)}")
                
            except Exception as e:
                logger.error(f"Failed to monitor data quality for {system}: {e}")
                continue
        
        logger.info("Data quality monitoring task completed")
        
    except Exception as e:
        logger.error(f"Data quality monitoring task failed: {e}")
        raise


@shared_task
def create_scheduled_backups():
    """Create scheduled backups for all systems."""
    try:
        logger.info("Starting scheduled backup task")
        
        # Initialize backup service
        backup_service = DataBackupRecovery()
        
        # Get systems that need backup
        systems_to_backup = [
            'weather_data',
            'construction_data',
            'supplier_data',
            'project_data'
        ]
        
        for system in systems_to_backup:
            try:
                # Configure backup if not already configured
                backup_config = {
                    'backup_directory': f'/backups/{system}',
                    'retention_days': 30,
                    'compression_enabled': True,
                    'encryption_enabled': False
                }
                backup_service.configure_backup(system, backup_config)
                
                # Create backup
                # This would typically fetch actual data from the system
                sample_data = {'system': system, 'timestamp': timezone.now().isoformat()}
                
                backup_result = backup_service.create_backup(system, sample_data, 'full')
                
                logger.info(f"Created backup for {system}: {backup_result.get('backup_id')}")
                
            except Exception as e:
                logger.error(f"Failed to create backup for {system}: {e}")
                continue
        
        logger.info("Scheduled backup task completed")
        
    except Exception as e:
        logger.error(f"Scheduled backup task failed: {e}")
        raise


@shared_task
def execute_data_flows():
    """Execute scheduled data flows."""
    try:
        logger.info("Starting data flow execution task")
        
        # Initialize flow orchestrator
        flow_orchestrator = DataFlowOrchestrator()
        
        # Get flows that need execution
        flows_to_execute = [
            'daily_weather_update',
            'weekly_data_quality_check',
            'monthly_backup_verification'
        ]
        
        for flow_name in flows_to_execute:
            try:
                # Check if flow is registered
                if flow_name in flow_orchestrator.flow_registry:
                    # Execute the flow
                    result = flow_orchestrator.execute_data_flow(flow_name, {})
                    
                    logger.info(f"Executed data flow {flow_name}: {result.get('status')}")
                else:
                    logger.warning(f"Data flow {flow_name} not registered")
                
            except Exception as e:
                logger.error(f"Failed to execute data flow {flow_name}: {e}")
                continue
        
        logger.info("Data flow execution task completed")
        
    except Exception as e:
        logger.error(f"Data flow execution task failed: {e}")
        raise


@shared_task
def check_api_health():
    """Check health status of all external APIs."""
    try:
        logger.info("Starting API health check task")
        
        # Get all active API configurations
        active_apis = ExternalAPIConfig.objects.filter(is_active=True)
        
        for api_config in active_apis:
            try:
                # Perform health check based on API type
                if api_config.api_type == 'weather':
                    # Test weather API
                    weather_client = OpenWeatherMapClient(api_key=api_config.api_key)
                    test_result = weather_client.get_current_weather('London')
                    
                    if test_result:
                        api_config.health_status = 'healthy'
                        api_config.last_health_check = timezone.now()
                        api_config.save()
                        
                        logger.info(f"API {api_config.api_name} is healthy")
                    else:
                        api_config.health_status = 'unhealthy'
                        api_config.last_health_check = timezone.now()
                        api_config.save()
                        
                        logger.warning(f"API {api_config.api_name} is unhealthy")
                
                else:
                    # Generic health check for other API types
                    api_config.health_status = 'unknown'
                    api_config.last_health_check = timezone.now()
                    api_config.save()
                    
                    logger.info(f"API {api_config.api_name} health status set to unknown")
                
            except Exception as e:
                logger.error(f"Failed to check health for API {api_config.api_name}: {e}")
                
                # Mark as unhealthy
                api_config.health_status = 'unhealthy'
                api_config.last_health_check = timezone.now()
                api_config.save()
                continue
        
        logger.info("API health check task completed")
        
    except Exception as e:
        logger.error(f"API health check task failed: {e}")
        raise


@shared_task
def generate_usage_reports():
    """Generate API usage reports."""
    try:
        logger.info("Starting usage report generation task")
        
        # Get usage data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        usage_data = APIUsageLog.objects.filter(
            request_timestamp__gte=thirty_days_ago
        ).values('api_config__api_name', 'status_code', 'success')
        
        # Process usage data
        api_usage = {}
        for usage in usage_data:
            api_name = usage['api_config__api_name']
            if api_name not in api_usage:
                api_usage[api_name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0
                }
            
            api_usage[api_name]['total_requests'] += 1
            if usage['success']:
                api_usage[api_name]['successful_requests'] += 1
            else:
                api_usage[api_name]['failed_requests'] += 1
        
        # Log usage summary
        for api_name, stats in api_usage.items():
            success_rate = (stats['successful_requests'] / stats['total_requests']) * 100
            logger.info(f"API {api_name}: {stats['total_requests']} requests, {success_rate:.1f}% success rate")
        
        logger.info("Usage report generation task completed")
        
    except Exception as e:
        logger.error(f"Usage report generation task failed: {e}")
        raise
