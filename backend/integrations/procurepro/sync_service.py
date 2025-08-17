"""
ProcurePro Data Synchronization Service

Handles synchronization of data between ProcurePro and our system,
including suppliers, purchase orders, invoices, and contracts.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

from .client import ProcureProClient, ProcureProAPIError
from .models import (
    ProcureProSupplier, ProcureProPurchaseOrder, ProcureProInvoice,
    ProcureProContract, ProcureProSyncLog
)

logger = logging.getLogger(__name__)


class ProcureProSyncService:
    """
    Service for synchronizing data between ProcurePro and our system.
    
    Features:
    - Incremental and full synchronization
    - Comprehensive error handling and logging
    - Transaction safety
    - Progress tracking and monitoring
    - Automatic retry logic
    """
    
    def __init__(self):
        self.client = ProcureProClient()
        self.sync_log = None
    
    def sync_suppliers(
        self,
        incremental: bool = True,
        max_records: Optional[int] = None,
        initiated_by: str = 'system'
    ) -> ProcureProSyncLog:
        """
        Synchronize suppliers from ProcurePro.
        
        Args:
            incremental: If True, only sync recently updated suppliers
            max_records: Maximum number of records to process
            initiated_by: User or system that initiated the sync
            
        Returns:
            SyncLog instance with results
        """
        try:
            # Create sync log
            self.sync_log = ProcureProSyncLog.objects.create(
                sync_type='suppliers',
                initiated_by=initiated_by
            )
            
            logger.info(f"Starting supplier synchronization (incremental: {incremental})")
            
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            api_calls = 0
            
            page = 1
            limit = 100
            
            while True:
                try:
                    # Get suppliers from ProcurePro
                    response = self.client.get_suppliers(page=page, limit=limit)
                    api_calls += 1
                    
                    suppliers_data = response.get('data', [])
                    if not suppliers_data:
                        break
                    
                    # Process each supplier
                    for supplier_data in suppliers_data:
                        try:
                            if max_records and records_processed >= max_records:
                                break
                            
                            result = self._sync_supplier(supplier_data)
                            records_processed += 1
                            
                            if result == 'created':
                                records_created += 1
                            elif result == 'updated':
                                records_updated += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to sync supplier {supplier_data.get('id')}: {e}")
                            records_failed += 1
                            continue
                    
                    if max_records and records_processed >= max_records:
                        break
                    
                    # Check if there are more pages
                    pagination = response.get('pagination', {})
                    if not pagination.get('has_next', False):
                        break
                    
                    page += 1
                    
                except ProcureProAPIError as e:
                    logger.error(f"API error during supplier sync: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error during supplier sync: {e}")
                    break
            
            # Update sync log
            status = 'success' if records_failed == 0 else 'partial'
            self.sync_log.mark_completed(
                status=status,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                api_calls_made=api_calls
            )
            
            logger.info(
                f"Supplier synchronization completed: "
                f"{records_created} created, {records_updated} updated, "
                f"{records_failed} failed"
            )
            
            return self.sync_log
            
        except Exception as e:
            logger.error(f"Supplier synchronization failed: {e}")
            if self.sync_log:
                self.sync_log.mark_completed(
                    status='failed',
                    error_message=str(e),
                    error_details={'exception_type': type(e).__name__}
                )
            raise
    
    def sync_purchase_orders(
        self,
        incremental: bool = True,
        max_records: Optional[int] = None,
        initiated_by: str = 'system'
    ) -> ProcureProSyncLog:
        """
        Synchronize purchase orders from ProcurePro.
        
        Args:
            incremental: If True, only sync recently updated POs
            max_records: Maximum number of records to process
            initiated_by: User or system that initiated the sync
            
        Returns:
            SyncLog instance with results
        """
        try:
            # Create sync log
            self.sync_log = ProcureProSyncLog.objects.create(
                sync_type='purchase_orders',
                initiated_by=initiated_by
            )
            
            logger.info(f"Starting purchase order synchronization (incremental: {incremental})")
            
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            api_calls = 0
            
            page = 1
            limit = 100
            
            while True:
                try:
                    # Get purchase orders from ProcurePro
                    response = self.client.get_purchase_orders(page=page, limit=limit)
                    api_calls += 1
                    
                    pos_data = response.get('data', [])
                    if not pos_data:
                        break
                    
                    # Process each purchase order
                    for po_data in pos_data:
                        try:
                            if max_records and records_processed >= max_records:
                                break
                            
                            result = self._sync_purchase_order(po_data)
                            records_processed += 1
                            
                            if result == 'created':
                                records_created += 1
                            elif result == 'updated':
                                records_updated += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to sync PO {po_data.get('id')}: {e}")
                            records_failed += 1
                            continue
                    
                    if max_records and records_processed >= max_records:
                        break
                    
                    # Check if there are more pages
                    pagination = response.get('pagination', {})
                    if not pagination.get('has_next', False):
                        break
                    
                    page += 1
                    
                except ProcureProAPIError as e:
                    logger.error(f"API error during PO sync: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error during PO sync: {e}")
                    break
            
            # Update sync log
            status = 'success' if records_failed == 0 else 'partial'
            self.sync_log.mark_completed(
                status=status,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                api_calls_made=api_calls
            )
            
            logger.info(
                f"Purchase order synchronization completed: "
                f"{records_created} created, {records_updated} updated, "
                f"{records_failed} failed"
            )
            
            return self.sync_log
            
        except Exception as e:
            logger.error(f"Purchase order synchronization failed: {e}")
            if self.sync_log:
                self.sync_log.mark_completed(
                    status='failed',
                    error_message=str(e),
                    error_details={'exception_type': type(e).__name__}
                )
            raise
    
    def sync_invoices(
        self,
        incremental: bool = True,
        max_records: Optional[int] = None,
        initiated_by: str = 'system'
    ) -> ProcureProSyncLog:
        """
        Synchronize invoices from ProcurePro.
        
        Args:
            incremental: If True, only sync recently updated invoices
            max_records: Maximum number of records to process
            initiated_by: User or system that initiated the sync
            
        Returns:
            SyncLog instance with results
        """
        try:
            # Create sync log
            self.sync_log = ProcureProSyncLog.objects.create(
                sync_type='invoices',
                initiated_by=initiated_by
            )
            
            logger.info(f"Starting invoice synchronization (incremental: {incremental})")
            
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            api_calls = 0
            
            page = 1
            limit = 100
            
            while True:
                try:
                    # Get invoices from ProcurePro
                    response = self.client.get_invoices(page=page, limit=limit)
                    api_calls += 1
                    
                    invoices_data = response.get('data', [])
                    if not invoices_data:
                        break
                    
                    # Process each invoice
                    for invoice_data in invoices_data:
                        try:
                            if max_records and records_processed >= max_records:
                                break
                            
                            result = self._sync_invoice(invoice_data)
                            records_processed += 1
                            
                            if result == 'created':
                                records_created += 1
                            elif result == 'updated':
                                records_updated += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to sync invoice {invoice_data.get('id')}: {e}")
                            records_failed += 1
                            continue
                    
                    if max_records and records_processed >= max_records:
                        break
                    
                    # Check if there are more pages
                    pagination = response.get('pagination', {})
                    if not pagination.get('has_next', False):
                        break
                    
                    page += 1
                    
                except ProcureProAPIError as e:
                    logger.error(f"API error during invoice sync: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error during invoice sync: {e}")
                    break
            
            # Update sync log
            status = 'success' if records_failed == 0 else 'partial'
            self.sync_log.mark_completed(
                status=status,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                api_calls_made=api_calls
            )
            
            logger.info(
                f"Invoice synchronization completed: "
                f"{records_created} created, {records_updated} updated, "
                f"{records_failed} failed"
            )
            
            return self.sync_log
            
        except Exception as e:
            logger.error(f"Invoice synchronization failed: {e}")
            if self.sync_log:
                self.sync_log.mark_completed(
                    status='failed',
                    error_message=str(e),
                    error_details={'exception_type': type(e).__name__}
                )
            raise
    
    def sync_contracts(
        self,
        incremental: bool = True,
        max_records: Optional[int] = None,
        initiated_by: str = 'system'
    ) -> ProcureProSyncLog:
        """
        Synchronize contracts from ProcurePro.
        
        Args:
            incremental: If True, only sync recently updated contracts
            max_records: Maximum number of records to process
            initiated_by: User or system that initiated the sync
            
        Returns:
            SyncLog instance with results
        """
        try:
            # Create sync log
            self.sync_log = ProcureProSyncLog.objects.create(
                sync_type='contracts',
                initiated_by=initiated_by
            )
            
            logger.info(f"Starting contract synchronization (incremental: {incremental})")
            
            records_processed = 0
            records_created = 0
            records_updated = 0
            records_failed = 0
            api_calls = 0
            
            page = 1
            limit = 100
            
            while True:
                try:
                    # Get contracts from ProcurePro
                    response = self.client.get_contracts(page=page, limit=limit)
                    api_calls += 1
                    
                    contracts_data = response.get('data', [])
                    if not contracts_data:
                        break
                    
                    # Process each contract
                    for contract_data in contracts_data:
                        try:
                            if max_records and records_processed >= max_records:
                                break
                            
                            result = self._sync_contract(contract_data)
                            records_processed += 1
                            
                            if result == 'created':
                                records_created += 1
                            elif result == 'updated':
                                records_updated += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to sync contract {contract_data.get('id')}: {e}")
                            records_failed += 1
                            continue
                    
                    if max_records and records_processed >= max_records:
                        break
                    
                    # Check if there are more pages
                    pagination = response.get('pagination', {})
                    if not pagination.get('has_next', False):
                        break
                    
                    page += 1
                    
                except ProcureProAPIError as e:
                    logger.error(f"API error during contract sync: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error during contract sync: {e}")
                    break
            
            # Update sync log
            status = 'success' if records_failed == 0 else 'partial'
            self.sync_log.mark_completed(
                status=status,
                records_processed=records_processed,
                records_created=records_created,
                records_updated=records_updated,
                records_failed=records_failed,
                api_calls_made=api_calls
            )
            
            logger.info(
                f"Contract synchronization completed: "
                f"{records_created} created, {records_updated} updated, "
                f"{records_failed} failed"
            )
            
            return self.sync_log
            
        except Exception as e:
            logger.error(f"Contract synchronization failed: {e}")
            if self.sync_log:
                self.sync_log.mark_completed(
                    status='failed',
                    error_message=str(e),
                    error_details={'exception_type': type(e).__name__}
                )
            raise
    
    def full_sync(self, initiated_by: str = 'system') -> Dict[str, ProcureProSyncLog]:
        """
        Perform a full synchronization of all ProcurePro data.
        
        Args:
            initiated_by: User or system that initiated the sync
            
        Returns:
            Dictionary containing sync logs for each entity type
        """
        logger.info("Starting full ProcurePro synchronization")
        
        results = {}
        
        try:
            # Sync suppliers first (as other entities depend on them)
            results['suppliers'] = self.sync_suppliers(
                incremental=False, initiated_by=initiated_by
            )
            
            # Sync other entities
            results['purchase_orders'] = self.sync_purchase_orders(
                incremental=False, initiated_by=initiated_by
            )
            
            results['invoices'] = self.sync_invoices(
                incremental=False, initiated_by=initiated_by
            )
            
            results['contracts'] = self.sync_contracts(
                incremental=False, initiated_by=initiated_by
            )
            
            logger.info("Full ProcurePro synchronization completed successfully")
            
        except Exception as e:
            logger.error(f"Full synchronization failed: {e}")
            raise
        
        return results
    
    def _sync_supplier(self, supplier_data: Dict[str, Any]) -> str:
        """
        Synchronize a single supplier.
        
        Args:
            supplier_data: Supplier data from ProcurePro API
            
        Returns:
            'created', 'updated', or 'error'
        """
        try:
            procurepro_id = supplier_data.get('id')
            if not procurepro_id:
                raise ValueError("Supplier ID is required")
            
            with transaction.atomic():
                supplier, created = ProcureProSupplier.objects.get_or_create(
                    procurepro_id=procurepro_id,
                    defaults={
                        'name': supplier_data.get('name', 'Unknown Supplier'),
                        'raw_data': supplier_data
                    }
                )
                
                if not created:
                    # Update existing supplier
                    supplier.update_from_procurepro_data(supplier_data)
                    supplier.save()
                    return 'updated'
                else:
                    # Set additional fields for new supplier
                    supplier.update_from_procurepro_data(supplier_data)
                    supplier.save()
                    return 'created'
                    
        except Exception as e:
            logger.error(f"Failed to sync supplier {supplier_data.get('id')}: {e}")
            raise
    
    def _sync_purchase_order(self, po_data: Dict[str, Any]) -> str:
        """
        Synchronize a single purchase order.
        
        Args:
            po_data: Purchase order data from ProcurePro API
            
        Returns:
            'created', 'updated', or 'error'
        """
        try:
            procurepro_id = po_data.get('id')
            if not procurepro_id:
                raise ValueError("Purchase Order ID is required")
            
            with transaction.atomic():
                po, created = ProcureProPurchaseOrder.objects.get_or_create(
                    procurepro_id=procurepro_id,
                    defaults={
                        'po_number': po_data.get('po_number', 'Unknown PO'),
                        'title': po_data.get('title', 'Unknown Title'),
                        'raw_data': po_data
                    }
                )
                
                # Get or create supplier
                supplier_id = po_data.get('supplier_id')
                if supplier_id:
                    try:
                        supplier = ProcureProSupplier.objects.get(procurepro_id=supplier_id)
                        po.supplier = supplier
                    except ProcureProSupplier.DoesNotExist:
                        logger.warning(f"Supplier {supplier_id} not found for PO {procurepro_id}")
                
                # Update fields
                po.title = po_data.get('title', po.title)
                po.description = po_data.get('description', po.description)
                po.total_amount = Decimal(str(po_data.get('total_amount', 0)))
                po.currency = po_data.get('currency', 'AUD')
                po.status = po_data.get('status', 'draft')
                
                # Parse dates
                if 'order_date' in po_data:
                    po.order_date = datetime.strptime(po_data['order_date'], '%Y-%m-%d').date()
                if 'expected_delivery_date' in po_data:
                    po.expected_delivery_date = datetime.strptime(po_data['expected_delivery_date'], '%Y-%m-%d').date()
                if 'actual_delivery_date' in po_data:
                    po.actual_delivery_date = datetime.strptime(po_data['actual_delivery_date'], '%Y-%m-%d').date()
                
                po.raw_data = po_data
                po.save()
                
                return 'created' if created else 'updated'
                
        except Exception as e:
            logger.error(f"Failed to sync PO {po_data.get('id')}: {e}")
            raise
    
    def _sync_invoice(self, invoice_data: Dict[str, Any]) -> str:
        """
        Synchronize a single invoice.
        
        Args:
            invoice_data: Invoice data from ProcurePro API
            
        Returns:
            'created', 'updated', or 'error'
        """
        try:
            procurepro_id = invoice_data.get('id')
            if not procurepro_id:
                raise ValueError("Invoice ID is required")
            
            with transaction.atomic():
                invoice, created = ProcureProInvoice.objects.get_or_create(
                    procurepro_id=procurepro_id,
                    defaults={
                        'invoice_number': invoice_data.get('invoice_number', 'Unknown Invoice'),
                        'title': invoice_data.get('title', 'Unknown Title'),
                        'raw_data': invoice_data
                    }
                )
                
                # Get or create supplier
                supplier_id = invoice_data.get('supplier_id')
                if supplier_id:
                    try:
                        supplier = ProcureProSupplier.objects.get(procurepro_id=supplier_id)
                        invoice.supplier = supplier
                    except ProcureProSupplier.DoesNotExist:
                        logger.warning(f"Supplier {supplier_id} not found for invoice {procurepro_id}")
                
                # Get or create purchase order
                po_id = invoice_data.get('purchase_order_id')
                if po_id:
                    try:
                        po = ProcureProPurchaseOrder.objects.get(procurepro_id=po_id)
                        invoice.purchase_order = po
                    except ProcureProPurchaseOrder.DoesNotExist:
                        logger.warning(f"PO {po_id} not found for invoice {procurepro_id}")
                
                # Update fields
                invoice.title = invoice_data.get('title', invoice.title)
                invoice.description = invoice_data.get('description', invoice.description)
                invoice.subtotal = Decimal(str(invoice_data.get('subtotal', 0)))
                invoice.tax_amount = Decimal(str(invoice_data.get('tax_amount', 0)))
                invoice.total_amount = Decimal(str(invoice_data.get('total_amount', 0)))
                invoice.currency = invoice_data.get('currency', 'AUD')
                invoice.status = invoice_data.get('status', 'pending')
                
                # Parse dates
                if 'invoice_date' in invoice_data:
                    invoice.invoice_date = datetime.strptime(invoice_data['invoice_date'], '%Y-%m-%d').date()
                if 'due_date' in invoice_data:
                    invoice.due_date = datetime.strptime(invoice_data['due_date'], '%Y-%m-%d').date()
                if 'paid_date' in invoice_data:
                    invoice.paid_date = datetime.strptime(invoice_data['paid_date'], '%Y-%m-%d').date()
                
                invoice.raw_data = invoice_data
                invoice.save()
                
                return 'created' if created else 'updated'
                
        except Exception as e:
            logger.error(f"Failed to sync invoice {invoice_data.get('id')}: {e}")
            raise
    
    def _sync_contract(self, contract_data: Dict[str, Any]) -> str:
        """
        Synchronize a single contract.
        
        Args:
            contract_data: Contract data from ProcurePro API
            
        Returns:
            'created', 'updated', or 'error'
        """
        try:
            procurepro_id = contract_data.get('id')
            if not procurepro_id:
                raise ValueError("Contract ID is required")
            
            with transaction.atomic():
                contract, created = ProcureProContract.objects.get_or_create(
                    procurepro_id=procurepro_id,
                    defaults={
                        'contract_number': contract_data.get('contract_number', 'Unknown Contract'),
                        'title': contract_data.get('title', 'Unknown Title'),
                        'raw_data': contract_data
                    }
                )
                
                # Get or create supplier
                supplier_id = contract_data.get('supplier_id')
                if supplier_id:
                    try:
                        supplier = ProcureProSupplier.objects.get(procurepro_id=supplier_id)
                        contract.supplier = supplier
                    except ProcureProSupplier.DoesNotExist:
                        logger.warning(f"Supplier {supplier_id} not found for contract {procurepro_id}")
                
                # Update fields
                contract.title = contract_data.get('title', contract.title)
                contract.description = contract_data.get('description', contract.description)
                contract.contract_type = contract_data.get('contract_type', contract.contract_type)
                contract.contract_value = Decimal(str(contract_data.get('contract_value', 0)))
                contract.currency = contract_data.get('currency', 'AUD')
                contract.status = contract_data.get('status', 'active')
                
                # Parse dates
                if 'start_date' in contract_data:
                    contract.start_date = datetime.strptime(contract_data['start_date'], '%Y-%m-%d').date()
                if 'end_date' in contract_data:
                    contract.end_date = datetime.strptime(contract_data['end_date'], '%Y-%m-%d').date()
                if 'renewal_date' in contract_data:
                    contract.renewal_date = datetime.strptime(contract_data['renewal_date'], '%Y-%m-%d').date()
                
                contract.raw_data = contract_data
                contract.save()
                
                return 'created' if created else 'updated'
                
        except Exception as e:
            logger.error(f"Failed to sync contract {contract_data.get('id')}: {e}")
            raise
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get the current synchronization status and statistics.
        
        Returns:
            Dictionary containing sync status information
        """
        try:
            # Get recent sync logs
            recent_syncs = ProcureProSyncLog.objects.filter(
                started_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-started_at')
            
            # Get entity counts
            supplier_count = ProcureProSupplier.objects.count()
            po_count = ProcureProPurchaseOrder.objects.count()
            invoice_count = ProcureProInvoice.objects.count()
            contract_count = ProcureProContract.objects.count()
            
            # Get last sync times
            last_supplier_sync = ProcureProSupplier.objects.order_by('-last_synced').first()
            last_po_sync = ProcureProPurchaseOrder.objects.order_by('-last_synced').first()
            last_invoice_sync = ProcureProInvoice.objects.order_by('-last_synced').first()
            last_contract_sync = ProcureProContract.objects.order_by('-last_synced').first()
            
            # Check API health
            try:
                health_status = self.client.health_check()
                api_healthy = health_status['status'] == 'healthy'
            except:
                api_healthy = False
            
            return {
                'api_healthy': api_healthy,
                'entity_counts': {
                    'suppliers': supplier_count,
                    'purchase_orders': po_count,
                    'invoices': invoice_count,
                    'contracts': contract_count,
                },
                'last_sync_times': {
                    'suppliers': last_supplier_sync.last_synced if last_supplier_sync else None,
                    'purchase_orders': last_po_sync.last_synced if last_po_sync else None,
                    'invoices': last_invoice_sync.last_synced if last_invoice_sync else None,
                    'contracts': last_contract_sync.last_synced if last_contract_sync else None,
                },
                'recent_syncs': [
                    {
                        'type': sync.sync_type,
                        'status': sync.status,
                        'started_at': sync.started_at,
                        'completed_at': sync.completed_at,
                        'records_processed': sync.records_processed,
                        'success_rate': sync.success_rate,
                    }
                    for sync in recent_syncs[:10]
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return {
                'error': str(e),
                'api_healthy': False
            }
    
    def close(self):
        """Close the service and clean up resources."""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
