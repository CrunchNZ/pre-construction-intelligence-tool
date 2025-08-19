"""
Signals for AI Models

This module provides Django signals for:
- Automatic model validation
- Performance monitoring
- Cleanup operations
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import MLModel, ModelTrainingHistory, ModelPrediction
from .tasks import monitor_model_performance_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=MLModel)
def ml_model_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for ML models"""
    
    if created:
        logger.info(f"New ML model created: {instance.name} (ID: {instance.id})")
        
        # Schedule initial performance monitoring
        monitor_model_performance_task.delay(instance.id)
        
    else:
        logger.info(f"ML model updated: {instance.name} (ID: {instance.id})")
        
        # If status changed to active, schedule monitoring
        if instance.status == 'active':
            monitor_model_performance_task.delay(instance.id)


@receiver(post_save, sender=ModelTrainingHistory)
def training_history_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for training history"""
    
    if created:
        logger.info(f"New training history created for model {instance.model.name}")
        
        # Update model last_trained timestamp
        instance.model.last_trained = instance.completed_at
        instance.model.save(update_fields=['last_trained'])
        
    else:
        # If training completed, update model status
        if instance.status == 'completed' and instance.model.status == 'training':
            instance.model.status = 'active'
            instance.model.save(update_fields=['status'])
            
            logger.info(f"Model {instance.model.name} training completed and status updated to active")


@receiver(post_save, sender=ModelPrediction)
def prediction_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for predictions"""
    
    if created:
        logger.info(f"New prediction created for model {instance.model.name}")
        
        # If this is a prediction with ground truth, calculate error
        if instance.actual_value is not None and instance.prediction_value is not None:
            instance.prediction_error = instance.actual_value - instance.prediction_value
            instance.save(update_fields=['prediction_error'])
            
            logger.info(f"Prediction error calculated: {instance.prediction_error}")


@receiver(pre_save, sender=MLModel)
def ml_model_pre_save(sender, instance, **kwargs):
    """Handle pre-save actions for ML models"""
    
    try:
        # Get the old instance if it exists
        if instance.pk:
            old_instance = MLModel.objects.get(pk=instance.pk)
            
            # Check if status is changing to 'failed'
            if old_instance.status != 'failed' and instance.status == 'failed':
                logger.warning(f"Model {instance.name} status changed to failed")
                
                # TODO: Send notification to administrators
                # TODO: Trigger automatic retry or fallback
                
    except MLModel.DoesNotExist:
        # New instance, nothing to compare
        pass


@receiver(post_delete, sender=MLModel)
def ml_model_post_delete(sender, instance, **kwargs):
    """Handle post-delete actions for ML models"""
    
    logger.info(f"ML model deleted: {instance.name} (ID: {instance.id})")
    
    # TODO: Clean up associated files
    # TODO: Archive training history
    # TODO: Notify stakeholders


@receiver(post_delete, sender=ModelPrediction)
def prediction_post_delete(sender, instance, **kwargs):
    """Handle post-delete actions for predictions"""
    
    logger.info(f"Prediction deleted for model {instance.model.name}")
    
    # TODO: Update model statistics
    # TODO: Archive prediction data if needed
