#!/usr/bin/env python3
"""
ML Model Training Script

This script demonstrates training ML models on construction data
for cost prediction, timeline prediction, and risk assessment.
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta
import random
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preconstruction_intelligence.settings')
django.setup()

from ai_models.models import MLModel, ModelTrainingHistory, FeatureEngineering
from ai_models.ml_pipeline import MLPipelineService
from ai_models.model_manager import MLModelManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Handles training of ML models for construction data"""
    
    def __init__(self):
        self.pipeline_service = MLPipelineService()
        self.model_manager = MLModelManager()
        
    def generate_sample_data(self, n_samples=1000):
        """Generate realistic sample construction data for training"""
        logger.info(f"Generating {n_samples} sample construction records...")
        
        # Generate realistic construction project features
        np.random.seed(42)  # For reproducible results
        
        data = {
            'project_size_sqft': np.random.normal(50000, 20000, n_samples),
            'project_complexity': np.random.choice(['low', 'medium', 'high'], n_samples, p=[0.3, 0.5, 0.2]),
            'location_factor': np.random.normal(1.0, 0.2, n_samples),
            'material_cost_index': np.random.normal(100, 15, n_samples),
            'labor_cost_index': np.random.normal(100, 20, n_samples),
            'weather_risk': np.random.uniform(0, 1, n_samples),
            'supply_chain_risk': np.random.uniform(0, 1, n_samples),
            'regulatory_complexity': np.random.uniform(0, 1, n_samples),
            'team_experience': np.random.uniform(0.5, 1.0, n_samples),
            'technology_adoption': np.random.uniform(0, 1, n_samples),
        }
        
        # Convert categorical to numerical
        complexity_map = {'low': 1, 'medium': 2, 'high': 3}
        data['project_complexity_numeric'] = [complexity_map[x] for x in data['project_complexity']]
        
        return data
    
    def train_cost_prediction_model(self):
        """Train a cost prediction model"""
        logger.info("Training cost prediction model...")
        
        # Generate sample data
        data = self.generate_sample_data(1000)
        
        # Create target variable (cost per sqft)
        base_cost = 150  # Base cost per sqft
        complexity_multiplier = np.array(data['project_complexity_numeric']) * 0.3
        location_multiplier = np.array(data['location_factor']) * 0.2
        material_multiplier = (np.array(data['material_cost_index']) - 100) / 100 * 0.3
        labor_multiplier = (np.array(data['labor_cost_index']) - 100) / 100 * 0.2
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.1, len(data['project_size_sqft']))
        
        cost_per_sqft = (base_cost + 
                         complexity_multiplier + 
                         location_multiplier + 
                         material_multiplier + 
                         labor_multiplier + 
                         noise)
        
        # Prepare features
        feature_names = [
            'project_size_sqft', 'project_complexity_numeric', 'location_factor',
            'material_cost_index', 'labor_cost_index', 'weather_risk',
            'supply_chain_risk', 'regulatory_complexity', 'team_experience',
            'technology_adoption'
        ]
        
        X = np.column_stack([data[name] for name in feature_names])
        y = cost_per_sqft
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        logger.info(f"Cost prediction model - RMSE: ${rmse:.2f}/sqft")
        
        # Save model
        model_path = 'cost_prediction_model.joblib'
        joblib.dump(model, model_path)
        
        # Create ML model record
        ml_model = MLModel.objects.create(
            name='Cost Prediction Model v1.0',
            model_type='cost_prediction',
            algorithm='random_forest',
            version='1.0.0',
            status='active',
            accuracy=1.0 - (rmse / np.mean(y)),  # Simple accuracy metric
            model_file_path=model_path,
            feature_names=feature_names,
            hyperparameters={'n_estimators': 100, 'random_state': 42}
        )
        
        # Create training history
        ModelTrainingHistory.objects.create(
            model=ml_model,
            training_started_at=datetime.now() - timedelta(hours=1),
            training_completed_at=datetime.now(),
            training_data_size=len(X_train),
            validation_data_size=len(X_test),
            training_metrics={'rmse': float(rmse), 'mse': float(mse)},
            model_performance={'test_rmse': float(rmse)}
        )
        
        logger.info(f"Cost prediction model saved with ID: {ml_model.id}")
        return ml_model
    
    def train_timeline_prediction_model(self):
        """Train a timeline prediction model"""
        logger.info("Training timeline prediction model...")
        
        # Generate sample data
        data = self.generate_sample_data(1000)
        
        # Create target variable (days per 1000 sqft)
        base_days = 30  # Base days per 1000 sqft
        complexity_multiplier = np.array(data['project_complexity_numeric']) * 0.4
        weather_risk_multiplier = np.array(data['weather_risk']) * 0.3
        team_experience_multiplier = (1 - np.array(data['team_experience'])) * 0.2
        technology_multiplier = (1 - np.array(data['technology_adoption'])) * 0.1
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.15, len(data['project_size_sqft']))
        
        days_per_1000_sqft = (base_days + 
                              complexity_multiplier + 
                              weather_risk_multiplier + 
                              team_experience_multiplier + 
                              technology_multiplier + 
                              noise)
        
        # Prepare features
        feature_names = [
            'project_size_sqft', 'project_complexity_numeric', 'location_factor',
            'weather_risk', 'supply_chain_risk', 'regulatory_complexity',
            'team_experience', 'technology_adoption'
        ]
        
        X = np.column_stack([data[name] for name in feature_names])
        y = days_per_1000_sqft
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        logger.info(f"Timeline prediction model - RMSE: {rmse:.2f} days per 1000 sqft")
        
        # Save model
        model_path = 'timeline_prediction_model.joblib'
        joblib.dump(model, model_path)
        
        # Create ML model record
        ml_model = MLModel.objects.create(
            name='Timeline Prediction Model v1.0',
            model_type='timeline_prediction',
            algorithm='random_forest',
            version='1.0.0',
            status='active',
            accuracy=1.0 - (rmse / np.mean(y)),  # Simple accuracy metric
            model_file_path=model_path,
            feature_names=feature_names,
            hyperparameters={'n_estimators': 100, 'random_state': 42}
        )
        
        # Create training history
        ModelTrainingHistory.objects.create(
            model=ml_model,
            training_started_at=datetime.now() - timedelta(hours=1),
            training_completed_at=datetime.now(),
            training_data_size=len(X_train),
            validation_data_size=len(X_test),
            training_metrics={'rmse': float(rmse), 'mse': float(mse)},
            model_performance={'test_rmse': float(rmse)}
        )
        
        logger.info(f"Timeline prediction model saved with ID: {ml_model.id}")
        return ml_model
    
    def train_risk_assessment_model(self):
        """Train a risk assessment model"""
        logger.info("Training risk assessment model...")
        
        # Generate sample data
        data = self.generate_sample_data(1000)
        
        # Create target variable (risk level: 0=low, 1=medium, 2=high)
        risk_scores = (
            np.array(data['weather_risk']) * 0.3 +
            np.array(data['supply_chain_risk']) * 0.3 +
            np.array(data['regulatory_complexity']) * 0.2 +
            (1 - np.array(data['team_experience'])) * 0.2
        )
        
        # Convert to risk levels
        risk_levels = np.zeros(len(risk_scores), dtype=int)
        risk_levels[risk_scores > 0.6] = 2  # High risk
        risk_levels[(risk_scores > 0.3) & (risk_scores <= 0.6)] = 1  # Medium risk
        # risk_levels[risk_scores <= 0.3] = 0  # Low risk (default)
        
        # Prepare features
        feature_names = [
            'project_size_sqft', 'project_complexity_numeric', 'location_factor',
            'weather_risk', 'supply_chain_risk', 'regulatory_complexity',
            'team_experience', 'technology_adoption'
        ]
        
        X = np.column_stack([data[name] for name in feature_names])
        y = risk_levels
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Risk assessment model - Accuracy: {accuracy:.3f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        # Save model
        model_path = 'risk_assessment_model.joblib'
        joblib.dump(model, model_path)
        
        # Create ML model record
        ml_model = MLModel.objects.create(
            name='Risk Assessment Model v1.0',
            model_type='risk_assessment',
            algorithm='random_forest',
            version='1.0.0',
            status='active',
            accuracy=accuracy,
            model_file_path=model_path,
            feature_names=feature_names,
            hyperparameters={'n_estimators': 100, 'random_state': 42}
        )
        
        # Create training history
        ModelTrainingHistory.objects.create(
            model=ml_model,
            training_started_at=datetime.now() - timedelta(hours=1),
            training_completed_at=datetime.now(),
            training_data_size=len(X_train),
            validation_data_size=len(X_test),
            training_metrics={'accuracy': float(accuracy)},
            model_performance={'test_accuracy': float(accuracy)}
        )
        
        logger.info(f"Risk assessment model saved with ID: {ml_model.id}")
        return ml_model
    
    def train_all_models(self):
        """Train all ML models"""
        logger.info("Starting training of all ML models...")
        
        try:
            # Train cost prediction model
            cost_model = self.train_cost_prediction_model()
            
            # Train timeline prediction model
            timeline_model = self.train_timeline_prediction_model()
            
            # Train risk assessment model
            risk_model = self.train_risk_assessment_model()
            
            logger.info("All models trained successfully!")
            logger.info(f"Cost Prediction Model ID: {cost_model.id}")
            logger.info(f"Timeline Prediction Model ID: {timeline_model.id}")
            logger.info(f"Risk Assessment Model ID: {risk_model.id}")
            
            return [cost_model, timeline_model, risk_model]
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise

def main():
    """Main function to run model training"""
    logger.info("Starting ML model training process...")
    
    try:
        trainer = ModelTrainer()
        models = trainer.train_all_models()
        
        logger.info("Model training completed successfully!")
        logger.info(f"Trained {len(models)} models:")
        for model in models:
            logger.info(f"- {model.name} (ID: {model.id}) - Accuracy: {model.accuracy:.3f}")
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
