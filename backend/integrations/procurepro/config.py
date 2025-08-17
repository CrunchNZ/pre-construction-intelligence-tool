"""
ProcurePro Integration Configuration

Centralized configuration for ProcurePro integration including
API settings, sync schedules, monitoring thresholds, and alerting.
"""

import os
from django.conf import settings
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    # API Configuration
    'api': {
        'base_url': 'https://api.procurepro.com',
        'timeout': 30,
        'max_retries': 3,
        'retry_delay': 5,
        'rate_limit': {
            'requests_per_minute': 60,
            'burst_limit': 10
        }
    },
    
    # Authentication
    'auth': {
        'method': 'oauth2',  # oauth2, api_key, basic
        'token_expiry_buffer': 300,  # 5 minutes before expiry
        'auto_refresh': True
    },
    
    # Synchronization Configuration
    'sync': {
        'default_batch_size': 100,
        'max_batch_size': 1000,
        'incremental_sync': True,
        'full_sync_interval_hours': 24,
        'sync_timeout': 3600,  # 1 hour
        'parallel_syncs': 3,
        'retry_failed_records': True,
        'max_retry_attempts': 3
    },
    
    # Entity-specific sync settings
    'entities': {
        'suppliers': {
            'sync_interval_minutes': 60,
            'batch_size': 50,
            'priority': 'high',
            'incremental': True
        },
        'purchase_orders': {
            'sync_interval_minutes': 30,
            'batch_size': 100,
            'priority': 'high',
            'incremental': True
        },
        'invoices': {
            'sync_interval_minutes': 30,
            'batch_size': 100,
            'priority': 'high',
            'incremental': True
        },
        'contracts': {
            'sync_interval_minutes': 120,
            'batch_size': 50,
            'priority': 'medium',
            'incremental': True
        }
    },
    
    # Monitoring and Alerting
    'monitoring': {
        'health_check_interval_minutes': 15,
        'performance_monitoring': True,
        'error_tracking': True,
        'circuit_breaker': {
            'enabled': True,
            'failure_threshold': 5,
            'recovery_timeout_seconds': 300,
            'monitoring_window_seconds': 600
        }
    },
    
    # Alert Thresholds
    'alerts': {
        'sync_success_rate_threshold': 90.0,
        'sync_failure_threshold': 3,
        'response_time_threshold_seconds': 30.0,
        'error_rate_threshold': 10.0,
        'circuit_breaker_open_threshold': 1
    },
    
    # Notification Channels
    'notifications': {
        'email': {
            'enabled': True,
            'recipients': [],
            'template_path': 'integrations/procurepro/emails/'
        },
        'slack': {
            'enabled': False,
            'webhook_url': None,
            'channel': '#procurepro-alerts'
        },
        'webhook': {
            'enabled': False,
            'endpoint': None,
            'timeout': 10
        }
    },
    
    # Data Processing
    'data_processing': {
        'validation': {
            'enabled': True,
            'strict_mode': False,
            'custom_validators': []
        },
        'transformation': {
            'enabled': True,
            'field_mappings': {},
            'data_cleanup': True
        },
        'deduplication': {
            'enabled': True,
            'strategy': 'timestamp_based'
        }
    },
    
    # Logging and Debugging
    'logging': {
        'level': 'INFO',
        'file_logging': True,
        'log_file_path': 'logs/procurepro/',
        'max_file_size_mb': 100,
        'backup_count': 5,
        'structured_logging': True
    },
    
    # Performance Optimization
    'performance': {
        'caching': {
            'enabled': True,
            'ttl_seconds': 3600,
            'max_size': 10000
        },
        'database': {
            'bulk_operations': True,
            'batch_size': 1000,
            'connection_pooling': True
        },
        'api': {
            'connection_pooling': True,
            'keep_alive': True,
            'compression': True
        }
    },
    
    # Security
    'security': {
        'data_encryption': True,
        'audit_logging': True,
        'access_control': {
            'enabled': True,
            'role_based': True
        },
        'api_key_rotation': {
            'enabled': True,
            'interval_days': 90
        }
    }
}


class ProcureProConfig:
    """Configuration manager for ProcurePro integration."""
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from Django settings and environment variables."""
        config = DEFAULT_CONFIG.copy()
        
        # Override with Django settings
        django_config = getattr(settings, 'PROCUREPRO_CONFIG', {})
        self._deep_merge(config, django_config)
        
        # Override with environment variables
        self._load_from_environment(config)
        
        return config
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _load_from_environment(self, config: Dict):
        """Load configuration values from environment variables."""
        env_mappings = {
            'PROCUREPRO_API_BASE_URL': ('api', 'base_url'),
            'PROCUREPRO_API_TIMEOUT': ('api', 'timeout'),
            'PROCUREPRO_SYNC_BATCH_SIZE': ('sync', 'default_batch_size'),
            'PROCUREPRO_SYNC_INTERVAL': ('sync', 'full_sync_interval_hours'),
            'PROCUREPRO_MONITORING_ENABLED': ('monitoring', 'enabled'),
            'PROCUREPRO_ALERT_EMAILS': ('notifications', 'email', 'recipients'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config, config_path, self._parse_env_value(value))
    
    def _set_nested_value(self, config: Dict, path: tuple, value: Any):
        """Set a nested configuration value."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Try to parse as boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get_sync_config(self, entity_type: str) -> Dict[str, Any]:
        """Get synchronization configuration for a specific entity type."""
        entity_config = self.get(f'entities.{entity_type}', {})
        sync_config = self.get('sync', {})
        
        # Merge entity-specific config with general sync config
        config = sync_config.copy()
        config.update(entity_config)
        
        return config
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get('monitoring', {})
    
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert configuration."""
        return self.get('alerts', {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration."""
        return self.get('notifications', {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.get(f'{feature}.enabled', False)
    
    def get_all(self) -> Dict[str, Any]:
        """Get complete configuration."""
        return self._config.copy()
    
    def reload(self):
        """Reload configuration from sources."""
        self._config = self._load_config()
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return validation results."""
        errors = []
        warnings = []
        
        # Validate required fields
        required_fields = [
            'api.base_url',
            'auth.method',
            'sync.default_batch_size'
        ]
        
        for field in required_fields:
            if not self.get(field):
                errors.append(f"Required field missing: {field}")
        
        # Validate numeric ranges
        numeric_validations = [
            ('api.timeout', 1, 300),
            ('sync.default_batch_size', 1, 10000),
            ('monitoring.health_check_interval_minutes', 1, 1440)
        ]
        
        for field, min_val, max_val in numeric_validations:
            value = self.get(field)
            if value is not None and (value < min_val or value > max_val):
                errors.append(f"Invalid value for {field}: {value} (must be between {min_val} and {max_val})")
        
        # Validate email recipients if email notifications are enabled
        if self.is_feature_enabled('notifications.email'):
            recipients = self.get('notifications.email.recipients', [])
            if not recipients:
                warnings.append("Email notifications enabled but no recipients configured")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Global configuration instance
config = ProcureProConfig()


def get_procurepro_config() -> ProcureProConfig:
    """Get the global ProcurePro configuration instance."""
    return config


def get_sync_schedule() -> Dict[str, Any]:
    """Get synchronization schedule configuration."""
    return {
        'suppliers': config.get_sync_config('suppliers'),
        'purchase_orders': config.get_sync_config('purchase_orders'),
        'invoices': config.get_sync_config('invoices'),
        'contracts': config.get_sync_config('contracts'),
        'general': config.get('sync', {})
    }


def get_monitoring_thresholds() -> Dict[str, Any]:
    """Get monitoring threshold configuration."""
    return config.get_alert_config()


def is_monitoring_enabled() -> bool:
    """Check if monitoring is enabled."""
    return config.is_feature_enabled('monitoring')


def get_notification_channels() -> Dict[str, bool]:
    """Get enabled notification channels."""
    notification_config = config.get_notification_config()
    return {
        'email': notification_config.get('email', {}).get('enabled', False),
        'slack': notification_config.get('slack', {}).get('enabled', False),
        'webhook': notification_config.get('webhook', {}).get('enabled', False)
    }
