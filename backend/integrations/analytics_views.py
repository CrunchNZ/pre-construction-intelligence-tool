"""
Analytics API Views

This module provides REST API endpoints for accessing project analytics,
portfolio summaries, and trend analysis across all integrated systems.

Key Features:
- Portfolio summary analytics
- Project-specific analytics
- System-specific analytics
- Comparative analytics
- Trend analysis
- Risk assessment
- Performance metrics

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.utils import timezone

from .analytics_service import ProjectAnalyticsService
from .models import UnifiedProject, IntegrationSystem

logger = logging.getLogger(__name__)


class AnalyticsViewSet(ViewSet):
    """
    ViewSet for analytics operations.
    
    Provides comprehensive analytics endpoints for portfolio,
    project, and system-level insights.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analytics_service = ProjectAnalyticsService()
    
    def list(self, request):
        """Get overview of available analytics."""
        try:
            overview = {
                'available_endpoints': [
                    'portfolio_summary',
                    'project_analytics',
                    'system_analytics',
                    'comparative_analytics',
                    'trend_analytics',
                    'risk_assessment',
                    'performance_metrics'
                ],
                'description': 'Comprehensive analytics for integrated construction management systems',
                'version': '1.0.0'
            }
            
            return Response(overview, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get analytics overview: {str(e)}")
            return Response(
                {'error': 'Failed to get analytics overview'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def portfolio_summary(self, request):
        """Get comprehensive portfolio summary analytics."""
        try:
            summary = self.analytics_service.get_portfolio_summary()
            
            if 'error' in summary:
                return Response(
                    {'error': summary['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(summary, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {str(e)}")
            return Response(
                {'error': 'Failed to get portfolio summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def project_analytics(self, request, project_id=None):
        """Get detailed analytics for a specific project."""
        try:
            if not project_id:
                project_id = request.query_params.get('project_id')
            
            if not project_id:
                return Response(
                    {'error': 'Project ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = self.analytics_service.get_project_analytics(project_id)
            
            if 'error' in analytics:
                if analytics['error'] == 'Project not found':
                    return Response(
                        {'error': 'Project not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                else:
                    return Response(
                        {'error': analytics['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get project analytics for {project_id}: {str(e)}")
            return Response(
                {'error': 'Failed to get project analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def system_analytics(self, request, system_type=None):
        """Get analytics for a specific integration system."""
        try:
            if not system_type:
                system_type = request.query_params.get('system_type')
            
            if not system_type:
                return Response(
                    {'error': 'System type is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = self.analytics_service.get_system_analytics(system_type)
            
            if 'error' in analytics:
                if analytics['error'] == 'System not found':
                    return Response(
                        {'error': 'System not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                else:
                    return Response(
                        {'error': analytics['error']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get system analytics for {system_type}: {str(e)}")
            return Response(
                {'error': 'Failed to get system analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def comparative_analytics(self, request):
        """Get comparative analytics between multiple projects."""
        try:
            project_ids = request.query_params.getlist('project_ids[]')
            
            if not project_ids:
                return Response(
                    {'error': 'Project IDs are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(project_ids) < 2:
                return Response(
                    {'error': 'At least 2 project IDs are required for comparison'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = self.analytics_service.get_comparative_analytics(project_ids)
            
            if 'error' in analytics:
                return Response(
                    {'error': analytics['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get comparative analytics: {str(e)}")
            return Response(
                {'error': 'Failed to get comparative analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def trend_analytics(self, request):
        """Get trend analytics over a specified time period."""
        try:
            days = request.query_params.get('days', 30)
            
            try:
                days = int(days)
                if days <= 0 or days > 365:
                    return Response(
                        {'error': 'Days must be between 1 and 365'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Days must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analytics = self.analytics_service.get_trend_analytics(days)
            
            if 'error' in analytics:
                return Response(
                    {'error': analytics['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(analytics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get trend analytics: {str(e)}")
            return Response(
                {'error': 'Failed to get trend analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def risk_assessment(self, request):
        """Get comprehensive risk assessment across all projects."""
        try:
            # Get all projects with risk information
            projects = UnifiedProject.objects.all().values(
                'id', 'name', 'status', 'risk_score', 'risk_level',
                'progress_percentage', 'budget_variance', 'days_remaining'
            )
            
            risk_assessment = {
                'total_projects': len(projects),
                'risk_distribution': {
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'unknown': 0
                },
                'high_risk_projects': [],
                'medium_risk_projects': [],
                'low_risk_projects': [],
                'risk_factors': {
                    'over_budget': 0,
                    'behind_schedule': 0,
                    'low_progress': 0,
                    'high_change_orders': 0,
                    'many_open_rfis': 0
                },
                'recommendations': []
            }
            
            for project in projects:
                risk_level = project.get('risk_level', 'unknown')
                risk_assessment['risk_distribution'][risk_level] += 1
                
                # Categorize projects by risk level
                if risk_level == 'high':
                    risk_assessment['high_risk_projects'].append(project)
                elif risk_level == 'medium':
                    risk_assessment['medium_risk_projects'].append(project)
                elif risk_level == 'low':
                    risk_assessment['low_risk_projects'].append(project)
                
                # Analyze risk factors
                if project.get('budget_variance', 0) > 0:
                    risk_assessment['risk_factors']['over_budget'] += 1
                
                if project.get('days_remaining', 0) < 0:
                    risk_assessment['risk_factors']['behind_schedule'] += 1
                
                if project.get('progress_percentage', 0) < 50:
                    risk_assessment['risk_factors']['low_progress'] += 1
            
            # Generate recommendations
            if risk_assessment['risk_distribution']['high'] > 0:
                risk_assessment['recommendations'].append(
                    f"Review {risk_assessment['risk_distribution']['high']} high-risk projects immediately"
                )
            
            if risk_assessment['risk_factors']['over_budget'] > 0:
                risk_assessment['recommendations'].append(
                    f"Address budget issues in {risk_assessment['risk_factors']['over_budget']} projects"
                )
            
            if risk_assessment['risk_factors']['behind_schedule'] > 0:
                risk_assessment['recommendations'].append(
                    f"Implement schedule recovery for {risk_assessment['risk_factors']['behind_schedule']} projects"
                )
            
            if not risk_assessment['recommendations']:
                risk_assessment['recommendations'].append("All projects are performing well")
            
            return Response(risk_assessment, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get risk assessment: {str(e)}")
            return Response(
                {'error': 'Failed to get risk assessment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def performance_metrics(self, request):
        """Get comprehensive performance metrics across all projects."""
        try:
            # Get performance metrics for all projects
            projects = UnifiedProject.objects.all()
            
            performance_metrics = {
                'total_projects': projects.count(),
                'performance_distribution': {
                    'excellent': 0,
                    'good': 0,
                    'fair': 0,
                    'poor': 0
                },
                'budget_performance': {
                    'under_budget': 0,
                    'on_budget': 0,
                    'over_budget': 0
                },
                'schedule_performance': {
                    'ahead_of_schedule': 0,
                    'on_schedule': 0,
                    'behind_schedule': 0
                },
                'progress_performance': {
                    'high_progress': 0,
                    'medium_progress': 0,
                    'low_progress': 0
                },
                'average_metrics': {
                    'average_progress': 0.0,
                    'average_budget_variance': 0.0,
                    'average_schedule_variance': 0.0
                },
                'top_performers': [],
                'bottom_performers': []
            }
            
            total_progress = 0
            total_budget_variance = 0
            total_schedule_variance = 0
            project_scores = []
            
            for project in projects:
                # Calculate performance score
                performance_score = 0
                
                # Progress score (40 points)
                progress = project.progress_percentage or 0
                performance_score += min(40, progress)
                
                # Budget score (30 points)
                if project.budget and project.actual_cost:
                    budget_variance_pct = abs(project.budget_variance / project.budget * 100) if project.budget != 0 else 0
                    if budget_variance_pct <= 5:
                        performance_score += 30
                    elif budget_variance_pct <= 10:
                        performance_score += 20
                    elif budget_variance_pct <= 20:
                        performance_score += 10
                
                # Schedule score (30 points)
                if project.end_date:
                    if project.end_date >= timezone.now().date():
                        performance_score += 30
                    elif project.status == 'completed':
                        performance_score += 25
                    else:
                        performance_score += 10
                
                # Categorize performance
                if performance_score >= 80:
                    performance_metrics['performance_distribution']['excellent'] += 1
                elif performance_score >= 60:
                    performance_metrics['performance_distribution']['good'] += 1
                elif performance_score >= 40:
                    performance_metrics['performance_distribution']['fair'] += 1
                else:
                    performance_metrics['performance_distribution']['poor'] += 1
                
                # Budget performance
                if project.is_over_budget:
                    performance_metrics['budget_performance']['over_budget'] += 1
                elif project.budget and project.actual_cost and project.actual_cost < project.budget:
                    performance_metrics['budget_performance']['under_budget'] += 1
                else:
                    performance_metrics['budget_performance']['on_budget'] += 1
                
                # Schedule performance
                if project.days_remaining and project.days_remaining < 0:
                    performance_metrics['schedule_performance']['behind_schedule'] += 1
                elif project.days_remaining and project.days_remaining > 7:
                    performance_metrics['schedule_performance']['ahead_of_schedule'] += 1
                else:
                    performance_metrics['schedule_performance']['on_schedule'] += 1
                
                # Progress performance
                if progress >= 70:
                    performance_metrics['progress_performance']['high_progress'] += 1
                elif progress >= 40:
                    performance_metrics['progress_performance']['medium_progress'] += 1
                else:
                    performance_metrics['progress_performance']['low_progress'] += 1
                
                # Accumulate totals for averages
                total_progress += progress
                if project.budget_variance:
                    total_budget_variance += project.budget_variance
                if project.days_remaining:
                    total_schedule_variance += project.days_remaining
                
                # Store project score for ranking
                project_scores.append({
                    'id': str(project.id),
                    'name': project.name,
                    'performance_score': performance_score,
                    'progress_percentage': progress,
                    'budget_variance': float(project.budget_variance) if project.budget_variance else 0,
                    'days_remaining': project.days_remaining
                })
            
            # Calculate averages
            if projects.count() > 0:
                performance_metrics['average_metrics']['average_progress'] = total_progress / projects.count()
                performance_metrics['average_metrics']['average_budget_variance'] = total_budget_variance / projects.count()
                performance_metrics['average_metrics']['average_schedule_variance'] = total_schedule_variance / projects.count()
            
            # Rank projects by performance
            project_scores.sort(key=lambda x: x['performance_score'], reverse=True)
            
            # Top 5 performers
            performance_metrics['top_performers'] = project_scores[:5]
            
            # Bottom 5 performers
            performance_metrics['bottom_performers'] = project_scores[-5:][::-1]
            
            return Response(performance_metrics, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            return Response(
                {'error': 'Failed to get performance metrics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Individual API Views for specific analytics endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def portfolio_summary_view(request):
    """Get portfolio summary analytics."""
    try:
        analytics_service = ProjectAnalyticsService()
        summary = analytics_service.get_portfolio_summary()
        
        if 'error' in summary:
            return Response(
                {'error': summary['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {str(e)}")
        return Response(
            {'error': 'Failed to get portfolio summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_analytics_view(request, project_id):
    """Get analytics for a specific project."""
    try:
        analytics_service = ProjectAnalyticsService()
        analytics = analytics_service.get_project_analytics(project_id)
        
        if 'error' in analytics:
            if analytics['error'] == 'Project not found':
                return Response(
                    {'error': 'Project not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': analytics['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get project analytics for {project_id}: {str(e)}")
        return Response(
            {'error': 'Failed to get project analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_analytics_view(request, system_type):
    """Get analytics for a specific integration system."""
    try:
        analytics_service = ProjectAnalyticsService()
        analytics = analytics_service.get_system_analytics(system_type)
        
        if 'error' in analytics:
            if analytics['error'] == 'System not found':
                return Response(
                    {'error': 'System not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': analytics['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get system analytics for {system_type}: {str(e)}")
        return Response(
            {'error': 'Failed to get system analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comparative_analytics_view(request):
    """Get comparative analytics between multiple projects."""
    try:
        project_ids = request.query_params.getlist('project_ids[]')
        
        if not project_ids:
            return Response(
                {'error': 'Project IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(project_ids) < 2:
            return Response(
                {'error': 'At least 2 project IDs are required for comparison'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        analytics_service = ProjectAnalyticsService()
        analytics = analytics_service.get_comparative_analytics(project_ids)
        
        if 'error' in analytics:
            return Response(
                {'error': analytics['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get comparative analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get comparative analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trend_analytics_view(request):
    """Get trend analytics over a specified time period."""
    try:
        days = request.query_params.get('days', 30)
        
        try:
            days = int(days)
            if days <= 0 or days > 365:
                return Response(
                    {'error': 'Days must be between 1 and 365'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Days must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        analytics_service = ProjectAnalyticsService()
        analytics = analytics_service.get_trend_analytics(days)
        
        if 'error' in analytics:
            return Response(
                {'error': analytics['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get trend analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get trend analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def risk_assessment_view(request):
    """Get comprehensive risk assessment across all projects."""
    try:
        # Get all projects with risk information
        projects = UnifiedProject.objects.all().values(
            'id', 'name', 'status', 'risk_score', 'risk_level',
            'progress_percentage', 'budget_variance', 'days_remaining'
        )
        
        risk_assessment = {
            'total_projects': len(projects),
            'risk_distribution': {
                'high': 0,
                'medium': 0,
                'low': 0,
                'unknown': 0
            },
            'high_risk_projects': [],
            'medium_risk_projects': [],
            'low_risk_projects': [],
            'risk_factors': {
                'over_budget': 0,
                'behind_schedule': 0,
                'low_progress': 0,
                'high_change_orders': 0,
                'many_open_rfis': 0
            },
            'recommendations': []
        }
        
        for project in projects:
            risk_level = project.get('risk_level', 'unknown')
            risk_assessment['risk_distribution'][risk_level] += 1
            
            # Categorize projects by risk level
            if risk_level == 'high':
                risk_assessment['high_risk_projects'].append(project)
            elif risk_level == 'medium':
                risk_assessment['medium_risk_projects'].append(project)
            elif risk_level == 'low':
                risk_assessment['low_risk_projects'].append(project)
            
            # Analyze risk factors
            if project.get('budget_variance', 0) > 0:
                risk_assessment['risk_factors']['over_budget'] += 1
            
            if project.get('days_remaining', 0) < 0:
                risk_assessment['risk_factors']['behind_schedule'] += 1
            
            if project.get('progress_percentage', 0) < 50:
                risk_assessment['risk_factors']['low_progress'] += 1
        
        # Generate recommendations
        if risk_assessment['risk_distribution']['high'] > 0:
            risk_assessment['recommendations'].append(
                f"Review {risk_assessment['risk_distribution']['high']} high-risk projects immediately"
            )
        
        if risk_assessment['risk_factors']['over_budget'] > 0:
            risk_assessment['recommendations'].append(
                f"Address budget issues in {risk_assessment['risk_factors']['over_budget']} projects"
            )
        
        if risk_assessment['risk_factors']['behind_schedule'] > 0:
            risk_assessment['recommendations'].append(
                f"Implement schedule recovery for {risk_assessment['risk_factors']['behind_schedule']} projects"
            )
        
        if not risk_assessment['recommendations']:
            risk_assessment['recommendations'].append("All projects are performing well")
        
        return Response(risk_assessment, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get risk assessment: {str(e)}")
        return Response(
            {'error': 'Failed to get risk assessment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_metrics_view(request):
    """Get comprehensive performance metrics across all projects."""
    try:
        # Get performance metrics for all projects
        projects = UnifiedProject.objects.all()
        
        performance_metrics = {
            'total_projects': projects.count(),
            'performance_distribution': {
                'excellent': 0,
                'good': 0,
                'fair': 0,
                'poor': 0
            },
            'budget_performance': {
                'under_budget': 0,
                'on_budget': 0,
                'over_budget': 0
            },
            'schedule_performance': {
                'ahead_of_schedule': 0,
                'on_schedule': 0,
                'behind_schedule': 0
            },
            'progress_performance': {
                'high_progress': 0,
                'medium_progress': 0,
                'low_progress': 0
            },
            'average_metrics': {
                'average_progress': 0.0,
                'average_budget_variance': 0.0,
                'average_schedule_variance': 0.0
            },
            'top_performers': [],
            'bottom_performers': []
        }
        
        total_progress = 0
        total_budget_variance = 0
        total_schedule_variance = 0
        project_scores = []
        
        for project in projects:
            # Calculate performance score
            performance_score = 0
            
            # Progress score (40 points)
            progress = project.progress_percentage or 0
            performance_score += min(40, progress)
            
            # Budget score (30 points)
            if project.budget and project.actual_cost:
                budget_variance_pct = abs(project.budget_variance / project.budget * 100) if project.budget != 0 else 0
                if budget_variance_pct <= 5:
                    performance_score += 30
                elif budget_variance_pct <= 10:
                    performance_score += 20
                elif budget_variance_pct <= 20:
                    performance_score += 10
            
            # Schedule score (30 points)
            if project.end_date:
                if project.end_date >= timezone.now().date():
                    performance_score += 30
                elif project.status == 'completed':
                    performance_score += 25
                else:
                    performance_score += 10
            
            # Categorize performance
            if performance_score >= 80:
                performance_metrics['performance_distribution']['excellent'] += 1
            elif performance_score >= 60:
                performance_metrics['performance_distribution']['good'] += 1
            elif performance_score >= 40:
                performance_metrics['performance_distribution']['fair'] += 1
            else:
                performance_metrics['performance_distribution']['poor'] += 1
            
            # Budget performance
            if project.is_over_budget:
                performance_metrics['budget_performance']['over_budget'] += 1
            elif project.budget and project.actual_cost and project.actual_cost < project.budget:
                performance_metrics['budget_performance']['under_budget'] += 1
            else:
                performance_metrics['budget_performance']['on_budget'] += 1
            
            # Schedule performance
            if project.days_remaining and project.days_remaining < 0:
                performance_metrics['schedule_performance']['behind_schedule'] += 1
            elif project.days_remaining and project.days_remaining > 7:
                performance_metrics['schedule_performance']['ahead_of_schedule'] += 1
            else:
                performance_metrics['schedule_performance']['on_schedule'] += 1
            
            # Progress performance
            if progress >= 70:
                performance_metrics['progress_performance']['high_progress'] += 1
            elif progress >= 40:
                performance_metrics['progress_performance']['medium_progress'] += 1
            else:
                performance_metrics['progress_performance']['low_progress'] += 1
            
            # Accumulate totals for averages
            total_progress += progress
            if project.budget_variance:
                total_budget_variance += project.budget_variance
            if project.days_remaining:
                total_schedule_variance += project.days_remaining
            
            # Store project score for ranking
            project_scores.append({
                'id': str(project.id),
                'name': project.name,
                'performance_score': performance_score,
                'progress_percentage': progress,
                'budget_variance': float(project.budget_variance) if project.budget_variance else 0,
                'days_remaining': project.days_remaining
            })
        
        # Calculate averages
        if projects.count() > 0:
            performance_metrics['average_metrics']['average_progress'] = total_progress / projects.count()
            performance_metrics['average_metrics']['average_budget_variance'] = total_budget_variance / projects.count()
            performance_metrics['average_metrics']['average_schedule_variance'] = total_schedule_variance / projects.count()
        
        # Rank projects by performance
        project_scores.sort(key=lambda x: x['performance_score'], reverse=True)
        
        # Top 5 performers
        performance_metrics['top_performers'] = project_scores[:5]
        
        # Bottom 5 performers
        performance_metrics['bottom_performers'] = project_scores[-5:][::-1]
        
        return Response(performance_metrics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        return Response(
            {'error': 'Failed to get performance metrics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_analytics_cache_view(request):
    """Clear analytics cache."""
    try:
        analytics_service = ProjectAnalyticsService()
        analytics_service.clear_cache()
        
        return Response(
            {'message': 'Analytics cache cleared successfully'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Failed to clear analytics cache: {str(e)}")
        return Response(
            {'error': 'Failed to clear analytics cache'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
