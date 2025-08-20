"""
Pre-Construction Intelligence Python SDK

A comprehensive Python SDK for interacting with the Pre-Construction Intelligence API.
Provides easy access to all endpoints with proper error handling, authentication, and data validation.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlencode
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Project:
    """Project data model"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    status: str = "planning"
    start_date: Optional[date] = None
    estimated_completion: Optional[date] = None
    budget: Optional[float] = None
    location: str = ""
    project_manager: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Supplier:
    """Supplier data model"""
    id: Optional[int] = None
    name: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    specialties: List[str] = None
    rating: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class RiskAssessment:
    """Risk assessment data model"""
    id: Optional[int] = None
    project_id: int = 0
    risk_type: str = ""
    description: str = ""
    probability: str = "low"
    impact: str = "low"
    mitigation_strategy: str = ""
    status: str = "open"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class MLPrediction:
    """Machine learning prediction data model"""
    id: Optional[int] = None
    model_name: str = ""
    prediction_type: str = ""
    input_data: Dict[str, Any] = None
    prediction_result: Dict[str, Any] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None

class PreConstructionIntelligenceError(Exception):
    """Base exception for Pre-Construction Intelligence SDK"""
    pass

class AuthenticationError(PreConstructionIntelligenceError):
    """Authentication failed"""
    pass

class ValidationError(PreConstructionIntelligenceError):
    """Data validation failed"""
    pass

class RateLimitError(PreConstructionIntelligenceError):
    """Rate limit exceeded"""
    pass

class APIError(PreConstructionIntelligenceError):
    """General API error"""
    def __init__(self, message: str, status_code: int, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class PreConstructionIntelligenceSDK:
    """
    Python SDK for Pre-Construction Intelligence Platform
    
    Provides easy access to all API endpoints with proper error handling,
    authentication, and data validation.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, session_token: Optional[str] = None):
        """
        Initialize the SDK
        
        Args:
            base_url: Base URL for the API (e.g., 'https://api.preconstruction-intelligence.com')
            api_key: API key for authentication
            session_token: Session token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session_token = session_token
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PreConstructionIntelligence-Python-SDK/1.0.0'
        })
        
        # Set authentication
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        elif session_token:
            self.session.cookies.set('sessionid', session_token)
        
        # Configure retry strategy
        self.max_retries = 3
        self.retry_delay = 1
        
        logger.info(f"SDK initialized for {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, retry_count: int = 0) -> Dict:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            retry_count: Current retry attempt
            
        Returns:
            Response data as dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If data validation fails
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle different response status codes
            if response.status_code == 200:
                return response.json() if response.content else {}
            elif response.status_code == 201:
                return response.json() if response.content else {}
            elif response.status_code == 204:
                return {}
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(f"Validation failed: {error_data.get('error', 'Unknown error')}")
            elif response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please check your credentials.")
            elif response.status_code == 403:
                raise APIError("Access denied. Insufficient permissions.", 403)
            elif response.status_code == 404:
                raise APIError("Resource not found.", 404)
            elif response.status_code == 429:
                if retry_count < self.max_retries:
                    wait_time = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, data, params, retry_count + 1)
                else:
                    raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status_code >= 500:
                if retry_count < self.max_retries:
                    wait_time = self.retry_delay * (2 ** retry_count)
                    logger.warning(f"Server error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, data, params, retry_count + 1)
                else:
                    raise APIError(f"Server error: {response.status_code}", response.status_code)
            else:
                raise APIError(f"Unexpected response: {response.status_code}", response.status_code)
                
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.warning(f"Request failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self._make_request(method, endpoint, data, params, retry_count + 1)
            else:
                raise APIError(f"Request failed: {str(e)}", 0)
    
    # Core API Methods
    
    def get_projects(self, page: int = 1, page_size: int = 20, 
                    search: Optional[str] = None, status: Optional[str] = None,
                    start_date: Optional[str] = None, end_date: Optional[str] = None,
                    ordering: Optional[str] = None) -> Dict:
        """
        Get list of projects with filtering and pagination
        
        Args:
            page: Page number
            page_size: Items per page
            search: Search term
            status: Filter by status
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            ordering: Order by field (prefix with - for descending)
            
        Returns:
            Dictionary containing projects and pagination info
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        
        if search:
            params['search'] = search
        if status:
            params['status'] = status
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if ordering:
            params['ordering'] = ordering
        
        return self._make_request('GET', '/api/projects/', params=params)
    
    def get_project(self, project_id: int) -> Dict:
        """
        Get a specific project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data
        """
        return self._make_request('GET', f'/api/projects/{project_id}/')
    
    def create_project(self, project: Project) -> Dict:
        """
        Create a new project
        
        Args:
            project: Project object
            
        Returns:
            Created project data
        """
        data = asdict(project)
        # Remove None values and convert dates to strings
        data = {k: v for k, v in data.items() if v is not None}
        if 'start_date' in data and isinstance(data['start_date'], date):
            data['start_date'] = data['start_date'].isoformat()
        if 'estimated_completion' in data and isinstance(data['estimated_completion'], date):
            data['estimated_completion'] = data['estimated_completion'].isoformat()
        
        return self._make_request('POST', '/api/projects/', data=data)
    
    def update_project(self, project_id: int, project: Project) -> Dict:
        """
        Update an existing project
        
        Args:
            project_id: Project ID
            project: Updated project data
            
        Returns:
            Updated project data
        """
        data = asdict(project)
        # Remove None values and convert dates to strings
        data = {k: v for k, v in data.items() if v is not None}
        if 'start_date' in data and isinstance(data['start_date'], date):
            data['start_date'] = data['start_date'].isoformat()
        if 'estimated_completion' in data and isinstance(data['estimated_completion'], date):
            data['estimated_completion'] = data['estimated_completion'].isoformat()
        
        return self._make_request('PUT', f'/api/projects/{project_id}/', data=data)
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
        """
        self._make_request('DELETE', f'/api/projects/{project_id}/')
        return True
    
    # Suppliers API Methods
    
    def get_suppliers(self, page: int = 1, page_size: int = 20,
                     search: Optional[str] = None, specialties: Optional[List[str]] = None,
                     min_rating: Optional[float] = None, ordering: Optional[str] = None) -> Dict:
        """
        Get list of suppliers with filtering and pagination
        
        Args:
            page: Page number
            page_size: Items per page
            search: Search term
            specialties: Filter by specialties
            min_rating: Minimum rating filter
            ordering: Order by field
            
        Returns:
            Dictionary containing suppliers and pagination info
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        
        if search:
            params['search'] = search
        if specialties:
            params['specialties'] = ','.join(specialties)
        if min_rating:
            params['min_rating'] = min_rating
        if ordering:
            params['ordering'] = ordering
        
        return self._make_request('GET', '/api/suppliers/', params=params)
    
    def get_supplier(self, supplier_id: int) -> Dict:
        """
        Get a specific supplier by ID
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Supplier data
        """
        return self._make_request('GET', f'/api/suppliers/{supplier_id}/')
    
    def create_supplier(self, supplier: Supplier) -> Dict:
        """
        Create a new supplier
        
        Args:
            supplier: Supplier object
            
        Returns:
            Created supplier data
        """
        data = asdict(supplier)
        data = {k: v for k, v in data.items() if v is not None}
        
        return self._make_request('POST', '/api/suppliers/', data=data)
    
    # Risk Analysis API Methods
    
    def get_risks(self, project_id: Optional[int] = None, page: int = 1, page_size: int = 20,
                  risk_type: Optional[str] = None, status: Optional[str] = None,
                  probability: Optional[str] = None, impact: Optional[str] = None) -> Dict:
        """
        Get list of risk assessments with filtering and pagination
        
        Args:
            project_id: Filter by project ID
            page: Page number
            page_size: Items per page
            risk_type: Filter by risk type
            status: Filter by status
            probability: Filter by probability
            impact: Filter by impact
            
        Returns:
            Dictionary containing risks and pagination info
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        
        if project_id:
            params['project_id'] = project_id
        if risk_type:
            params['risk_type'] = risk_type
        if status:
            params['status'] = status
        if probability:
            params['probability'] = probability
        if impact:
            params['impact'] = impact
        
        return self._make_request('GET', '/api/risks/', params=params)
    
    def create_risk_assessment(self, risk: RiskAssessment) -> Dict:
        """
        Create a new risk assessment
        
        Args:
            risk: Risk assessment object
            
        Returns:
            Created risk assessment data
        """
        data = asdict(risk)
        data = {k: v for k, v in data.items() if v is not None}
        
        return self._make_request('POST', '/api/risks/', data=data)
    
    # AI/ML API Methods
    
    def get_ml_predictions(self, model_name: Optional[str] = None, 
                          prediction_type: Optional[str] = None,
                          page: int = 1, page_size: int = 20) -> Dict:
        """
        Get list of ML predictions
        
        Args:
            model_name: Filter by model name
            prediction_type: Filter by prediction type
            page: Page number
            page_size: Items per page
            
        Returns:
            Dictionary containing predictions and pagination info
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        
        if model_name:
            params['model_name'] = model_name
        if prediction_type:
            params['prediction_type'] = prediction_type
        
        return self._make_request('GET', '/api/ai/predictions/', params=params)
    
    def create_ml_prediction(self, prediction: MLPrediction) -> Dict:
        """
        Create a new ML prediction request
        
        Args:
            prediction: ML prediction object
            
        Returns:
            Created prediction data
        """
        data = asdict(prediction)
        data = {k: v for k, v in data.items() if v is not None}
        
        return self._make_request('POST', '/api/ai/predictions/', data=data)
    
    def train_ml_model(self, model_name: str, model_type: str, 
                       training_data: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Train a new ML model
        
        Args:
            model_name: Name of the model
            model_type: Type of model (e.g., 'cost_prediction', 'timeline_prediction')
            training_data: Training data configuration
            parameters: Model training parameters
            
        Returns:
            Training job information
        """
        data = {
            'model_name': model_name,
            'model_type': model_type,
            'training_data': training_data
        }
        
        if parameters:
            data['parameters'] = parameters
        
        return self._make_request('POST', '/api/ai/models/train/', data=data)
    
    # Analytics API Methods
    
    def get_analytics_dashboard(self, project_id: Optional[int] = None,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict:
        """
        Get analytics dashboard data
        
        Args:
            project_id: Filter by project ID
            start_date: Start date for analytics (YYYY-MM-DD)
            end_date: End date for analytics (YYYY-MM-DD)
            
        Returns:
            Analytics dashboard data
        """
        params = {}
        
        if project_id:
            params['project_id'] = project_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_request('GET', '/api/analytics/dashboard/', params=params)
    
    def get_project_analytics(self, project_id: int, 
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> Dict:
        """
        Get analytics for a specific project
        
        Args:
            project_id: Project ID
            start_date: Start date for analytics (YYYY-MM-DD)
            end_date: End date for analytics (YYYY-MM-DD)
            
        Returns:
            Project analytics data
        """
        params = {}
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_request('GET', f'/api/analytics/projects/{project_id}/', params=params)
    
    # Integration API Methods
    
    def get_integrations(self) -> Dict:
        """
        Get list of available integrations
        
        Returns:
            List of integrations
        """
        return self._make_request('GET', '/api/integrations/')
    
    def sync_integration(self, integration_name: str, project_id: Optional[int] = None) -> Dict:
        """
        Trigger synchronization for a specific integration
        
        Args:
            integration_name: Name of the integration
            project_id: Optional project ID to sync
            
        Returns:
            Sync job information
        """
        data = {'integration_name': integration_name}
        if project_id:
            data['project_id'] = project_id
        
        return self._make_request('POST', '/api/integrations/sync/', data=data)
    
    # Kafka/Real-time API Methods
    
    def get_kafka_topics(self) -> Dict:
        """
        Get list of available Kafka topics
        
        Returns:
            List of Kafka topics
        """
        return self._make_request('GET', '/api/kafka/topics/')
    
    def publish_message(self, topic: str, message: Dict[str, Any]) -> Dict:
        """
        Publish a message to a Kafka topic
        
        Args:
            topic: Kafka topic name
            message: Message data
            
        Returns:
            Publication confirmation
        """
        data = {
            'topic': topic,
            'message': message
        }
        
        return self._make_request('POST', '/api/kafka/publish/', data=data)
    
    # Utility Methods
    
    def get_api_status(self) -> Dict:
        """
        Get API status and health information
        
        Returns:
            API status information
        """
        return self._make_request('GET', '/api/status/')
    
    def get_api_documentation(self) -> Dict:
        """
        Get API documentation schema
        
        Returns:
            OpenAPI schema
        """
        return self._make_request('GET', '/api/schema/')
    
    def close(self):
        """Close the SDK session"""
        self.session.close()
        logger.info("SDK session closed")

# Convenience function for quick SDK initialization
def create_sdk(base_url: str, api_key: Optional[str] = None, 
               session_token: Optional[str] = None) -> PreConstructionIntelligenceSDK:
    """
    Create a new SDK instance
    
    Args:
        base_url: Base URL for the API
        api_key: API key for authentication
        session_token: Session token for authentication
        
    Returns:
        SDK instance
    """
    return PreConstructionIntelligenceSDK(base_url, api_key, session_token)
