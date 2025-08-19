"""
Frontend Integration Service for ML Models

This module provides ML insights and predictions to the frontend interfaces,
connecting the AI/ML capabilities with the user interface.
"""

import logging
from typing import Dict, List, Any, Optional
from django.utils import timezone
from datetime import timedelta

from .models import MLModel, ModelPrediction
from .data_integration import ConstructionDataIntegrationService
from core.models import Project, RiskAssessment
from integrations.models import UnifiedProject

logger = logging.getLogger(__name__)


class MLFrontendIntegrationService:
    """Service for integrating ML insights with frontend interfaces"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_integration = ConstructionDataIntegrationService()
    
    def get_dashboard_ml_insights(self) -> Dict[str, Any]:
        """
        Get ML insights for the Dashboard interface
        
        Returns:
            Dictionary containing ML insights for dashboard display
        """
        try:
            insights = {
                'cost_predictions': self._get_cost_predictions_summary(),
                'risk_insights': self._get_risk_insights_summary(),
                'quality_metrics': self._get_quality_metrics_summary(),
                'safety_insights': self._get_safety_insights_summary(),
                'timeline_predictions': self._get_timeline_predictions_summary(),
                'model_performance': self._get_model_performance_summary(),
                'last_updated': timezone.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard ML insights: {str(e)}")
            return {'error': str(e)}
    
    def get_project_ml_insights(self, project_id: int) -> Dict[str, Any]:
        """
        Get ML insights for a specific project
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary containing ML insights for the project
        """
        try:
            project = Project.objects.get(id=project_id)
            
            insights = {
                'project_id': project_id,
                'project_name': project.name,
                'cost_prediction': self._get_project_cost_prediction(project),
                'timeline_prediction': self._get_project_timeline_prediction(project),
                'risk_assessment': self._get_project_risk_assessment(project),
                'quality_prediction': self._get_project_quality_prediction(project),
                'safety_prediction': self._get_project_safety_prediction(project),
                'change_order_impact': self._get_project_change_order_impact(project),
                'recommendations': self._get_project_recommendations(project),
                'last_updated': timezone.now().isoformat()
            }
            
            return insights
            
        except Project.DoesNotExist:
            return {'error': 'Project not found'}
        except Exception as e:
            self.logger.error(f"Error getting project ML insights: {str(e)}")
            return {'error': str(e)}
    
    def get_risk_analysis_ml_insights(self) -> Dict[str, Any]:
        """
        Get ML insights for the Risk Analysis interface
        
        Returns:
            Dictionary containing ML risk insights
        """
        try:
            insights = {
                'overall_risk_score': self._calculate_overall_risk_score(),
                'high_risk_projects': self._get_high_risk_projects(),
                'risk_trends': self._get_risk_trends(),
                'risk_predictions': self._get_risk_predictions(),
                'mitigation_recommendations': self._get_mitigation_recommendations(),
                'last_updated': timezone.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting risk analysis ML insights: {str(e)}")
            return {'error': str(e)}
    
    def get_reports_ml_insights(self, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Get ML insights for the Reports interface
        
        Args:
            report_type: Type of report ('comprehensive', 'cost', 'timeline', 'risk', 'quality')
            
        Returns:
            Dictionary containing ML insights for reports
        """
        try:
            if report_type == 'comprehensive':
                insights = {
                    'cost_analysis': self._get_cost_analysis_report(),
                    'timeline_analysis': self._get_timeline_analysis_report(),
                    'risk_analysis': self._get_risk_analysis_report(),
                    'quality_analysis': self._get_quality_analysis_report(),
                    'safety_analysis': self._get_safety_analysis_report(),
                    'predictions_summary': self._get_predictions_summary(),
                    'last_updated': timezone.now().isoformat()
                }
            elif report_type == 'cost':
                insights = self._get_cost_analysis_report()
            elif report_type == 'timeline':
                insights = self._get_timeline_analysis_report()
            elif report_type == 'risk':
                insights = self._get_risk_analysis_report()
            elif report_type == 'quality':
                insights = self._get_quality_analysis_report()
            else:
                insights = {'error': f'Unknown report type: {report_type}'}
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting reports ML insights: {str(e)}")
            return {'error': str(e)}
    
    # Private methods for generating specific insights
    
    def _get_cost_predictions_summary(self) -> Dict[str, Any]:
        """Get cost predictions summary for dashboard"""
        try:
            # Get active cost prediction models
            cost_models = MLModel.objects.filter(
                model_type='cost_prediction',
                status='active'
            )
            
            if not cost_models.exists():
                return {'message': 'No active cost prediction models'}
            
            # Get recent predictions
            recent_predictions = ModelPrediction.objects.filter(
                model__model_type='cost_prediction',
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:10]
            
            total_predicted_cost = sum(p.prediction_value for p in recent_predictions)
            avg_prediction_confidence = sum(p.prediction_confidence or 0 for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0
            
            return {
                'total_predicted_cost': total_predicted_cost,
                'avg_prediction_confidence': avg_prediction_confidence,
                'recent_predictions_count': len(recent_predictions),
                'active_models_count': cost_models.count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost predictions summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_risk_insights_summary(self) -> Dict[str, Any]:
        """Get risk insights summary for dashboard"""
        try:
            # Get active risk assessment models
            risk_models = MLModel.objects.filter(
                model_type='risk_assessment',
                status='active'
            )
            
            if not risk_models.exists():
                return {'message': 'No active risk assessment models'}
            
            # Get recent risk assessments
            recent_risks = RiskAssessment.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            high_risk_count = recent_risks.filter(risk_level__in=['high', 'critical']).count()
            total_risks = recent_risks.count()
            
            return {
                'high_risk_count': high_risk_count,
                'total_risks': total_risks,
                'risk_ratio': high_risk_count / total_risks if total_risks > 0 else 0,
                'active_models_count': risk_models.count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk insights summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_quality_metrics_summary(self) -> Dict[str, Any]:
        """Get quality metrics summary for dashboard"""
        try:
            # Get active quality prediction models
            quality_models = MLModel.objects.filter(
                model_type='quality_prediction',
                status='active'
            )
            
            if not quality_models.exists():
                return {'message': 'No active quality prediction models'}
            
            # Get recent quality predictions
            recent_predictions = ModelPrediction.objects.filter(
                model__model_type='quality_prediction',
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:10]
            
            avg_quality_score = sum(p.prediction_value for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0
            
            return {
                'avg_quality_score': avg_quality_score,
                'recent_predictions_count': len(recent_predictions),
                'active_models_count': quality_models.count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting quality metrics summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_safety_insights_summary(self) -> Dict[str, Any]:
        """Get safety insights summary for dashboard"""
        try:
            # Get active safety prediction models
            safety_models = MLModel.objects.filter(
                model_type='safety_prediction',
                status='active'
            )
            
            if not safety_models.exists():
                return {'message': 'No active safety prediction models'}
            
            # Get recent safety predictions
            recent_predictions = ModelPrediction.objects.filter(
                model__model_type='safety_prediction',
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:10]
            
            avg_safety_score = sum(p.prediction_value for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0
            
            return {
                'avg_safety_score': avg_safety_score,
                'recent_predictions_count': len(recent_predictions),
                'active_models_count': safety_models.count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting safety insights summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_timeline_predictions_summary(self) -> Dict[str, Any]:
        """Get timeline predictions summary for dashboard"""
        try:
            # Get active timeline prediction models
            timeline_models = MLModel.objects.filter(
                model_type='timeline_prediction',
                status='active'
            )
            
            if not timeline_models.exists():
                return {'message': 'No active timeline prediction models'}
            
            # Get recent timeline predictions
            recent_predictions = ModelPrediction.objects.filter(
                model__model_type='timeline_prediction',
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:10]
            
            avg_predicted_duration = sum(p.prediction_value for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0
            
            return {
                'avg_predicted_duration': avg_predicted_duration,
                'recent_predictions_count': len(recent_predictions),
                'active_models_count': timeline_models.count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting timeline predictions summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_model_performance_summary(self) -> Dict[str, Any]:
        """Get overall model performance summary for dashboard"""
        try:
            active_models = MLModel.objects.filter(status='active')
            
            if not active_models.exists():
                return {'message': 'No active models'}
            
            total_models = active_models.count()
            models_with_predictions = active_models.filter(predictions__isnull=False).distinct().count()
            
            # Calculate average accuracy across all models
            total_accuracy = 0
            models_with_accuracy = 0
            
            for model in active_models:
                if model.accuracy is not None:
                    total_accuracy += model.accuracy
                    models_with_accuracy += 1
            
            avg_accuracy = total_accuracy / models_with_accuracy if models_with_accuracy > 0 else 0
            
            return {
                'total_active_models': total_models,
                'models_with_predictions': models_with_predictions,
                'avg_model_accuracy': avg_accuracy,
                'prediction_coverage': models_with_predictions / total_models if total_models > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model performance summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_cost_prediction(self, project: Project) -> Dict[str, Any]:
        """Get cost prediction for a specific project"""
        try:
            # Get active cost prediction model
            cost_model = MLModel.objects.filter(
                model_type='cost_prediction',
                status='active'
            ).first()
            
            if not cost_model:
                return {'message': 'No active cost prediction model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=cost_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_cost': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': cost_model.version
                }
            else:
                return {'message': 'No cost prediction available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project cost prediction: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_timeline_prediction(self, project: Project) -> Dict[str, Any]:
        """Get timeline prediction for a specific project"""
        try:
            # Get active timeline prediction model
            timeline_model = MLModel.objects.filter(
                model_type='timeline_prediction',
                status='active'
            ).first()
            
            if not timeline_model:
                return {'message': 'No active timeline prediction model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=timeline_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_duration': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': timeline_model.version
                }
            else:
                return {'message': 'No timeline prediction available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project timeline prediction: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_risk_assessment(self, project: Project) -> Dict[str, Any]:
        """Get risk assessment for a specific project"""
        try:
            # Get active risk assessment model
            risk_model = MLModel.objects.filter(
                model_type='risk_assessment',
                status='active'
            ).first()
            
            if not risk_model:
                return {'message': 'No active risk assessment model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=risk_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_risk_level': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': risk_model.version
                }
            else:
                return {'message': 'No risk assessment available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project risk assessment: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_quality_prediction(self, project: Project) -> Dict[str, Any]:
        """Get quality prediction for a specific project"""
        try:
            # Get active quality prediction model
            quality_model = MLModel.objects.filter(
                model_type='quality_prediction',
                status='active'
            ).first()
            
            if not quality_model:
                return {'message': 'No active quality prediction model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=quality_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_quality_score': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': quality_model.version
                }
            else:
                return {'message': 'No quality prediction available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project quality prediction: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_safety_prediction(self, project: Project) -> Dict[str, Any]:
        """Get safety prediction for a specific project"""
        try:
            # Get active safety prediction model
            safety_model = MLModel.objects.filter(
                model_type='safety_prediction',
                status='active'
            ).first()
            
            if not safety_model:
                return {'message': 'No active safety prediction model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=safety_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_safety_score': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': safety_model.version
                }
            else:
                return {'message': 'No safety prediction available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project safety prediction: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_change_order_impact(self, project: Project) -> Dict[str, Any]:
        """Get change order impact prediction for a specific project"""
        try:
            # Get active change order impact model
            change_order_model = MLModel.objects.filter(
                model_type='change_order_impact',
                status='active'
            ).first()
            
            if not change_order_model:
                return {'message': 'No active change order impact model'}
            
            # Get recent prediction for this project
            recent_prediction = ModelPrediction.objects.filter(
                model=change_order_model,
                project_id=str(project.id)
            ).order_by('-created_at').first()
            
            if recent_prediction:
                return {
                    'predicted_cost_impact': recent_prediction.prediction_value,
                    'confidence': recent_prediction.prediction_confidence,
                    'prediction_date': recent_prediction.created_at.isoformat(),
                    'model_version': change_order_model.version
                }
            else:
                return {'message': 'No change order impact prediction available for this project'}
                
        except Exception as e:
            self.logger.error(f"Error getting project change order impact: {str(e)}")
            return {'error': str(e)}
    
    def _get_project_recommendations(self, project: Project) -> Dict[str, Any]:
        """Get ML-based recommendations for a specific project"""
        try:
            recommendations = []
            
            # Cost recommendations
            if project.estimated_budget and project.actual_budget:
                variance = abs(project.cost_variance_percentage or 0)
                if variance > 20:
                    recommendations.append({
                        'type': 'cost',
                        'priority': 'high',
                        'message': 'Significant cost variance detected. Review budget controls.',
                        'action': 'Implement cost monitoring and control measures'
                    })
            
            # Schedule recommendations
            if project.start_date and project.end_date:
                days_remaining = (project.end_date - timezone.now().date()).days
                if days_remaining < 30:
                    recommendations.append({
                        'type': 'schedule',
                        'priority': 'high',
                        'message': 'Project approaching deadline.',
                        'action': 'Accelerate critical path activities'
                    })
            
            # Risk recommendations
            high_risks = project.risk_assessments.filter(
                is_active=True,
                risk_level__in=['high', 'critical']
            ).count()
            
            if high_risks > 0:
                recommendations.append({
                    'type': 'risk',
                    'priority': 'high' if high_risks > 2 else 'medium',
                    'message': f'{high_risks} high-risk items identified.',
                    'action': 'Review and mitigate high-priority risks'
                })
            
            return {
                'recommendations': recommendations,
                'total_count': len(recommendations),
                'high_priority_count': len([r for r in recommendations if r['priority'] == 'high'])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting project recommendations: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_overall_risk_score(self) -> float:
        """Calculate overall risk score across all projects"""
        try:
            active_projects = Project.objects.filter(
                status__in=['planning', 'bidding', 'execution']
            )
            
            total_risk_score = 0
            project_count = 0
            
            for project in active_projects:
                risk_assessments = project.risk_assessments.filter(is_active=True)
                if risk_assessments.exists():
                    # Calculate weighted risk score for this project
                    project_risk_score = 0
                    total_weight = 0
                    
                    for risk in risk_assessments:
                        weight = risk.impact_score
                        score = float(risk.probability) / 100 * weight
                        project_risk_score += score
                        total_weight += weight
                    
                    if total_weight > 0:
                        avg_project_score = project_risk_score / total_weight
                        total_risk_score += avg_project_score
                        project_count += 1
            
            return total_risk_score / project_count if project_count > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating overall risk score: {str(e)}")
            return 0
    
    def _get_high_risk_projects(self) -> List[Dict[str, Any]]:
        """Get list of high-risk projects"""
        try:
            high_risk_projects = []
            
            active_projects = Project.objects.filter(
                status__in=['planning', 'bidding', 'execution']
            )
            
            for project in active_projects:
                risk_assessments = project.risk_assessments.filter(
                    is_active=True,
                    risk_level__in=['high', 'critical']
                )
                
                if risk_assessments.exists():
                    high_risk_projects.append({
                        'id': project.id,
                        'name': project.name,
                        'status': project.status,
                        'high_risk_count': risk_assessments.count(),
                        'overall_risk_score': self._calculate_project_risk_score(project)
                    })
            
            # Sort by risk score (highest first)
            high_risk_projects.sort(key=lambda x: x['overall_risk_score'], reverse=True)
            
            return high_risk_projects[:10]  # Return top 10
            
        except Exception as e:
            self.logger.error(f"Error getting high-risk projects: {str(e)}")
            return []
    
    def _calculate_project_risk_score(self, project: Project) -> float:
        """Calculate risk score for a specific project"""
        try:
            risk_assessments = project.risk_assessments.filter(is_active=True)
            
            if not risk_assessments.exists():
                return 0
            
            total_score = 0
            total_weight = 0
            
            for risk in risk_assessments:
                weight = risk.impact_score
                score = float(risk.probability) / 100 * weight
                total_score += score
                total_weight += weight
            
            return total_score / total_weight if total_weight > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating project risk score: {str(e)}")
            return 0
    
    def _get_risk_trends(self) -> Dict[str, Any]:
        """Get risk trends over time"""
        try:
            # Get risk assessments over the last 90 days
            end_date = timezone.now()
            start_date = end_date - timedelta(days=90)
            
            risk_assessments = RiskAssessment.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            # Group by week
            weekly_risks = {}
            current_date = start_date
            
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                week_key = week_start.strftime('%Y-%W')
                
                weekly_risks[week_key] = {
                    'total': 0,
                    'high': 0,
                    'critical': 0
                }
                
                current_date += timedelta(days=7)
            
            # Count risks by week
            for risk in risk_assessments:
                week_start = risk.created_at.date() - timedelta(days=risk.created_at.date().weekday())
                week_key = week_start.strftime('%Y-%W')
                
                if week_key in weekly_risks:
                    weekly_risks[week_key]['total'] += 1
                    if risk.risk_level in ['high', 'critical']:
                        weekly_risks[week_key]['high'] += 1
                    if risk.risk_level == 'critical':
                        weekly_risks[week_key]['critical'] += 1
            
            return {
                'weekly_trends': weekly_risks,
                'total_risks': risk_assessments.count(),
                'high_critical_ratio': sum(w['high'] for w in weekly_risks.values()) / sum(w['total'] for w in weekly_risks.values()) if any(w['total'] > 0 for w in weekly_risks.values()) else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk trends: {str(e)}")
            return {'error': str(e)}
    
    def _get_risk_predictions(self) -> Dict[str, Any]:
        """Get risk predictions from ML models"""
        try:
            # Get active risk assessment models
            risk_models = MLModel.objects.filter(
                model_type='risk_assessment',
                status='active'
            )
            
            if not risk_models.exists():
                return {'message': 'No active risk assessment models'}
            
            # Get recent predictions
            recent_predictions = ModelPrediction.objects.filter(
                model__model_type='risk_assessment',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-created_at')[:20]
            
            predictions_summary = {
                'total_predictions': len(recent_predictions),
                'avg_confidence': sum(p.prediction_confidence or 0 for p in recent_predictions) / len(recent_predictions) if recent_predictions else 0,
                'risk_level_distribution': {}
            }
            
            # Count predictions by risk level
            for prediction in recent_predictions:
                risk_level = int(prediction.prediction_value)
                risk_level_key = f'level_{risk_level}'
                predictions_summary['risk_level_distribution'][risk_level_key] = predictions_summary['risk_level_distribution'].get(risk_level_key, 0) + 1
            
            return predictions_summary
            
        except Exception as e:
            self.logger.error(f"Error getting risk predictions: {str(e)}")
            return {'error': str(e)}
    
    def _get_mitigation_recommendations(self) -> List[Dict[str, Any]]:
        """Get ML-based mitigation recommendations"""
        try:
            recommendations = []
            
            # Get high-risk projects
            high_risk_projects = self._get_high_risk_projects()
            
            for project_data in high_risk_projects[:5]:  # Top 5 high-risk projects
                project = Project.objects.get(id=project_data['id'])
                
                # Get specific risks for this project
                high_risks = project.risk_assessments.filter(
                    is_active=True,
                    risk_level__in=['high', 'critical']
                )
                
                for risk in high_risks[:3]:  # Top 3 risks per project
                    recommendations.append({
                        'project_name': project.name,
                        'risk_title': risk.title,
                        'risk_level': risk.risk_level,
                        'probability': risk.probability,
                        'impact_score': risk.impact_score,
                        'mitigation_strategy': risk.mitigation_strategy or 'Implement risk mitigation measures',
                        'priority': 'critical' if risk.risk_level == 'critical' else 'high'
                    })
            
            # Sort by priority and probability
            recommendations.sort(key=lambda x: (x['priority'] == 'critical', x['probability']), reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting mitigation recommendations: {str(e)}")
            return []
    
    # Report generation methods
    
    def _get_cost_analysis_report(self) -> Dict[str, Any]:
        """Generate cost analysis report"""
        try:
            # Get cost-related data
            projects = Project.objects.filter(
                estimated_budget__isnull=False,
                actual_budget__isnull=False
            )
            
            total_estimated = sum(float(p.estimated_budget) for p in projects)
            total_actual = sum(float(p.actual_budget) for p in projects)
            total_variance = total_actual - total_estimated
            
            # Get cost predictions
            cost_predictions = self._get_cost_predictions_summary()
            
            return {
                'total_estimated_budget': total_estimated,
                'total_actual_budget': total_actual,
                'total_variance': total_variance,
                'variance_percentage': (total_variance / total_estimated * 100) if total_estimated > 0 else 0,
                'project_count': projects.count(),
                'cost_predictions': cost_predictions
            }
            
        except Exception as e:
            self.logger.error(f"Error generating cost analysis report: {str(e)}")
            return {'error': str(e)}
    
    def _get_timeline_analysis_report(self) -> Dict[str, Any]:
        """Generate timeline analysis report"""
        try:
            # Get timeline-related data
            projects = Project.objects.filter(
                start_date__isnull=False,
                end_date__isnull=False,
                estimated_duration_days__isnull=False
            )
            
            total_estimated_days = sum(p.estimated_duration_days for p in projects)
            total_actual_days = sum((p.end_date - p.start_date).days for p in projects)
            total_variance = total_actual_days - total_estimated_days
            
            # Get timeline predictions
            timeline_predictions = self._get_timeline_predictions_summary()
            
            return {
                'total_estimated_days': total_estimated_days,
                'total_actual_days': total_actual_days,
                'total_variance': total_variance,
                'variance_percentage': (total_variance / total_estimated_days * 100) if total_estimated_days > 0 else 0,
                'project_count': projects.count(),
                'timeline_predictions': timeline_predictions
            }
            
        except Exception as e:
            self.logger.error(f"Error generating timeline analysis report: {str(e)}")
            return {'error': str(e)}
    
    def _get_risk_analysis_report(self) -> Dict[str, Any]:
        """Generate risk analysis report"""
        try:
            # Get risk-related data
            risk_assessments = RiskAssessment.objects.filter(is_active=True)
            
            risk_distribution = {
                'low': risk_assessments.filter(risk_level='low').count(),
                'medium': risk_assessments.filter(risk_level='medium').count(),
                'high': risk_assessments.filter(risk_level='high').count(),
                'critical': risk_assessments.filter(risk_level='critical').count()
            }
            
            # Get risk insights
            risk_insights = self._get_risk_insights_summary()
            
            return {
                'total_risks': risk_assessments.count(),
                'risk_distribution': risk_distribution,
                'high_critical_count': risk_distribution['high'] + risk_distribution['critical'],
                'risk_insights': risk_insights
            }
            
        except Exception as e:
            self.logger.error(f"Error generating risk analysis report: {str(e)}")
            return {'error': str(e)}
    
    def _get_quality_analysis_report(self) -> Dict[str, Any]:
        """Generate quality analysis report"""
        try:
            # Get quality-related data
            quality_predictions = self._get_quality_metrics_summary()
            
            return {
                'quality_metrics': quality_predictions,
                'quality_trends': 'Stable',  # Placeholder - could be enhanced with historical data
                'recommendations': [
                    'Monitor quality metrics regularly',
                    'Implement quality control measures',
                    'Review supplier performance'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating quality analysis report: {str(e)}")
            return {'error': str(e)}
    
    def _get_safety_analysis_report(self) -> Dict[str, Any]:
        """Generate safety analysis report"""
        try:
            # Get safety-related data
            safety_predictions = self._get_safety_insights_summary()
            
            return {
                'safety_metrics': safety_predictions,
                'safety_trends': 'Improving',  # Placeholder - could be enhanced with historical data
                'recommendations': [
                    'Maintain safety protocols',
                    'Conduct regular safety audits',
                    'Provide safety training'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating safety analysis report: {str(e)}")
            return {'error': str(e)}
    
    def _get_predictions_summary(self) -> Dict[str, Any]:
        """Get summary of all ML predictions"""
        try:
            # Get all recent predictions
            recent_predictions = ModelPrediction.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            predictions_by_type = {}
            for prediction in recent_predictions:
                model_type = prediction.model.model_type
                if model_type not in predictions_by_type:
                    predictions_by_type[model_type] = []
                
                predictions_by_type[model_type].append({
                    'value': prediction.prediction_value,
                    'confidence': prediction.prediction_confidence,
                    'created_at': prediction.created_at.isoformat()
                })
            
            return {
                'total_predictions': recent_predictions.count(),
                'predictions_by_type': predictions_by_type,
                'avg_confidence': sum(p.prediction_confidence or 0 for p in recent_predictions) / recent_predictions.count() if recent_predictions.exists() else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting predictions summary: {str(e)}")
            return {'error': str(e)}
