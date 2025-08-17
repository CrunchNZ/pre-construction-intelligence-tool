"""
ProcurePro Automated Synchronization Tasks

Provides Celery tasks for automated data synchronization with
ProcurePro system including scheduling, error handling, and monitoring.
"""

import logging
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import traceback

from .models import ProcureProSyncLog
from .sync_service import ProcureProSyncService

logger = get_task_logger(__name__)


@shared_task(
    name='procurepro.sync_suppliers',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def sync_suppliers_task(self, incremental=True, max_records=None, initiated_by='celery'):
    """
    Celery task for synchronizing ProcurePro suppliers.
    
    Args:
        incremental (bool): Whether to perform incremental sync
        max_records (int): Maximum number of records to sync
        initiated_by (str): Who initiated the sync
    
    Returns:
        dict: Sync results and status
    """
    task_id = self.request.id
    logger.info(f"Starting supplier sync task {task_id} (incremental: {incremental})")
    
    # Create sync log entry
    sync_log = ProcureProSyncLog.objects.create(
        sync_type='suppliers',
        status='started',
        initiated_by=initiated_by
    )
    
    try:
        # Perform synchronization
        with ProcureProSyncService() as sync_service:
            result = sync_service.sync_suppliers(
                incremental=incremental,
                max_records=max_records,
                initiated_by=initiated_by
            )
        
        # Update sync log with success
        sync_log.mark_completed(
            status='success',
            records_processed=result.get('records_processed', 0),
            records_created=result.get('records_created', 0),
            records_updated=result.get('records_updated', 0),
            records_failed=result.get('records_failed', 0),
            api_calls_made=result.get('api_calls_made', 0)
        )
        
        logger.info(f"Supplier sync task {task_id} completed successfully: {result}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'sync_log_id': sync_log.id,
            'result': result
        }
        
    except Exception as exc:
        # Log the error
        error_msg = f"Supplier sync task {task_id} failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        # Update sync log with failure
        sync_log.mark_completed(
            status='failed',
            error_message=error_msg,
            error_details={
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'task_id': task_id
            }
        )
        
        # Retry the task if possible
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying supplier sync task {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        else:
            logger.error(f"Supplier sync task {task_id} failed after {self.max_retries} retries")
            raise exc


@shared_task(
    name='procurepro.sync_purchase_orders',
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def sync_purchase_orders_task(self, incremental=True, max_records=None, initiated_by='celery'):
    """
    Celery task for synchronizing ProcurePro purchase orders.
    """
    task_id = self.request.id
    logger.info(f"Starting purchase order sync task {task_id} (incremental: {incremental})")
    
    sync_log = ProcureProSyncLog.objects.create(
        sync_type='purchase_orders',
        status='started',
        initiated_by=initiated_by
    )
    
    try:
        with ProcureProSyncService() as sync_service:
            result = sync_service.sync_purchase_orders(
                incremental=incremental,
                max_records=max_records,
                initiated_by=initiated_by
            )
        
        sync_log.mark_completed(
            status='success',
            records_processed=result.get('records_processed', 0),
            records_created=result.get('records_created', 0),
            records_updated=result.get('records_updated', 0),
            records_failed=result.get('records_failed', 0),
            api_calls_made=result.get('api_calls_made', 0)
        )
        
        logger.info(f"Purchase order sync task {task_id} completed successfully: {result}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'sync_log_id': sync_log.id,
            'result': result
        }
        
    except Exception as exc:
        error_msg = f"Purchase order sync task {task_id} failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        sync_log.mark_completed(
            status='failed',
            error_message=error_msg,
            error_details={
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'task_id': task_id
            }
        )
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying purchase order sync task {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        else:
            logger.error(f"Purchase order sync task {task_id} failed after {self.max_retries} retries")
            raise exc


@shared_task(
    name='procurepro.sync_invoices',
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def sync_invoices_task(self, incremental=True, max_records=None, initiated_by='celery'):
    """
    Celery task for synchronizing ProcurePro invoices.
    """
    task_id = self.request.id
    logger.info(f"Starting invoice sync task {task_id} (incremental: {incremental})")
    
    sync_log = ProcureProSyncLog.objects.create(
        sync_type='invoices',
        status='started',
        initiated_by=initiated_by
    )
    
    try:
        with ProcureProSyncService() as sync_service:
            result = sync_service.sync_invoices(
                incremental=incremental,
                max_records=max_records,
                initiated_by=initiated_by
            )
        
        sync_log.mark_completed(
            status='success',
            records_processed=result.get('records_processed', 0),
            records_created=result.get('records_created', 0),
            records_updated=result.get('records_updated', 0),
            records_failed=result.get('records_failed', 0),
            api_calls_made=result.get('api_calls_made', 0)
        )
        
        logger.info(f"Invoice sync task {task_id} completed successfully: {result}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'sync_log_id': sync_log.id,
            'result': result
        }
        
    except Exception as exc:
        error_msg = f"Invoice sync task {task_id} failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        sync_log.mark_completed(
            status='failed',
            error_message=error_msg,
            error_details={
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'task_id': task_id
            }
        )
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying invoice sync task {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        else:
            logger.error(f"Invoice sync task {task_id} failed after {self.max_retries} retries")
            raise exc


@shared_task(
    name='procurepro.sync_contracts',
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def sync_contracts_task(self, incremental=True, max_records=None, initiated_by='celery'):
    """
    Celery task for synchronizing ProcurePro contracts.
    """
    task_id = self.request.id
    logger.info(f"Starting contract sync task {task_id} (incremental: {incremental})")
    
    sync_log = ProcureProSyncLog.objects.create(
        sync_type='contracts',
        status='started',
        initiated_by=initiated_by
    )
    
    try:
        with ProcureProSyncService() as sync_service:
            result = sync_service.sync_contracts(
                incremental=incremental,
                max_records=max_records,
                initiated_by=initiated_by
            )
        
        sync_log.mark_completed(
            status='success',
            records_processed=result.get('records_processed', 0),
            records_created=result.get('records_created', 0),
            records_updated=result.get('records_updated', 0),
            records_failed=result.get('records_failed', 0),
            api_calls_made=result.get('api_calls_made', 0)
        )
        
        logger.info(f"Contract sync task {task_id} completed successfully: {result}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'sync_log_id': sync_log.id,
            'result': result
        }
        
    except Exception as exc:
        error_msg = f"Contract sync task {task_id} failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        sync_log.mark_completed(
            status='failed',
            error_message=error_msg,
            error_details={
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'task_id': task_id
            }
        )
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying contract sync task {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        else:
            logger.error(f"Contract sync task {task_id} failed after {self.max_retries} retries")
            raise exc


@shared_task(
    name='procurepro.full_sync',
    bind=True,
    max_retries=2,
    default_retry_delay=600,  # 10 minutes for full sync
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def full_sync_task(self, initiated_by='celery'):
    """
    Celery task for performing a full synchronization of all ProcurePro entities.
    """
    task_id = self.request.id
    logger.info(f"Starting full sync task {task_id}")
    
    # Create sync log for full sync
    sync_log = ProcureProSyncLog.objects.create(
        sync_type='full',
        status='started',
        initiated_by=initiated_by
    )
    
    try:
        with ProcureProSyncService() as sync_service:
            results = sync_service.full_sync(initiated_by=initiated_by)
        
        # Aggregate results
        total_processed = sum(result.get('records_processed', 0) for result in results.values())
        total_created = sum(result.get('records_created', 0) for result in results.values())
        total_updated = sum(result.get('records_updated', 0) for result in results.values())
        total_failed = sum(result.get('records_failed', 0) for result in results.values())
        total_api_calls = sum(result.get('api_calls_made', 0) for result in results.values())
        
        # Determine overall status
        overall_status = 'success' if total_failed == 0 else 'partial'
        
        sync_log.mark_completed(
            status=overall_status,
            records_processed=total_processed,
            records_created=total_created,
            records_updated=total_updated,
            records_failed=total_failed,
            api_calls_made=total_api_calls
        )
        
        logger.info(f"Full sync task {task_id} completed with status: {overall_status}")
        
        return {
            'task_id': task_id,
            'status': overall_status,
            'sync_log_id': sync_log.id,
            'results': results,
            'summary': {
                'total_processed': total_processed,
                'total_created': total_created,
                'total_updated': total_updated,
                'total_failed': total_failed,
                'total_api_calls': total_api_calls
            }
        }
        
    except Exception as exc:
        error_msg = f"Full sync task {task_id} failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        sync_log.mark_completed(
            status='failed',
            error_message=error_msg,
            error_details={
                'exception_type': type(exc).__name__,
                'traceback': traceback.format_exc(),
                'task_id': task_id
            }
        )
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying full sync task {task_id} (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        else:
            logger.error(f"Full sync task {task_id} failed after {self.max_retries} retries")
            raise exc


@shared_task(name='procurepro.health_check')
def health_check_task():
    """
    Celery task for performing health checks on ProcurePro integration.
    """
    logger.info("Starting ProcurePro health check task")
    
    try:
        with ProcureProSyncService() as sync_service:
            health_status = sync_service.client.health_check()
        
        logger.info(f"Health check completed: {health_status}")
        
        return {
            'status': 'success',
            'health_status': health_status,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        error_msg = f"Health check failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            'status': 'failed',
            'error': error_msg,
            'timestamp': timezone.now().isoformat()
        }


@shared_task(name='procurepro.cleanup_old_logs')
def cleanup_old_logs_task(days_to_keep=30):
    """
    Celery task for cleaning up old synchronization logs.
    
    Args:
        days_to_keep (int): Number of days of logs to keep
    """
    logger.info(f"Starting cleanup of logs older than {days_to_keep} days")
    
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        deleted_count, _ = ProcureProSyncLog.objects.filter(
            started_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old sync logs")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        error_msg = f"Log cleanup failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            'status': 'failed',
            'error': error_msg
        }


@shared_task(name='procurepro.monitor_sync_health')
def monitor_sync_health_task():
    """
    Celery task for monitoring overall sync health and sending alerts if needed.
    """
    logger.info("Starting sync health monitoring task")
    
    try:
        # Check recent sync activity
        recent_syncs = ProcureProSyncLog.objects.filter(
            started_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        # Calculate success rate
        total_syncs = recent_syncs.count()
        successful_syncs = recent_syncs.filter(status='success').count()
        failed_syncs = recent_syncs.filter(status='failed').count()
        
        success_rate = (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        
        # Check for critical failures
        critical_failures = recent_syncs.filter(
            status='failed',
            started_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Determine health status
        if success_rate >= 90 and critical_failures == 0:
            health_status = 'healthy'
        elif success_rate >= 75 and critical_failures <= 1:
            health_status = 'degraded'
        else:
            health_status = 'critical'
        
        # Log health status
        logger.info(f"Sync health status: {health_status} (success rate: {success_rate:.1f}%)")
        
        # TODO: Send alerts if health is critical
        if health_status == 'critical':
            logger.warning("CRITICAL: ProcurePro sync health is poor - alerts should be sent")
        
        return {
            'status': 'success',
            'health_status': health_status,
            'success_rate': success_rate,
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'failed_syncs': failed_syncs,
            'critical_failures': critical_failures,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        error_msg = f"Sync health monitoring failed: {str(exc)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            'status': 'failed',
            'error': error_msg
        }
