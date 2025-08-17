"""
Tests for Procore integration.

Tests the Procore API client, views, and integration functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .client import ProcoreAPIClient

User = get_user_model()


class ProcoreAPIClientTestCase(TestCase):
    """Test cases for Procore API client."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('integrations.procore.client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test Procore API client initialization."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        mock_session_instance.post.return_value = mock_response
        
        client = ProcoreAPIClient()
        self.assertIsNotNone(client)
    
    @patch('integrations.procore.client.requests.Session')
    def test_health_check(self, mock_session):
        """Test health check functionality."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock successful authentication and health check
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = [{'id': 1, 'name': 'Test User'}]
        
        mock_session_instance.post.return_value = mock_auth_response
        mock_session_instance.request.return_value = mock_health_response
        
        client = ProcoreAPIClient()
        health_data = client.health_check()
        
        self.assertEqual(health_data['status'], 'healthy')
        self.assertIn('response_time', health_data)


class ProcoreViewsTestCase(APITestCase):
    """Test cases for Procore views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    @patch('integrations.procore.views.ProcoreAPIClient')
    def test_health_check_view(self, mock_client_class):
        """Test health check view."""
        mock_client = MagicMock()
        mock_client.return_value.health_check.return_value = {
            'status': 'healthy',
            'response_time': 0.1
        }
        mock_client_class.return_value = mock_client
        
        url = reverse('procore:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    @patch('integrations.procore.views.ProcoreAPIClient')
    def test_projects_list_view(self, mock_client_class):
        """Test projects list view."""
        mock_client = MagicMock()
        mock_client.return_value.get_projects.return_value = [
            {'id': 1, 'name': 'Project 1'},
            {'id': 2, 'name': 'Project 2'}
        ]
        mock_client_class.return_value = mock_client
        
        url = reverse('procore:projects_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    @patch('integrations.procore.views.ProcoreAPIClient')
    def test_project_detail_view(self, mock_client_class):
        """Test project detail view."""
        mock_client = MagicMock()
        mock_client.return_value.get_project.return_value = {
            'id': 1,
            'name': 'Test Project',
            'description': 'Test Description'
        }
        mock_client_class.return_value = mock_client
        
        url = reverse('procore:project_detail', kwargs={'project_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')
    
    def test_health_check_view_unauthenticated(self):
        """Test health check view without authentication."""
        self.client.force_authenticate(user=None)
        url = reverse('procore:health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProcoreIntegrationTestCase(TestCase):
    """Test cases for Procore integration functionality."""
    
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
        client = ProcoreAPIClient()
        self.assertIsNotNone(client.config)
        self.assertIn('client_id', client.config)
        self.assertIn('client_secret', client.config)
    
    @patch('integrations.procore.client.requests.Session')
    def test_error_handling(self, mock_session):
        """Test error handling in API client."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Mock authentication failure
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_session_instance.post.return_value = mock_response
        
        with self.assertRaises(Exception):
            ProcoreAPIClient()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        client = ProcoreAPIClient()
        
        # Test rate limit check
        # Note: This is a basic test - actual rate limiting would need more complex setup
        self.assertTrue(hasattr(client, '_check_rate_limit'))
