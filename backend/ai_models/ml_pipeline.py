"""
Machine Learning Pipeline Service

This module provides the core ML infrastructure for:
- Model training and validation
- Feature engineering and preprocessing
- Prediction generation
- Model performance monitoring
"""

import os
import pickle
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib

from .models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction
from .data_integration import ConstructionDataIntegrationService
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class MLPipelineService:
    """Core ML pipeline service for model management"""
    
    def __init__(self):
        self.models_dir = getattr(settings, 'ML_MODELS_DIR', 'ml_models')
        self.data_integration = ConstructionDataIntegrationService()
        self.ensure_models_directory()
    
    def ensure_models_directory(self):
        """Ensure the models directory exists"""
        os.makedirs(self.models_dir, exist_ok=True)
    
    def get_model_path(self, model_id: int, model_name: str) -> str:
        """Get the file path for a model"""
        safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return os.path.join(self.models_dir, f"{model_id}_{safe_name}.pkl")
    
    def get_scaler_path(self, model_id: int, model_name: str) -> str:
        """Get the file path for a model scaler"""
        safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return os.path.join(self.models_dir, f"{model_id}_{safe_name}_scaler.pkl")
    
    def get_encoder_path(self, model_id: int, model_name: str) -> str:
        """Get the file path for a model encoder"""
        safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return os.path.join(self.models_dir, f"{model_id}_{safe_name}_encoder.pkl")
    
    def create_model_instance(self, algorithm: str, hyperparameters: Dict[str, Any]):
        """Create a model instance based on algorithm and hyperparameters"""
        algorithm_map = {
            'Random Forest': RandomForestRegressor,
            'Random Forest Classifier': RandomForestClassifier,
            'Linear Regression': LinearRegression,
            'Logistic Regression': LogisticRegression,
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        model_class = algorithm_map[algorithm]
        return model_class(**hyperparameters)
    
    def prepare_features(self, data: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
        """Prepare features for training/prediction"""
        if not feature_columns:
            raise ValueError("No feature columns specified")
        
        # Select only the specified features
        features = data[feature_columns].copy()
        
        # Handle missing values
        numeric_features = features.select_dtypes(include=[np.number]).columns
        categorical_features = features.select_dtypes(include=['object']).columns
        
        # Create preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('encoder', pd.get_dummies)
        ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            remainder='drop'
        )
        
        return preprocessor, features
    
    def train_model(self, model_id: int, training_data: pd.DataFrame, 
                   feature_columns: List[str], target_column: str,
                   algorithm: str, hyperparameters: Dict[str, Any],
                   test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """Train a machine learning model"""
        
        logger.info(f"Starting training for model {model_id}")
        
        try:
            # Prepare features and target
            preprocessor, features = self.prepare_features(training_data, feature_columns)
            target = training_data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=test_size, random_state=random_state
            )
            
            # Create and train model
            model = self.create_model_instance(algorithm, hyperparameters)
            
            # Fit preprocessor and transform data
            X_train_processed = preprocessor.fit_transform(X_train)
            X_test_processed = preprocessor.transform(X_test)
            
            # Train model
            start_time = timezone.now()
            model.fit(X_train_processed, y_train)
            training_duration = timezone.now() - start_time
            
            # Make predictions
            y_train_pred = model.predict(X_train_processed)
            y_test_pred = model.predict(X_test_processed)
            
            # Calculate metrics
            metrics = self.calculate_metrics(y_train, y_train_pred, y_test, y_test_pred)
            
            # Save model and preprocessor
            model_path = self.get_model_path(model_id, f"model_{model_id}")
            preprocessor_path = self.get_scaler_path(model_id, f"model_{model_id}")
            
            joblib.dump(model, model_path)
            joblib.dump(preprocessor, preprocessor_path)
            
            # Update model in database
            ml_model = MLModel.objects.get(id=model_id)
            ml_model.model_file_path = model_path
            ml_model.scaler_file_path = preprocessor_path
            ml_model.status = 'active'
            ml_model.last_trained = timezone.now()
            ml_model.training_data_size = len(X_train)
            ml_model.validation_data_size = len(X_test)
            ml_model.training_duration = training_duration
            
            # Update performance metrics
            for key, value in metrics.items():
                if hasattr(ml_model, key):
                    setattr(ml_model, key, value)
            
            ml_model.save()
            
            # Create training history record
            training_history = ModelTrainingHistory.objects.create(
                model=ml_model,
                training_run_id=f"run_{model_id}_{int(timezone.now().timestamp())}",
                training_accuracy=metrics.get('accuracy', 0.0),
                validation_accuracy=metrics.get('accuracy', 0.0),
                training_loss=metrics.get('mae', 0.0),
                validation_loss=metrics.get('mae', 0.0),
                precision=metrics.get('precision', 0.0),
                recall=metrics.get('recall', 0.0),
                f1_score=metrics.get('f1_score', 0.0),
                epochs=1,  # For non-neural network models
                batch_size=len(X_train),
                learning_rate=hyperparameters.get('learning_rate', 0.0),
                hyperparameters=hyperparameters,
                started_at=start_time,
                completed_at=timezone.now(),
                duration=training_duration,
                data_size=len(training_data),
                status='completed'
            )
            
            logger.info(f"Training completed for model {model_id}")
            
            return {
                'success': True,
                'metrics': metrics,
                'training_duration': training_duration,
                'training_history_id': training_history.id
            }
            
        except Exception as e:
            logger.error(f"Training failed for model {model_id}: {str(e)}")
            
            # Update model status to failed
            ml_model = MLModel.objects.get(id=model_id)
            ml_model.status = 'failed'
            ml_model.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_metrics(self, y_train: pd.Series, y_train_pred: np.ndarray,
                         y_test: pd.Series, y_test_pred: np.ndarray) -> Dict[str, float]:
        """Calculate model performance metrics"""
        metrics = {}
        
        # Training metrics
        if self._is_classification(y_train):
            metrics['accuracy'] = accuracy_score(y_train, y_train_pred)
            metrics['precision'] = precision_score(y_train, y_train_pred, average='weighted', zero_division=0)
            metrics['recall'] = recall_score(y_train, y_train_pred, average='weighted', zero_division=0)
            metrics['f1_score'] = f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
        else:
            metrics['mae'] = mean_absolute_error(y_train, y_train_pred)
            metrics['rmse'] = np.sqrt(mean_squared_error(y_train, y_train_pred))
            metrics['r2_score'] = r2_score(y_train, y_train_pred)
        
        # Test metrics
        if self._is_classification(y_test):
            metrics['test_accuracy'] = accuracy_score(y_test, y_test_pred)
            metrics['test_precision'] = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
            metrics['test_recall'] = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
            metrics['test_f1_score'] = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        else:
            metrics['test_mae'] = mean_absolute_error(y_test, y_test_pred)
            metrics['test_rmse'] = np.sqrt(mean_squared_error(y_test, y_test_pred))
            metrics['test_r2_score'] = r2_score(y_test, y_test_pred)
        
        return metrics
    
    def _is_classification(self, y: pd.Series) -> bool:
        """Check if the target variable is for classification"""
        return y.dtype == 'object' or len(y.unique()) < len(y) * 0.1
    
    def make_prediction(self, model_id: int, input_features: Dict[str, Any],
                       include_confidence: bool = False, include_intervals: bool = False) -> Dict[str, Any]:
        """Make a prediction using a trained model"""
        
        try:
            # Get model from database
            ml_model = MLModel.objects.get(id=model_id, status='active')
            
            if not ml_model.model_file_path or not os.path.exists(ml_model.model_file_path):
                raise ValueError("Model file not found")
            
            # Load model and preprocessor
            model = joblib.load(ml_model.model_file_path)
            preprocessor = joblib.load(ml_model.scaler_file_path)
            
            # Prepare input data
            input_df = pd.DataFrame([input_features])
            processed_features = preprocessor.transform(input_df)
            
            # Make prediction
            prediction = model.predict(processed_features)[0]
            
            # Calculate confidence and intervals if requested
            confidence = None
            interval_lower = None
            interval_upper = None
            
            if include_confidence and hasattr(model, 'predict_proba'):
                proba = model.predict_proba(processed_features)[0]
                confidence = max(proba)
            
            if include_intervals and hasattr(model, 'predict'):
                # For regression models, we can estimate intervals
                if hasattr(model, 'estimators_'):
                    predictions = []
                    for estimator in model.estimators_:
                        pred = estimator.predict(processed_features)[0]
                        predictions.append(pred)
                    
                    predictions = np.array(predictions)
                    interval_lower = np.percentile(predictions, 2.5)
                    interval_upper = np.percentile(predictions, 97.5)
            
            return {
                'success': True,
                'prediction': float(prediction),
                'confidence': confidence,
                'interval_lower': interval_lower,
                'interval_upper': interval_upper,
                'model_name': ml_model.name,
                'model_version': ml_model.version
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for model {model_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def evaluate_model(self, model_id: int, test_data: pd.DataFrame,
                      feature_columns: List[str], target_column: str) -> Dict[str, Any]:
        """Evaluate a trained model on new data"""
        
        try:
            # Get model from database
            ml_model = MLModel.objects.get(id=model_id, status='active')
            
            if not ml_model.model_file_path or not os.path.exists(ml_model.model_file_path):
                raise ValueError("Model file not found")
            
            # Load model and preprocessor
            model = joblib.load(ml_model.model_file_path)
            preprocessor = joblib.load(ml_model.scaler_file_path)
            
            # Prepare test data
            processed_features = preprocessor.transform(test_data[feature_columns])
            true_values = test_data[target_column]
            
            # Make predictions
            predictions = model.predict(processed_features)
            
            # Calculate metrics
            metrics = self.calculate_metrics(true_values, predictions, true_values, predictions)
            
            return {
                'success': True,
                'metrics': metrics,
                'predictions': predictions.tolist(),
                'true_values': true_values.tolist()
            }
            
        except Exception as e:
            logger.error(f"Model evaluation failed for model {model_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_model_performance_summary(self, model_id: int) -> Dict[str, Any]:
        """Get a comprehensive performance summary for a model"""
        
        try:
            ml_model = MLModel.objects.get(id=model_id)
            
            # Get recent predictions
            recent_predictions = ModelPrediction.objects.filter(
                model=ml_model,
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            # Calculate recent accuracy
            recent_accuracy = None
            if recent_predictions.exists():
                accurate_predictions = recent_predictions.filter(
                    actual_value__isnull=False
                ).exclude(actual_value=0)
                if accurate_predictions.exists():
                    recent_accuracy = sum(
                        1 for p in accurate_predictions if p.is_accurate
                    ) / accurate_predictions.count()
            
            # Get training history
            training_history = ml_model.training_history.all().order_by('-started_at')
            
            summary = {
                'model_info': {
                    'id': ml_model.id,
                    'name': ml_model.name,
                    'type': ml_model.model_type,
                    'algorithm': ml_model.algorithm,
                    'status': ml_model.status,
                    'version': ml_model.version
                },
                'performance_metrics': ml_model.performance_summary,
                'recent_accuracy': recent_accuracy,
                'total_predictions': recent_predictions.count(),
                'training_history_count': training_history.count(),
                'last_trained': ml_model.last_trained,
                'model_file_exists': os.path.exists(ml_model.model_file_path) if ml_model.model_file_path else False
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary for model {model_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
