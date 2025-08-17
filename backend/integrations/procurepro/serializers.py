"""
ProcurePro API Serializers

Provides serialization for ProcurePro models including suppliers,
purchase orders, invoices, contracts, and sync logs.
"""

from rest_framework import serializers
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    ProcureProSupplier, ProcureProPurchaseOrder, ProcureProInvoice,
    ProcureProContract, ProcureProSyncLog
)


class ProcureProSupplierSerializer(serializers.ModelSerializer):
    """Serializer for ProcurePro suppliers."""
    
    # Computed fields
    full_address = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    # Related data counts
    purchase_orders_count = serializers.SerializerMethodField()
    invoices_count = serializers.SerializerMethodField()
    contracts_count = serializers.SerializerMethodField()
    
    # Financial summary
    total_purchase_value = serializers.SerializerMethodField()
    total_invoice_value = serializers.SerializerMethodField()
    total_contract_value = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcureProSupplier
        fields = [
            'id', 'procurepro_id', 'procurepro_code', 'name', 'legal_name', 'trading_name',
            'email', 'phone', 'website', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'abn', 'acn', 'tax_id', 'supplier_type', 'category',
            'subcategory', 'status', 'rating', 'credit_limit', 'payment_terms',
            'last_synced', 'sync_status', 'sync_errors', 'created_at', 'updated_at',
            'full_address', 'is_active', 'purchase_orders_count', 'invoices_count',
            'contracts_count', 'total_purchase_value', 'total_invoice_value', 'total_contract_value'
        ]
        read_only_fields = [
            'id', 'procurepro_id', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'full_address', 'is_active'
        ]
    
    def get_purchase_orders_count(self, obj):
        """Get count of purchase orders for this supplier."""
        return obj.purchase_orders.count()
    
    def get_invoices_count(self, obj):
        """Get count of invoices for this supplier."""
        return obj.invoices.count()
    
    def get_contracts_count(self, obj):
        """Get count of contracts for this supplier."""
        return obj.contracts.count()
    
    def get_total_purchase_value(self, obj):
        """Get total value of purchase orders for this supplier."""
        result = obj.purchase_orders.aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def get_total_invoice_value(self, obj):
        """Get total value of invoices for this supplier."""
        result = obj.invoices.aggregate(total=Sum('total_amount'))
        return result['total'] or 0
    
    def get_total_contract_value(self, obj):
        """Get total value of contracts for this supplier."""
        result = obj.contracts.aggregate(total=Sum('contract_value'))
        return result['total'] or 0


class ProcureProPurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for ProcurePro purchase orders."""
    
    # Computed fields
    is_delivered = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    # Related data
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_id = serializers.IntegerField(source='supplier.id', read_only=True)
    
    # Invoice summary
    invoices_count = serializers.SerializerMethodField()
    total_invoiced = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcureProPurchaseOrder
        fields = [
            'id', 'procurepro_id', 'po_number', 'title', 'description', 'supplier',
            'supplier_name', 'supplier_id', 'total_amount', 'currency', 'status',
            'order_date', 'expected_delivery_date', 'actual_delivery_date',
            'approved_by', 'approved_date', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'is_delivered', 'is_overdue', 'days_overdue',
            'invoices_count', 'total_invoiced'
        ]
        read_only_fields = [
            'id', 'procurepro_id', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'is_delivered', 'is_overdue', 'days_overdue'
        ]
    
    def get_invoices_count(self, obj):
        """Get count of invoices for this purchase order."""
        return obj.invoices.count()
    
    def get_total_invoiced(self, obj):
        """Get total amount invoiced for this purchase order."""
        result = obj.invoices.aggregate(total=Sum('total_amount'))
        return result['total'] or 0


class ProcureProInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for ProcurePro invoices."""
    
    # Computed fields
    is_paid = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    tax_rate = serializers.ReadOnlyField()
    
    # Related data
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_id = serializers.IntegerField(source='supplier.id', read_only=True)
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    purchase_order_id = serializers.IntegerField(source='purchase_order.id', read_only=True)
    
    class Meta:
        model = ProcureProInvoice
        fields = [
            'id', 'procurepro_id', 'invoice_number', 'title', 'description', 'supplier',
            'supplier_name', 'supplier_id', 'purchase_order', 'purchase_order_number',
            'purchase_order_id', 'subtotal', 'tax_amount', 'total_amount', 'currency',
            'status', 'invoice_date', 'due_date', 'paid_date', 'payment_method',
            'payment_reference', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'is_paid', 'is_overdue', 'days_overdue', 'tax_rate'
        ]
        read_only_fields = [
            'id', 'procurepro_id', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'is_paid', 'is_overdue', 'days_overdue', 'tax_rate'
        ]


class ProcureProContractSerializer(serializers.ModelSerializer):
    """Serializer for ProcurePro contracts."""
    
    # Computed fields
    is_active = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    contract_duration_days = serializers.ReadOnlyField()
    
    # Related data
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_id = serializers.IntegerField(source='supplier.id', read_only=True)
    
    class Meta:
        model = ProcureProContract
        fields = [
            'id', 'procurepro_id', 'contract_number', 'title', 'description',
            'contract_type', 'supplier', 'supplier_name', 'supplier_id', 'contract_value',
            'currency', 'status', 'start_date', 'end_date', 'renewal_date',
            'payment_terms', 'termination_clause', 'last_synced', 'sync_status',
            'sync_errors', 'created_at', 'updated_at', 'is_active', 'is_expired',
            'days_until_expiry', 'contract_duration_days'
        ]
        read_only_fields = [
            'id', 'procurepro_id', 'last_synced', 'sync_status', 'sync_errors',
            'created_at', 'updated_at', 'is_active', 'is_expired', 'days_until_expiry',
            'contract_duration_days'
        ]


class ProcureProSyncLogSerializer(serializers.ModelSerializer):
    """Serializer for ProcurePro synchronization logs."""
    
    # Computed fields
    is_completed = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    # Duration formatting
    duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcureProSyncLog
        fields = [
            'id', 'sync_type', 'status', 'started_at', 'completed_at',
            'duration_seconds', 'duration_formatted', 'records_processed',
            'records_created', 'records_updated', 'records_failed',
            'error_message', 'error_details', 'initiated_by', 'api_calls_made',
            'is_completed', 'success_rate'
        ]
        read_only_fields = [
            'id', 'started_at', 'is_completed', 'success_rate'
        ]
    
    def get_duration_formatted(self, obj):
        """Format duration in human-readable format."""
        if not obj.duration_seconds:
            return None
        
        duration = float(obj.duration_seconds)
        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            minutes = duration / 60
            return f"{minutes:.1f}m"
        else:
            hours = duration / 3600
            return f"{hours:.1f}h"


class ProcureProSupplierDetailSerializer(ProcureProSupplierSerializer):
    """Detailed serializer for ProcurePro suppliers with related data."""
    
    # Related data lists
    purchase_orders = ProcureProPurchaseOrderSerializer(many=True, read_only=True)
    invoices = ProcureProInvoiceSerializer(many=True, read_only=True)
    contracts = ProcureProContractSerializer(many=True, read_only=True)
    
    class Meta(ProcureProSupplierSerializer.Meta):
        fields = ProcureProSupplierSerializer.Meta.fields + [
            'purchase_orders', 'invoices', 'contracts'
        ]


class ProcureProPurchaseOrderDetailSerializer(ProcureProPurchaseOrderSerializer):
    """Detailed serializer for ProcurePro purchase orders with related data."""
    
    # Related data lists
    invoices = ProcureProInvoiceSerializer(many=True, read_only=True)
    
    class Meta(ProcureProPurchaseOrderSerializer.Meta):
        fields = ProcureProPurchaseOrderSerializer.Meta.fields + ['invoices']


class ProcureProAnalyticsSerializer(serializers.Serializer):
    """Serializer for ProcurePro analytics data."""
    
    # Summary statistics
    total_suppliers = serializers.IntegerField()
    active_suppliers = serializers.IntegerField()
    total_purchase_orders = serializers.IntegerField()
    total_invoices = serializers.IntegerField()
    total_contracts = serializers.IntegerField()
    
    # Financial summary
    total_purchase_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_invoice_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_contract_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Status counts
    overdue_purchase_orders = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    expiring_contracts = serializers.IntegerField()
    
    # Recent activity
    last_sync_date = serializers.DateTimeField()
    sync_success_rate = serializers.FloatField()
    
    # Period information
    period_days = serializers.IntegerField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()


class ProcureProSearchSerializer(serializers.Serializer):
    """Serializer for ProcurePro search parameters."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    min_rating = serializers.FloatField(required=False, min_value=0.0, max_value=5.0)
    country = serializers.CharField(required=False, allow_blank=True)
    supplier_type = serializers.CharField(required=False, allow_blank=True)
    
    # Date filters
    created_after = serializers.DateField(required=False)
    created_before = serializers.DateField(required=False)
    last_synced_after = serializers.DateTimeField(required=False)
    
    # Financial filters
    min_credit_limit = serializers.DecimalField(required=False, max_digits=15, decimal_places=2)
    max_credit_limit = serializers.DecimalField(required=False, max_digits=15, decimal_places=2)
    
    # Pagination
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100, default=20)
    
    # Sorting
    ordering = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate search parameters."""
        # Ensure date ranges are logical
        if 'created_after' in data and 'created_before' in data:
            if data['created_after'] > data['created_before']:
                raise serializers.ValidationError(
                    "created_after must be before created_before"
                )
        
        # Ensure credit limit range is logical
        if 'min_credit_limit' in data and 'max_credit_limit' in data:
            if data['min_credit_limit'] > data['max_credit_limit']:
                raise serializers.ValidationError(
                    "min_credit_limit must be less than max_credit_limit"
                )
        
        return data


class ProcureProSyncRequestSerializer(serializers.Serializer):
    """Serializer for ProcurePro synchronization requests."""
    
    # Sync options
    incremental = serializers.BooleanField(default=True)
    max_records = serializers.IntegerField(required=False, min_value=1)
    
    # Entity selection
    sync_suppliers = serializers.BooleanField(default=True)
    sync_purchase_orders = serializers.BooleanField(default=True)
    sync_invoices = serializers.BooleanField(default=True)
    sync_contracts = serializers.BooleanField(default=True)
    
    # Advanced options
    force_full_sync = serializers.BooleanField(default=False)
    validate_data = serializers.BooleanField(default=True)
    log_level = serializers.ChoiceField(
        choices=['debug', 'info', 'warning', 'error'],
        default='info'
    )
    
    def validate(self, data):
        """Validate sync request parameters."""
        # Ensure at least one entity type is selected
        entity_types = [
            data.get('sync_suppliers', False),
            data.get('sync_purchase_orders', False),
            data.get('sync_invoices', False),
            data.get('sync_contracts', False)
        ]
        
        if not any(entity_types):
            raise serializers.ValidationError(
                "At least one entity type must be selected for synchronization"
            )
        
        return data

