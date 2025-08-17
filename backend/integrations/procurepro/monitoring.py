"""
ProcurePro Monitoring and Alerting System

Provides comprehensive monitoring, health checks, performance metrics,
and alert notifications for ProcurePro synchronization operations.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from enum import Enum

from .models import ProcureProSyncLog
from .error_handling import error_tracker, circuit_breakers, get_error_handling_status

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    CRITICAL = 'critical'
    UNKNOWN = 'unknown'


class AlertLevel(Enum):
    """Alert level enumeration."""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class ProcureProMonitor:
    """Main monitoring class for ProcurePro integration."""
    
    def __init__(self):
        self.alert_thresholds = {
            'sync_success_rate': 90.0,      # Minimum 90% success rate
            'sync_failure_threshold': 3,     # Max 3 consecutive failures
            'response_time_threshold': 30.0,  # Max 30 seconds response time
            'error_rate_threshold': 10.0,    # Max 10% error rate
            'circuit_breaker_open_threshold': 1,  # Max 1 circuit breaker open
        }
        
        self.alert_channels = {
            'email': True,
            'slack': False,  # TODO: Implement Slack integration
            'webhook': False,  # TODO: Implement webhook notifications
            'database': True,
        }
    
    def check_overall_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of ProcurePro integration.
        
        Returns:
            dict: Overall health status and details
        """
        logger.info("Starting comprehensive ProcurePro health check")
        
        health_checks = {
            'sync_health': self._check_sync_health(),
            'api_health': self._check_api_health(),
            'database_health': self._check_database_health(),
            'error_health': self._check_error_health(),
            'circuit_breaker_health': self._check_circuit_breaker_health(),
            'performance_health': self._check_performance_health(),
        }
        
        # Determine overall health status
        overall_status = self._determine_overall_health(health_checks)
        
        health_result = {
            'status': overall_status.value,
            'timestamp': timezone.now().isoformat(),
            'checks': health_checks,
            'overall_score': self._calculate_health_score(health_checks),
            'recommendations': self._generate_recommendations(health_checks),
        }
        
        # Send alerts if health is poor
        if overall_status in [HealthStatus.DEGRADED, HealthStatus.CRITICAL]:
            self._send_health_alert(overall_status, health_result)
        
        logger.info(f"Health check completed: {overall_status.value}")
        return health_result
    
    def _check_sync_health(self) -> Dict[str, Any]:
        """Check synchronization health."""
        try:
            # Get recent sync activity (last 24 hours)
            recent_syncs = ProcureProSyncLog.objects.filter(
                started_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            total_syncs = recent_syncs.count()
            successful_syncs = recent_syncs.filter(status='success').count()
            failed_syncs = recent_syncs.filter(status='failed').count()
            partial_syncs = recent_syncs.filter(status='partial').count()
            
            success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            
            # Check for critical failures in last hour
            critical_failures = recent_syncs.filter(
                status='failed',
                started_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            # Determine sync health status
            if success_rate >= 95 and critical_failures == 0:
                sync_status = HealthStatus.HEALTHY
            elif success_rate >= 80 and critical_failures <= 1:
                sync_status = HealthStatus.DEGRADED
            else:
                sync_status = HealthStatus.CRITICAL
            
            return {
                'status': sync_status.value,
                'success_rate': success_rate,
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'partial_syncs': partial_syncs,
                'critical_failures': critical_failures,
                'healthy': sync_status == HealthStatus.HEALTHY
            }
            
        except Exception as e:
            logger.error(f"Error checking sync health: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'healthy': False
            }
    
    def _check_api_health(self) -> Dict[str, Any]:
        """Check API connectivity and health."""
        try:
            # TODO: Implement actual API health check
            # For now, return a placeholder
            return {
                'status': HealthStatus.HEALTHY.value,
                'connectivity': True,
                'response_time': 0.5,
                'healthy': True
            }
            
        except Exception as e:
            logger.error(f"Error checking API health: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'healthy': False
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and health."""
        try:
            # Test database connectivity
            start_time = time.time()
            
            # Simple query to test connectivity
            sync_count = ProcureProSyncLog.objects.count()
            
            response_time = time.time() - start_time
            
            # Determine database health status
            if response_time < 1.0:
                db_status = HealthStatus.HEALTHY
            elif response_time < 5.0:
                db_status = HealthStatus.DEGRADED
            else:
                db_status = HealthStatus.CRITICAL
            
            return {
                'status': db_status.value,
                'connectivity': True,
                'response_time': response_time,
                'record_count': sync_count,
                'healthy': db_status == HealthStatus.HEALTHY
            }
            
        except Exception as e:
            logger.error(f"Error checking database health: {e}")
            return {
                'status': HealthStatus.CRITICAL.value,
                'connectivity': False,
                'error': str(e),
                'healthy': False
            }
    
    def _check_error_health(self) -> Dict[str, Any]:
        """Check error patterns and rates."""
        try:
            error_summary = error_tracker.get_error_summary(hours=24)
            
            total_errors = error_summary['total_errors']
            critical_errors = error_summary['severity_counts'].get('critical', 0)
            high_errors = error_summary['severity_counts'].get('high', 0)
            
            # Calculate error rate (assuming some baseline activity)
            # This is a simplified calculation
            error_rate = min(total_errors / 100 * 100, 100) if total_errors > 0 else 0
            
            # Determine error health status
            if error_rate < 5 and critical_errors == 0:
                error_status = HealthStatus.HEALTHY
            elif error_rate < 15 and critical_errors <= 1:
                error_status = HealthStatus.DEGRADED
            else:
                error_status = HealthStatus.CRITICAL
            
            return {
                'status': error_status.value,
                'total_errors': total_errors,
                'critical_errors': critical_errors,
                'high_errors': high_errors,
                'error_rate': error_rate,
                'healthy': error_status == HealthStatus.HEALTHY
            }
            
        except Exception as e:
            logger.error(f"Error checking error health: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'healthy': False
            }
    
    def _check_circuit_breaker_health(self) -> Dict[str, Any]:
        """Check circuit breaker status."""
        try:
            circuit_breaker_status = get_error_handling_status()['circuit_breakers']
            
            open_circuits = sum(
                1 for status in circuit_breaker_status.values()
                if status['state'] == 'OPEN'
            )
            
            # Determine circuit breaker health status
            if open_circuits == 0:
                cb_status = HealthStatus.HEALTHY
            elif open_circuits <= 1:
                cb_status = HealthStatus.DEGRADED
            else:
                cb_status = HealthStatus.CRITICAL
            
            return {
                'status': cb_status.value,
                'open_circuits': open_circuits,
                'total_circuits': len(circuit_breaker_status),
                'circuit_details': circuit_breaker_status,
                'healthy': cb_status == HealthStatus.HEALTHY
            }
            
        except Exception as e:
            logger.error(f"Error checking circuit breaker health: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'healthy': False
            }
    
    def _check_performance_health(self) -> Dict[str, Any]:
        """Check performance metrics."""
        try:
            # Get recent sync performance data
            recent_syncs = ProcureProSyncLog.objects.filter(
                started_at__gte=timezone.now() - timedelta(hours=24),
                completed_at__isnull=False
            )
            
            if recent_syncs.exists():
                # Calculate average duration
                total_duration = sum(
                    (sync.completed_at - sync.started_at).total_seconds()
                    for sync in recent_syncs
                )
                avg_duration = total_duration / recent_syncs.count()
                
                # Determine performance health status
                if avg_duration < 60:  # Less than 1 minute
                    perf_status = HealthStatus.HEALTHY
                elif avg_duration < 300:  # Less than 5 minutes
                    perf_status = HealthStatus.DEGRADED
                else:
                    perf_status = HealthStatus.CRITICAL
            else:
                avg_duration = 0
                perf_status = HealthStatus.UNKNOWN
            
            return {
                'status': perf_status.value,
                'average_sync_duration': avg_duration,
                'healthy': perf_status == HealthStatus.HEALTHY
            }
            
        except Exception as e:
            logger.error(f"Error checking performance health: {e}")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'healthy': False
            }
    
    def _determine_overall_health(self, health_checks: Dict) -> HealthStatus:
        """Determine overall health status based on individual checks."""
        critical_count = sum(
            1 for check in health_checks.values()
            if check.get('status') == HealthStatus.CRITICAL.value
        )
        
        degraded_count = sum(
            1 for check in health_checks.values()
            if check.get('status') == HealthStatus.DEGRADED.value
        )
        
        if critical_count > 0:
            return HealthStatus.CRITICAL
        elif degraded_count > 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def _calculate_health_score(self, health_checks: Dict) -> float:
        """Calculate overall health score (0-100)."""
        total_checks = len(health_checks)
        healthy_checks = sum(
            1 for check in health_checks.values()
            if check.get('healthy', False)
        )
        
        return (healthy_checks / total_checks * 100) if total_checks > 0 else 0
    
    def _generate_recommendations(self, health_checks: Dict) -> List[str]:
        """Generate recommendations based on health check results."""
        recommendations = []
        
        # Sync health recommendations
        sync_check = health_checks.get('sync_health', {})
        if sync_check.get('status') == HealthStatus.CRITICAL.value:
            recommendations.append("Critical sync failures detected - investigate immediately")
        elif sync_check.get('status') == HealthStatus.DEGRADED.value:
            recommendations.append("Sync success rate below threshold - review error logs")
        
        # Error health recommendations
        error_check = health_checks.get('error_health', {})
        if error_check.get('critical_errors', 0) > 0:
            recommendations.append("Critical errors detected - review error handling")
        
        # Circuit breaker recommendations
        cb_check = health_checks.get('circuit_breaker_health', {})
        if cb_check.get('open_circuits', 0) > 0:
            recommendations.append("Circuit breakers open - external service issues detected")
        
        # Performance recommendations
        perf_check = health_checks.get('performance_health', {})
        if perf_check.get('average_sync_duration', 0) > 300:
            recommendations.append("Sync performance degraded - optimize sync operations")
        
        if not recommendations:
            recommendations.append("All systems operating normally")
        
        return recommendations
    
    def _send_health_alert(self, health_status: HealthStatus, health_result: Dict):
        """Send health alert notifications."""
        try:
            alert_level = AlertLevel.ERROR if health_status == HealthStatus.CRITICAL else AlertLevel.WARNING
            
            # Send email alert
            if self.alert_channels.get('email'):
                self._send_email_alert(alert_level, health_status, health_result)
            
            # TODO: Implement other alert channels (Slack, webhook, etc.)
            
            logger.info(f"Health alert sent: {health_status.value} - {alert_level.value}")
            
        except Exception as e:
            logger.error(f"Failed to send health alert: {e}")
    
    def _send_email_alert(self, alert_level: AlertLevel, health_status: HealthStatus, health_result: Dict):
        """Send email health alert."""
        try:
            subject = f"ProcurePro Health Alert: {health_status.value.upper()}"
            
            # Prepare email context
            context = {
                'health_status': health_status.value,
                'alert_level': alert_level.value,
                'timestamp': health_result['timestamp'],
                'overall_score': health_result['overall_score'],
                'recommendations': health_result['recommendations'],
                'health_checks': health_result['checks']
            }
            
            # Render email template
            html_message = render_to_string('integrations/procurepro/health_alert.html', context)
            plain_message = render_to_string('integrations/procurepro/health_alert.txt', context)
            
            # Get alert recipients from settings
            recipients = getattr(settings, 'PROCUREPRO_ALERT_EMAILS', [])
            if not recipients:
                logger.warning("No alert email recipients configured")
                return
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")


class PerformanceMonitor:
    """Monitor performance metrics for ProcurePro operations."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_operation(self, operation_name: str, duration: float, success: bool, **kwargs):
        """Record performance metrics for an operation."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_duration': 0,
                'success_count': 0,
                'failure_count': 0,
                'min_duration': float('inf'),
                'max_duration': 0,
                'last_updated': timezone.now()
            }
        
        metric = self.metrics[operation_name]
        metric['count'] += 1
        metric['total_duration'] += duration
        metric['min_duration'] = min(metric['min_duration'], duration)
        metric['max_duration'] = max(metric['max_duration'], duration)
        metric['last_updated'] = timezone.now()
        
        if success:
            metric['success_count'] += 1
        else:
            metric['failure_count'] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all operations."""
        summary = {}
        
        for operation_name, metric in self.metrics.items():
            if metric['count'] > 0:
                summary[operation_name] = {
                    'total_operations': metric['count'],
                    'success_rate': (metric['success_count'] / metric['count']) * 100,
                    'average_duration': metric['total_duration'] / metric['count'],
                    'min_duration': metric['min_duration'],
                    'max_duration': metric['max_duration'],
                    'last_updated': metric['last_updated'].isoformat()
                }
        
        return summary
    
    def clear_metrics(self):
        """Clear all performance metrics."""
        self.metrics.clear()


class AlertManager:
    """Manage alert notifications and escalation."""
    
    def __init__(self):
        self.alert_history = []
        self.escalation_rules = {
            'critical': {
                'immediate': True,
                'escalation_delay': 0,
                'max_escalations': 3
            },
            'error': {
                'immediate': False,
                'escalation_delay': 300,  # 5 minutes
                'max_escalations': 2
            },
            'warning': {
                'immediate': False,
                'escalation_delay': 1800,  # 30 minutes
                'max_escalations': 1
            }
        }
    
    def create_alert(self, level: AlertLevel, message: str, details: Dict = None, 
                    source: str = 'procurepro') -> Dict:
        """Create a new alert."""
        alert = {
            'id': len(self.alert_history) + 1,
            'level': level.value,
            'message': message,
            'details': details or {},
            'source': source,
            'timestamp': timezone.now().isoformat(),
            'status': 'active',
            'escalation_count': 0,
            'last_escalated': None
        }
        
        self.alert_history.append(alert)
        
        # Check if immediate escalation is needed
        if self.escalation_rules[level.value]['immediate']:
            self._escalate_alert(alert)
        
        logger.info(f"Alert created: {level.value} - {message}")
        return alert
    
    def _escalate_alert(self, alert: Dict):
        """Escalate an alert based on escalation rules."""
        level = alert['level']
        rules = self.escalation_rules[level]
        
        if alert['escalation_count'] >= rules['max_escalations']:
            logger.warning(f"Alert {alert['id']} has reached maximum escalations")
            return
        
        # TODO: Implement escalation logic (notify managers, create tickets, etc.)
        alert['escalation_count'] += 1
        alert['last_escalated'] = timezone.now().isoformat()
        
        logger.info(f"Alert {alert['id']} escalated (count: {alert['escalation_count']})")
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts."""
        return [alert for alert in self.alert_history if alert['status'] == 'active']
    
    def resolve_alert(self, alert_id: int, resolution_notes: str = None):
        """Resolve an alert."""
        for alert in self.alert_history:
            if alert['id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = timezone.now().isoformat()
                alert['resolution_notes'] = resolution_notes
                logger.info(f"Alert {alert_id} resolved")
                break


# Global instances
monitor = ProcureProMonitor()
performance_monitor = PerformanceMonitor()
alert_manager = AlertManager()


def get_monitoring_status() -> Dict[str, Any]:
    """Get comprehensive monitoring status."""
    return {
        'health': monitor.check_overall_health(),
        'performance': performance_monitor.get_performance_summary(),
        'alerts': {
            'active': alert_manager.get_active_alerts(),
            'total': len(alert_manager.alert_history)
        },
        'error_handling': get_error_handling_status()
    }
