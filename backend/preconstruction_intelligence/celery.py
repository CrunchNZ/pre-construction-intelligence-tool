"""
Celery configuration for the Pre-Construction Intelligence Tool.

This module configures Celery for handling background tasks
such as data synchronization, AI model processing, and report generation.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'preconstruction_intelligence.settings')

# Create the Celery app
app = Celery('preconstruction_intelligence')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure Celery settings
app.conf.update(
    # Task routing
    task_routes={
        'integrations.*': {'queue': 'integrations'},
        'ai_models.*': {'queue': 'ai_models'},
        'analytics.*': {'queue': 'analytics'},
        'core.*': {'queue': 'default'},
    },
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Task execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'sync-procurepro-data': {
            'task': 'integrations.tasks.sync_procurepro_data',
            'schedule': 300.0,  # Every 5 minutes
        },
        'sync-procore-data': {
            'task': 'integrations.tasks.sync_procore_data',
            'schedule': 900.0,  # Every 15 minutes
        },
        'sync-jobpac-data': {
            'task': 'integrations.tasks.sync_jobpac_data',
            'schedule': 1800.0,  # Every 30 minutes
        },
        'sync-greentree-data': {
            'task': 'integrations.tasks.sync_greentree_data',
            'schedule': 3600.0,  # Every hour
        },
        'update-weather-data': {
            'task': 'integrations.tasks.update_weather_data',
            'schedule': 7200.0,  # Every 2 hours
        },
        'process-ai-models': {
            'task': 'ai_models.tasks.process_ai_models',
            'schedule': 3600.0,  # Every hour
        },
        'generate-daily-reports': {
            'task': 'analytics.tasks.generate_daily_reports',
            'schedule': 86400.0,  # Daily at midnight
        },
        'cleanup-old-data': {
            'task': 'core.tasks.cleanup_old_data',
            'schedule': 604800.0,  # Weekly
        },
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,        # 10 minutes
    
    # Worker time limits
    worker_disable_rate_limits=False,
    worker_max_memory_per_child=200000,  # 200MB
    
    # Queue settings
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Retry settings
    task_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Security
    security_key=os.getenv('CELERY_SECURITY_KEY', ''),
    security_certificate=os.getenv('CELERY_SECURITY_CERT', ''),
    security_cert_store=os.getenv('CELERY_SECURITY_CERT_STORE', ''),
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')


# Import tasks to ensure they are registered
from integrations import tasks as integration_tasks
from ai_models import tasks as ai_tasks
from analytics import tasks as analytics_tasks
from core import tasks as core_tasks
