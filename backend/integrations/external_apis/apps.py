"""
Django App Configuration for External APIs Integration

This app handles external API integrations and data flow orchestration
for the Pre-Construction Intelligence Tool.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.apps import AppConfig


class ExternalAPIsConfig(AppConfig):
    """Configuration for External APIs Integration app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations.external_apis'
    verbose_name = 'External APIs Integration'
    
    def ready(self):
        """Initialize app when Django is ready."""
        try:
            # Import signals and tasks when app is ready
            from . import signals
            from . import tasks
        except ImportError:
            pass
