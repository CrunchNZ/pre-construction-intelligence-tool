"""
Celery tasks for AI Models

This module provides asynchronous tasks for:
- Model training
- Batch predictions
- Model evaluation
- Performance monitoring
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import pandas as pd
import numpy as np
from typing import Dict, List, Any

from .models import MLModel, ModelTrainingHistory, ModelPrediction
from .ml_pipeline import MLPipelineService
from .data_integration import ConstructionDataIntegrationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def train_model_task(self, model_id: int, training_data_path: str = None):
    """
    Asynchronous task for training ML models
    
    Args:
        model_id: ID of the ML model to train
        training_data_path: Optional path to training data file
    """
    
    logger.info(f"Starting model training task for model {model_id}")
    
    try:
        # Get the model
        model = MLModel.objects.get(id=model_id)
        
        # Update model status
        model.status = 'training'
        model.save()
        
        # Initialize ML pipeline service
        ml_service = MLPipelineService()
        
        # Load training data
        if training_data_path:
            # Load from file path
            training_data = pd.read_csv(training_data_path)
        else:
            # Use data integration service to get real construction data
            data_integration = ConstructionDataIntegrationService()
            
            if model.model_type == 'cost_prediction':
                training_data = data_integration.get_cost_prediction_training_data()
            elif model.model_type == 'timeline_prediction':
                training_data = data_integration.get_timeline_prediction_training_data()
            elif model.model_type == 'risk_assessment':
                training_data = data_integration.get_risk_assessment_training_data()
            elif model.model_type == 'quality_prediction':
                training_data = data_integration.get_quality_prediction_training_data()
            elif model.model_type == 'safety_prediction':
                training_data = data_integration.get_safety_prediction_training_data()
            elif model.model_type == 'change_order_impact':
                training_data = data_integration.get_change_order_impact_training_data()
            else:
                # Fallback to sample data for unknown model types
                training_data = create_sample_training_data(model)
        
        # Train the model
        result = ml_service.train_model(
            model_id=model_id,
            training_data=training_data,
            feature_columns=model.feature_columns,
            target_column=model.target_column,
            algorithm=model.algorithm,
            hyperparameters=model.hyperparameters
        )
        
        if result['success']:
            logger.info(f"Model training completed successfully for model {model_id}")
            
            # Update training history status
            if 'training_history_id' in result:
                training_history = ModelTrainingHistory.objects.get(
                    id=result['training_history_id']
                )
                training_history.status = 'completed'
                training_history.save()
            
        else:
            logger.error(f"Model training failed for model {model_id}: {result['error']}")
            
            # Update model status to failed
            model.status = 'failed'
            model.save()
            
            # Update training history status
            training_history = ModelTrainingHistory.objects.filter(
                model=model,
                status='running'
            ).first()
            if training_history:
                training_history.status = 'failed'
                training_history.error_message = result['error']
                training_history.save()
            
            # Retry the task
            raise self.retry(countdown=60, exc=Exception(result['error']))
            
    except MLModel.DoesNotExist:
        logger.error(f"Model {model_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in training task for model {model_id}: {str(exc)}")
        
        # Update model status to failed
        try:
            model = MLModel.objects.get(id=model_id)
            model.status = 'failed'
            model.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def batch_prediction_task(self, model_id: int, input_data: List[Dict[str, Any]], 
                         project_id: str = None, user_id: str = None):
    """
    Asynchronous task for batch predictions
    
    Args:
        model_id: ID of the ML model to use
        input_data: List of input feature dictionaries
        project_id: Optional project identifier
        user_id: Optional user identifier
    """
    
    logger.info(f"Starting batch prediction task for model {model_id} with {len(input_data)} inputs")
    
    try:
        # Get the model
        model = MLModel.objects.get(id=model_id, status='active')
        
        # Initialize ML pipeline service
        ml_service = MLPipelineService()
        
        predictions = []
        
        for i, input_features in enumerate(input_data):
            try:
                # Make prediction
                result = ml_service.make_prediction(
                    model_id=model_id,
                    input_features=input_features,
                    include_confidence=True,
                    include_intervals=True
                )
                
                if result['success']:
                    # Store prediction in database
                    prediction = ModelPrediction.objects.create(
                        model=model,
                        input_features=input_features,
                        input_data_hash=f"batch_{model_id}_{i}_{int(timezone.now().timestamp())}",
                        prediction_value=result['prediction'],
                        prediction_confidence=result['confidence'],
                        prediction_interval_lower=result['interval_lower'],
                        prediction_interval_upper=result['interval_upper'],
                        project_id=project_id or '',
                        user_id=user_id or ''
                    )
                    
                    predictions.append({
                        'input_features': input_features,
                        'prediction': result['prediction'],
                        'confidence': result['confidence'],
                        'prediction_id': prediction.id
                    })
                else:
                    logger.warning(f"Prediction failed for input {i}: {result['error']}")
                    predictions.append({
                        'input_features': input_features,
                        'error': result['error']
                    })
                    
            except Exception as e:
                logger.error(f"Error processing input {i}: {str(e)}")
                predictions.append({
                    'input_features': input_features,
                    'error': str(e)
                })
        
        logger.info(f"Batch prediction completed for model {model_id}. "
                   f"Successfully processed {len([p for p in predictions if 'prediction' in p])} predictions")
        
        return {
            'success': True,
            'total_inputs': len(input_data),
            'successful_predictions': len([p for p in predictions if 'prediction' in p]),
            'failed_predictions': len([p for p in predictions if 'error' in p]),
            'predictions': predictions
        }
        
    except MLModel.DoesNotExist:
        logger.error(f"Model {model_id} not found or not active")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in batch prediction task for model {model_id}: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def evaluate_model_task(self, model_id: int, test_data_path: str = None):
    """
    Asynchronous task for model evaluation
    
    Args:
        model_id: ID of the ML model to evaluate
        test_data_path: Optional path to test data file
    """
    
    logger.info(f"Starting model evaluation task for model {model_id}")
    
    try:
        # Get the model
        model = MLModel.objects.get(id=model_id, status='active')
        
        # Initialize ML pipeline service
        ml_service = MLPipelineService()
        
        # Load test data
        if test_data_path:
            # Load from file path
            test_data = pd.read_csv(test_data_path)
        else:
            # Use data integration service to get real construction data
            data_integration = ConstructionDataIntegrationService()
            
            if model.model_type == 'cost_prediction':
                test_data = data_integration.get_cost_prediction_training_data()
            elif model.model_type == 'timeline_prediction':
                test_data = data_integration.get_timeline_prediction_training_data()
            elif model.model_type == 'risk_assessment':
                test_data = data_integration.get_risk_assessment_training_data()
            elif model.model_type == 'quality_prediction':
                test_data = data_integration.get_quality_prediction_training_data()
            elif model.model_type == 'safety_prediction':
                test_data = data_integration.get_safety_prediction_training_data()
            elif model.model_type == 'change_order_impact':
                test_data = data_integration.get_change_order_impact_training_data()
            else:
                # Fallback to sample data for unknown model types
                test_data = create_sample_test_data(model)
        
        # Evaluate the model
        result = ml_service.evaluate_model(
            model_id=model_id,
            test_data=test_data,
            feature_columns=model.feature_columns,
            target_column=model.target_column
        )
        
        if result['success']:
            logger.info(f"Model evaluation completed successfully for model {model_id}")
            
            # Update model performance metrics if they're better
            metrics = result['metrics']
            updated = False
            
            for metric_name, metric_value in metrics.items():
                if hasattr(model, metric_name):
                    current_value = getattr(model, metric_name)
                    if current_value is None or metric_value > current_value:
                        setattr(model, metric_name, metric_value)
                        updated = True
            
            if updated:
                model.save()
                logger.info(f"Updated performance metrics for model {model_id}")
            
            return result
        else:
            logger.error(f"Model evaluation failed for model {model_id}: {result['error']}")
            raise self.retry(countdown=60, exc=Exception(result['error']))
            
    except MLModel.DoesNotExist:
        logger.error(f"Model {model_id} not found or not active")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in evaluation task for model {model_id}: {str(exc)}")
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True)
def monitor_model_performance_task(self, model_id: int = None):
    """
    Asynchronous task for monitoring model performance
    
    Args:
        model_id: Optional specific model ID to monitor. If None, monitor all active models.
    """
    
    logger.info(f"Starting model performance monitoring task")
    
    try:
        # Initialize ML pipeline service
        ml_service = MLPipelineService()
        
        if model_id:
            # Monitor specific model
            models = [MLModel.objects.get(id=model_id)]
        else:
            # Monitor all active models
            models = MLModel.objects.filter(status='active')
        
        monitoring_results = []
        
        for model in models:
            try:
                # Get performance summary
                summary = ml_service.get_model_performance_summary(model.id)
                
                if summary.get('success', False):
                    monitoring_results.append({
                        'model_id': model.id,
                        'model_name': model.name,
                        'status': 'monitored',
                        'summary': summary
                    })
                    
                    # Check for performance degradation
                    if should_alert_performance_degradation(summary):
                        logger.warning(f"Performance degradation detected for model {model.name}")
                        # TODO: Send alert notification
                        
                else:
                    monitoring_results.append({
                        'model_id': model.id,
                        'model_name': model.name,
                        'status': 'error',
                        'error': summary.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"Error monitoring model {model.id}: {str(e)}")
                monitoring_results.append({
                    'model_id': model.id,
                    'model_name': getattr(model, 'name', 'Unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        logger.info(f"Model performance monitoring completed. "
                   f"Monitored {len(monitoring_results)} models")
        
        return {
            'success': True,
            'monitoring_results': monitoring_results,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Unexpected error in performance monitoring task: {str(exc)}")
        raise


@shared_task(bind=True)
def cleanup_old_predictions_task(self, days_to_keep: int = 90):
    """
    Asynchronous task for cleaning up old predictions
    
    Args:
        days_to_keep: Number of days to keep predictions
    """
    
    logger.info(f"Starting cleanup of predictions older than {days_to_keep} days")
    
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        # Delete old predictions
        deleted_count, _ = ModelPrediction.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old predictions")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Error in cleanup task: {str(exc)}")
        raise


def create_sample_training_data(model: MLModel) -> pd.DataFrame:
    """Create sample training data for testing purposes"""
    
    np.random.seed(42)
    n_samples = 1000
    
    if model.model_type == 'cost_prediction':
        # Generate sample construction cost data
        area = np.random.uniform(100, 10000, n_samples)
        complexity = np.random.choice(['low', 'medium', 'high'], n_samples)
        location = np.random.choice(['urban', 'suburban', 'rural'], n_samples)
        
        # Generate target cost based on features
        base_cost = area * 150  # Base cost per square foot
        complexity_multiplier = {'low': 1.0, 'medium': 1.3, 'high': 1.8}
        location_multiplier = {'urban': 1.4, 'suburban': 1.1, 'rural': 0.9}
        
        cost = []
        for i in range(n_samples):
            total_cost = base_cost[i] * complexity_multiplier[complexity[i]] * location_multiplier[location[i]]
            # Add some noise
            total_cost += np.random.normal(0, total_cost * 0.1)
            cost.append(max(0, total_cost))
        
        return pd.DataFrame({
            'area': area,
            'complexity': complexity,
            'location': location,
            'cost': cost
        })
    
    elif model.model_type == 'timeline_prediction':
        # Generate sample timeline data
        scope = np.random.uniform(1, 100, n_samples)
        team_size = np.random.randint(1, 20, n_samples)
        complexity = np.random.choice(['low', 'medium', 'high'], n_samples)
        
        # Generate target timeline based on features
        base_timeline = scope * 0.5 + team_size * 2
        complexity_multiplier = {'low': 0.8, 'medium': 1.0, 'high': 1.5}
        
        timeline = []
        for i in range(n_samples):
            total_timeline = base_timeline[i] * complexity_multiplier[complexity[i]]
            # Add some noise
            total_timeline += np.random.normal(0, total_timeline * 0.15)
            timeline.append(max(1, total_timeline))
        
        return pd.DataFrame({
            'scope': scope,
            'team_size': team_size,
            'complexity': complexity,
            'timeline': timeline
        })
    
    else:
        # Default sample data
        feature1 = np.random.normal(0, 1, n_samples)
        feature2 = np.random.normal(0, 1, n_samples)
        target = feature1 * 2 + feature2 * 3 + np.random.normal(0, 0.5, n_samples)
        
        return pd.DataFrame({
            'feature1': feature1,
            'feature2': feature2,
            'target': target
        })


def create_sample_test_data(model: MLModel) -> pd.DataFrame:
    """Create sample test data for testing purposes"""
    
    # Use the same logic as training data but with fewer samples
    training_data = create_sample_training_data(model)
    return training_data.sample(n=min(200, len(training_data)), random_state=42)


def should_alert_performance_degradation(summary: Dict[str, Any]) -> bool:
    """Check if performance degradation should trigger an alert"""
    
    # Simple threshold-based alerting
    # In production, this could be more sophisticated (e.g., statistical process control)
    
    performance_metrics = summary.get('performance_metrics', {})
    
    # Check accuracy degradation
    if 'accuracy' in performance_metrics:
        accuracy = performance_metrics['accuracy']
        if accuracy is not None and accuracy < 0.7:  # Threshold: 70%
            return True
    
    # Check MAE degradation for regression models
    if 'mae' in performance_metrics:
        mae = performance_metrics['mae']
        if mae is not None and mae > 1000:  # Threshold: 1000
            return True
    
    # Check recent accuracy degradation
    recent_accuracy = summary.get('recent_accuracy')
    if recent_accuracy is not None and recent_accuracy < 0.6:  # Threshold: 60%
        return True
    
    return False
