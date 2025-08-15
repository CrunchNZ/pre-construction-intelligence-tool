"""
Core views for the Pre-Construction Intelligence Tool.

This module contains the ViewSets and custom views for handling
API requests related to projects, suppliers, and analytics.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Project, Supplier, ProjectSupplier, HistoricalData, RiskAssessment
from .serializers import (
    ProjectSerializer, SupplierSerializer, ProjectSupplierSerializer,
    HistoricalDataSerializer, RiskAssessmentSerializer
)

logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing projects.
    
    Provides CRUD operations for construction projects and
    additional actions for project analysis.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = Project.objects.all()
        
        # Filter by project type
        project_type = self.request.query_params.get('project_type', None)
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics data for a specific project."""
        project = self.get_object()
        
        # Calculate cost variance
        cost_variance = project.calculate_cost_variance()
        
        # Get supplier performance
        supplier_performance = project.suppliers.all().aggregate(
            avg_quality=Avg('quality_rating'),
            avg_cost_variance=Avg('cost_variance'),
            on_time_delivery_rate=Count('on_time_delivery', filter=Q(on_time_delivery=True)) * 100.0 / Count('on_time_delivery')
        )
        
        # Get risk assessments
        risk_assessments = project.risk_assessments.filter(is_active=True)
        high_risks = risk_assessments.filter(risk_level__in=['high', 'critical']).count()
        
        analytics_data = {
            'project_id': project.id,
            'project_name': project.name,
            'cost_variance': float(cost_variance) if cost_variance else None,
            'cost_variance_percentage': float(project.cost_variance_percentage) if project.cost_variance_percentage else None,
            'supplier_performance': supplier_performance,
            'risk_summary': {
                'total_risks': risk_assessments.count(),
                'high_risks': high_risks,
                'risk_levels': list(risk_assessments.values_list('risk_level', flat=True))
            }
        }
        
        return Response(analytics_data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for all projects."""
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__in=['planning', 'bidding', 'execution']).count()
        completed_projects = Project.objects.filter(status='completed').count()
        
        # Calculate average cost variance
        avg_cost_variance = Project.objects.filter(
            cost_variance__isnull=False
        ).aggregate(avg_variance=Avg('cost_variance_percentage'))
        
        summary_data = {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'average_cost_variance': float(avg_cost_variance['avg_variance']) if avg_cost_variance['avg_variance'] else 0,
            'project_types': list(Project.objects.values('project_type').annotate(count=Count('id')).values('project_type', 'count'))
        }
        
        return Response(summary_data)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing suppliers.
    
    Provides CRUD operations for suppliers and contractors,
    along with performance analytics.
    """
    
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = Supplier.objects.all()
        
        # Filter by company type
        company_type = self.request.query_params.get('company_type', None)
        if company_type:
            queryset = queryset.filter(company_type=company_type)
        
        # Filter by performance score
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            queryset = queryset.filter(overall_score__gte=min_score)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get detailed performance metrics for a supplier."""
        supplier = self.get_object()
        
        # Get project history
        project_history = supplier.projects.all()
        total_projects = project_history.count()
        completed_projects = project_history.filter(project__status='completed').count()
        
        # Calculate performance metrics
        avg_quality = project_history.aggregate(avg_quality=Avg('quality_rating'))['avg_quality']
        avg_cost_variance = project_history.aggregate(avg_cost_variance=Avg('cost_variance'))['avg_cost_variance']
        on_time_rate = project_history.filter(on_time_delivery=True).count() / total_projects * 100 if total_projects > 0 else 0
        
        performance_data = {
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0,
            'average_quality_rating': float(avg_quality) if avg_quality else None,
            'average_cost_variance': float(avg_cost_variance) if avg_cost_variance else None,
            'on_time_delivery_rate': on_time_rate,
            'overall_score': float(supplier.overall_score) if supplier.overall_score else None,
            'recent_projects': list(project_history.order_by('-created_at')[:5].values(
                'project__name', 'project__status', 'quality_rating', 'cost_variance'
            ))
        }
        
        return Response(performance_data)
    
    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        """Get top performing suppliers based on overall score."""
        top_suppliers = Supplier.objects.filter(
            overall_score__isnull=False,
            is_active=True
        ).order_by('-overall_score')[:10]
        
        serializer = self.get_serializer(top_suppliers, many=True)
        return Response(serializer.data)


class ProjectSupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing project-supplier relationships.
    """
    
    queryset = ProjectSupplier.objects.all()
    serializer_class = ProjectSupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = ProjectSupplier.objects.all()
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by supplier
        supplier_id = self.request.query_params.get('supplier_id', None)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Filter by relationship type
        relationship_type = self.request.query_params.get('relationship_type', None)
        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)
        
        return queryset


class HistoricalDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing historical data from external systems.
    """
    
    queryset = HistoricalData.objects.all()
    serializer_class = HistoricalDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = HistoricalData.objects.all()
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by data type
        data_type = self.request.query_params.get('data_type', None)
        if data_type:
            queryset = queryset.filter(data_type=data_type)
        
        # Filter by source system
        source_system = self.request.query_params.get('source_system', None)
        if source_system:
            queryset = queryset.filter(source_system=source_system)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(data_date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(data_date__lte=end_date)
        
        return queryset


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI-generated risk assessments.
    """
    
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = RiskAssessment.objects.all()
        
        # Filter by project
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level', None)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filter by risk category
        risk_category = self.request.query_params.get('risk_category', None)
        if risk_category:
            queryset = queryset.filter(risk_category=risk_category)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class DashboardView(APIView):
    """
    Dashboard view providing overview of key metrics and insights.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data."""
        try:
            # Get recent projects
            recent_projects = Project.objects.order_by('-created_at')[:5]
            
            # Get risk summary
            risk_summary = RiskAssessment.objects.filter(is_active=True).aggregate(
                total_risks=Count('id'),
                high_risks=Count('id', filter=Q(risk_level__in=['high', 'critical'])),
                avg_probability=Avg('probability')
            )
            
            # Get supplier performance summary
            supplier_summary = Supplier.objects.filter(is_active=True).aggregate(
                total_suppliers=Count('id'),
                avg_score=Avg('overall_score')
            )
            
            # Get cost variance trends
            cost_variance_trend = Project.objects.filter(
                cost_variance__isnull=False
            ).aggregate(
                avg_variance=Avg('cost_variance_percentage'),
                projects_over_budget=Count('id', filter=Q(cost_variance__gt=0))
            )
            
            dashboard_data = {
                'recent_projects': list(recent_projects.values('id', 'name', 'status', 'project_type', 'cost_variance_percentage')),
                'risk_summary': {
                    'total_risks': risk_summary['total_risks'],
                    'high_risks': risk_summary['high_risks'],
                    'average_probability': float(risk_summary['avg_probability']) if risk_summary['avg_probability'] else 0
                },
                'supplier_summary': {
                    'total_suppliers': supplier_summary['total_suppliers'],
                    'average_score': float(supplier_summary['avg_score']) if supplier_summary['avg_score'] else 0
                },
                'cost_analysis': {
                    'average_variance': float(cost_variance_trend['avg_variance']) if cost_variance_trend['avg_variance'] else 0,
                    'projects_over_budget': cost_variance_trend['projects_over_budget']
                }
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            return Response(
                {'error': 'Failed to generate dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectCostVarianceView(APIView):
    """
    View for analyzing cost variance for a specific project.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get cost variance analysis for a project."""
        try:
            project = Project.objects.get(pk=pk)
            
            # Calculate cost variance
            cost_variance = project.calculate_cost_variance()
            
            # Get supplier cost variances
            supplier_variances = project.suppliers.all().values(
                'supplier__name', 'cost_variance', 'contract_value'
            )
            
            analysis_data = {
                'project_id': project.id,
                'project_name': project.name,
                'estimated_budget': float(project.estimated_budget) if project.estimated_budget else None,
                'actual_budget': float(project.actual_budget) if project.actual_budget else None,
                'cost_variance': float(cost_variance) if cost_variance else None,
                'cost_variance_percentage': float(project.cost_variance_percentage) if project.cost_variance_percentage else None,
                'supplier_breakdown': list(supplier_variances)
            }
            
            return Response(analysis_data)
            
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing project cost variance: {str(e)}")
            return Response(
                {'error': 'Failed to analyze cost variance'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SupplierScoreView(APIView):
    """
    View for analyzing supplier performance scores.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get detailed score analysis for a supplier."""
        try:
            supplier = Supplier.objects.get(pk=pk)
            
            # Calculate overall score
            overall_score = supplier.calculate_overall_score()
            
            # Get project performance history
            project_performance = supplier.projects.all().values(
                'project__name', 'quality_rating', 'cost_variance', 'on_time_delivery'
            )
            
            score_data = {
                'supplier_id': supplier.id,
                'supplier_name': supplier.name,
                'overall_score': float(overall_score) if overall_score else None,
                'reliability_score': float(supplier.reliability_score) if supplier.reliability_score else None,
                'quality_score': float(supplier.quality_score) if supplier.quality_score else None,
                'cost_score': float(supplier.cost_score) if supplier.cost_score else None,
                'project_performance': list(project_performance)
            }
            
            return Response(score_data)
            
        except Supplier.DoesNotExist:
            return Response(
                {'error': 'Supplier not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing supplier score: {str(e)}")
            return Response(
                {'error': 'Failed to analyze supplier score'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RiskAnalysisView(APIView):
    """
    View for comprehensive risk analysis across projects.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive risk analysis."""
        try:
            # Get risk distribution by category
            risk_by_category = RiskAssessment.objects.filter(
                is_active=True
            ).values('risk_category').annotate(
                count=Count('id'),
                avg_probability=Avg('probability'),
                avg_impact=Avg('impact_score')
            )
            
            # Get high-risk projects
            high_risk_projects = RiskAssessment.objects.filter(
                risk_level__in=['high', 'critical'],
                is_active=True
            ).values('project__name', 'risk_category', 'probability', 'impact_score')
            
            # Get risk trends over time
            recent_risks = RiskAssessment.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            analysis_data = {
                'risk_distribution': list(risk_by_category),
                'high_risk_projects': list(high_risk_projects),
                'recent_risks': recent_risks,
                'total_active_risks': RiskAssessment.objects.filter(is_active=True).count()
            }
            
            return Response(analysis_data)
            
        except Exception as e:
            logger.error(f"Error performing risk analysis: {str(e)}")
            return Response(
                {'error': 'Failed to perform risk analysis'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
