"""
Unified Project Analytics Service

This service provides comprehensive analytics and insights across all
integrated construction management systems. It calculates key metrics,
risk scores, and performance indicators for projects and portfolios.

Key Features:
- Multi-system data aggregation
- Risk assessment and scoring
- Performance metrics calculation
- Trend analysis and forecasting
- Custom report generation
- Real-time analytics dashboard

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg, Sum, F, Max, Min
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal

from .models import (
    UnifiedProject,
    ProjectSystemMapping,
    ProjectDocument,
    ProjectSchedule,
    ProjectFinancial,
    ProjectChangeOrder,
    ProjectRFI,
    IntegrationSystem,
)

logger = logging.getLogger(__name__)


class ProjectAnalyticsService:
    """
    Unified project analytics service.
    
    Provides comprehensive analytics and insights across all integrated
    construction management systems with risk assessment and performance
    metrics.
    """
    
    def __init__(self):
        """Initialize the analytics service."""
        self.cache_timeout = 3600  # 1 hour
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary analytics."""
        cache_key = 'portfolio_summary'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            projects = UnifiedProject.objects.all()
            
            summary = {
                'total_projects': projects.count(),
                'active_projects': projects.filter(status='construction').count(),
                'planning_projects': projects.filter(status='planning').count(),
                'completed_projects': projects.filter(status='completed').count(),
                'on_hold_projects': projects.filter(status='on_hold').count(),
                
                # Financial metrics
                'total_budget': float(projects.aggregate(total=Sum('budget'))['total'] or 0),
                'total_actual_cost': float(projects.aggregate(total=Sum('actual_cost'))['total'] or 0),
                'average_budget': float(projects.aggregate(avg=Avg('budget'))['avg'] or 0),
                'budget_variance': self._calculate_budget_variance(),
                
                # Timeline metrics
                'average_duration_days': projects.aggregate(avg=Avg('estimated_duration_days'))['avg'] or 0,
                'projects_behind_schedule': self._count_projects_behind_schedule(),
                'projects_ahead_of_schedule': self._count_projects_ahead_of_schedule(),
                
                # Progress metrics
                'average_progress': self._calculate_average_progress(),
                'projects_over_budget': self._count_projects_over_budget(),
                'projects_under_budget': self._count_projects_under_budget(),
                
                # Risk metrics
                'high_risk_projects': self._count_high_risk_projects(),
                'medium_risk_projects': self._count_medium_risk_projects(),
                'low_risk_projects': self._count_low_risk_projects(),
                
                # Integration metrics
                'integration_status': self._get_integration_status_summary(),
                
                # Last updated
                'last_updated': timezone.now().isoformat(),
            }
            
            cache.set(cache_key, summary, timeout=self.cache_timeout)
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate portfolio summary: {str(e)}")
            return {'error': str(e)}
    
    def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific project."""
        cache_key = f'project_analytics_{project_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            project = UnifiedProject.objects.get(id=project_id)
            
            analytics = {
                'project_id': str(project.id),
                'project_name': project.name,
                'project_number': project.project_number,
                'status': project.status,
                'project_type': project.project_type,
                
                # Basic metrics
                'progress_percentage': project.progress_percentage,
                'days_remaining': project.days_remaining,
                'budget_variance': float(project.budget_variance) if project.budget_variance else 0,
                'is_over_budget': project.is_over_budget,
                
                # Risk assessment
                'risk_score': self._calculate_project_risk_score(project),
                'risk_factors': self._identify_risk_factors(project),
                'risk_level': self._get_risk_level(project),
                
                # Financial analytics
                'financial_metrics': self._get_financial_metrics(project),
                
                # Schedule analytics
                'schedule_metrics': self._get_schedule_metrics(project),
                
                # Document analytics
                'document_metrics': self._get_document_metrics(project),
                
                # Change order analytics
                'change_order_metrics': self._get_change_order_metrics(project),
                
                # RFI analytics
                'rfi_metrics': self._get_rfi_metrics(project),
                
                # Integration status
                'integration_status': self._get_project_integration_status(project),
                
                # Performance trends
                'performance_trends': self._get_performance_trends(project),
                
                # Recommendations
                'recommendations': self._generate_recommendations(project),
                
                'last_updated': timezone.now().isoformat(),
            }
            
            cache.set(cache_key, analytics, timeout=self.cache_timeout)
            return analytics
            
        except UnifiedProject.DoesNotExist:
            return {'error': 'Project not found'}
        except Exception as e:
            logger.error(f"Failed to generate project analytics for {project_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_system_analytics(self, system_type: str) -> Dict[str, Any]:
        """Get analytics for a specific integration system."""
        cache_key = f'system_analytics_{system_type}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            system = IntegrationSystem.objects.get(system_type=system_type)
            projects = UnifiedProject.objects.filter(integration_systems=system)
            
            analytics = {
                'system_name': system.name,
                'system_type': system.system_type,
                'status': system.status,
                'connection_status': system.connection_status,
                
                # Project metrics
                'total_projects': projects.count(),
                'active_projects': projects.filter(status='construction').count(),
                'completed_projects': projects.filter(status='completed').count(),
                
                # Financial metrics
                'total_budget': float(projects.aggregate(total=Sum('budget'))['total'] or 0),
                'total_actual_cost': float(projects.aggregate(total=Sum('actual_cost'))['total'] or 0),
                'average_budget': float(projects.aggregate(avg=Avg('budget'))['avg'] or 0),
                
                # Performance metrics
                'average_progress': self._calculate_average_progress_for_system(system),
                'projects_over_budget': self._count_projects_over_budget_for_system(system),
                'projects_behind_schedule': self._count_projects_behind_schedule_for_system(system),
                
                # Sync metrics
                'last_sync': system.last_connection.isoformat() if system.last_connection else None,
                'success_rate': system.success_rate,
                'avg_response_time': system.avg_response_time,
                
                'last_updated': timezone.now().isoformat(),
            }
            
            cache.set(cache_key, analytics, timeout=self.cache_timeout)
            return analytics
            
        except IntegrationSystem.DoesNotExist:
            return {'error': 'System not found'}
        except Exception as e:
            logger.error(f"Failed to generate system analytics for {system_type}: {str(e)}")
            return {'error': str(e)}
    
    def get_comparative_analytics(self, project_ids: List[str]) -> Dict[str, Any]:
        """Get comparative analytics between multiple projects."""
        try:
            projects = UnifiedProject.objects.filter(id__in=project_ids)
            
            if not projects.exists():
                return {'error': 'No projects found'}
            
            comparative = {
                'projects_compared': len(projects),
                'project_names': [p.name for p in projects],
                
                # Budget comparison
                'budget_comparison': {
                    'budgets': [float(p.budget) if p.budget else 0 for p in projects],
                    'actual_costs': [float(p.actual_cost) if p.actual_cost else 0 for p in projects],
                    'variances': [float(p.budget_variance) if p.budget_variance else 0 for p in projects],
                },
                
                # Progress comparison
                'progress_comparison': {
                    'progress_percentages': [p.progress_percentage for p in projects],
                    'days_remaining': [p.days_remaining for p in projects],
                },
                
                # Risk comparison
                'risk_comparison': {
                    'risk_scores': [self._calculate_project_risk_score(p) for p in projects],
                    'risk_levels': [self._get_risk_level(p) for p in projects],
                },
                
                # Performance ranking
                'performance_ranking': self._rank_projects_by_performance(projects),
                
                'last_updated': timezone.now().isoformat(),
            }
            
            return comparative
            
        except Exception as e:
            logger.error(f"Failed to generate comparative analytics: {str(e)}")
            return {'error': str(e)}
    
    def get_trend_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get trend analytics over a specified time period."""
        cache_key = f'trend_analytics_{days}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get projects created/updated in the time period
            recent_projects = UnifiedProject.objects.filter(
                Q(created_at__date__gte=start_date) | Q(updated_at__date__gte=start_date)
            )
            
            trends = {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                
                # Project trends
                'new_projects': recent_projects.filter(created_at__date__gte=start_date).count(),
                'updated_projects': recent_projects.filter(updated_at__date__gte=start_date).count(),
                
                # Status trends
                'status_changes': self._analyze_status_changes(start_date, end_date),
                
                # Financial trends
                'budget_trends': self._analyze_budget_trends(start_date, end_date),
                
                # Risk trends
                'risk_trends': self._analyze_risk_trends(start_date, end_date),
                
                # Integration trends
                'integration_trends': self._analyze_integration_trends(start_date, end_date),
                
                'last_updated': timezone.now().isoformat(),
            }
            
            cache.set(cache_key, trends, timeout=self.cache_timeout)
            return trends
            
        except Exception as e:
            logger.error(f"Failed to generate trend analytics: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_budget_variance(self) -> float:
        """Calculate overall budget variance across all projects."""
        try:
            projects = UnifiedProject.objects.filter(
                Q(budget__isnull=False) & Q(actual_cost__isnull=False)
            )
            
            if not projects.exists():
                return 0.0
            
            total_budget = projects.aggregate(total=Sum('budget'))['total']
            total_actual = projects.aggregate(total=Sum('actual_cost'))['total']
            
            if total_budget == 0:
                return 0.0
            
            return float((total_actual - total_budget) / total_budget * 100)
            
        except Exception as e:
            logger.error(f"Failed to calculate budget variance: {str(e)}")
            return 0.0
    
    def _count_projects_behind_schedule(self) -> int:
        """Count projects that are behind schedule."""
        try:
            today = timezone.now().date()
            return UnifiedProject.objects.filter(
                Q(end_date__lt=today) & ~Q(status='completed')
            ).count()
        except Exception as e:
            logger.error(f"Failed to count projects behind schedule: {str(e)}")
            return 0
    
    def _count_projects_ahead_of_schedule(self) -> int:
        """Count projects that are ahead of schedule."""
        try:
            today = timezone.now().date()
            return UnifiedProject.objects.filter(
                Q(end_date__gt=today) & Q(status='construction')
            ).count()
        except Exception as e:
            logger.error(f"Failed to count projects ahead of schedule: {str(e)}")
            return 0
    
    def _calculate_average_progress(self) -> float:
        """Calculate average progress across all projects."""
        try:
            projects = UnifiedProject.objects.filter(status__in=['planning', 'construction'])
            if not projects.exists():
                return 0.0
            
            total_progress = sum(p.progress_percentage for p in projects)
            return total_progress / projects.count()
            
        except Exception as e:
            logger.error(f"Failed to calculate average progress: {str(e)}")
            return 0.0
    
    def _count_projects_over_budget(self) -> int:
        """Count projects that are over budget."""
        try:
            return UnifiedProject.objects.filter(
                Q(budget__isnull=False) & Q(actual_cost__isnull=False) & Q(actual_cost__gt=F('budget'))
            ).count()
        except Exception as e:
            logger.error(f"Failed to count projects over budget: {str(e)}")
            return 0
    
    def _count_projects_under_budget(self) -> int:
        """Count projects that are under budget."""
        try:
            return UnifiedProject.objects.filter(
                Q(budget__isnull=False) & Q(actual_cost__isnull=False) & Q(actual_cost__lt=F('budget'))
            ).count()
        except Exception as e:
            logger.error(f"Failed to count projects under budget: {str(e)}")
            return 0
    
    def _count_high_risk_projects(self) -> int:
        """Count high-risk projects."""
        try:
            high_risk_count = 0
            projects = UnifiedProject.objects.all()
            
            for project in projects:
                if self._get_risk_level(project) == 'high':
                    high_risk_count += 1
            
            return high_risk_count
            
        except Exception as e:
            logger.error(f"Failed to count high-risk projects: {str(e)}")
            return 0
    
    def _count_medium_risk_projects(self) -> int:
        """Count medium-risk projects."""
        try:
            medium_risk_count = 0
            projects = UnifiedProject.objects.all()
            
            for project in projects:
                if self._get_risk_level(project) == 'medium':
                    medium_risk_count += 1
            
            return medium_risk_count
            
        except Exception as e:
            logger.error(f"Failed to count medium-risk projects: {str(e)}")
            return 0
    
    def _count_low_risk_projects(self) -> int:
        """Count low-risk projects."""
        try:
            low_risk_count = 0
            projects = UnifiedProject.objects.all()
            
            for project in projects:
                if self._get_risk_level(project) == 'low':
                    low_risk_count += 1
            
            return low_risk_count
            
        except Exception as e:
            logger.error(f"Failed to count low-risk projects: {str(e)}")
            return 0
    
    def _get_integration_status_summary(self) -> Dict[str, Any]:
        """Get summary of integration system statuses."""
        try:
            systems = IntegrationSystem.objects.all()
            
            return {
                'total_systems': systems.count(),
                'active_systems': systems.filter(status='active').count(),
                'error_systems': systems.filter(status='error').count(),
                'systems_by_type': list(systems.values('system_type').annotate(count=Count('id'))),
                'connection_status': list(systems.values('connection_status').annotate(count=Count('id'))),
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status summary: {str(e)}")
            return {}
    
    def _calculate_project_risk_score(self, project: UnifiedProject) -> float:
        """Calculate risk score for a specific project (0-100)."""
        try:
            risk_score = 0.0
            
            # Budget risk (30 points max)
            if project.budget and project.actual_cost:
                budget_variance_pct = abs(project.budget_variance / project.budget * 100) if project.budget != 0 else 0
                if budget_variance_pct > 20:
                    risk_score += 30
                elif budget_variance_pct > 10:
                    risk_score += 20
                elif budget_variance_pct > 5:
                    risk_score += 10
            
            # Schedule risk (25 points max)
            if project.end_date and project.end_date < timezone.now().date():
                risk_score += 25
            elif project.end_date:
                days_remaining = (project.end_date - timezone.now().date()).days
                if days_remaining < 30:
                    risk_score += 20
                elif days_remaining < 60:
                    risk_score += 15
                elif days_remaining < 90:
                    risk_score += 10
            
            # Progress risk (20 points max)
            if project.progress_percentage < 30 and project.status == 'construction':
                risk_score += 20
            elif project.progress_percentage < 50 and project.status == 'construction':
                risk_score += 15
            elif project.progress_percentage < 70 and project.status == 'construction':
                risk_score += 10
            
            # Change order risk (15 points max)
            change_orders = ProjectChangeOrder.objects.filter(project=project)
            if change_orders.count() > 10:
                risk_score += 15
            elif change_orders.count() > 5:
                risk_score += 10
            elif change_orders.count() > 0:
                risk_score += 5
            
            # RFI risk (10 points max)
            open_rfis = ProjectRFI.objects.filter(project=project, status='open')
            if open_rfis.count() > 20:
                risk_score += 10
            elif open_rfis.count() > 10:
                risk_score += 7
            elif open_rfis.count() > 5:
                risk_score += 5
            
            return min(100.0, risk_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate risk score for project {project.id}: {str(e)}")
            return 0.0
    
    def _identify_risk_factors(self, project: UnifiedProject) -> List[str]:
        """Identify specific risk factors for a project."""
        risk_factors = []
        
        try:
            # Budget risks
            if project.budget and project.actual_cost:
                if project.actual_cost > project.budget:
                    risk_factors.append('Over budget')
                elif project.actual_cost > project.budget * 0.9:
                    risk_factors.append('Approaching budget limit')
            
            # Schedule risks
            if project.end_date and project.end_date < timezone.now().date():
                risk_factors.append('Behind schedule')
            elif project.end_date:
                days_remaining = (project.end_date - timezone.now().date()).days
                if days_remaining < 30:
                    risk_factors.append('Critical timeline')
                elif days_remaining < 60:
                    risk_factors.append('Tight timeline')
            
            # Progress risks
            if project.progress_percentage < 50 and project.status == 'construction':
                risk_factors.append('Slow progress')
            
            # Change order risks
            change_order_count = ProjectChangeOrder.objects.filter(project=project).count()
            if change_order_count > 5:
                risk_factors.append('High change order volume')
            
            # RFI risks
            open_rfi_count = ProjectRFI.objects.filter(project=project, status='open').count()
            if open_rfi_count > 10:
                risk_factors.append('Many open RFIs')
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Failed to identify risk factors for project {project.id}: {str(e)}")
            return ['Unable to assess risks']
    
    def _get_risk_level(self, project: UnifiedProject) -> str:
        """Get risk level (low, medium, high) for a project."""
        try:
            risk_score = self._calculate_project_risk_score(project)
            
            if risk_score >= 70:
                return 'high'
            elif risk_score >= 40:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Failed to get risk level for project {project.id}: {str(e)}")
            return 'unknown'
    
    def _get_financial_metrics(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get financial metrics for a project."""
        try:
            financials = ProjectFinancial.objects.filter(project=project)
            
            return {
                'total_financial_records': financials.count(),
                'budget_records': financials.filter(financial_type='budget').count(),
                'actual_records': financials.filter(financial_type='actual').count(),
                'forecast_records': financials.filter(financial_type='forecast').count(),
                'total_budget_amount': float(financials.filter(financial_type='budget').aggregate(total=Sum('amount'))['total'] or 0),
                'total_actual_amount': float(financials.filter(financial_type='actual').aggregate(total=Sum('amount'))['total'] or 0),
                'budget_variance_percentage': self._calculate_budget_variance_percentage(project),
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial metrics for project {project.id}: {str(e)}")
            return {}
    
    def _get_schedule_metrics(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get schedule metrics for a project."""
        try:
            schedules = ProjectSchedule.objects.filter(project=project)
            
            return {
                'total_schedules': schedules.count(),
                'average_completion_percentage': float(schedules.aggregate(avg=Avg('completion_percentage'))['avg'] or 0),
                'average_duration_days': float(schedules.aggregate(avg=Avg('total_duration_days'))['avg'] or 0),
                'schedule_variance_days': self._calculate_schedule_variance(project),
            }
            
        except Exception as e:
            logger.error(f"Failed to get schedule metrics for project {project.id}: {str(e)}")
            return {}
    
    def _get_document_metrics(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get document metrics for a project."""
        try:
            documents = ProjectDocument.objects.filter(project=project)
            
            return {
                'total_documents': documents.count(),
                'documents_by_type': list(documents.values('document_type').annotate(count=Count('id'))),
                'documents_by_status': list(documents.values('status').annotate(count=Count('id'))),
                'total_file_size': documents.aggregate(total=Sum('file_size'))['total'] or 0,
                'average_file_size': float(documents.aggregate(avg=Avg('file_size'))['avg'] or 0),
            }
            
        except Exception as e:
            logger.error(f"Failed to get document metrics for project {project.id}: {str(e)}")
            return {}
    
    def _get_change_order_metrics(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get change order metrics for a project."""
        try:
            change_orders = ProjectChangeOrder.objects.filter(project=project)
            
            return {
                'total_change_orders': change_orders.count(),
                'change_orders_by_status': list(change_orders.values('status').annotate(count=Count('id'))),
                'total_change_order_value': float(change_orders.aggregate(total=Sum('change_order_value'))['total'] or 0),
                'average_change_order_value': float(change_orders.aggregate(avg=Avg('change_order_value'))['avg'] or 0),
                'schedule_impact_days': change_orders.aggregate(total=Sum('schedule_impact_days'))['total'] or 0,
            }
            
        except Exception as e:
            logger.error(f"Failed to get change order metrics for project {project.id}: {str(e)}")
            return {}
    
    def _get_rfi_metrics(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get RFI metrics for a project."""
        try:
            rfis = ProjectRFI.objects.filter(project=project)
            
            return {
                'total_rfis': rfis.count(),
                'open_rfis': rfis.filter(status='open').count(),
                'answered_rfis': rfis.filter(status='answered').count(),
                'closed_rfis': rfis.filter(status='closed').count(),
                'rfis_by_priority': list(rfis.values('priority').annotate(count=Count('id'))),
                'average_days_open': float(rfis.aggregate(avg=Avg('days_open'))['avg'] or 0),
                'urgent_rfis': rfis.filter(Q(status='open') & Q(priority__in=['high', 'critical'])).count(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get RFI metrics for project {project.id}: {str(e)}")
            return {}
    
    def _get_project_integration_status(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get integration status for a project."""
        try:
            mappings = ProjectSystemMapping.objects.filter(project=project)
            
            return {
                'total_integrations': mappings.count(),
                'active_integrations': mappings.filter(sync_status='completed').count(),
                'failed_integrations': mappings.filter(sync_status='failed').count(),
                'last_sync': max([m.last_sync for m in mappings if m.last_sync]) if mappings.exists() else None,
                'integration_details': list(mappings.values('system__name', 'sync_status', 'last_sync', 'sync_error')),
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status for project {project.id}: {str(e)}")
            return {}
    
    def _get_performance_trends(self, project: UnifiedProject) -> Dict[str, Any]:
        """Get performance trends for a project."""
        try:
            # This would typically involve historical data analysis
            # For now, return basic trend indicators
            
            return {
                'progress_trend': 'stable',  # Would calculate from historical data
                'budget_trend': 'stable',    # Would calculate from historical data
                'schedule_trend': 'stable',  # Would calculate from historical data
                'risk_trend': 'stable',      # Would calculate from historical data
                'last_updated': timezone.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance trends for project {project.id}: {str(e)}")
            return {}
    
    def _generate_recommendations(self, project: UnifiedProject) -> List[str]:
        """Generate recommendations for a project."""
        recommendations = []
        
        try:
            # Budget recommendations
            if project.is_over_budget:
                recommendations.append('Review budget allocation and identify cost-saving opportunities')
                recommendations.append('Analyze change orders for potential scope reduction')
            
            # Schedule recommendations
            if project.days_remaining and project.days_remaining < 30:
                recommendations.append('Implement accelerated construction methods')
                recommendations.append('Review critical path and optimize resource allocation')
            
            # Progress recommendations
            if project.progress_percentage < 50 and project.status == 'construction':
                recommendations.append('Assess resource constraints and increase capacity')
                recommendations.append('Review workflow efficiency and identify bottlenecks')
            
            # Change order recommendations
            change_order_count = ProjectChangeOrder.objects.filter(project=project).count()
            if change_order_count > 5:
                recommendations.append('Implement change management process improvements')
                recommendations.append('Review scope definition and stakeholder communication')
            
            # RFI recommendations
            open_rfi_count = ProjectRFI.objects.filter(project=project, status='open').count()
            if open_rfi_count > 10:
                recommendations.append('Establish RFI response team and escalation process')
                recommendations.append('Review design documentation for clarity and completeness')
            
            # Risk-based recommendations
            risk_level = self._get_risk_level(project)
            if risk_level == 'high':
                recommendations.append('Implement weekly risk review meetings')
                recommendations.append('Develop contingency plans for critical risk factors')
            
            return recommendations if recommendations else ['Project is performing well with no immediate actions required']
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for project {project.id}: {str(e)}")
            return ['Unable to generate recommendations at this time']
    
    def _calculate_budget_variance_percentage(self, project: UnifiedProject) -> float:
        """Calculate budget variance percentage for a project."""
        try:
            if not project.budget or project.budget == 0:
                return 0.0
            
            variance = project.budget_variance or 0
            return float((variance / project.budget) * 100)
            
        except Exception as e:
            logger.error(f"Failed to calculate budget variance percentage for project {project.id}: {str(e)}")
            return 0.0
    
    def _calculate_schedule_variance(self, project: UnifiedProject) -> int:
        """Calculate schedule variance in days for a project."""
        try:
            if not project.end_date:
                return 0
            
            today = timezone.now().date()
            variance = (project.end_date - today).days
            
            return variance
            
        except Exception as e:
            logger.error(f"Failed to calculate schedule variance for project {project.id}: {str(e)}")
            return 0
    
    def _calculate_average_progress_for_system(self, system: IntegrationSystem) -> float:
        """Calculate average progress for projects in a specific system."""
        try:
            projects = UnifiedProject.objects.filter(integration_systems=system, status__in=['planning', 'construction'])
            if not projects.exists():
                return 0.0
            
            total_progress = sum(p.progress_percentage for p in projects)
            return total_progress / projects.count()
            
        except Exception as e:
            logger.error(f"Failed to calculate average progress for system {system.name}: {str(e)}")
            return 0.0
    
    def _count_projects_over_budget_for_system(self, system: IntegrationSystem) -> int:
        """Count projects over budget for a specific system."""
        try:
            projects = UnifiedProject.objects.filter(integration_systems=system)
            return sum(1 for p in projects if p.is_over_budget)
            
        except Exception as e:
            logger.error(f"Failed to count projects over budget for system {system.name}: {str(e)}")
            return 0
    
    def _count_projects_behind_schedule_for_system(self, system: IntegrationSystem) -> int:
        """Count projects behind schedule for a specific system."""
        try:
            projects = UnifiedProject.objects.filter(integration_systems=system)
            today = timezone.now().date()
            return sum(1 for p in projects if p.end_date and p.end_date < today and p.status != 'completed')
            
        except Exception as e:
            logger.error(f"Failed to count projects behind schedule for system {system.name}: {str(e)}")
            return 0
    
    def _rank_projects_by_performance(self, projects) -> List[Dict[str, Any]]:
        """Rank projects by performance score."""
        try:
            project_scores = []
            
            for project in projects:
                # Calculate performance score (0-100)
                performance_score = 0
                
                # Progress score (40 points)
                performance_score += min(40, project.progress_percentage)
                
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
                
                project_scores.append({
                    'project_id': str(project.id),
                    'project_name': project.name,
                    'performance_score': performance_score,
                    'progress_percentage': project.progress_percentage,
                    'budget_variance': float(project.budget_variance) if project.budget_variance else 0,
                    'days_remaining': project.days_remaining,
                })
            
            # Sort by performance score (descending)
            project_scores.sort(key=lambda x: x['performance_score'], reverse=True)
            
            return project_scores
            
        except Exception as e:
            logger.error(f"Failed to rank projects by performance: {str(e)}")
            return []
    
    def _analyze_status_changes(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Analyze project status changes over time period."""
        try:
            # This would typically involve historical data analysis
            # For now, return basic analysis
            
            return {
                'status_changes_count': 0,  # Would calculate from historical data
                'most_common_transitions': [],  # Would analyze from historical data
                'status_change_frequency': 'low',  # Would calculate from historical data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze status changes: {str(e)}")
            return {}
    
    def _analyze_budget_trends(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Analyze budget trends over time period."""
        try:
            # This would typically involve historical data analysis
            # For now, return basic analysis
            
            return {
                'budget_increases': 0,  # Would calculate from historical data
                'budget_decreases': 0,  # Would calculate from historical data
                'average_budget_change': 0.0,  # Would calculate from historical data
                'budget_volatility': 'low',  # Would calculate from historical data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze budget trends: {str(e)}")
            return {}
    
    def _analyze_risk_trends(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Analyze risk trends over time period."""
        try:
            # This would typically involve historical data analysis
            # For now, return basic analysis
            
            return {
                'risk_level_changes': 0,  # Would calculate from historical data
                'new_risk_factors': [],  # Would analyze from historical data
                'risk_mitigation_effectiveness': 'medium',  # Would calculate from historical data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze risk trends: {str(e)}")
            return {}
    
    def _analyze_integration_trends(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Analyze integration trends over time period."""
        try:
            # This would typically involve historical data analysis
            # For now, return basic analysis
            
            return {
                'sync_success_rate': 95.0,  # Would calculate from historical data
                'average_sync_duration': 300,  # Would calculate from historical data
                'integration_errors': 0,  # Would calculate from historical data
                'system_uptime': 99.5,  # Would calculate from historical data
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze integration trends: {str(e)}")
            return {}
    
    def clear_cache(self):
        """Clear all cached analytics data."""
        try:
            cache.delete('portfolio_summary')
            cache.delete('trend_analytics_30')
            cache.delete('trend_analytics_60')
            cache.delete('trend_analytics_90')
            
            # Clear project-specific caches
            projects = UnifiedProject.objects.values_list('id', flat=True)
            for project_id in projects:
                cache.delete(f'project_analytics_{project_id}')
            
            # Clear system-specific caches
            systems = IntegrationSystem.objects.values_list('system_type', flat=True)
            for system_type in systems:
                cache.delete(f'system_analytics_{system_type}')
            
            logger.info("Analytics cache cleared successfully")
            
        except Exception as e:
            logger.error(f"Failed to clear analytics cache: {str(e)}")
