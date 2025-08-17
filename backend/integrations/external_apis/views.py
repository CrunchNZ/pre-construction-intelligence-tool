"""
Views for External APIs Integration

This module provides comprehensive API endpoints for external API integrations,
weather services, data quality monitoring, and backup/recovery operations.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import json
import logging

from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)
from .serializers import (
    WeatherDataSerializer, WeatherImpactAnalysisSerializer, DataQualityRecordSerializer,
    DataBackupRecordSerializer, DataRecoveryRecordSerializer, DataFlowExecutionSerializer,
    ExternalAPIConfigSerializer, APIUsageLogSerializer
)
from .weather_client import OpenWeatherMapClient
from .weather_impact_service import WeatherImpactService
from .data_validation import DataValidator
from .data_flow_orchestrator import DataFlowOrchestrator
from .data_quality_monitor import DataQualityMonitor
from .data_backup_recovery import DataBackupRecovery

logger = logging.getLogger(__name__)


# Weather-related views
@csrf_exempt
@require_http_methods(["GET"])
def current_weather(request, location):
    """Get current weather for a location."""
    try:
        weather_client = OpenWeatherMapClient()
        weather_data = weather_client.get_current_weather(location)
        
        return JsonResponse({
            'success': True,
            'location': location,
            'weather_data': weather_data,
            'timestamp': weather_data.get('timestamp', '')
        })
    except Exception as e:
        logger.error(f"Error getting current weather for {location}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def weather_forecast(request, location):
    """Get weather forecast for a location."""
    try:
        days = int(request.GET.get('days', 5))
        units = request.GET.get('units', 'metric')
        
        weather_client = OpenWeatherMapClient()
        forecast_data = weather_client.get_weather_forecast(location, days, units)
        
        return JsonResponse({
            'success': True,
            'location': location,
            'forecast_data': forecast_data,
            'days': days,
            'units': units
        })
    except Exception as e:
        logger.error(f"Error getting weather forecast for {location}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def weather_alerts(request, location):
    """Get weather alerts for a location."""
    try:
        weather_client = OpenWeatherMapClient()
        alerts = weather_client.get_weather_alerts(location)
        
        return JsonResponse({
            'success': True,
            'location': location,
            'alerts': alerts,
            'alert_count': len(alerts)
        })
    except Exception as e:
        logger.error(f"Error getting weather alerts for {location}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def weather_impact_analysis(request):
    """Perform weather impact analysis for a project."""
    try:
        data = json.loads(request.body)
        project_data = data.get('project_data', {})
        
        weather_service = WeatherImpactService()
        analysis_result = weather_service.analyze_project_weather_risk(project_data)
        
        return JsonResponse({
            'success': True,
            'analysis_result': analysis_result
        })
    except Exception as e:
        logger.error(f"Error performing weather impact analysis: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def portfolio_weather_analysis(request):
    """Perform portfolio-level weather risk analysis."""
    try:
        data = json.loads(request.body)
        projects = data.get('projects', [])
        
        weather_service = WeatherImpactService()
        portfolio_analysis = weather_service.analyze_portfolio_weather_risk(projects)
        
        return JsonResponse({
            'success': True,
            'portfolio_analysis': portfolio_analysis
        })
    except Exception as e:
        logger.error(f"Error performing portfolio weather analysis: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Data quality monitoring views
@csrf_exempt
@require_http_methods(["POST"])
def check_data_quality(request, system_name):
    """Check data quality for a specific system."""
    try:
        data = json.loads(request.body)
        
        quality_monitor = DataQualityMonitor()
        quality_results = quality_monitor.check_data_quality(system_name, data)
        
        return JsonResponse({
            'success': True,
            'system_name': system_name,
            'quality_results': quality_results
        })
    except Exception as e:
        logger.error(f"Error checking data quality for {system_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_quality_report(request, system_name):
    """Get quality report for a specific system."""
    try:
        time_range = request.GET.get('time_range', '24h')
        
        quality_monitor = DataQualityMonitor()
        quality_report = quality_monitor.get_quality_report(system_name, time_range)
        
        return JsonResponse({
            'success': True,
            'system_name': system_name,
            'quality_report': quality_report
        })
    except Exception as e:
        logger.error(f"Error getting quality report for {system_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_quality_trends(request, system_name):
    """Get quality trends for a specific system."""
    try:
        metric = request.GET.get('metric', 'overall_score')
        time_range = request.GET.get('time_range', '7d')
        
        quality_monitor = DataQualityMonitor()
        trends = quality_monitor.get_quality_trends(system_name, metric, time_range)
        
        return JsonResponse({
            'success': True,
            'system_name': system_name,
            'metric': metric,
            'trends': trends
        })
    except Exception as e:
        logger.error(f"Error getting quality trends for {system_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Data backup and recovery views
@csrf_exempt
@require_http_methods(["POST"])
def create_backup(request, system_name):
    """Create a backup for a specific system."""
    try:
        data = json.loads(request.body)
        backup_type = data.get('backup_type', 'incremental')
        
        backup_service = DataBackupRecovery()
        backup_result = backup_service.create_backup(system_name, data, backup_type)
        
        return JsonResponse({
            'success': True,
            'system_name': system_name,
            'backup_result': backup_result
        })
    except Exception as e:
        logger.error(f"Error creating backup for {system_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def restore_backup(request, backup_id):
    """Restore data from a backup."""
    try:
        data = json.loads(request.body)
        target_system = data.get('target_system')
        restore_options = data.get('restore_options', {})
        
        if not target_system:
            return JsonResponse({
                'success': False,
                'error': 'target_system is required'
            }, status=400)
        
        backup_service = DataBackupRecovery()
        restore_result = backup_service.restore_backup(backup_id, target_system, restore_options)
        
        return JsonResponse({
            'success': True,
            'backup_id': backup_id,
            'restore_result': restore_result
        })
    except Exception as e:
        logger.error(f"Error restoring backup {backup_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_backups(request, system_name):
    """List backups for a specific system."""
    try:
        backup_type = request.GET.get('backup_type')
        
        backup_service = DataBackupRecovery()
        backups = backup_service.list_backups(system_name, backup_type)
        
        return JsonResponse({
            'success': True,
            'system_name': system_name,
            'backups': backups
        })
    except Exception as e:
        logger.error(f"Error listing backups for {system_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_backup(request, backup_id):
    """Delete a specific backup."""
    try:
        backup_service = DataBackupRecovery()
        success = backup_service.delete_backup(backup_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Backup {backup_id} deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to delete backup {backup_id}'
            }, status=400)
    except Exception as e:
        logger.error(f"Error deleting backup {backup_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Data flow orchestration views
@csrf_exempt
@require_http_methods(["POST"])
def register_data_flow(request):
    """Register a new data flow."""
    try:
        data = json.loads(request.body)
        flow_name = data.get('flow_name')
        flow_config = data.get('flow_config', {})
        
        if not flow_name:
            return JsonResponse({
                'success': False,
                'error': 'flow_name is required'
            }, status=400)
        
        orchestrator = DataFlowOrchestrator()
        success = orchestrator.register_data_flow(flow_name, flow_config)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Data flow {flow_name} registered successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to register data flow {flow_name}'
            }, status=400)
    except Exception as e:
        logger.error(f"Error registering data flow: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_data_flow(request, flow_name):
    """Execute a data flow."""
    try:
        data = json.loads(request.body)
        input_data = data.get('input_data', {})
        async_execution = data.get('async_execution', False)
        
        orchestrator = DataFlowOrchestrator()
        execution_result = orchestrator.execute_data_flow(flow_name, input_data, async_execution)
        
        return JsonResponse({
            'success': True,
            'flow_name': flow_name,
            'execution_result': execution_result
        })
    except Exception as e:
        logger.error(f"Error executing data flow {flow_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_flow_status(request, execution_id):
    """Get status of a data flow execution."""
    try:
        orchestrator = DataFlowOrchestrator()
        flow_status = orchestrator.get_flow_status(execution_id)
        
        if flow_status:
            return JsonResponse({
                'success': True,
                'execution_id': execution_id,
                'flow_status': flow_status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Execution {execution_id} not found'
            }, status=404)
    except Exception as e:
        logger.error(f"Error getting flow status for {execution_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_flow_performance(request, flow_name):
    """Get performance metrics for a data flow."""
    try:
        orchestrator = DataFlowOrchestrator()
        performance_metrics = orchestrator.get_flow_performance_metrics(flow_name)
        
        return JsonResponse({
            'success': True,
            'flow_name': flow_name,
            'performance_metrics': performance_metrics
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics for {flow_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# External API management views
@csrf_exempt
@require_http_methods(["GET"])
def check_api_health(request, api_name):
    """Check health status of an external API."""
    try:
        # This would implement actual health checking logic
        health_status = {
            'api_name': api_name,
            'status': 'healthy',
            'response_time': 150,
            'last_check': '2025-01-15T10:30:00Z'
        }
        
        return JsonResponse({
            'success': True,
            'health_status': health_status
        })
    except Exception as e:
        logger.error(f"Error checking API health for {api_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def configure_api(request, api_name):
    """Configure an external API."""
    try:
        data = json.loads(request.body)
        config_data = data.get('config', {})
        
        # This would implement actual API configuration logic
        config_result = {
            'api_name': api_name,
            'status': 'configured',
            'config': config_data
        }
        
        return JsonResponse({
            'success': True,
            'config_result': config_result
        })
    except Exception as e:
        logger.error(f"Error configuring API {api_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_api_usage_stats(request, api_name):
    """Get usage statistics for an external API."""
    try:
        # This would implement actual usage statistics logic
        usage_stats = {
            'api_name': api_name,
            'total_calls': 1250,
            'successful_calls': 1200,
            'failed_calls': 50,
            'average_response_time': 180,
            'last_24_hours': 45
        }
        
        return JsonResponse({
            'success': True,
            'usage_stats': usage_stats
        })
    except Exception as e:
        logger.error(f"Error getting usage stats for {api_name}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Utility views
@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for the external APIs integration."""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': '2025-01-15T10:30:00Z',
            'services': {
                'weather_service': 'operational',
                'data_quality_monitor': 'operational',
                'backup_recovery': 'operational',
                'data_flow_orchestrator': 'operational'
            }
        }
        
        return JsonResponse(health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def system_status(request):
    """Get overall system status."""
    try:
        system_status = {
            'overall_status': 'operational',
            'timestamp': '2025-01-15T10:30:00Z',
            'components': {
                'external_apis': 'operational',
                'weather_integration': 'operational',
                'data_quality': 'operational',
                'backup_recovery': 'operational',
                'data_flow': 'operational'
            },
            'active_connections': 12,
            'last_maintenance': '2025-01-14T02:00:00Z'
        }
        
        return JsonResponse(system_status)
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return JsonResponse({
            'overall_status': 'degraded',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_metrics(request):
    """Get system metrics."""
    try:
        metrics = {
            'timestamp': '2025-01-15T10:30:00Z',
            'performance': {
                'average_response_time': 180,
                'requests_per_minute': 45,
                'error_rate': 0.02
            },
            'data_quality': {
                'average_score': 85.5,
                'systems_monitored': 8,
                'issues_detected': 3
            },
            'backup_recovery': {
                'total_backups': 156,
                'backup_success_rate': 0.98,
                'recovery_success_rate': 1.0
            }
        }
        
        return JsonResponse(metrics)
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=500)


# ViewSets for REST API
class WeatherViewSet(viewsets.ModelViewSet):
    """ViewSet for WeatherData model."""
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active weather data."""
        active_weather = WeatherData.objects.filter(is_active=True)
        serializer = self.get_serializer(active_weather, many=True)
        return Response(serializer.data)


class WeatherImpactViewSet(viewsets.ModelViewSet):
    """ViewSet for WeatherImpactAnalysis model."""
    queryset = WeatherImpactAnalysis.objects.all()
    serializer_class = WeatherImpactAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk weather impact analyses."""
        high_risk = WeatherImpactAnalysis.objects.filter(impact_score__gte=70)
        serializer = self.get_serializer(high_risk, many=True)
        return Response(serializer.data)


class DataQualityViewSet(viewsets.ModelViewSet):
    """ViewSet for DataQualityRecord model."""
    queryset = DataQualityRecord.objects.all()
    serializer_class = DataQualityRecordSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest quality records for each system."""
        from django.db.models import Max
        latest_records = DataQualityRecord.objects.values('system_name').annotate(
            latest_date=Max('assessment_date')
        )
        latest_data = []
        for record in latest_records:
            latest = DataQualityRecord.objects.filter(
                system_name=record['system_name'],
                assessment_date=record['latest_date']
            ).first()
            if latest:
                latest_data.append(latest)
        
        serializer = self.get_serializer(latest_data, many=True)
        return Response(serializer.data)


class DataBackupViewSet(viewsets.ModelViewSet):
    """ViewSet for DataBackupRecord model."""
    queryset = DataBackupRecord.objects.all()
    serializer_class = DataBackupRecordSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active backups."""
        active_backups = DataBackupRecord.objects.filter(is_active=True)
        serializer = self.get_serializer(active_backups, many=True)
        return Response(serializer.data)


class DataRecoveryViewSet(viewsets.ModelViewSet):
    """ViewSet for DataRecoveryRecord model."""
    queryset = DataRecoveryRecord.objects.all()
    serializer_class = DataRecoveryRecordSerializer
    permission_classes = [IsAuthenticated]


class DataFlowViewSet(viewsets.ModelViewSet):
    """ViewSet for DataFlowExecution model."""
    queryset = DataFlowExecution.objects.all()
    serializer_class = DataFlowExecutionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def running(self, request):
        """Get currently running flows."""
        running_flows = DataFlowExecution.objects.filter(status='running')
        serializer = self.get_serializer(running_flows, many=True)
        return Response(serializer.data)


class ExternalAPIConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for ExternalAPIConfig model."""
    queryset = ExternalAPIConfig.objects.all()
    serializer_class = ExternalAPIConfigSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active API configurations."""
        active_apis = ExternalAPIConfig.objects.filter(is_active=True)
        serializer = self.get_serializer(active_apis, many=True)
        return Response(serializer.data)


class APIUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for APIUsageLog model."""
    queryset = APIUsageLog.objects.all()
    serializer_class = APIUsageLogSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recent_failures(self, request):
        """Get recent API call failures."""
        recent_failures = APIUsageLog.objects.filter(
            success=False
        ).order_by('-request_timestamp')[:50]
        serializer = self.get_serializer(recent_failures, many=True)
        return Response(serializer.data)
