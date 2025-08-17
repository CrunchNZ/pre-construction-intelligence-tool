"""
Greentree API Client

Handles authentication, API communication, and data retrieval from Greentree.
Supports API key authentication, rate limiting, and comprehensive error handling.

Key Features:
- API key authentication with secure credential management
- Rate limiting and request throttling
- Comprehensive error handling and retry logic
- Support for all major Greentree API endpoints
- Automatic pagination handling
- Request/response logging and monitoring
- Financial data extraction and normalization

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


class GreentreeAPIClient:
    """
    Greentree API client for handling all API communications.
    
    Supports API key authentication, rate limiting, and comprehensive
    error handling for production use.
    """
    
    # API Configuration
    BASE_URL = "https://api.greentree.com"  # Example URL
    API_VERSION = "v1"
    
    # Authentication Configuration
    API_KEY_HEADER = "X-API-Key"
    API_SECRET_HEADER = "X-API-Secret"
    COMPANY_ID_HEADER = "X-Company-ID"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    MAX_REQUESTS_PER_WINDOW = 300  # Greentree typically has moderate limits
    
    # Retry Configuration
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Greentree API client.
        
        Args:
            config: Configuration dictionary with API credentials and settings
        """
        self.config = config or self._get_default_config()
        self.session = self._create_session()
        self.api_key = None
        self.api_secret = None
        self.company_id = None
        
        # Initialize authentication
        self._authenticate()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from Django settings."""
        return {
            'api_key': getattr(settings, 'GREENTREE_API_KEY', ''),
            'api_secret': getattr(settings, 'GREENTREE_API_SECRET', ''),
            'company_id': getattr(settings, 'GREENTREE_COMPANY_ID', ''),
            'base_url': getattr(settings, 'GREENTREE_BASE_URL', self.BASE_URL),
            'api_version': getattr(settings, 'GREENTREE_API_VERSION', self.API_VERSION),
        }
    
    def _create_session(self) -> requests.Session:
        """Create and configure the requests session."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=self.BACKOFF_FACTOR
        )
        
        # Configure adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'PreConstructionIntelligence/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        return session
    
    def _authenticate(self) -> None:
        """Authenticate with the Greentree API."""
        try:
            # Get credentials from config
            self.api_key = self.config['api_key']
            self.api_secret = self.config['api_secret']
            self.company_id = self.config['company_id']
            
            if not all([self.api_key, self.api_secret, self.company_id]):
                raise AuthenticationError("Missing Greentree API credentials")
            
            # Test authentication with a simple API call
            test_response = self._make_request('GET', '/company/info')
            if test_response.status_code == 200:
                logger.info("Greentree API authentication successful")
            else:
                raise AuthenticationError(f"Authentication failed: {test_response.status_code}")
                
        except Exception as e:
            logger.error(f"Greentree authentication failed: {str(e)}")
            raise AuthenticationError(f"Failed to authenticate with Greentree: {str(e)}")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        cache_key = f'greentree_rate_limit_{int(time.time() // self.RATE_LIMIT_WINDOW)}'
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.MAX_REQUESTS_PER_WINDOW:
            return False
        
        cache.set(cache_key, current_requests + 1, self.RATE_LIMIT_WINDOW)
        return True
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make an authenticated request to the Greentree API.
        
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
                raise RateLimitError("Greentree API rate limit exceeded")
            
            # Prepare request
            url = f"{self.config['base_url']}/api/{self.config['api_version']}{endpoint}"
            request_headers = {
                self.API_KEY_HEADER: self.api_key,
                self.API_SECRET_HEADER: self.api_secret,
                self.COMPANY_ID_HEADER: str(self.company_id),
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
                logger.warning("Greentree authentication failed, clearing cache and re-authenticating...")
                cache.delete('greentree_api_credentials')
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
                f"Greentree API {method} {endpoint} - Status: {response.status_code}"
            )
            
            # Handle API errors
            if response.status_code >= 400:
                self._handle_api_error(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in Greentree API request: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Greentree API request: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown API error')
        except ValueError:
            error_message = f"HTTP {response.status_code}: {response.text}"
        
        logger.error(f"Greentree API error: {error_message}")
        
        if response.status_code == 400:
            raise APIError(f"Bad request: {error_message}")
        elif response.status_code == 403:
            raise AuthenticationError(f"Access denied: {error_message}")
        elif response.status_code == 404:
            raise APIError(f"Resource not found: {error_message}")
        elif response.status_code >= 500:
            raise APIError(f"Server error: {error_message}")
        else:
            raise APIError(f"API error {response.status_code}: {error_message}")
    
    # Financial Data Endpoints
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get company information."""
        response = self._make_request('GET', '/company/info')
        return response.json()
    
    def get_financial_periods(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get financial periods."""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self._make_request('GET', '/financial/periods', params=params)
        return response.json()
    
    def get_general_ledger(self, period_id: str = None, account_code: str = None) -> List[Dict[str, Any]]:
        """Get general ledger entries."""
        params = {}
        if period_id:
            params['period_id'] = period_id
        if account_code:
            params['account_code'] = account_code
        
        response = self._make_request('GET', '/financial/general-ledger', params=params)
        return response.json()
    
    def get_profit_loss(self, period_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get profit and loss statement."""
        params = {}
        if period_id:
            params['period_id'] = period_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self._make_request('GET', '/financial/profit-loss', params=params)
        return response.json()
    
    def get_balance_sheet(self, period_id: str = None, as_of_date: str = None) -> Dict[str, Any]:
        """Get balance sheet."""
        params = {}
        if period_id:
            params['period_id'] = period_id
        if as_of_date:
            params['as_of_date'] = as_of_date
        
        response = self._make_request('GET', '/financial/balance-sheet', params=params)
        return response.json()
    
    def get_cash_flow(self, period_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get cash flow statement."""
        params = {}
        if period_id:
            params['period_id'] = period_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self._make_request('GET', '/financial/cash-flow', params=params)
        return response.json()
    
    def get_budget_vs_actual(self, period_id: str = None, account_code: str = None) -> List[Dict[str, Any]]:
        """Get budget vs actual comparison."""
        params = {}
        if period_id:
            params['period_id'] = period_id
        if account_code:
            params['account_code'] = account_code
        
        response = self._make_request('GET', '/financial/budget-vs-actual', params=params)
        return response.json()
    
    def get_cost_centres(self) -> List[Dict[str, Any]]:
        """Get cost centres."""
        response = self._make_request('GET', '/financial/cost-centres')
        return response.json()
    
    def get_job_costing(self, job_number: str = None, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get job costing information."""
        params = {}
        if job_number:
            params['job_number'] = job_number
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self._make_request('GET', '/financial/job-costing', params=params)
        return response.json()
    
    def get_tax_codes(self) -> List[Dict[str, Any]]:
        """Get tax codes."""
        response = self._make_request('GET', '/financial/tax-codes')
        return response.json()
    
    def get_currency_rates(self, base_currency: str = 'USD', target_currencies: List[str] = None) -> Dict[str, Any]:
        """Get currency exchange rates."""
        params = {'base_currency': base_currency}
        if target_currencies:
            params['target_currencies'] = ','.join(target_currencies)
        
        response = self._make_request('GET', '/financial/currency-rates', params=params)
        return response.json()
    
    # Health Check and Monitoring
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Greentree API connection."""
        try:
            start_time = time.time()
            response = self._make_request('GET', '/health')
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': round(response_time, 3),
                'timestamp': timezone.now().isoformat(),
                'api_version': self.config['api_version'],
                'company_id': self.company_id
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
                'api_version': self.config['api_version'],
                'company_id': self.company_id
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get detailed API status information."""
        try:
            # Test multiple endpoints
            endpoints = [
                '/company/info',
                '/financial/periods',
                '/financial/cost-centres'
            ]
            
            status_results = {}
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = self._make_request('GET', endpoint)
                    response_time = time.time() - start_time
                    
                    status_results[endpoint] = {
                        'status': 'healthy',
                        'response_time': round(response_time, 3),
                        'status_code': response.status_code
                    }
                except Exception as e:
                    status_results[endpoint] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            return {
                'overall_status': 'healthy' if all(
                    result['status'] == 'healthy' for result in status_results.values()
                ) else 'degraded',
                'endpoints': status_results,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
