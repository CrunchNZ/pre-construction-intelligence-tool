"""
Custom exceptions for the integrations app
"""


class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass


class AuthenticationError(IntegrationError):
    """Raised when authentication fails"""
    pass


class APIError(IntegrationError):
    """Raised when an API call fails"""
    pass


class ConfigurationError(IntegrationError):
    """Raised when configuration is invalid"""
    pass


class DataValidationError(IntegrationError):
    """Raised when data validation fails"""
    pass


class RateLimitError(IntegrationError):
    """Raised when rate limits are exceeded"""
    pass


class NetworkError(IntegrationError):
    """Raised when network-related errors occur"""
    pass


class ConnectionError(IntegrationError):
    """Raised when connection to external service fails"""
    pass


class TimeoutError(IntegrationError):
    """Raised when a request times out"""
    pass
