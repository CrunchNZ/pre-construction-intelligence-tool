from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class MLModel(models.Model):
    """Machine Learning Model for storing model metadata and configuration"""
    
    MODEL_TYPES = [
        ('cost_prediction', 'Cost Prediction'),
        ('timeline_prediction', 'Timeline Prediction'),
        ('risk_assessment', 'Risk Assessment'),
        ('quality_prediction', 'Quality Prediction'),
        ('safety_prediction', 'Safety Prediction'),
        ('change_order_impact', 'Change Order Impact'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('training', 'Training'),
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=20, default='1.0.0')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Model Configuration
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict)
    feature_columns = models.JSONField(default=list)
    target_column = models.CharField(max_length=100)
    
    # Model Files
    model_file_path = models.CharField(max_length=500, blank=True)
    scaler_file_path = models.CharField(max_length=500, blank=True)
    encoder_file_path = models.CharField(max_length=500, blank=True)
    
    # Performance Metrics
    accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    precision = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    recall = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    f1_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    mae = models.FloatField(null=True, blank=True)  # Mean Absolute Error
    rmse = models.FloatField(null=True, blank=True)  # Root Mean Square Error
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_trained = models.DateTimeField(null=True, blank=True)
    
    # Training Configuration
    training_data_size = models.IntegerField(null=True, blank=True)
    validation_data_size = models.IntegerField(null=True, blank=True)
    training_duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ML Model'
        verbose_name_plural = 'ML Models'
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def performance_summary(self):
        """Return a summary of model performance metrics"""
        metrics = {}
        if self.accuracy is not None:
            metrics['accuracy'] = self.accuracy
        if self.precision is not None:
            metrics['precision'] = self.precision
        if self.recall is not None:
            metrics['recall'] = self.recall
        if self.f1_score is not None:
            metrics['f1_score'] = self.f1_score
        if self.mae is not None:
            metrics['mae'] = self.mae
        if self.rmse is not None:
            metrics['rmse'] = self.rmse
        return metrics


class ModelTrainingHistory(models.Model):
    """Track training history and performance evolution"""
    
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_history')
    training_run_id = models.CharField(max_length=100, unique=True)
    
    # Training Results
    training_accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    validation_accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    training_loss = models.FloatField()
    validation_loss = models.FloatField()
    
    # Performance Metrics
    precision = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    recall = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    f1_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    
    # Training Details
    epochs = models.IntegerField()
    batch_size = models.IntegerField()
    learning_rate = models.FloatField()
    hyperparameters = models.JSONField(default=dict)
    
    # Metadata
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    duration = models.DurationField()
    data_size = models.IntegerField()
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ])
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Model Training History'
        verbose_name_plural = 'Model Training History'
    
    def __str__(self):
        return f"{self.model.name} - Training Run {self.training_run_id}"
    
    @property
    def training_time_minutes(self):
        """Return training duration in minutes"""
        return self.duration.total_seconds() / 60


class FeatureEngineering(models.Model):
    """Track feature engineering configurations and transformations"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Feature Configuration
    input_features = models.JSONField(default=list)
    output_features = models.JSONField(default=list)
    transformations = models.JSONField(default=list)
    
    # Scaling and Encoding
    scaling_method = models.CharField(max_length=50, choices=[
        ('standard', 'Standard Scaler'),
        ('minmax', 'Min-Max Scaler'),
        ('robust', 'Robust Scaler'),
        ('none', 'No Scaling'),
    ], default='standard')
    
    encoding_method = models.CharField(max_length=50, choices=[
        ('onehot', 'One-Hot Encoding'),
        ('label', 'Label Encoding'),
        ('target', 'Target Encoding'),
        ('none', 'No Encoding'),
    ], default='onehot')
    
    # Validation
    validation_rules = models.JSONField(default=dict)
    data_quality_checks = models.JSONField(default=list)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feature Engineering'
        verbose_name_plural = 'Feature Engineering'
    
    def __str__(self):
        return self.name


class ModelPrediction(models.Model):
    """Store model predictions for analysis and monitoring"""
    
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    
    # Input Data
    input_features = models.JSONField()
    input_data_hash = models.CharField(max_length=64)  # SHA-256 hash for deduplication
    
    # Prediction Results
    prediction_value = models.FloatField()
    prediction_confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    prediction_interval_lower = models.FloatField(null=True, blank=True)
    prediction_interval_upper = models.FloatField(null=True, blank=True)
    
    # Ground Truth (if available)
    actual_value = models.FloatField(null=True, blank=True)
    prediction_error = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    project_id = models.CharField(max_length=100, blank=True)
    user_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Model Prediction'
        verbose_name_plural = 'Model Predictions'
        indexes = [
            models.Index(fields=['model', 'created_at']),
            models.Index(fields=['input_data_hash']),
        ]
    
    def __str__(self):
        return f"{self.model.name} - {self.prediction_value} ({self.created_at})"
    
    @property
    def is_accurate(self):
        """Check if prediction is within acceptable error range"""
        if self.actual_value is None or self.prediction_error is None:
            return None
        # Define acceptable error threshold (e.g., 10%)
        threshold = 0.1
        return abs(self.prediction_error) <= threshold
