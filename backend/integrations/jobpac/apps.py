"""
Django app configuration for Jobpac integration.

This app handles all Jobpac-related functionality including
API integration, data synchronization, and analytics.
"""

from django.apps import AppConfig


class JobpacConfig(AppConfig):
    """Configuration for the Jobpac integration app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations.jobpac'
    verbose_name = 'Jobpac Integration'
    
    def ready(self):
        """Initialize the app when Django is ready."""
        try:
            # Import signals and tasks when Django is ready
            import integrations.jobpac.signals  # noqa
        except ImportError:
            pass
