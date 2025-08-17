"""
ProcurePro Automated Synchronization Schedules

Defines Celery Beat schedules for automated data synchronization
with ProcurePro system including configurable intervals and schedules.
"""

from django.conf import settings
from celery.schedules import crontab
from datetime import timedelta

# Default sync intervals (can be overridden in settings)
DEFAULT_SYNC_INTERVALS = {
    'suppliers': 3600,        # 1 hour
    'purchase_orders': 1800,  # 30 minutes
    'invoices': 1800,         # 30 minutes
    'contracts': 7200,        # 2 hours
    'full_sync': 86400,       # 24 hours
    'health_check': 900,      # 15 minutes
    'cleanup_logs': 604800,   # 7 days
    'monitor_health': 1800,   # 30 minutes
}

# Get sync intervals from settings or use defaults
SYNC_INTERVALS = getattr(settings, 'PROCUREPRO_SYNC_INTERVALS', DEFAULT_SYNC_INTERVALS)

# Celery Beat schedule configuration
beat_schedule = {
    # Supplier synchronization - every hour during business hours
    'procurepro-sync-suppliers': {
        'task': 'procurepro.sync_suppliers',
        'schedule': crontab(
            minute=0,          # At the top of every hour
            hour='8-18',       # 8 AM to 6 PM
            day_of_week='1-5'  # Monday to Friday
        ),
        'args': (True, None, 'scheduled'),  # incremental=True, max_records=None, initiated_by='scheduled'
        'options': {
            'expires': 3600,   # Task expires after 1 hour
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.5,
            }
        }
    },
    
    # Purchase order synchronization - every 30 minutes during business hours
    'procurepro-sync-purchase-orders': {
        'task': 'procurepro.sync_purchase_orders',
        'schedule': crontab(
            minute='*/30',     # Every 30 minutes
            hour='8-18',       # 8 AM to 6 PM
            day_of_week='1-5'  # Monday to Friday
        ),
        'args': (True, None, 'scheduled'),
        'options': {
            'expires': 1800,   # Task expires after 30 minutes
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.5,
            }
        }
    },
    
    # Invoice synchronization - every 30 minutes during business hours
    'procurepro-sync-invoices': {
        'task': 'procurepro.sync_invoices',
        'schedule': crontab(
            minute='*/30',     # Every 30 minutes
            hour='8-18',       # 8 AM to 6 PM
            day_of_week='1-5'  # Monday to Friday
        ),
        'args': (True, None, 'scheduled'),
        'options': {
            'expires': 1800,   # Task expires after 30 minutes
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.5,
            }
        }
    },
    
    # Contract synchronization - every 2 hours during business hours
    'procurepro-sync-contracts': {
        'task': 'procurepro.sync_contracts',
        'schedule': crontab(
            minute=0,          # At the top of every 2 hours
            hour='8,10,12,14,16,18',  # 8 AM, 10 AM, 12 PM, 2 PM, 4 PM, 6 PM
            day_of_week='1-5'  # Monday to Friday
        ),
        'args': (True, None, 'scheduled'),
        'options': {
            'expires': 7200,   # Task expires after 2 hours
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.5,
            }
        }
    },
    
    # Full synchronization - daily at 2 AM (off-peak hours)
    'procurepro-full-sync': {
        'task': 'procurepro.full_sync',
        'schedule': crontab(
            minute=0,          # At 2 AM
            hour=2,
            day_of_week='1-6'  # Monday to Saturday (avoid Sunday)
        ),
        'args': ('scheduled',),
        'options': {
            'expires': 28800,  # Task expires after 8 hours
            'retry': True,
            'retry_policy': {
                'max_retries': 2,
                'interval_start': 0,
                'interval_step': 0.5,
                'interval_max': 1.0,
            }
        }
    },
    
    # Health check - every 15 minutes
    'procurepro-health-check': {
        'task': 'procurepro.health_check',
        'schedule': timedelta(minutes=15),
        'options': {
            'expires': 900,    # Task expires after 15 minutes
            'retry': False,    # No retry for health checks
        }
    },
    
    # Log cleanup - weekly on Sunday at 3 AM
    'procurepro-cleanup-logs': {
        'task': 'procurepro.cleanup_old_logs',
        'schedule': crontab(
            minute=0,          # At 3 AM
            hour=3,
            day_of_week=0      # Sunday
        ),
        'args': (30,),        # Keep logs for 30 days
        'options': {
            'expires': 3600,   # Task expires after 1 hour
            'retry': True,
            'retry_policy': {
                'max_retries': 2,
                'interval_start': 0,
                'interval_step': 0.5,
                'interval_max': 1.0,
            }
        }
    },
    
    # Sync health monitoring - every 30 minutes
    'procurepro-monitor-sync-health': {
        'task': 'procurepro.monitor_sync_health',
        'schedule': timedelta(minutes=30),
        'options': {
            'expires': 1800,   # Task expires after 30 minutes
            'retry': True,
            'retry_policy': {
                'max_retries': 2,
                'interval_start': 0,
                'interval_step': 0.5,
                'interval_max': 1.0,
            }
        }
    },
}

# Alternative schedules for different environments
development_schedule = {
    # More frequent syncs for development
    'procurepro-sync-suppliers-dev': {
        'task': 'procurepro.sync_suppliers',
        'schedule': timedelta(minutes=30),
        'args': (True, 100, 'scheduled-dev'),  # Limit to 100 records for dev
        'options': {'expires': 1800}
    },
    
    'procurepro-sync-purchase-orders-dev': {
        'task': 'procurepro.sync_purchase_orders',
        'schedule': timedelta(minutes=15),
        'args': (True, 100, 'scheduled-dev'),
        'options': {'expires': 900}
    },
    
    'procurepro-sync-invoices-dev': {
        'task': 'procurepro.sync_invoices',
        'schedule': timedelta(minutes=15),
        'args': (True, 100, 'scheduled-dev'),
        'options': {'expires': 900}
    },
    
    'procurepro-sync-contracts-dev': {
        'task': 'procurepro.sync_contracts',
        'schedule': timedelta(minutes=60),
        'args': (True, 100, 'scheduled-dev'),
        'options': {'expires': 3600}
    },
    
    'procurepro-full-sync-dev': {
        'task': 'procurepro.full_sync',
        'schedule': timedelta(hours=6),
        'args': ('scheduled-dev',),
        'options': {'expires': 14400}
    },
}

testing_schedule = {
    # Minimal syncs for testing
    'procurepro-sync-suppliers-test': {
        'task': 'procurepro.sync_suppliers',
        'schedule': timedelta(hours=4),
        'args': (True, 50, 'scheduled-test'),  # Limit to 50 records for testing
        'options': {'expires': 7200}
    },
    
    'procurepro-sync-purchase-orders-test': {
        'task': 'procurepro.sync_purchase_orders',
        'schedule': timedelta(hours=2),
        'args': (True, 50, 'scheduled-test'),
        'options': {'expires': 3600}
    },
    
    'procurepro-sync-invoices-test': {
        'task': 'procurepro.sync_invoices',
        'schedule': timedelta(hours=2),
        'args': (True, 50, 'scheduled-test'),
        'options': {'expires': 3600}
    },
    
    'procurepro-sync-contracts-test': {
        'task': 'procurepro.sync_contracts',
        'schedule': timedelta(hours=4),
        'args': (True, 50, 'scheduled-test'),
        'options': {'expires': 7200}
    },
    
    'procurepro-full-sync-test': {
        'task': 'procurepro.full_sync',
        'schedule': timedelta(hours=12),
        'args': ('scheduled-test',),
        'options': {'expires': 28800}
    },
}

# Function to get appropriate schedule based on environment
def get_sync_schedule():
    """
    Get the appropriate sync schedule based on the current environment.
    
    Returns:
        dict: Celery Beat schedule configuration
    """
    environment = getattr(settings, 'ENVIRONMENT', 'production').lower()
    
    if environment == 'development':
        return {**beat_schedule, **development_schedule}
    elif environment == 'testing':
        return {**beat_schedule, **testing_schedule}
    else:
        return beat_schedule

# Function to get sync intervals
def get_sync_intervals():
    """
    Get the current sync intervals configuration.
    
    Returns:
        dict: Sync interval configuration
    """
    return SYNC_INTERVALS.copy()

# Function to update sync intervals
def update_sync_intervals(new_intervals):
    """
    Update sync intervals (for runtime configuration changes).
    
    Args:
        new_intervals (dict): New interval configuration
    
    Returns:
        dict: Updated interval configuration
    """
    global SYNC_INTERVALS
    SYNC_INTERVALS.update(new_intervals)
    return SYNC_INTERVALS.copy()

# Function to get schedule summary
def get_schedule_summary():
    """
    Get a summary of all scheduled tasks.
    
    Returns:
        dict: Schedule summary information
    """
    schedule = get_sync_schedule()
    
    summary = {
        'total_tasks': len(schedule),
        'sync_tasks': [],
        'maintenance_tasks': [],
        'monitoring_tasks': []
    }
    
    for task_name, task_config in schedule.items():
        task_info = {
            'name': task_name,
            'task': task_config['task'],
            'schedule': str(task_config['schedule']),
            'args': task_config.get('args', ()),
            'expires': task_config.get('options', {}).get('expires', 'Not set')
        }
        
        if 'sync' in task_name:
            summary['sync_tasks'].append(task_info)
        elif 'cleanup' in task_name:
            summary['maintenance_tasks'].append(task_info)
        else:
            summary['monitoring_tasks'].append(task_info)
    
    return summary
