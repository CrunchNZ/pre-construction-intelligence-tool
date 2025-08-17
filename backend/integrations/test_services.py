"""
Comprehensive Tests for Task 3 Services

This module tests all the services created for Task 3: Procore & Jobpac Integration
including the sync service, analytics service, automated updates, and change detection.

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    IntegrationSystem,
    UnifiedProject,
    ProjectSystemMapping,
    ProjectDocument,
    ProjectSchedule,
    ProjectFinancial,
    ProjectChangeOrder,
    ProjectRFI,
)
from .sync_service import ProjectSyncService
from .analytics_service import ProjectAnalyticsService
from .automated_updates import AutomatedUpdateService
from .change_detection import ChangeDetectionService


class ProjectSyncServiceTestCase(TestCase):
    """Test cases for ProjectSyncService."""
    
    def setUp(self):
        """Set up test data."""
        # Create test integration systems
        self.procurepro_system = IntegrationSystem.objects.create(
            name='Test ProcurePro',
            system_type='procurepro',
            status='active',
            connection_status='active'
        )
        
        self.procore_system = IntegrationSystem.objects.create(
            name='Test Procore',
            system_type='procore',
            status='active',
            connection_status='active'
        )
        
        self.jobpac_system = IntegrationSystem.objects.create(
            name='Test Jobpac',
            system_type='jobpac',
            status='active',
            connection_status='active'
        )
        
        # Create test project
        self.test_project = UnifiedProject.objects.create(
            name='Test Project',
            description='Test project description',
            project_number='TEST-001',
            status='planning',
            project_type='commercial',
            budget=100000.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date()
        )
        
        # Create test project mapping
        self.project_mapping = ProjectSystemMapping.objects.create(
            project=self.test_project,
            system=self.procurepro_system,
            external_project_id='12345',
            external_project_number='TEST-001',
            external_project_name='Test Project',
            sync_status='completed'
        )
    
    def test_sync_service_initialization(self):
        """Test sync service initialization."""
        service = ProjectSyncService()
        self.assertIsNotNone(service)
        self.assertEqual(service.sync_stats['projects_processed'], 0)
        self.assertEqual(service.sync_stats['projects_created'], 0)
        self.assertEqual(service.sync_stats['projects_updated'], 0)
    
    def test_get_client_procurepro(self):
        """Test getting ProcurePro client."""
        service = ProjectSyncService()
        client = service.get_client('procurepro')
        self.assertIsNotNone(client)
        self.assertEqual(client.__class__.__name__, 'ProcureProAPIClient')
    
    def test_get_client_procore(self):
        """Test getting Procore client."""
        service = ProjectSyncService()
        client = service.get_client('procore')
        self.assertIsNotNone(client)
        self.assertEqual(client.__class__.__name__, 'ProcoreAPIClient')
    
    def test_get_client_jobpac(self):
        """Test getting Jobpac client."""
        service = ProjectSyncService()
        client = service.get_client('jobpac')
        self.assertIsNotNone(client)
        self.assertEqual(client.__class__.__name__, 'JobpacAPIClient')
    
    def test_get_client_invalid_type(self):
        """Test getting client with invalid system type."""
        service = ProjectSyncService()
        with self.assertRaises(ValueError):
            service.get_client('invalid_system')
    
    @patch('integrations.sync_service.ProcureProAPIClient')
    def test_sync_system_projects_procurepro(self, mock_client_class):
        """Test syncing projects from ProcurePro system."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_projects.return_value = [
            {
                'id': '12345',
                'name': 'Test Project',
                'project_number': 'TEST-001',
                'status': 'active',
                'budget': 100000.00
            }
        ]
        mock_client_class.return_value = mock_client
        
        service = ProjectSyncService()
        result = service.sync_system_projects(self.procurepro_system, force_full_sync=False)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['projects_processed'], 1)
        self.assertEqual(result['projects_updated'], 1)
    
    def test_map_project_status(self):
        """Test project status mapping."""
        service = ProjectSyncService()
        
        # Test various status mappings
        self.assertEqual(service._map_project_status('planning'), 'planning')
        self.assertEqual(service._map_project_status('active'), 'construction')
        self.assertEqual(service._map_project_status('completed'), 'completed')
        self.assertEqual(service._map_project_status('on_hold'), 'on_hold')
        self.assertEqual(service._map_project_status('unknown'), 'planning')
    
    def test_map_project_type(self):
        """Test project type mapping."""
        service = ProjectSyncService()
        
        # Test various type mappings
        self.assertEqual(service._map_project_type('commercial'), 'commercial')
        self.assertEqual(service._map_project_type('residential'), 'residential')
        self.assertEqual(service._map_project_type('office'), 'commercial')
        self.assertEqual(service._map_project_type('unknown'), 'other')
    
    def test_parse_date(self):
        """Test date parsing."""
        service = ProjectSyncService()
        
        # Test string date parsing
        date_str = '2025-08-15'
        parsed_date = service._parse_date(date_str)
        self.assertEqual(parsed_date, datetime(2025, 8, 15).date())
        
        # Test None date
        self.assertIsNone(service._parse_date(None))
        
        # Test invalid date
        self.assertIsNone(service._parse_date('invalid-date'))
    
    def test_parse_decimal(self):
        """Test decimal parsing."""
        service = ProjectSyncService()
        
        # Test valid decimal
        self.assertEqual(service._parse_decimal('100.50'), 100.50)
        self.assertEqual(service._parse_decimal(100.50), 100.50)
        
        # Test None value
        self.assertIsNone(service._parse_decimal(None))
        
        # Test invalid value
        self.assertIsNone(service._parse_decimal('invalid'))


class ProjectAnalyticsServiceTestCase(TestCase):
    """Test cases for ProjectAnalyticsService."""
    
    def setUp(self):
        """Set up test data."""
        # Create test integration system
        self.test_system = IntegrationSystem.objects.create(
            name='Test System',
            system_type='procurepro',
            status='active',
            connection_status='active'
        )
        
        # Create test projects
        self.project1 = UnifiedProject.objects.create(
            name='Project 1',
            description='Test project 1',
            project_number='PROJ-001',
            status='construction',
            project_type='commercial',
            budget=100000.00,
            actual_cost=95000.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            progress_percentage=75.0
        )
        
        self.project2 = UnifiedProject.objects.create(
            name='Project 2',
            description='Test project 2',
            project_number='PROJ-002',
            status='planning',
            project_type='residential',
            budget=200000.00,
            actual_cost=220000.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=60)).date(),
            progress_percentage=25.0
        )
        
        # Add systems to projects
        self.project1.integration_systems.add(self.test_system)
        self.project2.integration_systems.add(self.test_system)
    
    def test_analytics_service_initialization(self):
        """Test analytics service initialization."""
        service = ProjectAnalyticsService()
        self.assertIsNotNone(service)
        self.assertEqual(service.cache_timeout, 3600)
    
    def test_get_portfolio_summary(self):
        """Test portfolio summary generation."""
        service = ProjectAnalyticsService()
        summary = service.get_portfolio_summary()
        
        self.assertIn('total_projects', summary)
        self.assertEqual(summary['total_projects'], 2)
        self.assertIn('active_projects', summary)
        self.assertEqual(summary['active_projects'], 1)
        self.assertIn('planning_projects', summary)
        self.assertEqual(summary['planning_projects'], 1)
        self.assertIn('total_budget', summary)
        self.assertEqual(summary['total_budget'], 300000.0)
    
    def test_get_project_analytics(self):
        """Test project analytics generation."""
        service = ProjectAnalyticsService()
        analytics = service.get_project_analytics(str(self.project1.id))
        
        self.assertIn('project_id', analytics)
        self.assertEqual(analytics['project_id'], str(self.project1.id))
        self.assertIn('project_name', analytics)
        self.assertEqual(analytics['project_name'], 'Project 1')
        self.assertIn('risk_score', analytics)
        self.assertIn('risk_level', analytics)
        self.assertIn('financial_metrics', analytics)
        self.assertIn('recommendations', analytics)
    
    def test_get_system_analytics(self):
        """Test system analytics generation."""
        service = ProjectAnalyticsService()
        analytics = service.get_system_analytics('procurepro')
        
        self.assertIn('system_name', analytics)
        self.assertEqual(analytics['system_name'], 'Test System')
        self.assertIn('total_projects', analytics)
        self.assertEqual(analytics['total_projects'], 2)
        self.assertIn('total_budget', analytics)
        self.assertEqual(analytics['total_budget'], 300000.0)
    
    def test_calculate_project_risk_score(self):
        """Test project risk score calculation."""
        service = ProjectAnalyticsService()
        
        # Test project with good metrics
        risk_score = service._calculate_project_risk_score(self.project1)
        self.assertIsInstance(risk_score, float)
        self.assertGreaterEqual(risk_score, 0)
        self.assertLessEqual(risk_score, 100)
        
        # Test project with poor metrics
        risk_score = service._calculate_project_risk_score(self.project2)
        self.assertIsInstance(risk_score, float)
        self.assertGreaterEqual(risk_score, 0)
        self.assertLessEqual(risk_score, 100)
    
    def test_get_risk_level(self):
        """Test risk level determination."""
        service = ProjectAnalyticsService()
        
        risk_level = service._get_risk_level(self.project1)
        self.assertIn(risk_level, ['low', 'medium', 'high'])
        
        risk_level = service._get_risk_level(self.project2)
        self.assertIn(risk_level, ['low', 'medium', 'high'])
    
    def test_identify_risk_factors(self):
        """Test risk factor identification."""
        service = ProjectAnalyticsService()
        
        risk_factors = service._identify_risk_factors(self.project1)
        self.assertIsInstance(risk_factors, list)
        
        risk_factors = service._identify_risk_factors(self.project2)
        self.assertIsInstance(risk_factors, list)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        service = ProjectAnalyticsService()
        
        recommendations = service._generate_recommendations(self.project1)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        recommendations = service._generate_recommendations(self.project2)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)


class AutomatedUpdateServiceTestCase(TestCase):
    """Test cases for AutomatedUpdateService."""
    
    def setUp(self):
        """Set up test data."""
        # Create test integration system
        self.test_system = IntegrationSystem.objects.create(
            name='Test System',
            system_type='procurepro',
            status='active',
            connection_status='active'
        )
    
    def test_automated_update_service_initialization(self):
        """Test automated update service initialization."""
        service = AutomatedUpdateService()
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.sync_service)
        self.assertIsNotNone(service.analytics_service)
        self.assertEqual(service.update_stats['updates_processed'], 0)
    
    def test_start_automated_updates(self):
        """Test starting automated updates."""
        service = AutomatedUpdateService()
        result = service.start_automated_updates()
        
        self.assertIn('status', result)
        self.assertIn('message', result)
        self.assertIn('scheduled_updates', result)
        self.assertIn('monitoring', result)
    
    def test_stop_automated_updates(self):
        """Test stopping automated updates."""
        service = AutomatedUpdateService()
        result = service.stop_automated_updates()
        
        self.assertIn('status', result)
        self.assertIn('message', result)
    
    def test_get_update_status(self):
        """Test getting update status."""
        service = AutomatedUpdateService()
        status = service.get_update_status()
        
        self.assertIn('status', status)
        self.assertIn('updates_processed', status)
        self.assertIn('updates_successful', status)
        self.assertIn('updates_failed', status)
        self.assertIn('error_count', status)
        self.assertIn('scheduled_updates', status)
        self.assertIn('monitoring_status', status)
    
    def test_schedule_updates(self):
        """Test scheduling updates."""
        service = AutomatedUpdateService()
        
        # This should not raise an exception
        try:
            service._schedule_updates()
        except Exception as e:
            self.fail(f"Schedule updates failed: {e}")
    
    def test_get_scheduled_updates_info(self):
        """Test getting scheduled updates information."""
        service = AutomatedUpdateService()
        info = service._get_scheduled_updates_info()
        
        self.assertIn('hourly_tasks', info)
        self.assertIn('daily_tasks', info)
        self.assertIn('weekly_tasks', info)
        self.assertIn('next_hourly_update', info)
        self.assertIn('next_daily_update', info)
        self.assertIn('next_weekly_update', info)


class ChangeDetectionServiceTestCase(TestCase):
    """Test cases for ChangeDetectionService."""
    
    def setUp(self):
        """Set up test data."""
        # Create test integration system
        self.test_system = IntegrationSystem.objects.create(
            name='Test System',
            system_type='procurepro',
            status='active',
            connection_status='active'
        )
        
        # Create test project
        self.test_project = UnifiedProject.objects.create(
            name='Test Project',
            description='Test project description',
            project_number='TEST-001',
            status='planning',
            project_type='commercial',
            budget=100000.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            progress_percentage=50.0
        )
        
        # Create test project mapping
        self.project_mapping = ProjectSystemMapping.objects.create(
            project=self.test_project,
            system=self.test_system,
            external_project_id='12345',
            external_project_number='TEST-001',
            external_project_name='Test Project',
            sync_status='completed'
        )
    
    def test_change_detection_service_initialization(self):
        """Test change detection service initialization."""
        service = ChangeDetectionService()
        self.assertIsNotNone(service)
        self.assertIn('project', service.change_types)
        self.assertIn('document', service.change_types)
        self.assertIn('schedule', service.change_types)
        self.assertIn('financial', service.change_types)
        self.assertIn('change_order', service.change_types)
        self.assertIn('rfi', service.change_types)
    
    def test_detect_changes_project_specific(self):
        """Test change detection for specific project."""
        service = ChangeDetectionService()
        result = service.detect_changes(project_id=str(self.test_project.id))
        
        self.assertIn('timestamp', result)
        self.assertIn('total_changes', result)
        self.assertIn('changes_by_type', result)
        self.assertIn('changes_by_priority', result)
        self.assertIn('affected_projects', result)
        self.assertIn('notifications_sent', result)
        self.assertIn('errors', result)
    
    def test_detect_changes_system_specific(self):
        """Test change detection for specific system."""
        service = ChangeDetectionService()
        result = service.detect_changes(system_type='procurepro')
        
        self.assertIn('timestamp', result)
        self.assertIn('total_changes', result)
        self.assertIn('changes_by_type', result)
        self.assertIn('changes_by_priority', result)
        self.assertIn('affected_projects', result)
        self.assertIn('notifications_sent', result)
        self.assertIn('errors', result)
    
    def test_determine_change_type(self):
        """Test change type determination."""
        service = ChangeDetectionService()
        
        # Test added change
        self.assertEqual(service._determine_change_type(None, 'new_value'), 'added')
        
        # Test removed change
        self.assertEqual(service._determine_change_type('old_value', None), 'removed')
        
        # Test increased change
        self.assertEqual(service._determine_change_type(10, 20), 'increased')
        
        # Test decreased change
        self.assertEqual(service._determine_change_type(20, 10), 'decreased')
        
        # Test modified change
        self.assertEqual(service._determine_change_type('old', 'new'), 'modified')
    
    def test_calculate_change_priority(self):
        """Test change priority calculation."""
        service = ChangeDetectionService()
        
        # Test high priority field
        priority = service._calculate_change_priority('status', 'old', 'new', 'project')
        self.assertEqual(priority, 'high')
        
        # Test medium priority field
        priority = service._calculate_change_priority('progress_percentage', 'old', 'new', 'project')
        self.assertEqual(priority, 'medium')
        
        # Test low priority field
        priority = service._calculate_change_priority('description', 'old', 'new', 'project')
        self.assertEqual(priority, 'low')
    
    def test_requires_approval(self):
        """Test approval requirement determination."""
        service = ChangeDetectionService()
        
        # Test fields that require approval
        self.assertTrue(service._requires_approval('status', 'project'))
        self.assertTrue(service._requires_approval('budget', 'project'))
        self.assertTrue(service._requires_approval('amount', 'financial'))
        
        # Test fields that don't require approval
        self.assertFalse(service._requires_approval('description', 'project'))
        self.assertFalse(service._requires_approval('name', 'project'))
    
    def test_get_change_history(self):
        """Test getting change history."""
        service = ChangeDetectionService()
        history = service.get_change_history(str(self.test_project.id), 'project', 30)
        
        self.assertIn('entity_id', history)
        self.assertIn('entity_type', history)
        self.assertIn('period_days', history)
        self.assertIn('total_changes', history)
    
    def test_get_recent_changes(self):
        """Test getting recent changes."""
        service = ChangeDetectionService()
        changes = service.get_recent_changes(24)
        
        self.assertIn('period_hours', changes)
        self.assertIn('total_changes', changes)
        self.assertIn('changes_by_priority', changes)
        self.assertIn('affected_projects', changes)
        self.assertIn('recent_results', changes)


class IntegrationEndToEndTestCase(TestCase):
    """End-to-end integration tests for Task 3 services."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        # Create integration systems
        self.procurepro_system = IntegrationSystem.objects.create(
            name='Test ProcurePro',
            system_type='procurepro',
            status='active',
            connection_status='active'
        )
        
        self.procore_system = IntegrationSystem.objects.create(
            name='Test Procore',
            system_type='procore',
            status='active',
            connection_status='active'
        )
        
        self.jobpac_system = IntegrationSystem.objects.create(
            name='Test Jobpac',
            system_type='jobpac',
            status='active',
            connection_status='active'
        )
        
        # Create test projects
        self.project1 = UnifiedProject.objects.create(
            name='Commercial Building',
            description='Office building construction',
            project_number='COMM-001',
            status='construction',
            project_type='commercial',
            budget=500000.00,
            actual_cost=475000.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=45)).date(),
            progress_percentage=65.0
        )
        
        self.project2 = UnifiedProject.objects.create(
            name='Residential Complex',
            description='Apartment complex development',
            project_number='RES-001',
            status='planning',
            project_type='residential',
            budget=800000.00,
            actual_cost=0.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date(),
            progress_percentage=15.0
        )
        
        # Add systems to projects
        self.project1.integration_systems.add(self.procurepro_system, self.procore_system)
        self.project2.integration_systems.add(self.procurepro_system, self.jobpac_system)
        
        # Create project mappings
        ProjectSystemMapping.objects.create(
            project=self.project1,
            system=self.procurepro_system,
            external_project_id='PROC-001',
            external_project_number='COMM-001',
            external_project_name='Commercial Building',
            sync_status='completed'
        )
        
        ProjectSystemMapping.objects.create(
            project=self.project1,
            system=self.procore_system,
            external_project_id='PROC-001',
            external_project_number='COMM-001',
            external_project_name='Commercial Building',
            sync_status='completed'
        )
        
        ProjectSystemMapping.objects.create(
            project=self.project2,
            system=self.procurepro_system,
            external_project_id='PROC-002',
            external_project_number='RES-001',
            external_project_name='Residential Complex',
            sync_status='completed'
        )
        
        ProjectSystemMapping.objects.create(
            project=self.project2,
            system=self.jobpac_system,
            external_project_id='JOB-001',
            external_project_number='RES-001',
            external_project_name='Residential Complex',
            sync_status='completed'
        )
    
    def test_full_integration_workflow(self):
        """Test the complete integration workflow."""
        # Test sync service
        sync_service = ProjectSyncService()
        self.assertIsNotNone(sync_service)
        
        # Test analytics service
        analytics_service = ProjectAnalyticsService()
        self.assertIsNotNone(analytics_service)
        
        # Test automated updates service
        automated_service = AutomatedUpdateService()
        self.assertIsNotNone(automated_service)
        
        # Test change detection service
        change_service = ChangeDetectionService()
        self.assertIsNotNone(change_service)
    
    def test_cross_system_data_consistency(self):
        """Test data consistency across different systems."""
        # Verify project mappings are consistent
        mappings = ProjectSystemMapping.objects.filter(project=self.project1)
        self.assertEqual(mappings.count(), 2)
        
        for mapping in mappings:
            self.assertEqual(mapping.external_project_number, 'COMM-001')
            self.assertEqual(mapping.external_project_name, 'Commercial Building')
            self.assertEqual(mapping.sync_status, 'completed')
    
    def test_analytics_across_systems(self):
        """Test analytics working across multiple systems."""
        analytics_service = ProjectAnalyticsService()
        
        # Test portfolio summary
        summary = analytics_service.get_portfolio_summary()
        self.assertEqual(summary['total_projects'], 2)
        self.assertEqual(summary['total_budget'], 1300000.0)
        
        # Test system analytics
        procurepro_analytics = analytics_service.get_system_analytics('procurepro')
        self.assertEqual(procurepro_analytics['total_projects'], 2)
        
        procore_analytics = analytics_service.get_system_analytics('procore')
        self.assertEqual(procore_analytics['total_projects'], 1)
        
        jobpac_analytics = analytics_service.get_system_analytics('jobpac')
        self.assertEqual(jobpac_analytics['total_projects'], 1)
    
    def test_change_detection_across_entities(self):
        """Test change detection working across all entity types."""
        change_service = ChangeDetectionService()
        
        # Test project-level change detection
        project_changes = change_service.detect_changes(project_id=str(self.project1.id))
        self.assertIsInstance(project_changes, dict)
        self.assertIn('total_changes', project_changes)
        
        # Test system-level change detection
        system_changes = change_service.detect_changes(system_type='procurepro')
        self.assertIsInstance(system_changes, dict)
        self.assertIn('total_changes', system_changes)
    
    def test_automated_workflow_integration(self):
        """Test integration between automated updates and other services."""
        automated_service = AutomatedUpdateService()
        
        # Test service initialization
        self.assertIsNotNone(automated_service.sync_service)
        self.assertIsNotNone(automated_service.analytics_service)
        
        # Test status reporting
        status = automated_service.get_update_status()
        self.assertIsInstance(status, dict)
        self.assertIn('status', status)
        self.assertIn('scheduled_updates', status)


if __name__ == '__main__':
    unittest.main()
