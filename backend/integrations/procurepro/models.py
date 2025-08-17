"""
ProcurePro Data Models

Defines Django models for ProcurePro entities including suppliers,
purchase orders, invoices, and contracts.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import json


class ProcureProSupplier(models.Model):
    """
    Represents a supplier from ProcurePro system.
    
    This model stores supplier information synchronized from ProcurePro
    and maintains relationships with our core supplier model.
    """
    
    # ProcurePro identifiers
    procurepro_id = models.CharField(max_length=100, unique=True, db_index=True)
    procurepro_code = models.CharField(max_length=50, blank=True, null=True)
    
    # Basic supplier information
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    trading_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Contact information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Address information
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Business information
    abn = models.CharField(max_length=50, blank=True, null=True)  # Australian Business Number
    acn = models.CharField(max_length=50, blank=True, null=True)  # Australian Company Number
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Supplier classification
    supplier_type = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    
    # Status and ratings
    status = models.CharField(max_length=50, default='active')
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        blank=True, 
        null=True
    )
    
    # Financial information
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    
    # Integration metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='success')
    sync_errors = models.TextField(blank=True, null=True)
    
    # Raw data from ProcurePro
    raw_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'procurepro_supplier'
        verbose_name = 'ProcurePro Supplier'
        verbose_name_plural = 'ProcurePro Suppliers'
        indexes = [
            models.Index(fields=['procurepro_id']),
            models.Index(fields=['name']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['last_synced']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.procurepro_id})"
    
    @property
    def full_address(self):
        """Get the complete formatted address."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Address not provided'
    
    @property
    def is_active(self):
        """Check if supplier is active."""
        return self.status.lower() == 'active'
    
    def update_from_procurepro_data(self, data: dict):
        """Update supplier data from ProcurePro API response."""
        self.raw_data = data
        
        # Update basic fields
        self.name = data.get('name', self.name)
        self.legal_name = data.get('legal_name', self.legal_name)
        self.trading_name = data.get('trading_name', self.trading_name)
        self.email = data.get('email', self.email)
        self.phone = data.get('phone', self.phone)
        self.website = data.get('website', self.website)
        
        # Update address
        address = data.get('address', {})
        self.address_line1 = address.get('line1', self.address_line1)
        self.address_line2 = address.get('line2', self.address_line2)
        self.city = address.get('city', self.city)
        self.state = address.get('state', self.state)
        self.postal_code = address.get('postal_code', self.postal_code)
        self.country = address.get('country', self.country)
        
        # Update business info
        self.abn = data.get('abn', self.abn)
        self.acn = data.get('acn', self.acn)
        self.tax_id = data.get('tax_id', self.tax_id)
        
        # Update classification
        self.supplier_type = data.get('supplier_type', self.supplier_type)
        self.category = data.get('category', self.category)
        self.subcategory = data.get('subcategory', self.subcategory)
        
        # Update status and ratings
        self.status = data.get('status', self.status)
        if 'rating' in data:
            self.rating = data['rating']
        
        # Update financial info
        if 'credit_limit' in data:
            self.credit_limit = data['credit_limit']
        self.payment_terms = data.get('payment_terms', self.payment_terms)
        
        self.sync_status = 'success'
        self.sync_errors = None


class ProcureProPurchaseOrder(models.Model):
    """
    Represents a purchase order from ProcurePro system.
    """
    
    # ProcurePro identifiers
    procurepro_id = models.CharField(max_length=100, unique=True, db_index=True)
    po_number = models.CharField(max_length=100, db_index=True)
    
    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    supplier = models.ForeignKey(
        ProcureProSupplier,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    
    # Financial information
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='AUD')
    
    # Status and dates
    status = models.CharField(max_length=50, default='draft')
    order_date = models.DateField()
    expected_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    
    # Approval and workflow
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    
    # Integration metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='success')
    sync_errors = models.TextField(blank=True, null=True)
    
    # Raw data from ProcurePro
    raw_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'procurepro_purchase_order'
        verbose_name = 'ProcurePro Purchase Order'
        verbose_name_plural = 'ProcurePro Purchase Orders'
        indexes = [
            models.Index(fields=['procurepro_id']),
            models.Index(fields=['po_number']),
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.name}"
    
    @property
    def is_delivered(self):
        """Check if purchase order has been delivered."""
        return self.actual_delivery_date is not None
    
    @property
    def is_overdue(self):
        """Check if purchase order is overdue."""
        if self.expected_delivery_date and not self.is_delivered:
            return timezone.now().date() > self.expected_delivery_date
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if self.is_overdue:
            return (timezone.now().date() - self.expected_delivery_date).days
        return 0


class ProcureProInvoice(models.Model):
    """
    Represents an invoice from ProcurePro system.
    """
    
    # ProcurePro identifiers
    procurepro_id = models.CharField(max_length=100, unique=True, db_index=True)
    invoice_number = models.CharField(max_length=100, db_index=True)
    
    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    supplier = models.ForeignKey(
        ProcureProSupplier,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    purchase_order = models.ForeignKey(
        ProcureProPurchaseOrder,
        on_delete=models.SET_NULL,
        related_name='invoices',
        blank=True,
        null=True
    )
    
    # Financial information
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='AUD')
    
    # Status and dates
    status = models.CharField(max_length=50, default='pending')
    invoice_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    
    # Payment information
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Integration metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='success')
    sync_errors = models.TextField(blank=True, null=True)
    
    # Raw data from ProcurePro
    raw_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'procurepro_invoice'
        verbose_name = 'ProcurePro Invoice'
        verbose_name_plural = 'ProcurePro Invoices'
        indexes = [
            models.Index(fields=['procurepro_id']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.supplier.name}"
    
    @property
    def is_paid(self):
        """Check if invoice has been paid."""
        return self.paid_date is not None
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        if not self.is_paid:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def tax_rate(self):
        """Calculate tax rate as percentage."""
        if self.subtotal > 0:
            return (self.tax_amount / self.subtotal) * 100
        return 0


class ProcureProContract(models.Model):
    """
    Represents a contract from ProcurePro system.
    """
    
    # ProcurePro identifiers
    procurepro_id = models.CharField(max_length=100, unique=True, db_index=True)
    contract_number = models.CharField(max_length=100, db_index=True)
    
    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contract_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Relationships
    supplier = models.ForeignKey(
        ProcureProSupplier,
        on_delete=models.CASCADE,
        related_name='contracts'
    )
    
    # Financial information
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='AUD')
    
    # Status and dates
    status = models.CharField(max_length=50, default='active')
    start_date = models.DateField()
    end_date = models.DateField()
    renewal_date = models.DateField(blank=True, null=True)
    
    # Contract terms
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    termination_clause = models.TextField(blank=True, null=True)
    
    # Integration metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, default='success')
    sync_errors = models.TextField(blank=True, null=True)
    
    # Raw data from ProcurePro
    raw_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'procurepro_contract'
        verbose_name = 'ProcurePro Contract'
        verbose_name_plural = 'ProcurePro Contracts'
        indexes = [
            models.Index(fields=['procurepro_id']),
            models.Index(fields=['contract_number']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['supplier']),
        ]
    
    def __str__(self):
        return f"Contract {self.contract_number} - {self.supplier.name}"
    
    @property
    def is_active(self):
        """Check if contract is currently active."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_expired(self):
        """Check if contract has expired."""
        return timezone.now().date() > self.end_date
    
    @property
    def days_until_expiry(self):
        """Calculate days until contract expires."""
        if not self.is_expired:
            return (self.end_date - timezone.now().date()).days
        return 0
    
    @property
    def contract_duration_days(self):
        """Calculate total contract duration in days."""
        return (self.end_date - self.start_date).days


class ProcureProSyncLog(models.Model):
    """
    Logs synchronization activities with ProcurePro system.
    """
    
    SYNC_TYPES = [
        ('suppliers', 'Suppliers'),
        ('purchase_orders', 'Purchase Orders'),
        ('invoices', 'Invoices'),
        ('contracts', 'Contracts'),
        ('full', 'Full Sync'),
    ]
    
    SYNC_STATUSES = [
        ('started', 'Started'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ]
    
    # Sync information
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=SYNC_STATUSES, default='started')
    
    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Results
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Error information
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Metadata
    initiated_by = models.CharField(max_length=100, blank=True, null=True)
    api_calls_made = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'procurepro_sync_log'
        verbose_name = 'ProcurePro Sync Log'
        verbose_name_plural = 'ProcurePro Sync Logs'
        indexes = [
            models.Index(fields=['sync_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.get_sync_type_display()} Sync - {self.status} ({self.started_at})"
    
    def mark_completed(self, status: str, **kwargs):
        """Mark sync as completed with results."""
        self.status = status
        self.completed_at = timezone.now()
        
        # Calculate duration
        if self.completed_at and self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_seconds = duration
        
        # Update result fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.save()
    
    @property
    def is_completed(self):
        """Check if sync has completed."""
        return self.completed_at is not None
    
    @property
    def success_rate(self):
        """Calculate success rate as percentage."""
        if self.records_processed > 0:
            successful = self.records_created + self.records_updated
            return (successful / self.records_processed) * 100
        return 0
