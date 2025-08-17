"""
Tests for Jobpac integration.

Tests the Jobpac API client, views, and integration functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .client import JobpacAPIClient

User = get_user_model()


class JobpacAPIClientTestCase(TestCase):
    """Test cases for Jobpac API client."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('integrations.jobpac.client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test Jobpac API client initialization."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'company_name': 'Test Company',
            'status': 'active'
        }
        mock_session_instance.request.return_value = mock_response
        
        client = JobpacAPIClient()
        self.assertIsNotNone(client)
    
    @patch('integrations.jobpac.client.requests.Session')
    def test_health_check(self, mock_session):
        """Test health check functionality."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock successful authentication and health check
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {
            'company_name': 'Test Company',
            'status': 'active'
        }
        
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {
            'company_name': 'Test Company',
            'status': 'active'
        }
        
        mock_session_instance.request.side_effect = [mock_auth_response, mock_health_response]
        
        client = JobpacAPIClient()
        health_data = client.health_check()
        
        self.assertEqual(health_data['status'], 'healthy')
        self.assertIn('response_time', health_data)


class JobpacViewsTestCase(APITestCase):
    """Test cases for Jobpac views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch('integrations.jobpac.views.JobpacAPIClient')
    def test_health_check_view(self, mock_client_class):
        """Test health check view."""
        mock_client = MagicMock()
        mock_client.return_value.health_check.return_value = {
            'status': 'healthy',
            'response_time': 0.1
        }
        mock_client_class.return_value = mock_client
        
        url = reverse('jobpac:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    @patch('integrations.jobpac.views.JobpacAPIClient')
    def test_projects_list_view(self, mock_client_class):
        """Test projects list view."""
        mock_client = MagicMock()
        mock_client.return_value.get_projects.return_value = [
            {'id': 1, 'name': 'Project 1'},
            {'id': 2, 'name': 'Project 2'}
        ]
        mock_client_class.return_value = mock_client
        
        url = reverse('jobpac:projects_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    @patch('integrations.jobpac.views.JobpacAPIClient')
    def test_project_detail_view(self, mock_client_class):
        """Test project detail view."""
        mock_client = MagicMock()
        mock_client.return_value.get_project.return_value = {
            'id': 1,
            'name': 'Test Project',
            'description': 'Test Description'
        }
        mock_client_class.return_value = mock_client
        
        url = reverse('jobpac:project_detail', kwargs={'project_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')
    
    def test_health_check_view_unauthenticated(self):
        """Test health check view without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('jobpac:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JobpacIntegrationTestCase(TestCase):
    """Test cases for Jobpac integration functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_client_configuration(self):
        """Test client configuration handling."""
        # Test with default configuration
        client = JobpacAPIClient()
        self.assertIsNotNone(client.config)
        self.assertIn('api_key', client.config)
        self.assertIn('api_secret', client.config)
    
    @patch('integrations.jobpac.client.requests.Session')
    def test_error_handling(self, mock_session):
        """Test error handling in API client."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock authentication failure
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_session_instance.request.return_value = mock_response
        
        with self.assertRaises(Exception):
            JobpacAPIClient()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        client = JobpacAPIClient()
        
        # Test rate limit check
        # Note: This is a basic test - actual rate limiting would need more complex setup
        self.assertTrue(hasattr(client, '_check_rate_limit'))
