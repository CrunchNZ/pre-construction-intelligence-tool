"""
Django App Configuration for Historical Data Analysis

This module configures the historical data analysis Django application,
including app metadata and initialization logic.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

from django.apps import AppConfig


class HistoricalDataConfig(AppConfig):
    """Configuration for the Historical Data Analysis app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics.historical_data'
    verbose_name = 'Historical Data Analysis'
    
    def ready(self):
        """Initialize the app when Django starts."""
        try:
            from . import signals
            from . import tasks
        except ImportError:
            pass
