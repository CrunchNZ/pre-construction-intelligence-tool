"""
API views for unified project management.

Provides comprehensive REST API endpoints for managing unified projects,
documents, schedules, financials, and other project-related entities
across all integrated construction management systems.
"""

import logging
from typing import Dict, Any, List
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

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
from .serializers import (
    IntegrationSystemSerializer,
    UnifiedProjectSerializer,
    UnifiedProjectCreateSerializer,
    UnifiedProjectUpdateSerializer,
    ProjectSystemMappingSerializer,
    ProjectDocumentSerializer,
    ProjectDocumentCreateSerializer,
    ProjectScheduleSerializer,
    ProjectScheduleCreateSerializer,
    ProjectFinancialSerializer,
    ProjectFinancialCreateSerializer,
    ProjectChangeOrderSerializer,
    ProjectChangeOrderCreateSerializer,
    ProjectRFISerializer,
    ProjectRFICreateSerializer,
    ProjectSummarySerializer,
    ProjectAnalyticsSerializer,
    IntegrationStatusSerializer,
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses."""
    
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class IntegrationSystemViewSet(viewsets.ModelViewSet):
    """ViewSet for integration systems."""
    
    queryset = IntegrationSystem.objects.all()
    serializer_class = IntegrationSystemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['system_type', 'status', 'connection_status']
    search_fields = ['name', 'base_url']
    ordering_fields = ['name', 'created_at', 'last_connection']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test connection to the integration system."""
        try:
            system = self.get_object()
            # TODO: Implement actual connection test
            system.update_connection_status('testing', '')
            
            # Simulate connection test
            import time
            time.sleep(1)
            
            system.update_connection_status('active', '')
            return Response({'status': 'success', 'message': 'Connection successful'})
            
        except Exception as e:
            logger.error(f"Connection test failed for system {pk}: {str(e)}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def status_summary(self, request):
        """Get summary of all integration system statuses."""
        try:
            systems = self.get_queryset()
            summary = {
                'total_systems': systems.count(),
                'active_systems': systems.filter(status='active').count(),
                'error_systems': systems.filter(status='error').count(),
                'maintenance_systems': systems.filter(status='maintenance').count(),
                'systems_by_type': systems.values('system_type').annotate(count=Count('id')),
                'connection_status': systems.values('connection_status').annotate(count=Count('id')),
            }
            return Response(summary)
            
        except Exception as e:
            logger.error(f"Failed to get integration status summary: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnifiedProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for unified projects."""
    
    queryset = UnifiedProject.objects.select_related(
        'project_manager', 'created_by'
    ).prefetch_related(
        'integration_systems', 'system_mappings__system'
    ).all()
    
    serializer_class = UnifiedProjectSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'project_type', 'city', 'state', 'country']
    search_fields = ['name', 'project_number', 'description', 'client', 'architect', 'contractor']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at', 'budget']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return UnifiedProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UnifiedProjectUpdateSerializer
        return UnifiedProjectSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get project summary statistics."""
        try:
            projects = self.get_queryset()
            
            summary = {
                'total_projects': projects.count(),
                'active_projects': projects.filter(status='construction').count(),
                'completed_projects': projects.filter(status='completed').count(),
                'total_budget': projects.aggregate(total=Sum('budget'))['total'] or 0,
                'total_actual_cost': projects.aggregate(total=Sum('actual_cost'))['total'] or 0,
                'average_progress': projects.aggregate(avg=Avg('progress_percentage'))['avg'] or 0,
                'projects_over_budget': projects.filter(
                    Q(budget__isnull=False) & Q(actual_cost__isnull=False) & 
                    Q(actual_cost__gt=F('budget'))
                ).count(),
                'projects_behind_schedule': projects.filter(
                    Q(end_date__lt=timezone.now().date()) & ~Q(status='completed')
                ).count(),
            }
            
            serializer = ProjectSummarySerializer(summary)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project summary: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get detailed project analytics."""
        try:
            projects = self.get_queryset()
            analytics_data = []
            
            for project in projects:
                # Calculate risk score based on various factors
                risk_score = 0.0
                
                # Budget risk
                if project.budget and project.actual_cost:
                    budget_variance_pct = (project.actual_cost - project.budget) / project.budget * 100
                    if budget_variance_pct > 10:
                        risk_score += 30
                    elif budget_variance_pct > 5:
                        risk_score += 15
                
                # Schedule risk
                if project.end_date and project.end_date < timezone.now().date():
                    risk_score += 25
                
                # Progress risk
                if project.progress_percentage < 50 and project.status == 'construction':
                    risk_score += 20
                
                # Integration status
                integration_status = {}
                for mapping in project.system_mappings.all():
                    integration_status[mapping.system.name] = {
                        'status': mapping.sync_status,
                        'last_sync': mapping.last_sync,
                        'error': mapping.sync_error
                    }
                
                analytics_data.append({
                    'project_id': project.id,
                    'project_name': project.name,
                    'progress_percentage': project.progress_percentage,
                    'budget_variance': project.budget_variance,
                    'days_remaining': project.days_remaining,
                    'risk_score': min(100, risk_score),
                    'integration_status': integration_status,
                    'last_updated': project.updated_at,
                })
            
            serializer = ProjectAnalyticsSerializer(analytics_data, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project analytics: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get documents for a specific project."""
        try:
            project = self.get_object()
            documents = ProjectDocument.objects.filter(project=project)
            
            # Apply filters
            doc_type = request.query_params.get('document_type')
            if doc_type:
                documents = documents.filter(document_type=doc_type)
            
            status_filter = request.query_params.get('status')
            if status_filter:
                documents = documents.filter(status=status_filter)
            
            # Pagination
            paginator = Paginator(documents, 25)
            page_number = request.query_params.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            serializer = ProjectDocumentSerializer(page_obj, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
            })
            
        except Exception as e:
            logger.error(f"Failed to get project documents: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get schedule information for a specific project."""
        try:
            project = self.get_object()
            schedules = ProjectSchedule.objects.filter(project=project)
            
            serializer = ProjectScheduleSerializer(schedules, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project schedule: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def financials(self, request, pk=None):
        """Get financial information for a specific project."""
        try:
            project = self.get_object()
            financials = ProjectFinancial.objects.filter(project=project)
            
            # Apply filters
            financial_type = request.query_params.get('financial_type')
            if financial_type:
                financials = financials.filter(financial_type=financial_type)
            
            serializer = ProjectFinancialSerializer(financials, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project financials: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def change_orders(self, request, pk=None):
        """Get change orders for a specific project."""
        try:
            project = self.get_object()
            change_orders = ProjectChangeOrder.objects.filter(project=project)
            
            # Apply filters
            status_filter = request.query_params.get('status')
            if status_filter:
                change_orders = change_orders.filter(status=status_filter)
            
            serializer = ProjectChangeOrderSerializer(change_orders, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project change orders: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def rfis(self, request, pk=None):
        """Get RFIs for a specific project."""
        try:
            project = self.get_object()
            rfis = ProjectRFI.objects.filter(project=project)
            
            # Apply filters
            status_filter = request.query_params.get('status')
            if status_filter:
                rfis = rfis.filter(status=status_filter)
            
            priority_filter = request.query_params.get('priority')
            if priority_filter:
                rfis = rfis.filter(priority=priority_filter)
            
            serializer = ProjectRFISerializer(rfis, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get project RFIs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectSystemMappingViewSet(viewsets.ModelViewSet):
    """ViewSet for project system mappings."""
    
    queryset = ProjectSystemMapping.objects.select_related('project', 'system').all()
    serializer_class = ProjectSystemMappingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['system', 'sync_status']
    search_fields = ['external_project_id', 'external_project_name']
    ordering_fields = ['last_sync', 'created_at']
    ordering = ['-last_sync']
    
    @action(detail=True, methods=['post'])
    def sync_now(self, request, pk=None):
        """Trigger immediate synchronization for a mapping."""
        try:
            mapping = self.get_object()
            # TODO: Implement actual sync logic
            mapping.sync_status = 'syncing'
            mapping.save()
            
            # Simulate sync process
            import time
            time.sleep(2)
            
            mapping.sync_status = 'completed'
            mapping.last_sync = timezone.now()
            mapping.save()
            
            return Response({'status': 'success', 'message': 'Synchronization completed'})
            
        except Exception as e:
            logger.error(f"Sync failed for mapping {pk}: {str(e)}")
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for project documents."""
    
    queryset = ProjectDocument.objects.select_related('project', 'system_mapping', 'created_by').all()
    serializer_class = ProjectDocumentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'status', 'project']
    search_fields = ['title', 'description', 'file_name']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return ProjectDocumentCreateSerializer
        return ProjectDocumentSerializer


class ProjectScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for project schedules."""
    
    queryset = ProjectSchedule.objects.select_related('project', 'system_mapping').all()
    serializer_class = ProjectScheduleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['start_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return ProjectScheduleCreateSerializer
        return ProjectScheduleSerializer


class ProjectFinancialViewSet(viewsets.ModelViewSet):
    """ViewSet for project financials."""
    
    queryset = ProjectFinancial.objects.select_related('project', 'system_mapping').all()
    serializer_class = ProjectFinancialSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['financial_type', 'currency', 'project']
    search_fields = ['project__name']
    ordering_fields = ['effective_date', 'amount', 'created_at']
    ordering = ['-effective_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return ProjectFinancialCreateSerializer
        return ProjectFinancialSerializer


class ProjectChangeOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for project change orders."""
    
    queryset = ProjectChangeOrder.objects.select_related('project', 'system_mapping', 'created_by').all()
    serializer_class = ProjectChangeOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'project']
    search_fields = ['change_order_number', 'title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return ProjectChangeOrderCreateSerializer
        return ProjectChangeOrderSerializer


class ProjectRFIViewSet(viewsets.ModelViewSet):
    """ViewSet for project RFIs."""
    
    queryset = ProjectRFI.objects.select_related(
        'project', 'system_mapping', 'submitted_by', 'answered_by'
    ).all()
    
    serializer_class = ProjectRFISerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project']
    search_fields = ['rfi_number', 'subject', 'question']
    ordering_fields = ['date_submitted', 'priority', 'created_at']
    ordering = ['-date_submitted']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return ProjectRFICreateSerializer
        return ProjectRFISerializer
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent RFIs that need attention."""
        try:
            urgent_rfis = self.get_queryset().filter(
                Q(status='open') & Q(priority__in=['high', 'critical'])
            ).order_by('priority', 'date_submitted')
            
            serializer = self.get_serializer(urgent_rfis, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Failed to get urgent RFIs: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
