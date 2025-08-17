"""
Django app configuration for Procore integration.

This app handles all Procore-related functionality including
API integration, data synchronization, and analytics.
"""

from django.apps import AppConfig


class ProcoreConfig(AppConfig):
    """Configuration for the Procore integration app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations.procore'
    verbose_name = 'Procore Integration'
    
    def ready(self):
        """Initialize the app when Django is ready."""
        try:
            # Import signals and tasks when Django is ready
            import integrations.procore.signals  # noqa
        except ImportError:
            pass
