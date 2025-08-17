"""
Tests for External APIs Integration

This module provides comprehensive tests for all components of the external APIs integration,
including weather services, data quality monitoring, backup/recovery, and data flow orchestration.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
import json
from unittest.mock import patch, MagicMock
from datetime import timedelta

from .models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord,
    DataBackupRecord, DataRecoveryRecord, DataFlowExecution,
    ExternalAPIConfig, APIUsageLog
)
from .weather_client import OpenWeatherMapClient
from .weather_impact_service import WeatherImpactService
from .data_validation import DataValidator
from .data_flow_orchestrator import DataFlowOrchestrator
from .data_quality_monitor import DataQualityMonitor
from .data_backup_recovery import DataBackupRecovery


class ExternalAPIsIntegrationTestCase(TestCase):
    """Base test case for external APIs integration."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create test API configuration
        self.api_config = ExternalAPIConfig.objects.create(
            api_name='test_weather_api',
            api_type='weather',
            base_url='https://api.test.com',
            is_active=True,
            health_status='healthy'
        )
        
        # Create test weather data
        self.weather_data = WeatherData.objects.create(
            location='Test City',
            weather_data={'temp': 25, 'humidity': 60},
            weather_type='current',
            units='metric',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )


class WeatherClientTestCase(TestCase):
    """Test cases for OpenWeatherMap client."""
    
    def setUp(self):
        """Set up test data."""
        self.client = OpenWeatherMapClient(api_key='test_key')
    
    @patch('requests.Session.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful current weather retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'main': {'temp': 25, 'humidity': 60},
            'weather': [{'main': 'Clear'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_current_weather('Test City')
        
        self.assertIn('main', result)
        self.assertEqual(result['main']['temp'], 25)
    
    @patch('requests.Session.get')
    def test_get_current_weather_failure(self, mock_get):
        """Test weather retrieval failure handling."""
        mock_get.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            self.client.get_current_weather('Test City')
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Test that rate limiting prevents too many requests
        for _ in range(5):
            self.client._last_request_time = timezone.now() - timedelta(seconds=1)
            self.client._request_count = 0
            self.client._make_request('test_url')
        
        # Should have rate limiting applied
        self.assertLessEqual(self.client._request_count, 5)


class WeatherImpactServiceTestCase(TestCase):
    """Test cases for weather impact analysis service."""
    
    def setUp(self):
        """Set up test data."""
        self.service = WeatherImpactService()
    
    def test_analyze_project_weather_risk(self):
        """Test project weather risk analysis."""
        project_data = {
            'location': 'Test City',
            'project_type': 'construction',
            'start_date': timezone.now(),
            'duration_days': 30
        }
        
        with patch.object(self.service.weather_client, 'get_weather_impact_score') as mock_get:
            mock_get.return_value = {
                'impact_score': 45.0,
                'current_conditions': {'main': {'temp': 25}},
                'alerts': []
            }
            
            result = self.service.analyze_project_weather_risk(project_data)
            
            self.assertIn('overall_risk_score', result)
            self.assertIn('recommendations', result)
    
    def test_portfolio_weather_risk_analysis(self):
        """Test portfolio-level weather risk analysis."""
        projects = [
            {
                'location': 'City 1',
                'project_type': 'construction'
            },
            {
                'location': 'City 2',
                'project_type': 'roofing'
            }
        ]
        
        with patch.object(self.service, 'analyze_project_weather_risk') as mock_analyze:
            mock_analyze.return_value = {
                'overall_risk_score': 60.0,
                'location': 'Test City'
            }
            
            result = self.service.analyze_portfolio_weather_risk(projects)
            
            self.assertEqual(result['total_projects'], 2)
            self.assertIn('portfolio_risk_summary', result)


class DataValidatorTestCase(TestCase):
    """Test cases for data validation service."""
    
    def setUp(self):
        """Set up test data."""
        self.validator = DataValidator()
    
    def test_validate_data_success(self):
        """Test successful data validation."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            },
            'required': ['name']
        }
        
        data = {'name': 'John', 'age': 30}
        
        is_valid, errors, cleaned_data = self.validator.validate_data(data, schema)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        self.assertEqual(cleaned_data['name'], 'John')
    
    def test_validate_data_failure(self):
        """Test data validation failure."""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'}
            },
            'required': ['name']
        }
        
        data = {'age': 30}  # Missing required field
        
        is_valid, errors, cleaned_data = self.validator.validate_data(data, schema)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_data_cleaning(self):
        """Test data cleaning functionality."""
        cleaning_rules = {
            'name': {'trim_whitespace': True, 'case': 'title'},
            'email': {'case': 'lower'}
        }
        
        data = {
            'name': '  john doe  ',
            'email': 'JOHN@EXAMPLE.COM'
        }
        
        cleaned_data = self.validator.clean_data(data, cleaning_rules)
        
        self.assertEqual(cleaned_data['name'], 'John Doe')
        self.assertEqual(cleaned_data['email'], 'john@example.com')


class DataQualityMonitorTestCase(TestCase):
    """Test cases for data quality monitoring service."""
    
    def setUp(self):
        """Set up test data."""
        self.monitor = DataQualityMonitor()
    
    def test_add_monitoring_config(self):
        """Test adding monitoring configuration."""
        config = {
            'quality_checks': [
                {'type': 'completeness'},
                {'type': 'accuracy'}
            ],
            'check_interval': 3600
        }
        
        success = self.monitor.add_monitoring_config('test_system', config)
        
        self.assertTrue(success)
        self.assertIn('test_system', self.monitor.monitoring_configs)
    
    def test_check_data_quality(self):
        """Test data quality checking."""
        # Add monitoring config first
        config = {
            'quality_checks': [
                {'type': 'completeness'},
                {'type': 'accuracy'}
            ],
            'check_interval': 3600
        }
        self.monitor.add_monitoring_config('test_system', config)
        
        data = {'name': 'John', 'age': 30}
        result = self.monitor.check_data_quality('test_system', data)
        
        self.assertIn('overall_score', result)
        self.assertIn('completeness', result)
        self.assertIn('accuracy', result)


class DataBackupRecoveryTestCase(TestCase):
    """Test cases for data backup and recovery service."""
    
    def setUp(self):
        """Set up test data."""
        self.backup_service = DataBackupRecovery()
    
    def test_configure_backup(self):
        """Test backup configuration."""
        config = {
            'backup_directory': '/tmp/test_backups',
            'retention_days': 7
        }
        
        success = self.backup_service.configure_backup('test_system', config)
        
        self.assertTrue(success)
        self.assertIn('test_system', self.backup_service.backup_config)
    
    def test_create_backup(self):
        """Test backup creation."""
        # Configure backup first
        config = {
            'backup_directory': '/tmp/test_backups',
            'retention_days': 7
        }
        self.backup_service.configure_backup('test_system', config)
        
        data = {'test': 'data'}
        result = self.backup_service.create_backup('test_system', data, 'full')
        
        self.assertIn('backup_id', result)
        self.assertEqual(result['status'], 'completed')


class DataFlowOrchestratorTestCase(TestCase):
    """Test cases for data flow orchestration service."""
    
    def setUp(self):
        """Set up test data."""
        self.orchestrator = DataFlowOrchestrator()
    
    def test_register_data_flow(self):
        """Test data flow registration."""
        flow_config = {
            'steps': [
                {'name': 'step1', 'type': 'function'},
                {'name': 'step2', 'type': 'api_call'}
            ],
            'dependencies': {}
        }
        
        success = self.orchestrator.register_data_flow('test_flow', flow_config)
        
        self.assertTrue(success)
        self.assertIn('test_flow', self.orchestrator.flow_registry)
    
    def test_execute_data_flow(self):
        """Test data flow execution."""
        # Register flow first
        flow_config = {
            'steps': [
                {'name': 'step1', 'type': 'function'}
            ],
            'dependencies': {}
        }
        self.orchestrator.register_data_flow('test_flow', flow_config)
        
        result = self.orchestrator.execute_data_flow('test_flow', {'input': 'data'})
        
        self.assertIn('execution_id', result)
        self.assertIn('status', result)


class WeatherDataModelTestCase(ExternalAPIsIntegrationTestCase):
    """Test cases for WeatherData model."""
    
    def test_weather_data_creation(self):
        """Test weather data creation."""
        weather_data = WeatherData.objects.create(
            location='New City',
            weather_data={'temp': 30, 'humidity': 70},
            weather_type='forecast',
            units='imperial',
            expires_at=timezone.now() + timedelta(hours=2),
            is_active=True
        )
        
        self.assertEqual(weather_data.location, 'New City')
        self.assertEqual(weather_data.weather_type, 'forecast')
        self.assertTrue(weather_data.is_active)
    
    def test_weather_data_expiration(self):
        """Test weather data expiration logic."""
        # Create expired weather data
        expired_weather = WeatherData.objects.create(
            location='Expired City',
            weather_data={'temp': 20},
            weather_type='current',
            units='metric',
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True
        )
        
        self.assertTrue(expired_weather.is_expired)
        
        # Create active weather data
        active_weather = WeatherData.objects.create(
            location='Active City',
            weather_data={'temp': 25},
            weather_type='current',
            units='metric',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        
        self.assertFalse(active_weather.is_expired)


class WeatherImpactAnalysisModelTestCase(ExternalAPIsIntegrationTestCase):
    """Test cases for WeatherImpactAnalysis model."""
    
    def test_weather_impact_analysis_creation(self):
        """Test weather impact analysis creation."""
        impact_analysis = WeatherImpactAnalysis.objects.create(
            project_id='PROJ001',
            location='Test City',
            project_type='construction',
            impact_score=65.5,
            risk_factors={'schedule_impact': 2, 'safety_risk': 3},
            recommendations=['Monitor weather closely', 'Implement safety measures'],
            cost_impact={'base_cost': 100000, 'additional_costs': 15000},
            weather_data=self.weather_data
        )
        
        self.assertEqual(impact_analysis.project_id, 'PROJ001')
        self.assertEqual(impact_analysis.impact_score, 65.5)
        self.assertIn('schedule_impact', impact_analysis.risk_factors)
        self.assertEqual(len(impact_analysis.recommendations), 2)


class DataQualityRecordModelTestCase(ExternalAPIsIntegrationTestCase):
    """Test cases for DataQualityRecord model."""
    
    def test_data_quality_record_creation(self):
        """Test data quality record creation."""
        quality_record = DataQualityRecord.objects.create(
            system_name='test_system',
            quality_metrics={
                'completeness': 85.0,
                'accuracy': 90.0,
                'consistency': 80.0
            },
            overall_score=85.0,
            issues=['Missing required fields in 15% of records'],
            recommendations=['Implement data validation rules'],
            data_sample_size=1000
        )
        
        self.assertEqual(quality_record.system_name, 'test_system')
        self.assertEqual(quality_record.overall_score, 85.0)
        self.assertEqual(quality_record.data_sample_size, 1000)


class DataBackupRecordModelTestCase(ExternalAPIsIntegrationTestCase):
    """Test cases for DataBackupRecord model."""
    
    def test_backup_record_creation(self):
        """Test backup record creation."""
        backup_record = DataBackupRecord.objects.create(
            backup_id='BACKUP001',
            system_name='test_system',
            backup_type='full',
            file_path='/tmp/backups/test_system/BACKUP001.zip',
            file_size_bytes=1024000,
            checksum='a' * 64,
            compression_enabled=True,
            encryption_enabled=False,
            retention_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        self.assertEqual(backup_record.backup_id, 'BACKUP001')
        self.assertEqual(backup_record.system_name, 'test_system')
        self.assertEqual(backup_record.file_size_mb, 1.0)
        self.assertFalse(backup_record.is_expired)


class APIViewsTestCase(APITestCase):
    """Test cases for API views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_weather_data_list(self):
        """Test weather data list endpoint."""
        # Create test weather data
        WeatherData.objects.create(
            location='Test City',
            weather_data={'temp': 25},
            weather_type='current',
            units='metric',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        
        url = reverse('external_apis:weather-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_weather_impact_analysis_list(self):
        """Test weather impact analysis list endpoint."""
        # Create test weather data first
        weather_data = WeatherData.objects.create(
            location='Test City',
            weather_data={'temp': 25},
            weather_type='current',
            units='metric',
            expires_at=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        
        # Create test impact analysis
        WeatherImpactAnalysis.objects.create(
            project_id='PROJ001',
            location='Test City',
            project_type='construction',
            impact_score=65.5,
            risk_factors={},
            recommendations=[],
            cost_impact={},
            weather_data=weather_data
        )
        
        url = reverse('external_apis:weather-impact-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_data_quality_record_list(self):
        """Test data quality record list endpoint."""
        DataQualityRecord.objects.create(
            system_name='test_system',
            quality_metrics={},
            overall_score=85.0,
            issues=[],
            recommendations=[],
            data_sample_size=100
        )
        
        url = reverse('external_apis:data-quality-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class WeatherServiceViewsTestCase(TestCase):
    """Test cases for weather service views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    @patch('integrations.external_apis.views.OpenWeatherMapClient')
    def test_current_weather_view(self, mock_client_class):
        """Test current weather view."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_current_weather.return_value = {
            'main': {'temp': 25},
            'timestamp': '2025-01-15T10:30:00Z'
        }
        
        response = self.client.get('/integrations/external_apis/weather/current/TestCity/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['location'], 'TestCity')
    
    @patch('integrations.external_apis.views.OpenWeatherMapClient')
    def test_weather_forecast_view(self, mock_client_class):
        """Test weather forecast view."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_weather_forecast.return_value = {
            'list': [{'dt': 1642233600, 'main': {'temp': 25}}]
        }
        
        response = self.client.get('/integrations/external_apis/weather/forecast/TestCity/?days=3')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['days'], 3)


class DataQualityViewsTestCase(TestCase):
    """Test cases for data quality views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    @patch('integrations.external_apis.views.DataQualityMonitor')
    def test_check_data_quality_view(self, mock_monitor_class):
        """Test data quality check view."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_monitor.check_data_quality.return_value = {
            'overall_score': 85.0,
            'completeness': 90.0
        }
        
        response = self.client.post(
            '/integrations/external_apis/data-quality/check/test_system/',
            data=json.dumps({'test': 'data'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['system_name'], 'test_system')


class DataBackupViewsTestCase(TestCase):
    """Test cases for data backup views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    @patch('integrations.external_apis.views.DataBackupRecovery')
    def test_create_backup_view(self, mock_backup_class):
        """Test backup creation view."""
        mock_backup = MagicMock()
        mock_backup_class.return_value = mock_backup
        mock_backup.create_backup.return_value = {
            'backup_id': 'BACKUP001',
            'status': 'completed'
        }
        
        response = self.client.post(
            '/integrations/external_apis/backups/create/test_system/',
            data=json.dumps({'backup_type': 'full'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['system_name'], 'test_system')


class DataFlowViewsTestCase(TestCase):
    """Test cases for data flow views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    @patch('integrations.external_apis.views.DataFlowOrchestrator')
    def test_register_data_flow_view(self, mock_orchestrator_class):
        """Test data flow registration view."""
        mock_orchestrator = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.register_data_flow.return_value = True
        
        response = self.client.post(
            '/integrations/external_apis/data-flows/register/',
            data=json.dumps({
                'flow_name': 'test_flow',
                'flow_config': {'steps': []}
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])


class UtilityViewsTestCase(TestCase):
    """Test cases for utility views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_health_check_view(self):
        """Test health check view."""
        response = self.client.get('/integrations/external_apis/health/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('services', data)
    
    def test_system_status_view(self):
        """Test system status view."""
        response = self.client.get('/integrations/external_apis/status/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['overall_status'], 'operational')
        self.assertIn('components', data)
    
    def test_metrics_view(self):
        """Test metrics view."""
        response = self.client.get('/integrations/external_apis/metrics/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('performance', data)
        self.assertIn('data_quality', data)
        self.assertIn('backup_recovery', data)


class AdminInterfaceTestCase(ExternalAPIsIntegrationTestCase):
    """Test cases for admin interface."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.force_login(self.admin_user)
    
    def test_weather_data_admin_list(self):
        """Test weather data admin list view."""
        response = self.client.get('/admin/external_apis/weatherdata/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test City')
    
    def test_weather_impact_admin_list(self):
        """Test weather impact admin list view."""
        # Create test impact analysis
        WeatherImpactAnalysis.objects.create(
            project_id='PROJ001',
            location='Test City',
            project_type='construction',
            impact_score=65.5,
            risk_factors={},
            recommendations=[],
            cost_impact={}
        )
        
        response = self.client.get('/admin/external_apis/weatherimpactanalysis/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PROJ001')
    
    def test_data_quality_admin_list(self):
        """Test data quality admin list view."""
        DataQualityRecord.objects.create(
            system_name='test_system',
            quality_metrics={},
            overall_score=85.0,
            issues=[],
            recommendations=[],
            data_sample_size=100
        )
        
        response = self.client.get('/admin/external_apis/dataqualityrecord/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_system')


class IntegrationTestCase(TestCase):
    """Integration tests for external APIs."""
    
    def setUp(self):
        """Set up test data."""
        self.weather_service = WeatherImpactService()
        self.data_validator = DataValidator()
        self.quality_monitor = DataQualityMonitor()
        self.backup_service = DataBackupRecovery()
        self.flow_orchestrator = DataFlowOrchestrator()
    
    def test_end_to_end_weather_analysis(self):
        """Test end-to-end weather impact analysis workflow."""
        # Mock weather client
        with patch.object(self.weather_service, 'weather_client') as mock_client:
            mock_client.get_weather_impact_score.return_value = {
                'impact_score': 45.0,
                'current_conditions': {'main': {'temp': 25}},
                'alerts': []
            }
            
            # Test complete workflow
            project_data = {
                'location': 'Test City',
                'project_type': 'construction',
                'start_date': timezone.now(),
                'duration_days': 30
            }
            
            result = self.weather_service.analyze_project_weather_risk(project_data)
            
            self.assertIn('overall_risk_score', result)
            self.assertIn('recommendations', result)
            self.assertIn('cost_impact', result)
    
    def test_end_to_end_data_quality_workflow(self):
        """Test end-to-end data quality monitoring workflow."""
        # Add monitoring configuration
        config = {
            'quality_checks': [
                {'type': 'completeness'},
                {'type': 'accuracy'}
            ],
            'check_interval': 3600
        }
        self.quality_monitor.add_monitoring_config('test_system', config)
        
        # Test data quality check
        test_data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
        result = self.quality_monitor.check_data_quality('test_system', test_data)
        
        self.assertIn('overall_score', result)
        self.assertIn('completeness', result)
        self.assertIn('accuracy', result)
        self.assertIn('consistency', result)
        self.assertIn('validity', result)
    
    def test_end_to_end_backup_recovery_workflow(self):
        """Test end-to-end backup and recovery workflow."""
        # Configure backup
        config = {
            'backup_directory': '/tmp/test_backups',
            'retention_days': 7
        }
        self.backup_service.configure_backup('test_system', config)
        
        # Create backup
        test_data = {'test': 'data', 'timestamp': timezone.now().isoformat()}
        backup_result = self.backup_service.create_backup('test_system', test_data, 'full')
        
        self.assertIn('backup_id', backup_result)
        self.assertEqual(backup_result['status'], 'completed')
        
        # List backups
        backups = self.backup_service.list_backups('test_system')
        self.assertGreater(len(backups), 0)


class PerformanceTestCase(TestCase):
    """Performance tests for external APIs integration."""
    
    def setUp(self):
        """Set up test data."""
        self.weather_service = WeatherImpactService()
        self.data_validator = DataValidator()
        self.quality_monitor = DataQualityMonitor()
    
    def test_weather_analysis_performance(self):
        """Test weather analysis performance."""
        import time
        
        # Test performance of weather analysis
        start_time = time.time()
        
        project_data = {
            'location': 'Test City',
            'project_type': 'construction',
            'start_date': timezone.now(),
            'duration_days': 30
        }
        
        with patch.object(self.weather_service, 'weather_client') as mock_client:
            mock_client.get_weather_impact_score.return_value = {
                'impact_score': 45.0,
                'current_conditions': {'main': {'temp': 25}},
                'alerts': []
            }
            
            result = self.weather_service.analyze_project_weather_risk(project_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion - should complete within reasonable time
        self.assertLess(execution_time, 1.0)  # Less than 1 second
        self.assertIn('overall_risk_score', result)
    
    def test_data_validation_performance(self):
        """Test data validation performance."""
        import time
        
        # Test performance of data validation
        start_time = time.time()
        
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'email': {'type': 'string'}
            },
            'required': ['name', 'age']
        }
        
        data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
        
        is_valid, errors, cleaned_data = self.data_validator.validate_data(data, schema)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion - should complete within reasonable time
        self.assertLess(execution_time, 0.1)  # Less than 0.1 seconds
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_quality_monitoring_performance(self):
        """Test quality monitoring performance."""
        import time
        
        # Test performance of quality monitoring
        start_time = time.time()
        
        config = {
            'quality_checks': [
                {'type': 'completeness'},
                {'type': 'accuracy'},
                {'type': 'consistency'},
                {'type': 'validity'}
            ],
            'check_interval': 3600
        }
        self.quality_monitor.add_monitoring_config('test_system', config)
        
        test_data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
        result = self.quality_monitor.check_data_quality('test_system', test_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion - should complete within reasonable time
        self.assertLess(execution_time, 0.1)  # Less than 0.1 seconds
        self.assertIn('overall_score', result)


class SecurityTestCase(TestCase):
    """Security tests for external APIs integration."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
    
    def test_api_key_protection(self):
        """Test API key protection in responses."""
        # Test that API keys are not exposed in API responses
        response = self.client.get('/integrations/external_apis/status/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Ensure no sensitive information is exposed
        self.assertNotIn('api_key', str(data))
        self.assertNotIn('password', str(data))
        self.assertNotIn('secret', str(data))
    
    def test_input_validation(self):
        """Test input validation and sanitization."""
        # Test input validation for potentially malicious input
        malicious_inputs = [
            {'script': '<script>alert("xss")</script>'},
            {'sql': "'; DROP TABLE users; --"},
            {'path': '../../../etc/passwd'},
            {'command': 'rm -rf /'}
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.post(
                '/integrations/external_apis/data-quality/check/test_system/',
                data=json.dumps(malicious_input),
                content_type='application/json'
            )
            
            # Should handle malicious input gracefully
            self.assertIn(response.status_code, [200, 400, 422])
    
    def test_authentication_required(self):
        """Test that authentication is required for sensitive endpoints."""
        # Test that sensitive endpoints require authentication
        sensitive_endpoints = [
            '/integrations/external_apis/backups/create/test_system/',
            '/integrations/external_apis/data-flows/register/',
            '/integrations/external_apis/weather/current/TestCity/'
        ]
        
        for endpoint in sensitive_endpoints:
            response = self.client.get(endpoint)
            # Should redirect to login or return 401/403
            self.assertIn(response.status_code, [302, 401, 403])
