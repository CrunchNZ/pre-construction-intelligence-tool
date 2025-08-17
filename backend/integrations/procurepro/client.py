"""
ProcurePro API Client

Provides a robust interface to the ProcurePro API with comprehensive
error handling, retry logic, and rate limiting.
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import time
import json

logger = logging.getLogger(__name__)


class ProcureProAPIError(Exception):
    """Custom exception for ProcurePro API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class ProcureProClient:
    """
    ProcurePro API Client with comprehensive error handling and retry logic.
    
    Features:
    - Automatic authentication and token refresh
    - Rate limiting and request throttling
    - Comprehensive error handling
    - Request/response logging
    - Caching for frequently accessed data
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'PROCUREPRO_API_BASE', 'https://api.procurepro.com')
        self.api_key = getattr(settings, 'PROCUREPRO_API_KEY', '')
        self.api_secret = getattr(settings, 'PROCUREPRO_API_SECRET', '')
        self.timeout = getattr(settings, 'PROCUREPRO_API_TIMEOUT', 30)
        self.max_retries = getattr(settings, 'PROCUREPRO_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'PROCUREPRO_RETRY_DELAY', 1)
        
        # Rate limiting
        self.rate_limit_requests = getattr(settings, 'PROCUREPRO_RATE_LIMIT_REQUESTS', 100)
        self.rate_limit_window = getattr(settings, 'PROCUREPRO_RATE_LIMIT_WINDOW', 60)  # seconds
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PreConstructionIntelligence/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Authentication state
        self._access_token = None
        self._token_expires_at = None
        
        logger.info(f"ProcurePro client initialized for {self.base_url}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self._access_token or self._is_token_expired():
            self._authenticate()
        
        return {
            'Authorization': f'Bearer {self._access_token}',
            'X-API-Key': self.api_key
        }
    
    def _is_token_expired(self) -> bool:
        """Check if the current access token is expired."""
        if not self._token_expires_at:
            return True
        return datetime.now() >= self._token_expires_at
    
    def _authenticate(self) -> None:
        """Authenticate with ProcurePro API and obtain access token."""
        try:
            auth_url = f"{self.base_url}/auth/token"
            auth_data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'grant_type': 'client_credentials'
            }
            
            response = self.session.post(
                auth_url,
                json=auth_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                
                logger.info("Successfully authenticated with ProcurePro API")
            else:
                raise ProcureProAPIError(
                    f"Authentication failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.json() if response.content else None
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            raise ProcureProAPIError(f"Authentication request failed: {e}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise ProcureProAPIError(f"Authentication failed: {e}")
    
    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        cache_key = f"procurepro_rate_limit_{int(time.time() // self.rate_limit_window)}"
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.rate_limit_requests:
            wait_time = self.rate_limit_window - (int(time.time()) % self.rate_limit_window)
            logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds.")
            time.sleep(wait_time)
        
        cache.set(cache_key, current_requests + 1, self.rate_limit_window)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the ProcurePro API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            retry_count: Current retry attempt number
            
        Returns:
            API response data
            
        Raises:
            ProcureProAPIError: If the request fails after all retries
        """
        self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            # Log response for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired, re-authenticate and retry
                logger.info("Token expired, re-authenticating...")
                self._authenticate()
                if retry_count < self.max_retries:
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise ProcureProAPIError("Max retries exceeded after re-authentication")
            elif response.status_code in [429, 503]:
                # Rate limited or service unavailable, wait and retry
                retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                logger.warning(f"Rate limited, waiting {retry_after} seconds before retry")
                time.sleep(retry_after)
                
                if retry_count < self.max_retries:
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise ProcureProAPIError("Max retries exceeded after rate limiting")
            else:
                # Other HTTP errors
                error_data = response.json() if response.content else None
                raise ProcureProAPIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {url}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1})")
                time.sleep(self.retry_delay * (2 ** retry_count))  # Exponential backoff
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            else:
                raise ProcureProAPIError(f"Request timeout after {self.max_retries} retries")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1})")
                time.sleep(self.retry_delay * (2 ** retry_count))
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            else:
                raise ProcureProAPIError(f"Request failed after {self.max_retries} retries: {e}")
    
    def get_suppliers(self, page: int = 1, limit: int = 100, **filters) -> Dict[str, Any]:
        """
        Get suppliers from ProcurePro.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            Dictionary containing suppliers data and pagination info
        """
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        
        return self._make_request('GET', '/suppliers', params=params)
    
    def get_supplier(self, supplier_id: str) -> Dict[str, Any]:
        """
        Get a specific supplier by ID.
        
        Args:
            supplier_id: Unique identifier for the supplier
            
        Returns:
            Supplier data dictionary
        """
        return self._make_request('GET', f'/suppliers/{supplier_id}')
    
    def get_purchase_orders(self, page: int = 1, limit: int = 100, **filters) -> Dict[str, Any]:
        """
        Get purchase orders from ProcurePro.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            Dictionary containing purchase orders data and pagination info
        """
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        
        return self._make_request('GET', '/purchase-orders', params=params)
    
    def get_purchase_order(self, po_id: str) -> Dict[str, Any]:
        """
        Get a specific purchase order by ID.
        
        Args:
            po_id: Unique identifier for the purchase order
            
        Returns:
            Purchase order data dictionary
        """
        return self._make_request('GET', f'/purchase-orders/{po_id}')
    
    def get_invoices(self, page: int = 1, limit: int = 100, **filters) -> Dict[str, Any]:
        """
        Get invoices from ProcurePro.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            Dictionary containing invoices data and pagination info
        """
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        
        return self._make_request('GET', '/invoices', params=params)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get a specific invoice by ID.
        
        Args:
            invoice_id: Unique identifier for the invoice
            
        Returns:
            Invoice data dictionary
        """
        return self._make_request('GET', f'/invoices/{invoice_id}')
    
    def get_contracts(self, page: int = 1, limit: int = 100, **filters) -> Dict[str, Any]:
        """
        Get contracts from ProcurePro.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            **filters: Additional filter parameters
            
        Returns:
            Dictionary containing contracts data and pagination info
        """
        params = {
            'page': page,
            'limit': limit,
            **filters
        }
        
        return self._make_request('GET', '/contracts', params=params)
    
    def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Get a specific contract by ID.
        
        Args:
            contract_id: Unique identifier for the contract
            
        Returns:
            Contract data dictionary
        """
        return self._make_request('GET', f'/contracts/{contract_id}')
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the ProcurePro API.
        
        Returns:
            Health status information
        """
        try:
            response = self._make_request('GET', '/health')
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'api_response': response
            }
        except ProcureProAPIError as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status_code': e.status_code
            }
    
    def close(self):
        """Close the client session and clean up resources."""
        if self.session:
            self.session.close()
            logger.info("ProcurePro client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
