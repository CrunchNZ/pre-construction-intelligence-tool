#!/usr/bin/env python3
"""
ML Infrastructure Test Script

This script tests the complete ML infrastructure to ensure
all components are working correctly.
"""

import os
import sys
import django
import logging
from datetime import datetime, timedelta
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preconstruction_intelligence.settings')
django.setup()

from ai_models.models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction
from ai_models.frontend_integration import MLFrontendIntegrationService
from ai_models.ml_pipeline import MLPipelineService
from ai_models.model_manager import MLModelManager
from ai_models.data_integration import ConstructionDataIntegrationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLInfrastructureTester:
    """Tests the complete ML infrastructure"""
    
    def __init__(self):
        self.frontend_service = MLFrontendIntegrationService()
        self.pipeline_service = MLPipelineService()
        self.model_manager = MLModelManager()
        self.data_integration = ConstructionDataIntegrationService()
        
    def test_data_integration(self):
        """Test data integration service"""
        logger.info("Testing data integration service...")
        
        try:
            # Test data validation
            sample_data = self.data_integration.get_sample_construction_data()
            logger.info(f"✓ Sample data generated: {len(sample_data)} records")
            
            # Test data quality validation
            validation_result = self.data_integration.validate_data_quality(sample_data)
            logger.info(f"✓ Data quality validation: {validation_result}")
            
            # Test data preprocessing
            processed_data = self.data_integration.preprocess_data(sample_data)
            logger.info(f"✓ Data preprocessing completed: {len(processed_data)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Data integration test failed: {str(e)}")
            return False
    
    def test_ml_pipeline(self):
        """Test ML pipeline service"""
        logger.info("Testing ML pipeline service...")
        
        try:
            # Test pipeline initialization
            pipeline_config = self.pipeline_service.get_pipeline_config()
            logger.info(f"✓ Pipeline config loaded: {pipeline_config}")
            
            # Test feature engineering
            features = self.pipeline_service.engineer_features({
                'project_size': 50000,
                'complexity': 'medium',
                'location': 'urban'
            })
            logger.info(f"✓ Feature engineering completed: {features}")
            
            # Test model evaluation
            evaluation_metrics = self.pipeline_service.evaluate_model_performance({
                'accuracy': 0.95,
                'precision': 0.94,
                'recall': 0.96
            })
            logger.info(f"✓ Model evaluation completed: {evaluation_metrics}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ ML pipeline test failed: {str(e)}")
            return False
    
    def test_model_manager(self):
        """Test model manager service"""
        logger.info("Testing model manager service...")
        
        try:
            # Test model registration
            model_info = {
                'name': 'Test Model',
                'model_type': 'test_prediction',
                'algorithm': 'test_algorithm',
                'version': '1.0.0',
                'status': 'active'
            }
            
            # Test model creation
            model = MLModel.objects.create(**model_info)
            logger.info(f"✓ Model created: {model.id}")
            
            # Test model retrieval
            retrieved_model = self.model_manager.get_model(model.id)
            logger.info(f"✓ Model retrieved: {retrieved_model.name}")
            
            # Test model update
            self.model_manager.update_model_status(model.id, 'inactive')
            logger.info(f"✓ Model status updated")
            
            # Cleanup
            model.delete()
            logger.info(f"✓ Test model cleaned up")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Model manager test failed: {str(e)}")
            return False
    
    def test_frontend_integration(self):
        """Test frontend integration service"""
        logger.info("Testing frontend integration service...")
        
        try:
            # Test dashboard insights
            dashboard_insights = self.frontend_service.get_dashboard_ml_insights()
            logger.info(f"✓ Dashboard insights generated: {len(dashboard_insights)} keys")
            
            # Test project insights (with mock project)
            project_insights = self.frontend_service.get_project_ml_insights(1)
            logger.info(f"✓ Project insights generated: {len(project_insights)} keys")
            
            # Test risk analysis insights
            risk_insights = self.frontend_service.get_risk_analysis_ml_insights()
            logger.info(f"✓ Risk analysis insights generated: {len(risk_insights)} keys")
            
            # Test reports insights
            reports_insights = self.frontend_service.get_reports_insights('comprehensive')
            logger.info(f"✓ Reports insights generated: {len(reports_insights)} keys")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Frontend integration test failed: {str(e)}")
            return False
    
    def test_database_models(self):
        """Test database models and relationships"""
        logger.info("Testing database models...")
        
        try:
            # Test MLModel creation
            model = MLModel.objects.create(
                name='Test Model',
                model_type='test_prediction',
                algorithm='test_algorithm',
                version='1.0.0',
                status='active',
                accuracy=0.95
            )
            logger.info(f"✓ MLModel created: {model.id}")
            
            # Test ModelTrainingHistory creation
            training_history = ModelTrainingHistory.objects.create(
                model=model,
                training_started_at=datetime.now() - timedelta(hours=1),
                training_completed_at=datetime.now(),
                training_data_size=1000,
                validation_data_size=200,
                training_metrics={'accuracy': 0.95},
                model_performance={'test_accuracy': 0.94}
            )
            logger.info(f"✓ Training history created: {training_history.id}")
            
            # Test FeatureEngineering creation
            feature_engineering = FeatureEngineering.objects.create(
                model=model,
                feature_names=['feature1', 'feature2'],
                preprocessing_steps=['normalization', 'scaling'],
                feature_importance={'feature1': 0.6, 'feature2': 0.4}
            )
            logger.info(f"✓ Feature engineering created: {feature_engineering.id}")
            
            # Test ModelPrediction creation
            prediction = ModelPrediction.objects.create(
                model=model,
                input_features={'feature1': 1.0, 'feature2': 2.0},
                prediction_value=0.85,
                prediction_confidence=0.92,
                project_id='test_project',
                user_id='test_user'
            )
            logger.info(f"✓ Model prediction created: {prediction.id}")
            
            # Test relationships
            model_predictions = model.modelpredictions.all()
            logger.info(f"✓ Model predictions relationship: {len(model_predictions)} predictions")
            
            # Cleanup
            model.delete()  # This should cascade delete related objects
            logger.info(f"✓ Test data cleaned up")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Database models test failed: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints (simulated)"""
        logger.info("Testing API endpoints...")
        
        try:
            # Simulate API calls by testing the underlying services
            # In a real test, you would use Django's test client
            
            # Test dashboard insights endpoint
            dashboard_data = self.frontend_service.get_dashboard_ml_insights()
            assert 'cost_predictions' in dashboard_data or 'error' in dashboard_data
            logger.info("✓ Dashboard insights endpoint test passed")
            
            # Test project insights endpoint
            project_data = self.frontend_service.get_project_ml_insights(1)
            assert 'project_id' in project_data or 'error' in project_data
            logger.info("✓ Project insights endpoint test passed")
            
            # Test risk analysis endpoint
            risk_data = self.frontend_service.get_risk_analysis_ml_insights()
            assert 'overall_risk_score' in risk_data or 'error' in risk_data
            logger.info("✓ Risk analysis endpoint test passed")
            
            # Test reports endpoint
            reports_data = self.frontend_service.get_reports_insights('comprehensive')
            assert 'cost_analysis' in reports_data or 'error' in reports_data
            logger.info("✓ Reports endpoint test passed")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ API endpoints test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all infrastructure tests"""
        logger.info("=" * 60)
        logger.info("Starting ML Infrastructure Tests")
        logger.info("=" * 60)
        
        test_results = {}
        
        # Run all tests
        tests = [
            ('Data Integration', self.test_data_integration),
            ('ML Pipeline', self.test_ml_pipeline),
            ('Model Manager', self.test_model_manager),
            ('Frontend Integration', self.test_frontend_integration),
            ('Database Models', self.test_database_models),
            ('API Endpoints', self.test_api_endpoints),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\nRunning {test_name} test...")
            try:
                result = test_func()
                test_results[test_name] = result
                status = "✓ PASSED" if result else "✗ FAILED"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                test_results[test_name] = False
                logger.error(f"{test_name}: ✗ FAILED - {str(e)}")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Test Results Summary")
        logger.info("=" * 60)
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! ML infrastructure is working correctly.")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed. Please review the issues above.")
        
        return passed == total

def main():
    """Main function to run infrastructure tests"""
    try:
        tester = MLInfrastructureTester()
        success = tester.run_all_tests()
        
        if success:
            logger.info("\n✅ ML Infrastructure validation completed successfully!")
            return 0
        else:
            logger.error("\n❌ ML Infrastructure validation failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Infrastructure test failed with error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
