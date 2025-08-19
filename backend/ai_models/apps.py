from django.apps import AppConfig


class AiModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_models'
    verbose_name = 'AI Models'
    
    def ready(self):
        """Initialize the app when Django starts"""
        try:
            # Import signals if they exist
            import ai_models.signals
        except ImportError:
            pass
