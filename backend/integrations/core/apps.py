"""
Core integrations app configuration.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations.core'
    verbose_name = 'Core Integrations'
    
    def ready(self):
        """App is ready."""
        pass

