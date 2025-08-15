"""
Core tasks for the Pre-Construction Intelligence Tool.

This module contains Celery tasks for core functionality
such as data cleanup, maintenance, and system health checks.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from .models import Project, Supplier, HistoricalData, RiskAssessment

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def cleanup_old_data(self):
    """
    Clean up old data to maintain system performance.
    
    This task removes old historical data, completed projects,
    and inactive risk assessments to keep the database lean.
    """
    try:
        logger.info("Starting data cleanup task")
        
        # Calculate cutoff dates
        now = timezone.now()
        historical_cutoff = now - timedelta(days=365)  # 1 year
        project_cutoff = now - timedelta(days=730)     # 2 years
        risk_cutoff = now - timedelta(days=180)        # 6 months
        
        # Clean up old historical data
        old_historical = HistoricalData.objects.filter(
            data_date__lt=historical_cutoff,
            is_processed=True
        )
        historical_count = old_historical.count()
        old_historical.delete()
        logger.info(f"Deleted {historical_count} old historical data records")
        
        # Clean up old completed projects (keep for 2 years)
        old_projects = Project.objects.filter(
            status='completed',
            end_date__lt=project_cutoff
        )
        project_count = old_projects.count()
        old_projects.delete()
        logger.info(f"Deleted {project_count} old completed projects")
        
        # Clean up old inactive risk assessments
        old_risks = RiskAssessment.objects.filter(
            is_active=False,
            updated_at__lt=risk_cutoff
        )
        risk_count = old_risks.count()
        old_risks.delete()
        logger.info(f"Deleted {risk_count} old inactive risk assessments")
        
        # Clean up suppliers with no recent activity
        inactive_suppliers = Supplier.objects.filter(
            is_active=True,
            projects__isnull=True,
            updated_at__lt=now - timedelta(days=365)
        )
        supplier_count = inactive_suppliers.count()
        inactive_suppliers.update(is_active=False)
        logger.info(f"Deactivated {supplier_count} inactive suppliers")
        
        total_cleaned = historical_count + project_count + risk_count
        logger.info(f"Data cleanup completed. Total records cleaned: {total_cleaned}")
        
        return {
            'historical_data_deleted': historical_count,
            'projects_deleted': project_count,
            'risks_deleted': risk_count,
            'suppliers_deactivated': supplier_count,
            'total_cleaned': total_cleaned
        }
        
    except Exception as exc:
        logger.error(f"Data cleanup task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry in 5 minutes


@shared_task(bind=True, max_retries=3)
def recalculate_supplier_scores(self):
    """
    Recalculate supplier performance scores based on recent data.
    
    This task updates supplier scores based on their performance
    in recent projects and historical data.
    """
    try:
        logger.info("Starting supplier score recalculation task")
        
        updated_count = 0
        suppliers = Supplier.objects.filter(is_active=True)
        
        for supplier in suppliers:
            try:
                old_score = supplier.overall_score
                new_score = supplier.calculate_overall_score()
                
                if old_score != new_score:
                    updated_count += 1
                    logger.debug(f"Updated supplier {supplier.name}: {old_score} -> {new_score}")
                    
            except Exception as e:
                logger.warning(f"Failed to update score for supplier {supplier.id}: {str(e)}")
                continue
        
        logger.info(f"Supplier score recalculation completed. Updated {updated_count} suppliers")
        
        return {
            'suppliers_processed': suppliers.count(),
            'suppliers_updated': updated_count
        }
        
    except Exception as exc:
        logger.error(f"Supplier score recalculation task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=600)  # Retry in 10 minutes


@shared_task(bind=True, max_retries=3)
def update_project_metrics(self):
    """
    Update project metrics and calculations.
    
    This task recalculates cost variances, updates project statuses,
    and refreshes project-related metrics.
    """
    try:
        logger.info("Starting project metrics update task")
        
        updated_projects = 0
        updated_risks = 0
        
        # Update active projects
        active_projects = Project.objects.filter(
            status__in=['planning', 'bidding', 'execution']
        )
        
        for project in active_projects:
            try:
                # Recalculate cost variance
                old_variance = project.cost_variance
                new_variance = project.calculate_cost_variance()
                
                if old_variance != new_variance:
                    updated_projects += 1
                    logger.debug(f"Updated cost variance for project {project.name}: {old_variance} -> {new_variance}")
                
                # Update project status based on dates
                if project.end_date and project.end_date <= timezone.now().date():
                    if project.status != 'completed':
                        project.status = 'completed'
                        project.save()
                        logger.info(f"Updated project {project.name} status to completed")
                
            except Exception as e:
                logger.warning(f"Failed to update project {project.id}: {str(e)}")
                continue
        
        # Update risk assessment probabilities based on project progress
        active_risks = RiskAssessment.objects.filter(
            is_active=True,
            project__status__in=['planning', 'bidding', 'execution']
        )
        
        for risk in active_risks:
            try:
                # Adjust probability based on project progress
                project = risk.project
                if project.start_date and project.start_date <= timezone.now().date():
                    # Reduce probability as project progresses
                    if risk.probability > 20:
                        risk.probability = max(20, risk.probability - 5)
                        risk.save()
                        updated_risks += 1
                        logger.debug(f"Updated risk probability for {risk.title}: {risk.probability}")
                        
            except Exception as e:
                logger.warning(f"Failed to update risk {risk.id}: {str(e)}")
                continue
        
        logger.info(f"Project metrics update completed. Projects: {updated_projects}, Risks: {updated_risks}")
        
        return {
            'projects_processed': active_projects.count(),
            'projects_updated': updated_projects,
            'risks_processed': active_risks.count(),
            'risks_updated': updated_risks
        }
        
    except Exception as exc:
        logger.error(f"Project metrics update task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=900)  # Retry in 15 minutes


@shared_task(bind=True, max_retries=3)
def system_health_check(self):
    """
    Perform system health check and report issues.
    
    This task checks various system components and reports
    any issues or anomalies that need attention.
    """
    try:
        logger.info("Starting system health check task")
        
        health_report = {
            'timestamp': timezone.now().isoformat(),
            'status': 'healthy',
            'issues': [],
            'metrics': {}
        }
        
        # Check database connectivity and basic queries
        try:
            total_projects = Project.objects.count()
            total_suppliers = Supplier.objects.count()
            total_risks = RiskAssessment.objects.filter(is_active=True).count()
            
            health_report['metrics'] = {
                'total_projects': total_projects,
                'total_suppliers': total_suppliers,
                'total_active_risks': total_risks
            }
            
        except Exception as e:
            health_report['status'] = 'critical'
            health_report['issues'].append(f"Database connectivity issue: {str(e)}")
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check for data anomalies
        try:
            # Projects with extreme cost variances
            extreme_variances = Project.objects.filter(
                cost_variance_percentage__gt=50
            ).count()
            
            if extreme_variances > 0:
                health_report['issues'].append(f"Found {extreme_variances} projects with >50% cost variance")
            
            # Suppliers with very low scores
            low_score_suppliers = Supplier.objects.filter(
                overall_score__lt=30,
                is_active=True
            ).count()
            
            if low_score_suppliers > 0:
                health_report['issues'].append(f"Found {low_score_suppliers} suppliers with very low scores")
            
            # High-risk projects without mitigation
            unmitigated_high_risks = RiskAssessment.objects.filter(
                risk_level__in=['high', 'critical'],
                is_active=True,
                mitigation_strategy=''
            ).count()
            
            if unmitigated_high_risks > 0:
                health_report['issues'].append(f"Found {unmitigated_high_risks} high-risk items without mitigation")
                
        except Exception as e:
            health_report['issues'].append(f"Data anomaly check failed: {str(e)}")
            logger.error(f"Data anomaly check failed: {str(e)}")
        
        # Update status based on issues
        if len(health_report['issues']) > 5:
            health_report['status'] = 'critical'
        elif len(health_report['issues']) > 2:
            health_report['status'] = 'warning'
        
        logger.info(f"System health check completed. Status: {health_report['status']}")
        
        return health_report
        
    except Exception as exc:
        logger.error(f"System health check task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=1800)  # Retry in 30 minutes


@shared_task(bind=True, max_retries=3)
def generate_system_report(self):
    """
    Generate comprehensive system report for monitoring.
    
    This task creates a detailed report of system status,
    performance metrics, and recommendations.
    """
    try:
        logger.info("Starting system report generation task")
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'summary': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        # Generate summary statistics
        try:
            report['summary'] = {
                'total_projects': Project.objects.count(),
                'active_projects': Project.objects.filter(status__in=['planning', 'bidding', 'execution']).count(),
                'completed_projects': Project.objects.filter(status='completed').count(),
                'total_suppliers': Supplier.objects.count(),
                'active_suppliers': Supplier.objects.filter(is_active=True).count(),
                'total_risks': RiskAssessment.objects.count(),
                'active_risks': RiskAssessment.objects.filter(is_active=True).count(),
                'high_risks': RiskAssessment.objects.filter(risk_level__in=['high', 'critical'], is_active=True).count()
            }
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
        
        # Generate performance metrics
        try:
            # Cost variance analysis
            cost_variance_stats = Project.objects.filter(
                cost_variance__isnull=False
            ).aggregate(
                avg_variance=Avg('cost_variance_percentage'),
                max_variance=Max('cost_variance_percentage'),
                min_variance=Min('cost_variance_percentage')
            )
            
            report['performance_metrics']['cost_variance'] = cost_variance_stats
            
            # Supplier performance analysis
            supplier_stats = Supplier.objects.filter(
                overall_score__isnull=False
            ).aggregate(
                avg_score=Avg('overall_score'),
                max_score=Max('overall_score'),
                min_score=Min('overall_score')
            )
            
            report['performance_metrics']['supplier_performance'] = supplier_stats
            
        except Exception as e:
            logger.error(f"Failed to generate performance metrics: {str(e)}")
        
        # Generate recommendations
        try:
            # Check for projects with high cost variances
            high_variance_projects = Project.objects.filter(
                cost_variance_percentage__gt=25
            ).count()
            
            if high_variance_projects > 0:
                report['recommendations'].append({
                    'type': 'cost_management',
                    'priority': 'high',
                    'message': f'Review {high_variance_projects} projects with >25% cost variance',
                    'action': 'Analyze cost overruns and implement corrective measures'
                })
            
            # Check for suppliers with low scores
            low_score_suppliers = Supplier.objects.filter(
                overall_score__lt=40,
                is_active=True
            ).count()
            
            if low_score_suppliers > 0:
                report['recommendations'].append({
                    'type': 'supplier_management',
                    'priority': 'medium',
                    'message': f'Review {low_score_suppliers} suppliers with scores <40',
                    'action': 'Evaluate supplier performance and consider alternatives'
                })
            
            # Check for unmitigated high risks
            unmitigated_risks = RiskAssessment.objects.filter(
                risk_level__in=['high', 'critical'],
                is_active=True,
                mitigation_strategy=''
            ).count()
            
            if unmitigated_risks > 0:
                report['recommendations'].append({
                    'type': 'risk_management',
                    'priority': 'critical',
                    'message': f'Address {unmitigated_risks} high-risk items without mitigation',
                    'action': 'Develop and implement mitigation strategies immediately'
                })
                
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
        
        logger.info("System report generation completed")
        
        return report
        
    except Exception as exc:
        logger.error(f"System report generation task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=3600)  # Retry in 1 hour
