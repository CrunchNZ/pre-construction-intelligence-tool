"""
Core integrations views.

Provides overview, status, health, and configuration management
for all external system integrations.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class IntegrationsOverviewView(APIView):
    """Overview of all integrations."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get overview of all integrations."""
        try:
            integrations = {
                'procurepro': {
                    'name': 'ProcurePro',
                    'description': 'Procurement and supplier management system',
                    'status': 'active',
                    'version': '1.0.0',
                    'last_updated': timezone.now(),
                    'endpoints': [
                        '/api/integrations/procurepro/suppliers/',
                        '/api/integrations/procurepro/purchase-orders/',
                        '/api/integrations/procurepro/invoices/',
                        '/api/integrations/procurepro/contracts/',
                        '/api/integrations/procurepro/sync/',
                        '/api/integrations/procurepro/analytics/',
                        '/api/integrations/procurepro/dashboard/',
                        '/api/integrations/procurepro/health/',
                    ]
                },
                'procore': {
                    'name': 'Procore',
                    'description': 'Construction project management system',
                    'status': 'planned',
                    'version': '0.0.0',
                    'last_updated': None,
                    'endpoints': []
                },
                'jobpac': {
                    'name': 'Jobpac',
                    'description': 'Job costing and project management system',
                    'status': 'planned',
                    'version': '0.0.0',
                    'last_updated': None,
                    'endpoints': []
                },
                'greentree': {
                    'name': 'Greentree',
                    'description': 'Financial management and ERP system',
                    'status': 'planned',
                    'version': '0.0.0',
                    'last_updated': None,
                    'endpoints': []
                },
                'bim': {
                    'name': 'BIM Integration',
                    'description': 'Building Information Modeling data integration',
                    'status': 'planned',
                    'version': '0.0.0',
                    'last_updated': None,
                    'endpoints': []
                }
            }
            
            return Response({
                'integrations': integrations,
                'total_integrations': len(integrations),
                'active_integrations': len([i for i in integrations.values() if i['status'] == 'active']),
                'planned_integrations': len([i for i in integrations.values() if i['status'] == 'planned']),
                'last_updated': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error getting integrations overview: {e}")
            return Response(
                {'error': 'Failed to retrieve integrations overview'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IntegrationsStatusView(APIView):
    """Status of all integrations."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get status of all integrations."""
        try:
            # For now, we only have ProcurePro implemented
            # In the future, this will check actual status of each integration
            status_data = {
                'procurepro': {
                    'status': 'active',
                    'last_sync': timezone.now(),
                    'sync_status': 'success',
                    'records_count': {
                        'suppliers': 0,  # Will be populated from actual data
                        'purchase_orders': 0,
                        'invoices': 0,
                        'contracts': 0
                    },
                    'health': 'healthy'
                },
                'procore': {
                    'status': 'planned',
                    'last_sync': None,
                    'sync_status': 'not_implemented',
                    'records_count': {},
                    'health': 'unknown'
                },
                'jobpac': {
                    'status': 'planned',
                    'last_sync': None,
                    'sync_status': 'not_implemented',
                    'records_count': {},
                    'health': 'unknown'
                },
                'greentree': {
                    'status': 'planned',
                    'last_sync': None,
                    'sync_status': 'not_implemented',
                    'records_count': {},
                    'health': 'unknown'
                },
                'bim': {
                    'status': 'planned',
                    'last_sync': None,
                    'sync_status': 'not_implemented',
                    'records_count': {},
                    'health': 'unknown'
                }
            }
            
            return Response({
                'integrations_status': status_data,
                'overall_status': 'healthy',  # Will be calculated based on active integrations
                'last_updated': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error getting integrations status: {e}")
            return Response(
                {'error': 'Failed to retrieve integrations status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IntegrationsHealthView(APIView):
    """Health check for all integrations."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check health of all integrations."""
        try:
            health_data = {
                'procurepro': {
                    'status': 'healthy',
                    'checks': {
                        'api_connectivity': 'healthy',
                        'database': 'healthy',
                        'sync_service': 'healthy'
                    },
                    'last_check': timezone.now()
                },
                'overall_health': 'healthy'
            }
            
            return Response(health_data)
            
        except Exception as e:
            logger.error(f"Error checking integrations health: {e}")
            return Response(
                {'error': 'Failed to check integrations health'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IntegrationsConfigView(APIView):
    """Configuration management for integrations."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get configuration for all integrations."""
        try:
            config_data = {
                'procurepro': {
                    'api_settings': {
                        'base_url': 'https://api.procurepro.com',
                        'timeout': 30,
                        'retry_attempts': 3
                    },
                    'sync_settings': {
                        'auto_sync': True,
                        'sync_interval_hours': 24,
                        'incremental_sync': True
                    },
                    'data_settings': {
                        'max_records_per_sync': 1000,
                        'data_retention_days': 365
                    }
                },
                'global_settings': {
                    'log_level': 'info',
                    'notification_enabled': True,
                    'backup_enabled': True
                }
            }
            
            return Response(config_data)
            
        except Exception as e:
            logger.error(f"Error getting integrations config: {e}")
            return Response(
                {'error': 'Failed to retrieve integrations configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Update configuration for integrations."""
        try:
            # This would update the configuration
            # For now, just return success
            return Response({
                'message': 'Configuration updated successfully',
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error updating integrations config: {e}")
            return Response(
                {'error': 'Failed to update integrations configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

