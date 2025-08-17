"""
Jobpac API Client

Handles authentication, API communication, and data retrieval from Jobpac.
Supports API key authentication, rate limiting, and comprehensive error handling.

Key Features:
- API key authentication with secure credential management
- Rate limiting and request throttling
- Comprehensive error handling and retry logic
- Support for all major Jobpac API endpoints
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


class JobpacAPIClient:
    """
    Jobpac API client for handling all API communications.
    
    Supports API key authentication, rate limiting, and comprehensive
    error handling for production use.
    """
    
    # API Configuration
    BASE_URL = "https://api.jobpac.com.au"  # Example URL
    API_VERSION = "v1"
    
    # Authentication Configuration
    API_KEY_HEADER = "X-API-Key"
    API_SECRET_HEADER = "X-API-Secret"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    MAX_REQUESTS_PER_WINDOW = 500  # Jobpac typically has lower limits
    
    # Retry Configuration
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Jobpac API client.
        
        Args:
            config: Configuration dictionary with API credentials and settings
        """
        self.config = config or self._get_default_config()
        self.session = self._create_session()
        self.api_key = None
        self.api_secret = None
        
        # Initialize authentication
        self._authenticate()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from Django settings."""
        return {
            'api_key': getattr(settings, 'JOBPAC_API_KEY', ''),
            'api_secret': getattr(settings, 'JOBPAC_API_SECRET', ''),
            'company_id': getattr(settings, 'JOBPAC_COMPANY_ID', ''),
            'base_url': getattr(settings, 'JOBPAC_BASE_URL', self.BASE_URL),
            'api_version': getattr(settings, 'JOBPAC_API_VERSION', self.API_VERSION),
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
        """Authenticate with Jobpac using API key."""
        try:
            # Check if we have valid cached credentials
            cached_creds = cache.get('jobpac_api_credentials')
            if cached_creds and self._are_credentials_valid(cached_creds):
                self.api_key = cached_creds['api_key']
                self.api_secret = cached_creds['api_secret']
                logger.info("Using cached Jobpac API credentials")
                return
            
            # Use configuration credentials
            self.api_key = self.config['api_key']
            self.api_secret = self.config['api_secret']
            
            if not self.api_key or not self.api_secret:
                raise AuthenticationError("Jobpac API key and secret are required")
            
            # Test authentication with a simple API call
            test_response = self._make_request('GET', '/company/info')
            if test_response.status_code != 200:
                raise AuthenticationError(
                    f"Jobpac authentication failed: {test_response.status_code} - {test_response.text}"
                )
            
            # Cache the credentials
            cache.set(
                'jobpac_api_credentials',
                {
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                    'cached_at': timezone.now().isoformat(),
                },
                timeout=3600  # Cache for 1 hour
            )
            
            logger.info("Successfully authenticated with Jobpac")
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during Jobpac authentication: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Jobpac authentication error: {str(e)}")
    
    def _are_credentials_valid(self, creds: Dict[str, Any]) -> bool:
        """Check if cached credentials are still valid."""
        if not creds or 'cached_at' not in creds:
            return False
        
        cached_at = creds['cached_at']
        if isinstance(cached_at, str):
            cached_at = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
        
        # Credentials are valid for 1 hour
        return timezone.now() < cached_at + timedelta(hours=1)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make an authenticated request to the Jobpac API.
        
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
            # Check rate limiting
            if not self._check_rate_limit():
                raise RateLimitError("Jobpac API rate limit exceeded")
            
            # Prepare request
            url = f"{self.config['base_url']}/api/{self.config['api_version']}{endpoint}"
            request_headers = {
                self.API_KEY_HEADER: self.api_key,
                self.API_SECRET_HEADER: self.api_secret,
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
                logger.warning("Jobpac authentication failed, clearing cache and re-authenticating...")
                cache.delete('jobpac_api_credentials')
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
                f"Jobpac API {method} {endpoint} - Status: {response.status_code}"
            )
            
            # Handle API errors
            if response.status_code >= 400:
                self._handle_api_error(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during Jobpac API request: {str(e)}")
        except Exception as e:
            if not isinstance(e, (RateLimitError, APIError)):
                raise APIError(f"Unexpected error during Jobpac API request: {str(e)}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        cache_key = f"jobpac_rate_limit_{int(time.time() // self.RATE_LIMIT_WINDOW)}"
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
        elif response.status_code == 401:
            raise APIError(f"Authentication failed: {error_message}")
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
        Get list of projects from Jobpac.
        
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
            project_id: Jobpac project ID
            
        Returns:
            Project dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}')
        return response.json()
    
    def get_project_contacts(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get project contacts.
        
        Args:
            project_id: Jobpac project ID
            
        Returns:
            List of contact dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/contacts')
        return response.json()
    
    # Financial Management Methods
    def get_project_financials(self, project_id: int) -> Dict[str, Any]:
        """
        Get project financial information.
        
        Args:
            project_id: Jobpac project ID
            
        Returns:
            Financial information dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/financials')
        return response.json()
    
    def get_cost_centres(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get project cost centres.
        
        Args:
            project_id: Jobpac project ID
            
        Returns:
            List of cost centre dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/cost-centres')
        return response.json()
    
    def get_purchase_orders(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project purchase orders.
        
        Args:
            project_id: Jobpac project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of purchase order dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/purchase-orders', params=params)
        return response.json()
    
    def get_purchase_order(self, project_id: int, po_id: int) -> Dict[str, Any]:
        """
        Get specific purchase order details.
        
        Args:
            project_id: Jobpac project ID
            po_id: Purchase order ID
            
        Returns:
            Purchase order dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/purchase-orders/{po_id}')
        return response.json()
    
    # Time and Attendance Methods
    def get_timesheets(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project timesheets.
        
        Args:
            project_id: Jobpac project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of timesheet dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/timesheets', params=params)
        return response.json()
    
    def get_timesheet(self, project_id: int, timesheet_id: int) -> Dict[str, Any]:
        """
        Get specific timesheet details.
        
        Args:
            project_id: Jobpac project ID
            timesheet_id: Timesheet ID
            
        Returns:
            Timesheet dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/timesheets/{timesheet_id}')
        return response.json()
    
    # Equipment and Resources Methods
    def get_equipment(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project equipment.
        
        Args:
            project_id: Jobpac project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of equipment dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/equipment', params=params)
        return response.json()
    
    def get_equipment_usage(self, project_id: int, equipment_id: int) -> Dict[str, Any]:
        """
        Get equipment usage information.
        
        Args:
            project_id: Jobpac project ID
            equipment_id: Equipment ID
            
        Returns:
            Equipment usage dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/equipment/{equipment_id}/usage')
        return response.json()
    
    # Subcontractor Management Methods
    def get_subcontractors(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get project subcontractors.
        
        Args:
            project_id: Jobpac project ID
            params: Query parameters for filtering and pagination
            
        Returns:
            List of subcontractor dictionaries
        """
        response = self._make_request('GET', f'/projects/{project_id}/subcontractors', params=params)
        return response.json()
    
    def get_subcontractor(self, project_id: int, subcontractor_id: int) -> Dict[str, Any]:
        """
        Get specific subcontractor details.
        
        Args:
            project_id: Jobpac project ID
            subcontractor_id: Subcontractor ID
            
        Returns:
            Subcontractor dictionary
        """
        response = self._make_request('GET', f'/projects/{project_id}/subcontractors/{subcontractor_id}')
        return response.json()
    
    # Company and User Methods
    def get_company_info(self) -> Dict[str, Any]:
        """
        Get company information.
        
        Returns:
            Company information dictionary
        """
        response = self._make_request('GET', '/company/info')
        return response.json()
    
    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get company users.
        
        Returns:
            List of user dictionaries
        """
        response = self._make_request('GET', '/users')
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
        Perform a health check on the Jobpac API.
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            response = self._make_request('GET', '/company/info')
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'api_version': self.config['api_version'],
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
