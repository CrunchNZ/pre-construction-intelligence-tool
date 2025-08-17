"""
BIM API Client using Autodesk Platform Services

Handles authentication, API communication, and data retrieval from Autodesk
Platform Services for BIM (Building Information Modeling) data.

Key Features:
- OAuth2 authentication with Autodesk Forge
- 3D model data extraction and processing
- Model viewer and visualization endpoints
- BIM data analysis and reporting
- Model versioning and change tracking
- Integration with construction management systems

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
import time
import base64
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


class BIMAPIClient:
    """
    BIM API client using Autodesk Platform Services.
    
    Supports OAuth2 authentication, 3D model processing, and comprehensive
    BIM data management for construction projects.
    """
    
    # Autodesk Platform Services Configuration
    BASE_URL = "https://developer.api.autodesk.com"
    AUTH_URL = "https://developer.api.autodesk.com/authentication/v1"
    DATA_URL = "https://developer.api.autodesk.com/data/v1"
    MODEL_DERIVATIVE_URL = "https://developer.api.autodesk.com/modelderivative/v2"
    BIM_360_URL = "https://developer.api.autodesk.com/bim360/v1"
    
    # OAuth2 Configuration
    GRANT_TYPE = "client_credentials"
    SCOPE = "data:read viewables:read bucket:read bucket:create data:write"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    MAX_REQUESTS_PER_WINDOW = 200  # Autodesk has moderate limits
    
    # Retry Configuration
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.3
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the BIM API client.
        
        Args:
            config: Configuration dictionary with API credentials and settings
        """
        self.config = config or self._get_default_config()
        self.session = self._create_session()
        self.access_token = None
        self.token_expires_at = None
        
        # Initialize authentication
        self._authenticate()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from Django settings."""
        return {
            'client_id': getattr(settings, 'AUTODESK_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'AUTODESK_CLIENT_SECRET', ''),
            'bucket_key': getattr(settings, 'AUTODESK_BUCKET_KEY', ''),
            'project_id': getattr(settings, 'AUTODESK_PROJECT_ID', ''),
            'hub_id': getattr(settings, 'AUTODESK_HUB_ID', ''),
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
        """Authenticate with Autodesk Platform Services."""
        try:
            # Check if we have a valid cached token
            if self._is_token_valid():
                return
            
            # Prepare authentication request
            auth_data = {
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'grant_type': self.GRANT_TYPE,
                'scope': self.SCOPE
            }
            
            # Encode credentials
            credentials = base64.b64encode(
                f"{self.config['client_id']}:{self.config['client_secret']}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Make authentication request
            response = self.session.post(
                f"{self.AUTH_URL}/authenticate",
                data=auth_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires_at = timezone.now() + timedelta(seconds=token_data['expires_in'] - 300)  # 5 min buffer
                
                # Cache the token
                cache.set('autodesk_access_token', self.access_token, token_data['expires_in'] - 300)
                cache.set('autodesk_token_expires', self.token_expires_at.isoformat(), token_data['expires_in'] - 300)
                
                logger.info("Autodesk Platform Services authentication successful")
            else:
                raise AuthenticationError(f"Authentication failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Autodesk authentication failed: {str(e)}")
            raise AuthenticationError(f"Failed to authenticate with Autodesk: {str(e)}")
    
    def _is_token_valid(self) -> bool:
        """Check if the current access token is valid."""
        if not self.access_token:
            # Try to get from cache
            cached_token = cache.get('autodesk_access_token')
            cached_expires = cache.get('autodesk_token_expires')
            
            if cached_token and cached_expires:
                self.access_token = cached_token
                self.token_expires_at = datetime.fromisoformat(cached_expires)
            else:
                return False
        
        return self.token_expires_at and timezone.now() < self.token_expires_at
    
    def _refresh_token_if_needed(self) -> None:
        """Refresh the access token if it's expired."""
        if not self._is_token_valid():
            logger.info("Autodesk access token expired, refreshing...")
            self._authenticate()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        cache_key = f'autodesk_rate_limit_{int(time.time() // self.RATE_LIMIT_WINDOW)}'
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
        Make an authenticated request to the Autodesk API.
        
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
                raise RateLimitError("Autodesk API rate limit exceeded")
            
            # Prepare request
            url = f"{self.BASE_URL}{endpoint}"
            request_headers = {
                'Authorization': f'Bearer {self.access_token}',
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
                logger.warning("Autodesk authentication expired, re-authenticating...")
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
                f"Autodesk API {method} {endpoint} - Status: {response.status_code}"
            )
            
            # Handle API errors
            if response.status_code >= 400:
                self._handle_api_error(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in Autodesk API request: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Autodesk API request: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Unknown API error')
        except ValueError:
            error_message = f"HTTP {response.status_code}: {response.text}"
        
        logger.error(f"Autodesk API error: {error_message}")
        
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
    
    # BIM 360 Project Management
    
    def get_hubs(self) -> List[Dict[str, Any]]:
        """Get all hubs accessible to the authenticated user."""
        response = self._make_request('GET', '/bim360/v1/hubs')
        return response.json()['data']
    
    def get_projects(self, hub_id: str = None) -> List[Dict[str, Any]]:
        """Get projects from a specific hub."""
        hub_id = hub_id or self.config['hub_id']
        response = self._make_request('GET', f'/bim360/v1/hubs/{hub_id}/projects')
        return response.json()['data']
    
    def get_project_details(self, project_id: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific project."""
        project_id = project_id or self.config['project_id']
        response = self._make_request('GET', f'/bim360/v1/projects/{project_id}')
        return response.json()['data']
    
    def get_project_top_folders(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Get top-level folders in a project."""
        project_id = project_id or self.config['project_id']
        response = self._make_request('GET', f'/bim360/v1/projects/{project_id}/topFolders')
        return response.json()['data']
    
    def get_folder_contents(self, project_id: str, folder_id: str) -> List[Dict[str, Any]]:
        """Get contents of a specific folder."""
        response = self._make_request('GET', f'/bim360/v1/projects/{project_id}/folders/{folder_id}/contents')
        return response.json()['data']
    
    def get_item_details(self, project_id: str, item_id: str) -> Dict[str, Any]:
        """Get details of a specific item (file, folder, etc.)."""
        response = self._make_request('GET', f'/bim360/v1/projects/{project_id}/items/{item_id}')
        return response.json()['data']
    
    def get_item_versions(self, project_id: str, item_id: str) -> List[Dict[str, Any]]:
        """Get versions of a specific item."""
        response = self._make_request('GET', f'/bim360/v1/projects/{project_id}/items/{item_id}/versions')
        return response.json()['data']
    
    # Model Derivative and Viewing
    
    def translate_model(self, urn: str, target_formats: List[str] = None) -> Dict[str, Any]:
        """Translate a model to viewable formats."""
        if target_formats is None:
            target_formats = ['svf', 'svf2']
        
        data = {
            'input': {'urn': urn},
            'output': {'formats': [{'type': fmt} for fmt in target_formats]}
        }
        
        response = self._make_request('POST', '/modelderivative/v2/designdata/job', data=data)
        return response.json()
    
    def get_translation_status(self, urn: str) -> Dict[str, Any]:
        """Get the status of a model translation."""
        response = self._make_request('GET', f'/modelderivative/v2/designdata/{urn}/manifest')
        return response.json()
    
    def get_model_viewables(self, urn: str) -> List[Dict[str, Any]]:
        """Get viewable formats for a translated model."""
        response = self._make_request('GET', f'/modelderivative/v2/designdata/{urn}/manifest')
        manifest = response.json()
        
        viewables = []
        for derivative in manifest.get('derivatives', []):
            for viewable in derivative.get('children', []):
                if viewable.get('type') == 'view':
                    viewables.append(viewable)
        
        return viewables
    
    def get_model_metadata(self, urn: str) -> Dict[str, Any]:
        """Get metadata for a translated model."""
        response = self._make_request('GET', f'/modelderivative/v2/designdata/{urn}/metadata')
        return response.json()
    
    def get_model_properties(self, urn: str, guid: str = None) -> Dict[str, Any]:
        """Get properties for a specific object in a model."""
        if guid:
            response = self._make_request('GET', f'/modelderivative/v2/designdata/{urn}/metadata/{guid}/properties')
        else:
            response = self._make_request('GET', f'/modelderivative/v2/designdata/{urn}/properties')
        return response.json()
    
    # Data Management
    
    def create_bucket(self, bucket_key: str, policy_key: str = 'transient') -> Dict[str, Any]:
        """Create a new bucket for storing data."""
        data = {
            'bucketKey': bucket_key,
            'policyKey': policy_key
        }
        
        response = self._make_request('POST', '/data/v1/buckets', data=data)
        return response.json()
    
    def upload_file(self, bucket_key: str, object_key: str, file_path: str) -> Dict[str, Any]:
        """Upload a file to a bucket."""
        # First, get upload URL
        response = self._make_request('POST', f'/data/v1/buckets/{bucket_key}/objects/{object_key}/signeds3upload')
        upload_data = response.json()
        
        # Upload to S3
        with open(file_path, 'rb') as f:
            upload_response = requests.put(
                upload_data['urls'][0],
                data=f,
                headers={'Content-Type': 'application/octet-stream'}
            )
        
        if upload_response.status_code == 200:
            # Complete the upload
            complete_data = {
                'uploadKey': upload_data['uploadKey']
            }
            complete_response = self._make_request(
                'POST',
                f'/data/v1/buckets/{bucket_key}/objects/{object_key}/signeds3upload',
                data=complete_data
            )
            return complete_response.json()
        else:
            raise APIError(f"File upload failed: {upload_response.status_code}")
    
    def get_bucket_contents(self, bucket_key: str) -> List[Dict[str, Any]]:
        """Get contents of a bucket."""
        response = self._make_request('GET', f'/data/v1/buckets/{bucket_key}/objects')
        return response.json()['items']
    
    def delete_file(self, bucket_key: str, object_key: str) -> bool:
        """Delete a file from a bucket."""
        response = self._make_request('DELETE', f'/data/v1/buckets/{bucket_key}/objects/{object_key}')
        return response.status_code == 204
    
    # BIM Data Analysis
    
    def extract_model_quantities(self, urn: str) -> Dict[str, Any]:
        """Extract quantity takeoffs from a BIM model."""
        # This would typically involve custom analysis of the model data
        # For now, return a placeholder structure
        return {
            'urn': urn,
            'quantities': {
                'concrete': {'volume': 0, 'units': 'm³'},
                'steel': {'weight': 0, 'units': 'kg'},
                'lumber': {'volume': 0, 'units': 'm³'},
                'drywall': {'area': 0, 'units': 'm²'}
            },
            'extraction_date': timezone.now().isoformat()
        }
    
    def analyze_model_clashes(self, urn: str) -> List[Dict[str, Any]]:
        """Analyze a model for potential clashes."""
        # This would involve clash detection algorithms
        # For now, return a placeholder structure
        return [
            {
                'clash_id': 'clash_001',
                'severity': 'high',
                'description': 'Structural beam intersects with HVAC duct',
                'location': {'x': 0, 'y': 0, 'z': 0},
                'elements': ['beam_001', 'duct_001']
            }
        ]
    
    def get_model_schedule_data(self, urn: str) -> Dict[str, Any]:
        """Extract schedule information from a BIM model."""
        # This would parse schedule data embedded in the model
        return {
            'urn': urn,
            'schedule_data': {
                'phases': [],
                'activities': [],
                'dependencies': []
            },
            'extraction_date': timezone.now().isoformat()
        }
    
    # Health Check and Monitoring
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Autodesk API connection."""
        try:
            start_time = time.time()
            response = self._make_request('GET', '/bim360/v1/hubs')
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': round(response_time, 3),
                'timestamp': timezone.now().isoformat(),
                'api_version': 'v1',
                'client_id': self.config['client_id'][:8] + '...' if self.config['client_id'] else None
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat(),
                'api_version': 'v1',
                'client_id': self.config['client_id'][:8] + '...' if self.config['client_id'] else None
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get detailed API status information."""
        try:
            # Test multiple endpoints
            endpoints = [
                '/bim360/v1/hubs',
                '/data/v1/buckets',
                '/modelderivative/v2/designdata'
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
