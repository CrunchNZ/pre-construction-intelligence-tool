"""
Procore API Client

Handles authentication, API communication, and data retrieval from Procore.
Supports OAuth2 authentication, rate limiting, and comprehensive error handling.

Key Features:
- OAuth2 authentication with refresh token support
- Rate limiting and request throttling
- Comprehensive error handling and retry logic
- Support for all major Procore API endpoints
- Automatic pagination handling
- Request/response logging and monitoring

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from integrations.core.exceptions import (
    IntegrationError,
    AuthenticationError,
    RateLimitError,
    APIError,
    NetworkError
)

logger = logging.getLogger(__name__)


class ProcoreAPIClient:
    """
    Procore API client for handling all API communications.
    
    Supports OAuth2 authentication, rate limiting, and comprehensive
    error handling for production use.
    """
    
    # API Configuration
    BASE_URL = "https://api.procore.com"
    API_VERSION = "v1.0"
    
    # OAuth2 Configuration
    TOKEN_ENDPOINT = "/oauth/token"
    AUTHORIZATION_ENDPOINT = "/oauth/authorize"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    MAX_REQUESTS_PER_WINDOW = 1000
    
    # Retry Configuration
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Procore API client.
        
        Args:
            config: Configuration dictionary with API credentials and settings
        """
        self.config = config or self._get_default_config()
        self.session = self._create_session()
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Initialize authentication
        self._authenticate()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from Django settings."""
        return {
            'client_id': getattr(settings, 'PROCORE_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'PROCORE_CLIENT_SECRET', ''),
            'redirect_uri': getattr(settings, 'PROCORE_REDIRECT_URI', ''),
            'company_id': getattr(settings, 'PROCORE_COMPANY_ID', ''),
            'username': getattr(settings, 'PROCORE_USERNAME', ''),
            'password': getattr(settings, 'PROCORE_PASSWORD', ''),
            'grant_type': 'password',  # Resource owner password credentials
        }
    
    def _create_session(self) -> requests.Session:
        """Create and configure the requests session."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            backoff_factor=self.BACKOFF_FACTOR,
        )
        
        # Configure adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'PreConstructionIntelligence/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        return session
    
    def _authenticate(self) -> None:
        """Authenticate with Procore using OAuth2."""
        try:
            # Check if we have a valid cached token
            cached_token = cache.get('procore_access_token')
            if cached_token and self._is_token_valid(cached_token):
                self.access_token = cached_token['access_token']
                self.refresh_token = cached_token['refresh_token']
                self.token_expires_at = cached_token['expires_at']
                logger.info("Using cached Procore access token")
                return
            
            # Perform OAuth2 authentication
            auth_data = {
                'grant_type': self.config['grant_type'],
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'username': self.config['username'],
                'password': self.config['password'],
            }
            
            response = self.session.post(
                f"{self.BASE_URL}{self.TOKEN_ENDPOINT}",
                data=auth_data,
                timeout=30
            )
            
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Procore authentication failed: {response.status_code} - {response.text}"
                )
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            self.token_expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'])
            
            # Cache the token
            cache.set(
                'procore_access_token',
                {
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token,
                    'expires_at': self.token_expires_at,
                },
                timeout=token_data['expires_in'] - 300  # Cache for 5 minutes less than expiry
            )
            
            logger.info("Successfully authenticated with Procore")
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during Procore authentication: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Procore authentication error: {str(e)}")
    
    def _is_token_valid(self, token_data: Dict[str, Any]) -> bool:
        """Check if a cached token is still valid."""
        if not token_data or 'expires_at' not in token_data:
            return False
        
        expires_at = token_data['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        return timezone.now() < expires_at - timedelta(minutes=5)
    
    def _refresh_token_if_needed(self) -> None:
        """Refresh the access token if it's expired or about to expire."""
        if not self.token_expires_at or timezone.now() >= self.token_expires_at - timedelta(minutes=5):
            logger.info("Procore access token expired, refreshing...")
            self._authenticate()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make an authenticated request to the Procore API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Response object
            
        Raises:
            RateLimitError: When rate limit is exceeded
            APIError: When API returns an error
            NetworkError: When network issues occur
        """
        try:
            # Ensure we have a valid token
            self._refresh_token_if_needed()
            
            # Check rate limiting
            if not self._check_rate_limit():
                raise RateLimitError("Procore API rate limit exceeded")
            
            # Prepare request
            url = f"{self.BASE_URL}/rest/{self.API_VERSION}{endpoint}"
            request_headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Procore-Company-Id': str(self.config['company_id']),
            }
            
            if headers:
                request_headers.update(headers)
            
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=30
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(f"Rate limit exceeded, retry after {retry_after} seconds")
            
            # Handle authentication errors
            if response.status_code == 401:
                logger.warning("Procore authentication expired, re-authenticating...")
                self._authenticate()
                # Retry the request once
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=30
                )
            
            # Log request
            logger.debug(
                f"Procore API {method} {endpoint} - Status: {response.status_code}"
            )
            
            # Handle API errors
            if response.status_code >= 400:
                self._handle_api_error(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during Procore API request: {str(e)}")
        except Exception as e:
            if not isinstance(e, (RateLimitError, APIError)):
                raise APIError(f"Unexpected error during Procore API request: {str(e)}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        cache_key = f"procore_rate_limit_{int(time.time() // self.RATE_LIMIT_WINDOW)}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.MAX_REQUESTS_PER_WINDOW:
            return False
        
        cache.set(cache_key, current_requests + 1, timeout=self.RATE_LIMIT_WINDOW)
        return True
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown API error')
            error_code = error_data.get('code', response.status_code)
        except ValueError:
            error_message = response.text or 'Unknown API error'
            error_code = response.status_code
        
        if response.status_code == 400:
            raise APIError(f"Bad request: {error_message}")
        elif response.status_code == 403:
            raise APIError(f"Access forbidden: {error_message}")
        elif response.status_code == 404:
            raise APIError(f"Resource not found: {error_message}")
        elif response.status_code == 422:
            raise APIError(f"Validation error: {error_message}")
        elif response.status_code >= 500:
            raise APIError(f"Server error: {error_message}")
        else:
            raise APIError(f"API error {error_code}: {error_message}")
    
    # Project Management Methods
    def get_projects(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get list of projects from Procore.
        
        Args:
            params: Query parameters for filtering and pagination
            
        Returns:
            List of project dictionaries
        """
        response = self._make_request('GET', '/projects', params=params)
        return response.json()
    
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """
        Get specific project details.
        
        Args:
            project_id: Procore project ID
            
        Returns:
            Project dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}')
        return response.json()
    
    def get_project_contacts(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get project contacts.
        
        Args:
            project_id: Procore project ID
            
        Returns:
            List of contact dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/contacts')
        return response.json()
    
    # Document Management Methods
    def get_project_documents(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project documents.
        
        Args:
            project_id: Procore project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of document dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/documents', params=params)
        return response.json()
    
    def get_document(self, project_id: int, document_id: int) -> Dict[str, Any]:
        """
        Get specific document details.
        
        Args:
            project_id: Procore project ID
            document_id: Document ID
            
        Returns:
            Document dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/documents/{document_id}')
        return response.json()
    
    # Schedule Management Methods
    def get_project_schedule(self, project_id: int) -> Dict[str, Any]:
        """
        Get project schedule.
        
        Args:
            project_id: Procore project ID
            
        Returns:
            Schedule dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/schedule')
        return response.json()
    
    def get_schedule_items(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get schedule items.
        
        Args:
            project_id: Procore project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of schedule item dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/schedule_items', params=params)
        return response.json()
    
    # Budget and Cost Management Methods
    def get_project_budget(self, project_id: int) -> Dict[str, Any]:
        """
        Get project budget.
        
        Args:
            project_id: Procore project ID
            
        Returns:
            Budget dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/budget')
        return response.json()
    
    def get_cost_codes(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get project cost codes.
        
        Args:
            project_id: Procore project ID
            
        Returns:
            List of cost code dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/cost_codes')
        return response.json()
    
    # Change Management Methods
    def get_change_orders(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project change orders.
        
        Args:
            project_id: Procore project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of change order dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/change_orders', params=params)
        return response.json()
    
    def get_change_order(self, project_id: int, change_order_id: int) -> Dict[str, Any]:
        """
        Get specific change order details.
        
        Args:
            project_id: Procore project ID
            change_order_id: Change order ID
            
        Returns:
            Change order dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/change_orders/{change_order_id}')
        return response.json()
    
    # Submittal Management Methods
    def get_submittals(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project submittals.
        
        Args:
            project_id: Procore project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of submittal dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/submittals', params=params)
        return response.json()
    
    def get_submittal(self, project_id: int, submittal_id: int) -> Dict[str, Any]:
        """
        Get specific submittal details.
        
        Args:
            project_id: Procore project ID
            submittal_id: Submittal ID
            
        Returns:
            Submittal dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/submittals/{submittal_id}')
        return response.json()
    
    # RFI Management Methods
    def get_rfis(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project RFIs.
        
        Args:
            project_id: Procore project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of RFI dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/rfis', params=params)
        return response.json()
    
    def get_rfi(self, project_id: int, rfi_id: int) -> Dict[str, Any]:
        """
        Get specific RFI details.
        
        Args:
            project_id: Procore project ID
            rfi_id: RFI ID
            
        Returns:
            RFI dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/rfis/{rfi_id}')
        return response.json()
    
    # Company and User Methods
    def get_company_users(self) -> List[Dict[str, Any]]:
        """
        Get company users.
        
        Returns:
            List of user dictionaries
        """
        response = self._make_request('GET', '/company/users')
        return response.json()
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get specific user details.
        
        Args:
            user_id: User ID
            
        Returns:
            User dictionary
        """
        response = self._make_request('GET', f'/users/{user_id}')
        return response.json()
    
    # Health Check Method
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Procore API.
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            response = self._make_request('GET', '/company/users', params={'per_page': 1})
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'api_version': self.API_VERSION,
                'company_id': self.config['company_id'],
                'last_check': timezone.now().isoformat(),
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': timezone.now().isoformat(),
            }
    
    def close(self) -> None:
        """Close the API client session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
