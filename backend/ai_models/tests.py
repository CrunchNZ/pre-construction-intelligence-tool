from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
import json

from .models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction
from .serializers import MLModelSerializer, MLModelCreateSerializer, MLModelUpdateSerializer


class MLModelModelTest(TestCase):
    """Test cases for MLModel model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.model = MLModel.objects.create(
            name='Test Cost Model',
            model_type='cost_prediction',
            version='1.0.0',
            description='Test model for cost prediction',
            algorithm='Random Forest',
            hyperparameters={'n_estimators': 100, 'max_depth': 10},
            feature_columns=['area', 'complexity', 'location'],
            target_column='cost',
            created_by=self.user
        )
    
    def test_model_creation(self):
        """Test ML model creation"""
        self.assertEqual(self.model.name, 'Test Cost Model')
        self.assertEqual(self.model.model_type, 'cost_prediction')
        self.assertEqual(self.model.algorithm, 'Random Forest')
        self.assertEqual(self.model.created_by, self.user)
    
    def test_model_string_representation(self):
        """Test model string representation"""
        expected = 'Test Cost Model v1.0.0 (Cost Prediction)'
        self.assertEqual(str(self.model), expected)
    
    def test_model_is_active_property(self):
        """Test is_active property"""
        self.assertFalse(self.model.is_active)
        
        self.model.status = 'active'
        self.model.save()
        self.assertTrue(self.model.is_active)
    
    def test_performance_summary_property(self):
        """Test performance_summary property"""
        # Initially no performance metrics
        self.assertEqual(len(self.model.performance_summary), 0)
        
        # Add performance metrics
        self.model.accuracy = 0.85
        self.model.precision = 0.82
        self.model.recall = 0.88
        self.model.save()
        
        summary = self.model.performance_summary
        self.assertEqual(summary['accuracy'], 0.85)
        self.assertEqual(summary['precision'], 0.82)
        self.assertEqual(summary['recall'], 0.88)


class ModelTrainingHistoryModelTest(TestCase):
    """Test cases for ModelTrainingHistory model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            created_by=self.user
        )
        
        self.training_history = ModelTrainingHistory.objects.create(
            model=self.model,
            training_run_id='test_run_001',
            training_accuracy=0.85,
            validation_accuracy=0.82,
            training_loss=0.15,
            validation_loss=0.18,
            epochs=100,
            batch_size=32,
            learning_rate=0.001,
            started_at=timezone.now() - timedelta(hours=1),
            completed_at=timezone.now(),
            duration=timedelta(hours=1),
            data_size=1000,
            status='completed'
        )
    
    def test_training_history_creation(self):
        """Test training history creation"""
        self.assertEqual(self.training_history.training_run_id, 'test_run_001')
        self.assertEqual(self.training_history.training_accuracy, 0.85)
        self.assertEqual(self.training_history.status, 'completed')
    
    def test_training_time_minutes_property(self):
        """Test training_time_minutes property"""
        self.assertEqual(self.training_history.training_time_minutes, 60.0)
    
    def test_training_history_string_representation(self):
        """Test training history string representation"""
        expected = 'Test Model - Training Run test_run_001'
        self.assertEqual(str(self.training_history), expected)


class FeatureEngineeringModelTest(TestCase):
    """Test cases for FeatureEngineering model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.feature_eng = FeatureEngineering.objects.create(
            name='Test Feature Engineering',
            description='Test feature engineering configuration',
            input_features=['feature1', 'feature2'],
            output_features=['processed_feature1', 'processed_feature2'],
            transformations=['normalize', 'encode'],
            scaling_method='standard',
            encoding_method='onehot',
            created_by=self.user
        )
    
    def test_feature_engineering_creation(self):
        """Test feature engineering creation"""
        self.assertEqual(self.feature_eng.name, 'Test Feature Engineering')
        self.assertEqual(self.feature_eng.scaling_method, 'standard')
        self.assertEqual(self.feature_eng.encoding_method, 'onehot')
        self.assertTrue(self.feature_eng.is_active)
    
    def test_feature_engineering_string_representation(self):
        """Test feature engineering string representation"""
        self.assertEqual(str(self.feature_eng), 'Test Feature Engineering')


class ModelPredictionModelTest(TestCase):
    """Test cases for ModelPrediction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            created_by=self.user
        )
        
        self.prediction = ModelPrediction.objects.create(
            model=self.model,
            input_features={'feature1': 100},
            input_data_hash='test_hash_123',
            prediction_value=1000.0,
            prediction_confidence=0.85,
            project_id='PROJ001',
            user_id='USER001'
        )
    
    def test_prediction_creation(self):
        """Test prediction creation"""
        self.assertEqual(self.prediction.prediction_value, 1000.0)
        self.assertEqual(self.prediction.prediction_confidence, 0.85)
        self.assertEqual(self.prediction.project_id, 'PROJ001')
    
    def test_prediction_is_accurate_property(self):
        """Test is_accurate property"""
        # Initially no ground truth
        self.assertIsNone(self.prediction.is_accurate)
        
        # Add ground truth
        self.prediction.actual_value = 1000.0
        self.prediction.prediction_error = 0.0
        self.prediction.save()
        self.assertTrue(self.prediction.is_accurate)
        
        # Test inaccurate prediction
        self.prediction.actual_value = 1200.0
        self.prediction.prediction_error = 200.0
        self.prediction.save()
        self.assertFalse(self.prediction.is_accurate)
    
    def test_prediction_string_representation(self):
        """Test prediction string representation"""
        expected = 'Test Model - 1000.0 ('
        self.assertTrue(str(self.prediction).startswith(expected))


class MLModelSerializerTest(TestCase):
    """Test cases for ML Model serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            created_by=self.user
        )
    
    def test_ml_model_serializer(self):
        """Test ML model serializer"""
        serializer = MLModelSerializer(self.model)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Model')
        self.assertEqual(data['model_type'], 'cost_prediction')
        self.assertEqual(data['algorithm'], 'Random Forest')
        self.assertEqual(data['created_by'], 'testuser')
        self.assertIn('performance_summary', data)
    
    def test_ml_model_create_serializer(self):
        """Test ML model create serializer"""
        data = {
            'name': 'New Model',
            'model_type': 'timeline_prediction',
            'version': '1.0.0',
            'description': 'New model',
            'algorithm': 'Linear Regression',
            'hyperparameters': {},
            'feature_columns': ['feature1'],
            'target_column': 'timeline'
        }
        
        serializer = MLModelCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_ml_model_update_serializer(self):
        """Test ML model update serializer"""
        data = {
            'description': 'Updated description',
            'status': 'active'
        }
        
        serializer = MLModelUpdateSerializer(self.model, data=data, partial=True)
        self.assertTrue(serializer.is_valid())


class MLModelAPITest(APITestCase):
    """Test cases for ML Model API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            created_by=self.user
        )
    
    def test_list_models(self):
        """Test listing ML models"""
        url = reverse('ai_models:mlmodel-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Model')
    
    def test_create_model(self):
        """Test creating ML model"""
        url = reverse('ai_models:mlmodel-list')
        data = {
            'name': 'New Model',
            'model_type': 'timeline_prediction',
            'version': '1.0.0',
            'description': 'New model',
            'algorithm': 'Linear Regression',
            'hyperparameters': {},
            'feature_columns': ['feature1'],
            'target_column': 'timeline'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MLModel.objects.count(), 2)
    
    def test_retrieve_model(self):
        """Test retrieving ML model"""
        url = reverse('ai_models:mlmodel-detail', args=[self.model.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Model')
    
    def test_update_model(self):
        """Test updating ML model"""
        url = reverse('ai_models:mlmodel-detail', args=[self.model.id])
        data = {'description': 'Updated description'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')
    
    def test_delete_model(self):
        """Test deleting ML model"""
        url = reverse('ai_models:mlmodel-detail', args=[self.model.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MLModel.objects.count(), 0)
    
    def test_train_model(self):
        """Test model training endpoint"""
        url = reverse('ai_models:mlmodel-train', args=[self.model.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Training started', response.data['message'])
        
        # Check model status was updated
        self.model.refresh_from_db()
        self.assertEqual(self.model.status, 'training')
    
    def test_deploy_model(self):
        """Test model deployment endpoint"""
        # Set model to active status
        self.model.status = 'active'
        self.model.save()
        
        url = reverse('ai_models:mlmodel-deploy', args=[self.model.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deployed successfully', response.data['message'])
    
    def test_performance_summary(self):
        """Test performance summary endpoint"""
        url = reverse('ai_models:mlmodel-performance-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No active models
    
    def test_training_history(self):
        """Test training history endpoint"""
        url = reverse('ai_models:mlmodel-training-history', args=[self.model.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No training history


class ModelPredictionAPITest(APITestCase):
    """Test cases for Model Prediction API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            status='active',
            created_by=self.user
        )
    
    def test_make_prediction(self):
        """Test making a prediction"""
        url = reverse('ai_models:prediction-predict')
        data = {
            'model_id': self.model.id,
            'input_features': {'feature1': 100},
            'project_id': 'PROJ001',
            'user_id': 'USER001'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check prediction was created
        self.assertEqual(ModelPrediction.objects.count(), 1)
        prediction = ModelPrediction.objects.first()
        self.assertEqual(prediction.prediction_value, 1000.0)
        self.assertEqual(prediction.project_id, 'PROJ001')
    
    def test_prediction_with_invalid_model(self):
        """Test prediction with invalid model ID"""
        url = reverse('ai_models:prediction-predict')
        data = {
            'model_id': 999,
            'input_features': {'feature1': 100}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_prediction_with_inactive_model(self):
        """Test prediction with inactive model"""
        self.model.status = 'draft'
        self.model.save()
        
        url = reverse('ai_models:prediction-predict')
        data = {
            'model_id': self.model.id,
            'input_features': {'feature1': 100}
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_accuracy_analysis(self):
        """Test accuracy analysis endpoint"""
        # Create some predictions with ground truth
        ModelPrediction.objects.create(
            model=self.model,
            input_features={'feature1': 100},
            input_data_hash='hash1',
            prediction_value=1000.0,
            actual_value=1000.0,
            prediction_error=0.0
        )
        
        ModelPrediction.objects.create(
            model=self.model,
            input_features={'feature1': 200},
            input_data_hash='hash2',
            prediction_value=2000.0,
            actual_value=2200.0,
            prediction_error=200.0
        )
        
        url = reverse('ai_models:prediction-accuracy-analysis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_predictions'], 2)
        self.assertEqual(response.data['accurate_predictions'], 1)
        self.assertEqual(response.data['overall_accuracy'], 0.5)


class FeatureEngineeringAPITest(APITestCase):
    """Test cases for Feature Engineering API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.feature_eng = FeatureEngineering.objects.create(
            name='Test Feature Engineering',
            description='Test configuration',
            input_features=['feature1'],
            output_features=['processed_feature1'],
            scaling_method='standard',
            encoding_method='onehot',
            created_by=self.user
        )
    
    def test_list_feature_engineering(self):
        """Test listing feature engineering configurations"""
        url = reverse('ai_models:featureengineering-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Feature Engineering')
    
    def test_create_feature_engineering(self):
        """Test creating feature engineering configuration"""
        url = reverse('ai_models:featureengineering-list')
        data = {
            'name': 'New Feature Engineering',
            'description': 'New configuration',
            'input_features': ['feature1', 'feature2'],
            'output_features': ['processed1', 'processed2'],
            'scaling_method': 'minmax',
            'encoding_method': 'label'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FeatureEngineering.objects.count(), 2)
    
    def test_validate_features(self):
        """Test feature validation endpoint"""
        url = reverse('ai_models:featureengineering-validate-features', args=[self.feature_eng.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])


class ModelTrainingHistoryAPITest(APITestCase):
    """Test cases for Model Training History API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.model = MLModel.objects.create(
            name='Test Model',
            model_type='cost_prediction',
            algorithm='Random Forest',
            feature_columns=['feature1'],
            target_column='target',
            created_by=self.user
        )
        
        self.training_history = ModelTrainingHistory.objects.create(
            model=self.model,
            training_run_id='test_run_001',
            training_accuracy=0.85,
            validation_accuracy=0.82,
            training_loss=0.15,
            validation_loss=0.18,
            epochs=100,
            batch_size=32,
            learning_rate=0.001,
            started_at=timezone.now() - timedelta(hours=1),
            completed_at=timezone.now(),
            duration=timedelta(hours=1),
            data_size=1000,
            status='completed'
        )
    
    def test_list_training_history(self):
        """Test listing training history"""
        url = reverse('ai_models:traininghistory-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['training_run_id'], 'test_run_001')
    
    def test_metrics_over_time(self):
        """Test metrics over time endpoint"""
        url = reverse('ai_models:traininghistory-metrics-over-time')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['training_run_id'], 'test_run_001')
    
    def test_metrics_over_time_with_model_filter(self):
        """Test metrics over time with model filter"""
        url = reverse('ai_models:traininghistory-metrics-over-time')
        response = self.client.get(url, {'model_id': self.model.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_metrics_over_time_with_date_filter(self):
        """Test metrics over time with date filter"""
        url = reverse('ai_models:traininghistory-metrics-over-time')
        response = self.client.get(url, {'days': 7})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still return 1 result since training was within last hour
        self.assertEqual(len(response.data), 1)
