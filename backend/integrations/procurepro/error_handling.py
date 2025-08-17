"""
ProcurePro Error Handling and Retry Logic

Provides comprehensive error handling, retry mechanisms, and circuit breaker
patterns for ProcurePro synchronization operations.
"""

import logging
import time
import traceback
from functools import wraps
from typing import Callable, Any, Dict, Optional, List
from django.utils import timezone
from datetime import timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification and handling."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class ErrorCategory(Enum):
    """Error categories for grouping and analysis."""
    NETWORK = 'network'
    AUTHENTICATION = 'authentication'
    AUTHORIZATION = 'authorization'
    RATE_LIMIT = 'rate_limit'
    VALIDATION = 'validation'
    DATABASE = 'database'
    EXTERNAL_API = 'external_api'
    INTERNAL = 'internal'
    UNKNOWN = 'unknown'


class ProcureProError(Exception):
    """Base exception class for ProcurePro-specific errors."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Optional[Dict] = None, retryable: bool = True):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.retryable = retryable
        self.timestamp = timezone.now()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict:
        """Convert error to dictionary for logging and serialization."""
        return {
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details,
            'retryable': self.retryable,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback
        }


class NetworkError(ProcureProError):
    """Network-related errors (timeouts, connection failures, etc.)."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=True
        )


class AuthenticationError(ProcureProError):
    """Authentication-related errors (invalid credentials, expired tokens, etc.)."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            retryable=False  # Don't retry auth errors
        )


class RateLimitError(ProcureProError):
    """Rate limiting errors from external API."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict] = None):
        if retry_after:
            details = details or {}
            details['retry_after'] = retry_after
        
        super().__init__(
            message=message,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            retryable=True
        )


class ValidationError(ProcureProError):
    """Data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        if field:
            details = details or {}
            details['field'] = field
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            retryable=False  # Don't retry validation errors
        )


class CircuitBreaker:
    """Circuit breaker pattern implementation for external API calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
        self._lock = None  # Would be threading.Lock() in production
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
            else:
                raise ProcureProError(
                    "Circuit breaker is OPEN - too many recent failures",
                    category=ErrorCategory.EXTERNAL_API,
                    severity=ErrorSeverity.HIGH,
                    retryable=True
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful function execution."""
        self.failure_count = 0
        self.state = 'CLOSED'
        logger.debug("Circuit breaker reset to CLOSED state")
    
    def _on_failure(self):
        """Handle function execution failure."""
        self.failure_count += 1
        self.last_failure_time = timezone.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        
        return (timezone.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout
    
    def get_status(self) -> Dict:
        """Get current circuit breaker status."""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout
        }


class RetryHandler:
    """Advanced retry logic with exponential backoff and jitter."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(f"Function failed after {self.max_retries} retries: {e}")
                    raise e
                
                # Calculate delay with exponential backoff
                delay = self._calculate_delay(attempt)
                
                logger.warning(f"Function failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                             f"retrying in {delay:.2f} seconds: {e}")
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter to prevent thundering herd
            import random
            jitter_factor = random.uniform(0.5, 1.5)
            delay *= jitter_factor
        
        return delay


class ErrorTracker:
    """Track and analyze errors for monitoring and alerting."""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self.errors: List[Dict] = []
        self.error_counts: Dict[str, int] = {}
        self.category_counts: Dict[str, int] = {}
        self.severity_counts: Dict[str, int] = {}
    
    def track_error(self, error: ProcureProError):
        """Track a new error."""
        error_dict = error.to_dict()
        
        # Add to errors list
        self.errors.append(error_dict)
        
        # Maintain max size
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)
        
        # Update counts
        error_key = f"{error.category.value}:{error.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        self.category_counts[error.category.value] = self.category_counts.get(error.category.value, 0) + 1
        self.severity_counts[error.severity.value] = self.severity_counts.get(error.severity.value, 0) + 1
    
    def get_error_summary(self, hours: int = 24) -> Dict:
        """Get error summary for the specified time period."""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.errors
            if timezone.datetime.fromisoformat(error['timestamp']) >= cutoff_time
        ]
        
        return {
            'total_errors': len(recent_errors),
            'error_counts': self.error_counts.copy(),
            'category_counts': self.category_counts.copy(),
            'severity_counts': self.severity_counts.copy(),
            'recent_errors': recent_errors[-10:],  # Last 10 errors
            'period_hours': hours
        }
    
    def clear_errors(self):
        """Clear all tracked errors."""
        self.errors.clear()
        self.error_counts.clear()
        self.category_counts.clear()
        self.severity_counts.clear()


# Global error tracker instance
error_tracker = ErrorTracker()

# Global circuit breaker instances
circuit_breakers = {
    'api_calls': CircuitBreaker(failure_threshold=10, recovery_timeout=300),
    'sync_operations': CircuitBreaker(failure_threshold=5, recovery_timeout=600),
    'health_checks': CircuitBreaker(failure_threshold=3, recovery_timeout=180)
}


def handle_procurepro_error(func: Callable) -> Callable:
    """Decorator for handling ProcurePro errors with proper logging and tracking."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
            
        except ProcureProError as e:
            # Track the error
            error_tracker.track_error(e)
            
            # Log based on severity
            if e.severity == ErrorSeverity.CRITICAL:
                logger.critical(f"CRITICAL ProcurePro error: {e.message}", extra=e.to_dict())
            elif e.severity == ErrorSeverity.HIGH:
                logger.error(f"HIGH ProcurePro error: {e.message}", extra=e.to_dict())
            elif e.severity == ErrorSeverity.MEDIUM:
                logger.warning(f"MEDIUM ProcurePro error: {e.message}", extra=e.to_dict())
            else:
                logger.info(f"LOW ProcurePro error: {e.message}", extra=e.to_dict())
            
            # Re-raise the error
            raise e
            
        except Exception as e:
            # Convert generic exceptions to ProcureProError
            procurepro_error = ProcureProError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                category=ErrorCategory.INTERNAL,
                severity=ErrorSeverity.HIGH,
                details={'original_exception': str(e)},
                retryable=True
            )
            
            error_tracker.track_error(procurepro_error)
            logger.error(f"Unexpected error converted to ProcureProError: {e}", exc_info=True)
            
            raise procurepro_error
    
    return wrapper


def with_circuit_breaker(circuit_breaker_name: str):
    """Decorator for applying circuit breaker pattern."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = circuit_breakers.get(circuit_breaker_name)
            if circuit_breaker:
                return circuit_breaker.call(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for applying retry logic."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(
                max_retries=max_retries,
                base_delay=base_delay
            )
            return retry_handler.retry(func, *args, **kwargs)
        return wrapper
    return decorator


def classify_error(error: Exception) -> ProcureProError:
    """Classify a generic exception into a ProcureProError."""
    
    error_message = str(error)
    error_type = type(error).__name__
    
    # Network-related errors
    if any(keyword in error_message.lower() for keyword in ['timeout', 'connection', 'network', 'dns']):
        return NetworkError(f"Network error: {error_message}", {'original_type': error_type})
    
    # Authentication errors
    if any(keyword in error_message.lower() for keyword in ['auth', 'token', 'credential', 'unauthorized']):
        return AuthenticationError(f"Authentication error: {error_message}", {'original_type': error_type})
    
    # Rate limiting errors
    if any(keyword in error_message.lower() for keyword in ['rate limit', 'throttle', 'too many requests']):
        return RateLimitError(f"Rate limit error: {error_message}", {'original_type': error_type})
    
    # Validation errors
    if any(keyword in error_message.lower() for keyword in ['validation', 'invalid', 'format']):
        return ValidationError(f"Validation error: {error_message}", {'original_type': error_type})
    
    # Default to internal error
    return ProcureProError(
        f"Internal error: {error_message}",
        category=ErrorCategory.INTERNAL,
        severity=ErrorSeverity.MEDIUM,
        details={'original_type': error_type},
        retryable=True
    )


def get_error_handling_status() -> Dict:
    """Get current status of error handling systems."""
    return {
        'error_tracker': error_tracker.get_error_summary(),
        'circuit_breakers': {
            name: breaker.get_status()
            for name, breaker in circuit_breakers.items()
        }
    }
