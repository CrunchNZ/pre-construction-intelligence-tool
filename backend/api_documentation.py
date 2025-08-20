"""
API Documentation Configuration for Pre-Construction Intelligence Platform

This module provides comprehensive configuration for API documentation using drf-spectacular,
including proper tagging, examples, and documentation for all API endpoints.
"""

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type, build_parameter_type
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# API Documentation Tags
API_TAGS = {
    'core': {
        'name': 'core',
        'description': 'Core project and analytics endpoints for managing construction projects, suppliers, and basic operations.',
        'externalDocs': {
            'description': 'Core API Documentation',
            'url': 'https://docs.preconstruction-intelligence.com/core/',
        }
    },
    'integrations': {
        'name': 'integrations',
        'description': 'External system integrations including Procore, Jobpac, Greentree, and ProcurePro for seamless data synchronization.',
        'externalDocs': {
            'description': 'Integrations Documentation',
            'url': 'https://docs.preconstruction-intelligence.com/integrations/',
        }
    },
    'ai-models': {
        'name': 'ai-models',
        'description': 'Machine learning models and predictions for cost estimation, timeline prediction, risk assessment, and quality analysis.',
        'externalDocs': {
            'description': 'AI/ML Documentation',
            'url': 'https://docs.preconstruction-intelligence.com/ai-models/',
        }
    },
    'analytics': {
        'name': 'analytics',
        'description': 'Historical data analytics, reporting, and trend analysis for construction projects and performance metrics.',
        'externalDocs': {
            'description': 'Analytics Documentation',
            'url': 'https://docs.preconstruction-intelligence.com/analytics/',
        }
    },
    'kafka': {
        'name': 'kafka',
        'description': 'Real-time data streaming endpoints for live construction data, event processing, and real-time analytics.',
        'externalDocs': {
            'description': 'Real-time Data Documentation',
            'url': 'https://docs.preconstruction-intelligence.com/real-time/',
        }
    },
}

# Common Response Examples
COMMON_EXAMPLES = {
    'project_created': OpenApiExample(
        'Project Created Successfully',
        value={
            'id': 1,
            'name': 'Downtown Office Complex',
            'status': 'planning',
            'start_date': '2024-01-15',
            'estimated_completion': '2025-06-30',
            'budget': 25000000,
            'created_at': '2024-01-10T10:00:00Z',
            'updated_at': '2024-01-10T10:00:00Z'
        },
        response_only=True,
        status_codes=['201']
    ),
    'project_updated': OpenApiExample(
        'Project Updated Successfully',
        value={
            'id': 1,
            'name': 'Downtown Office Complex - Updated',
            'status': 'active',
            'start_date': '2024-01-15',
            'estimated_completion': '2025-08-30',
            'budget': 27500000,
            'created_at': '2024-01-10T10:00:00Z',
            'updated_at': '2024-01-10T14:30:00Z'
        },
        response_only=True,
        status_codes=['200']
    ),
    'error_400': OpenApiExample(
        'Bad Request',
        value={
            'error': 'Validation failed',
            'details': {
                'name': ['This field is required.'],
                'budget': ['A valid number is required.']
            }
        },
        response_only=True,
        status_codes=['400']
    ),
    'error_401': OpenApiExample(
        'Unauthorized',
        value={
            'error': 'Authentication credentials were not provided.',
            'code': 'authentication_failed'
        },
        response_only=True,
        status_codes=['401']
    ),
    'error_404': OpenApiExample(
        'Not Found',
        value={
            'error': 'Project not found.',
            'code': 'not_found'
        },
        response_only=True,
        status_codes=['404']
    ),
    'error_500': OpenApiExample(
        'Internal Server Error',
        value={
            'error': 'An unexpected error occurred.',
            'code': 'internal_error',
            'request_id': 'req_123456789'
        },
        response_only=True,
        status_codes=['500']
    ),
}

# Common Parameters
COMMON_PARAMETERS = {
    'pagination': [
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination',
            default=1
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of items per page',
            default=20
        ),
    ],
    'filtering': [
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search term for filtering results'
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by status'
        ),
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Filter by start date (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Filter by end date (YYYY-MM-DD)'
        ),
    ],
    'ordering': [
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Order results by field (prefix with - for descending)',
            examples=[
                OpenApiExample('Name Ascending', value='name'),
                OpenApiExample('Name Descending', value='-name'),
                OpenApiExample('Date Ascending', value='created_at'),
                OpenApiExample('Date Descending', value='-created_at'),
            ]
        ),
    ],
}

# Authentication Schemes
AUTH_SCHEMES = {
    'session': {
        'type': 'apiKey',
        'in': 'cookie',
        'name': 'sessionid',
        'description': 'Session-based authentication'
    },
    'token': {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'Token',
        'description': 'Token-based authentication'
    }
}

# Rate Limiting Information
RATE_LIMITING = {
    'default': '1000/hour',
    'authenticated': '5000/hour',
    'admin': '10000/hour',
    'ml_endpoints': '100/hour',
    'kafka_endpoints': '1000/hour'
}

# API Versioning
API_VERSIONS = {
    'current': '1.0.0',
    'supported': ['1.0.0'],
    'deprecated': [],
    'sunset_date': None
}

# Contact Information
CONTACT_INFO = {
    'name': 'Pre-Construction Intelligence Team',
    'email': 'api-support@preconstruction-intelligence.com',
    'url': 'https://support.preconstruction-intelligence.com',
    'description': 'Technical support for the Pre-Construction Intelligence API'
}

# License Information
LICENSE_INFO = {
    'name': 'MIT License',
    'url': 'https://opensource.org/licenses/MIT',
    'description': 'Open source license allowing commercial use, modification, and distribution'
}

# External Documentation Links
EXTERNAL_DOCS = {
    'getting_started': 'https://docs.preconstruction-intelligence.com/getting-started/',
    'authentication': 'https://docs.preconstruction-intelligence.com/authentication/',
    'rate_limiting': 'https://docs.preconstruction-intelligence.com/rate-limiting/',
    'webhooks': 'https://docs.preconstruction-intelligence.com/webhooks/',
    'sdk_downloads': 'https://docs.preconstruction-intelligence.com/sdks/',
    'changelog': 'https://docs.preconstruction-intelligence.com/changelog/',
    'status_page': 'https://status.preconstruction-intelligence.com/',
}

# Webhook Information
WEBHOOK_INFO = {
    'supported_events': [
        'project.created',
        'project.updated',
        'project.deleted',
        'supplier.added',
        'risk.identified',
        'ml.prediction.completed',
        'integration.sync.completed'
    ],
    'webhook_url': 'https://api.preconstruction-intelligence.com/webhooks/',
    'webhook_docs': 'https://docs.preconstruction-intelligence.com/webhooks/'
}

# SDK Information
SDK_INFO = {
    'python': {
        'package_name': 'preconstruction-intelligence-python',
        'version': '1.0.0',
        'install_command': 'pip install preconstruction-intelligence-python',
        'docs_url': 'https://docs.preconstruction-intelligence.com/python-sdk/',
        'github_url': 'https://github.com/preconstruction-intelligence/python-sdk'
    },
    'javascript': {
        'package_name': '@preconstruction-intelligence/js-sdk',
        'version': '1.0.0',
        'install_command': 'npm install @preconstruction-intelligence/js-sdk',
        'docs_url': 'https://docs.preconstruction-intelligence.com/javascript-sdk/',
        'github_url': 'https://github.com/preconstruction-intelligence/javascript-sdk'
    },
    'postman': {
        'collection_url': 'https://docs.preconstruction-intelligence.com/postman-collection/',
        'environment_url': 'https://docs.preconstruction-intelligence.com/postman-environment/'
    }
}

def get_api_documentation_config():
    """
    Returns the complete API documentation configuration.
    
    Returns:
        dict: Complete configuration for API documentation
    """
    return {
        'tags': API_TAGS,
        'examples': COMMON_EXAMPLES,
        'parameters': COMMON_PARAMETERS,
        'auth_schemes': AUTH_SCHEMES,
        'rate_limiting': RATE_LIMITING,
        'versions': API_VERSIONS,
        'contact': CONTACT_INFO,
        'license': LICENSE_INFO,
        'external_docs': EXTERNAL_DOCS,
        'webhooks': WEBHOOK_INFO,
        'sdks': SDK_INFO,
    }
