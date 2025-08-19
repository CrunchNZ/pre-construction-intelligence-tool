"""
ML Model Management Service

This module provides comprehensive model management including:
- Model lifecycle management
- Versioning and deployment
- Performance monitoring
- A/B testing capabilities
"""

import os
import json
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import MLModel, ModelTrainingHistory, ModelPrediction
from .ml_pipeline import MLPipelineService

logger = logging.getLogger(__name__)


class MLModelManager:
    """Comprehensive ML model management service"""
    
    def __init__(self):
        self.ml_service = MLPipelineService()
        self.models_dir = getattr(settings, 'ML_MODELS_DIR', 'ml_models')
        self.backup_dir = os.path.join(self.models_dir, 'backups')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_model(self, model_data: Dict[str, Any], user) -> Tuple[bool, str, Optional[MLModel]]:
        """
        Create a new ML model
        
        Args:
            model_data: Model configuration data
            user: User creating the model
            
        Returns:
            Tuple of (success, message, model_instance)
        """
        
        try:
            with transaction.atomic():
                # Validate model data
                validation_result = self.validate_model_config(model_data)
                if not validation_result['is_valid']:
                    return False, f"Invalid model configuration: {validation_result['errors']}", None
                
                # Create model instance
                model = MLModel.objects.create(
                    name=model_data['name'],
                    model_type=model_data['model_type'],
                    version=model_data.get('version', '1.0.0'),
                    description=model_data.get('description', ''),
                    algorithm=model_data['algorithm'],
                    hyperparameters=model_data.get('hyperparameters', {}),
                    feature_columns=model_data['feature_columns'],
                    target_column=model_data['target_column'],
                    created_by=user,
                    status='draft'
                )
                
                logger.info(f"Created new ML model: {model.name} (ID: {model.id})")
                return True, "Model created successfully", model
                
        except Exception as e:
            logger.error(f"Failed to create model: {str(e)}")
            return False, f"Failed to create model: {str(e)}", None
    
    def validate_model_config(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model configuration data"""
        
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'model_type', 'algorithm', 'feature_columns', 'target_column']
        for field in required_fields:
            if field not in model_data or not model_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate model type
        valid_model_types = [choice[0] for choice in MLModel.MODEL_TYPES]
        if 'model_type' in model_data and model_data['model_type'] not in valid_model_types:
            errors.append(f"Invalid model type. Must be one of: {valid_model_types}")
        
        # Validate algorithm
        valid_algorithms = ['Random Forest', 'Random Forest Classifier', 'Linear Regression', 'Logistic Regression']
        if 'algorithm' in model_data and model_data['algorithm'] not in valid_algorithms:
            errors.append(f"Invalid algorithm. Must be one of: {valid_algorithms}")
        
        # Validate feature columns
        if 'feature_columns' in model_data:
            if not isinstance(model_data['feature_columns'], list) or len(model_data['feature_columns']) == 0:
                errors.append("Feature columns must be a non-empty list")
        
        # Validate hyperparameters
        if 'hyperparameters' in model_data and not isinstance(model_data['hyperparameters'], dict):
            errors.append("Hyperparameters must be a dictionary")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def update_model(self, model_id: int, update_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update an existing ML model
        
        Args:
            model_id: ID of the model to update
            update_data: Data to update
            
        Returns:
            Tuple of (success, message)
        """
        
        try:
            with transaction.atomic():
                model = MLModel.objects.get(id=model_id)
                
                # Check if model can be updated
                if model.status == 'training':
                    return False, "Cannot update model while it's training"
                
                if model.status == 'active' and 'algorithm' in update_data:
                    return False, "Cannot change algorithm of active model"
                
                # Update fields
                for field, value in update_data.items():
                    if hasattr(model, field) and field not in ['id', 'created_by', 'created_at']:
                        setattr(model, field, value)
                
                model.save()
                
                logger.info(f"Updated model {model.name} (ID: {model.id})")
                return True, "Model updated successfully"
                
        except MLModel.DoesNotExist:
            return False, "Model not found"
        except Exception as e:
            logger.error(f"Failed to update model {model_id}: {str(e)}")
            return False, f"Failed to update model: {str(e)}"
    
    def delete_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Delete an ML model
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            Tuple of (success, message)
        """
        
        try:
            with transaction.atomic():
                model = MLModel.objects.get(id=model_id)
                
                # Check if model can be deleted
                if model.status == 'active':
                    return False, "Cannot delete active model. Deactivate it first."
                
                # Delete model files
                self.delete_model_files(model)
                
                # Delete model from database
                model_name = model.name
                model.delete()
                
                logger.info(f"Deleted model {model_name} (ID: {model_id})")
                return True, "Model deleted successfully"
                
        except MLModel.DoesNotExist:
            return False, "Model not found"
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {str(e)}")
            return False, f"Failed to delete model: {str(e)}"
    
    def delete_model_files(self, model: MLModel):
        """Delete model files from disk"""
        
        try:
            if model.model_file_path and os.path.exists(model.model_file_path):
                os.remove(model.model_file_path)
            
            if model.scaler_file_path and os.path.exists(model.scaler_file_path):
                os.remove(model.scaler_file_path)
            
            if model.encoder_file_path and os.path.exists(model.encoder_file_path):
                os.remove(model.encoder_file_path)
                
        except Exception as e:
            logger.warning(f"Failed to delete some model files: {str(e)}")
    
    def deploy_model(self, model_id: int) -> Tuple[bool, str]:
        """
        Deploy a model to production
        
        Args:
            model_id: ID of the model to deploy
            
        Returns:
            Tuple of (success, message)
        """
        
        try:
            with transaction.atomic():
                model = MLModel.objects.get(id=model_id)
                
                # Check if model can be deployed
                if model.status != 'active':
                    return False, f"Model must be active to deploy. Current status: {model.status}"
                
                if not model.model_file_path or not os.path.exists(model.model_file_path):
                    return False, "Model file not found. Train the model first."
                
                # Create backup of current production model
                self.backup_production_model(model.model_type)
                
                # Update model deployment status
                model.status = 'deployed'
                model.save()
                
                logger.info(f"Deployed model {model.name} (ID: {model.id})")
                return True, "Model deployed successfully"
                
        except MLModel.DoesNotExist:
            return False, "Model not found"
        except Exception as e:
            logger.error(f"Failed to deploy model {model_id}: {str(e)}")
            return False, f"Failed to deploy model: {str(e)}"
    
    def backup_production_model(self, model_type: str):
        """Create backup of current production model"""
        
        try:
            # Find current production model of this type
            current_prod_model = MLModel.objects.filter(
                model_type=model_type,
                status='deployed'
            ).first()
            
            if current_prod_model:
                # Create backup
                backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{model_type}_{backup_timestamp}"
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                os.makedirs(backup_path, exist_ok=True)
                
                # Copy model files
                if current_prod_model.model_file_path and os.path.exists(current_prod_model.model_file_path):
                    shutil.copy2(
                        current_prod_model.model_file_path,
                        os.path.join(backup_path, 'model.pkl')
                    )
                
                if current_prod_model.scaler_file_path and os.path.exists(current_prod_model.scaler_file_path):
                    shutil.copy2(
                        current_prod_model.scaler_file_path,
                        os.path.join(backup_path, 'scaler.pkl')
                    )
                
                # Save model metadata
                metadata = {
                    'model_id': current_prod_model.id,
                    'name': current_prod_model.name,
                    'version': current_prod_model.version,
                    'backup_timestamp': backup_timestamp,
                    'performance_metrics': current_prod_model.performance_summary
                }
                
                with open(os.path.join(backup_path, 'metadata.json'), 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Update current model status
                current_prod_model.status = 'deprecated'
                current_prod_model.save()
                
                logger.info(f"Created backup of production model: {backup_name}")
                
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
    
    def rollback_model(self, model_type: str, backup_timestamp: str) -> Tuple[bool, str]:
        """
        Rollback to a previous model version
        
        Args:
            model_type: Type of model to rollback
            backup_timestamp: Timestamp of backup to restore
            
        Returns:
            Tuple of (success, message)
        """
        
        try:
            backup_path = os.path.join(self.backup_dir, f"{model_type}_{backup_timestamp}")
            
            if not os.path.exists(backup_path):
                return False, f"Backup not found: {backup_timestamp}"
            
            # Load backup metadata
            metadata_path = os.path.join(backup_path, 'metadata.json')
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Find the model to restore
            model = MLModel.objects.get(id=metadata['model_id'])
            
            # Restore model files
            model_file_path = os.path.join(backup_path, 'model.pkl')
            scaler_file_path = os.path.join(backup_path, 'scaler.pkl')
            
            if os.path.exists(model_file_path):
                model.model_file_path = model_file_path
            if os.path.exists(scaler_file_path):
                model.scaler_file_path = scaler_file_path
            
            # Update status
            model.status = 'active'
            model.save()
            
            logger.info(f"Rolled back model {model.name} to backup {backup_timestamp}")
            return True, "Model rollback successful"
            
        except Exception as e:
            logger.error(f"Failed to rollback model: {str(e)}")
            return False, f"Failed to rollback model: {str(e)}"
    
    def get_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """Get all versions of a model"""
        
        try:
            models = MLModel.objects.filter(name=model_name).order_by('-created_at')
            
            versions = []
            for model in models:
                versions.append({
                    'id': model.id,
                    'version': model.version,
                    'status': model.status,
                    'created_at': model.created_at,
                    'last_trained': model.last_trained,
                    'performance_metrics': model.performance_summary,
                    'has_model_file': bool(model.model_file_path and os.path.exists(model.model_file_path))
                })
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get model versions: {str(e)}")
            return []
    
    def get_model_performance_history(self, model_id: int, days: int = 30) -> Dict[str, Any]:
        """Get model performance history over time"""
        
        try:
            model = MLModel.objects.get(id=model_id)
            
            # Get training history
            training_history = model.training_history.filter(
                started_at__gte=timezone.now() - timedelta(days=days)
            ).order_by('started_at')
            
            # Get prediction accuracy over time
            predictions = model.predictions.filter(
                created_at__gte=timezone.now() - timedelta(days=days)
            ).order_by('created_at')
            
            # Calculate daily accuracy
            daily_accuracy = {}
            for pred in predictions:
                date = pred.created_at.date().isoformat()
                if date not in daily_accuracy:
                    daily_accuracy[date] = {'total': 0, 'accurate': 0}
                
                daily_accuracy[date]['total'] += 1
                if pred.is_accurate:
                    daily_accuracy[date]['accurate'] += 1
            
            # Convert to percentage
            for date in daily_accuracy:
                if daily_accuracy[date]['total'] > 0:
                    daily_accuracy[date]['accuracy'] = (
                        daily_accuracy[date]['accurate'] / daily_accuracy[date]['total']
                    )
                else:
                    daily_accuracy[date]['accuracy'] = 0
            
            return {
                'model_info': {
                    'id': model.id,
                    'name': model.name,
                    'type': model.model_type
                },
                'training_history': [
                    {
                        'date': th.started_at.date().isoformat(),
                        'accuracy': th.training_accuracy,
                        'validation_accuracy': th.validation_accuracy,
                        'status': th.status
                    }
                    for th in training_history
                ],
                'daily_accuracy': daily_accuracy,
                'overall_metrics': model.performance_summary
            }
            
        except MLModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get performance history: {str(e)}")
            return {'error': str(e)}
    
    def get_model_health_status(self, model_id: int) -> Dict[str, Any]:
        """Get comprehensive health status of a model"""
        
        try:
            model = MLModel.objects.get(id=model_id)
            
            # Check file existence
            model_file_exists = bool(model.model_file_path and os.path.exists(model.model_file_path))
            scaler_file_exists = bool(model.scaler_file_path and os.path.exists(model.scaler_file_path))
            
            # Check recent performance
            recent_predictions = model.predictions.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )
            
            recent_accuracy = None
            if recent_predictions.exists():
                accurate_predictions = recent_predictions.filter(
                    actual_value__isnull=False
                ).exclude(actual_value=0)
                if accurate_predictions.exists():
                    recent_accuracy = sum(
                        1 for p in accurate_predictions if p.is_accurate
                    ) / accurate_predictions.count()
            
            # Determine health status
            health_status = 'healthy'
            issues = []
            
            if not model_file_exists:
                health_status = 'critical'
                issues.append('Model file missing')
            
            if not scaler_file_exists:
                health_status = 'warning'
                issues.append('Scaler file missing')
            
            if recent_accuracy is not None and recent_accuracy < 0.7:
                health_status = 'warning'
                issues.append(f'Low recent accuracy: {recent_accuracy:.2%}')
            
            if model.status == 'failed':
                health_status = 'critical'
                issues.append('Model training failed')
            
            return {
                'model_id': model.id,
                'model_name': model.name,
                'health_status': health_status,
                'issues': issues,
                'file_status': {
                    'model_file': model_file_exists,
                    'scaler_file': scaler_file_exists
                },
                'recent_accuracy': recent_accuracy,
                'current_status': model.status,
                'last_trained': model.last_trained,
                'total_predictions': model.predictions.count()
            }
            
        except MLModel.DoesNotExist:
            return {'error': 'Model not found'}
        except Exception as e:
            logger.error(f"Failed to get health status: {str(e)}")
            return {'error': str(e)}
    
    def cleanup_old_models(self, days_threshold: int = 90) -> Dict[str, Any]:
        """Clean up old deprecated models"""
        
        try:
            cutoff_date = timezone.now() - timedelta(days=days_threshold)
            
            # Find old deprecated models
            old_models = MLModel.objects.filter(
                status='deprecated',
                updated_at__lt=cutoff_date
            )
            
            deleted_count = 0
            for model in old_models:
                try:
                    # Delete model files
                    self.delete_model_files(model)
                    
                    # Delete from database
                    model.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to delete old model {model.id}: {str(e)}")
            
            logger.info(f"Cleaned up {deleted_count} old models")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old models: {str(e)}")
            return {'success': False, 'error': str(e)}
