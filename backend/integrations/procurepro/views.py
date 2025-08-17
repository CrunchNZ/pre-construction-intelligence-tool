"""
ProcurePro API Views

Provides REST API endpoints for accessing ProcurePro data including
suppliers, purchase orders, invoices, and contracts.
"""

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from datetime import timedelta
import csv
import json
import logging

from .models import (
    ProcureProSupplier, ProcureProPurchaseOrder, ProcureProInvoice,
    ProcureProContract, ProcureProSyncLog
)
from .serializers import (
    ProcureProSupplierSerializer, ProcureProPurchaseOrderSerializer,
    ProcureProInvoiceSerializer, ProcureProContractSerializer,
    ProcureProSyncLogSerializer, ProcureProAnalyticsSerializer,
    ProcureProSearchSerializer, ProcureProSyncRequestSerializer
)
from .sync_service import ProcureProSyncService

logger = logging.getLogger(__name__)


class ProcureProSupplierViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProcurePro suppliers.
    
    Provides read-only access to supplier data with filtering,
    searching, and analytics capabilities.
    """
    
    queryset = ProcureProSupplier.objects.all()
    serializer_class = ProcureProSupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'supplier_type', 'country']
    search_fields = ['name', 'legal_name', 'trading_name', 'email']
    ordering_fields = ['name', 'rating', 'last_synced', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get supplier analytics and insights."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            # Basic counts
            total_suppliers = ProcureProSupplier.objects.count()
            active_suppliers = ProcureProSupplier.objects.filter(status='active').count()
            new_suppliers = ProcureProSupplier.objects.filter(created_at__gte=start_date).count()
            
            # Category distribution
            category_distribution = (
                ProcureProSupplier.objects
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Rating statistics
            rating_stats = (
                ProcureProSupplier.objects
                .filter(rating__isnull=False)
                .aggregate(
                    avg_rating=Avg('rating'),
                    min_rating=Avg('rating'),
                    max_rating=Avg('rating')
                )
            )
            
            # Top suppliers by rating
            top_suppliers = (
                ProcureProSupplier.objects
                .filter(rating__isnull=False)
                .order_by('-rating')[:10]
                .values('id', 'name', 'rating', 'category')
            )
            
            # Recent activity
            recent_activity = (
                ProcureProSupplier.objects
                .filter(last_synced__gte=start_date)
                .order_by('-last_synced')[:10]
                .values('id', 'name', 'last_synced', 'sync_status')
            )
            
            return Response({
                'summary': {
                    'total_suppliers': total_suppliers,
                    'active_suppliers': active_suppliers,
                    'new_suppliers': new_suppliers,
                    'inactive_suppliers': total_suppliers - active_suppliers
                },
                'category_distribution': list(category_distribution),
                'rating_statistics': rating_stats,
                'top_suppliers': list(top_suppliers),
                'recent_activity': list(recent_activity),
                'period_days': days
            })
            
        except Exception as e:
            logger.error(f"Error getting supplier analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced supplier search with multiple criteria."""
        try:
            query = request.query_params.get('q', '')
            category = request.query_params.get('category')
            status_filter = request.query_params.get('status')
            min_rating = request.query_params.get('min_rating')
            country = request.query_params.get('country')
            
            queryset = self.queryset
            
            # Apply filters
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(legal_name__icontains=query) |
                    Q(trading_name__icontains=query) |
                    Q(email__icontains=query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if min_rating:
                queryset = queryset.filter(rating__gte=float(min_rating))
            
            if country:
                queryset = queryset.filter(country=country)
            
            # Paginate results
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in supplier search: {e}")
            return Response(
                {'error': 'Search failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProPurchaseOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProcurePro purchase orders.
    
    Provides read-only access to purchase order data with filtering,
    searching, and analytics capabilities.
    """
    
    queryset = ProcureProPurchaseOrder.objects.select_related('supplier').all()
    serializer_class = ProcureProPurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'currency', 'supplier']
    search_fields = ['po_number', 'title', 'description']
    ordering_fields = ['order_date', 'expected_delivery_date', 'total_amount', 'created_at']
    ordering = ['-order_date']
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get purchase order analytics and insights."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            # Basic counts
            total_pos = ProcureProPurchaseOrder.objects.count()
            active_pos = ProcureProPurchaseOrder.objects.filter(status='active').count()
            delivered_pos = ProcureProPurchaseOrder.objects.filter(actual_delivery_date__isnull=False).count()
            overdue_pos = ProcureProPurchaseOrder.objects.filter(
                expected_delivery_date__lt=timezone.now().date(),
                actual_delivery_date__isnull=True
            ).count()
            
            # Financial statistics
            financial_stats = (
                ProcureProPurchaseOrder.objects
                .filter(order_date__gte=start_date)
                .aggregate(
                    total_value=Sum('total_amount'),
                    avg_value=Avg('total_amount'),
                    count=Count('id')
                )
            )
            
            # Status distribution
            status_distribution = (
                ProcureProPurchaseOrder.objects
                .values('status')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Overdue analysis
            overdue_analysis = (
                ProcureProPurchaseOrder.objects
                .filter(
                    expected_delivery_date__lt=timezone.now().date(),
                    actual_delivery_date__isnull=True
                )
                .values('supplier__name')
                .annotate(
                    overdue_count=Count('id'),
                    overdue_value=Sum('total_amount')
                )
                .order_by('-overdue_value')[:10]
            )
            
            # Recent activity
            recent_activity = (
                ProcureProPurchaseOrder.objects
                .filter(created_at__gte=start_date)
                .order_by('-created_at')[:10]
                .values('id', 'po_number', 'title', 'supplier__name', 'total_amount', 'status')
            )
            
            return Response({
                'summary': {
                    'total_purchase_orders': total_pos,
                    'active_orders': active_pos,
                    'delivered_orders': delivered_pos,
                    'overdue_orders': overdue_pos
                },
                'financial_statistics': financial_stats,
                'status_distribution': list(status_distribution),
                'overdue_analysis': list(overdue_analysis),
                'recent_activity': list(recent_activity),
                'period_days': days
            })
            
        except Exception as e:
            logger.error(f"Error getting PO analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProcurePro invoices.
    
    Provides read-only access to invoice data with filtering,
    searching, and analytics capabilities.
    """
    
    queryset = ProcureProInvoice.objects.select_related('supplier', 'purchase_order').all()
    serializer_class = ProcureProInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'currency', 'supplier', 'purchase_order']
    search_fields = ['invoice_number', 'title', 'description']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-invoice_date']
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get invoice analytics and insights."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            # Basic counts
            total_invoices = ProcureProInvoice.objects.count()
            paid_invoices = ProcureProInvoice.objects.filter(paid_date__isnull=False).count()
            pending_invoices = ProcureProInvoice.objects.filter(status='pending').count()
            overdue_invoices = ProcureProInvoice.objects.filter(
                due_date__lt=timezone.now().date(),
                paid_date__isnull=True
            ).count()
            
            # Financial statistics
            financial_stats = (
                ProcureProInvoice.objects
                .filter(invoice_date__gte=start_date)
                .aggregate(
                    total_value=Sum('total_amount'),
                    total_tax=Sum('tax_amount'),
                    avg_value=Avg('total_amount'),
                    count=Count('id')
                )
            )
            
            # Status distribution
            status_distribution = (
                ProcureProInvoice.objects
                .values('status')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Overdue analysis
            overdue_analysis = (
                ProcureProInvoice.objects
                .filter(
                    due_date__lt=timezone.now().date(),
                    paid_date__isnull=True
                )
                .values('supplier__name')
                .annotate(
                    overdue_count=Count('id'),
                    overdue_value=Sum('total_amount')
                )
                .order_by('-overdue_value')[:10]
            )
            
            # Payment trends
            payment_trends = (
                ProcureProInvoice.objects
                .filter(paid_date__gte=start_date)
                .extra(select={'payment_date': 'DATE(paid_date)'})
                .values('payment_date')
                .annotate(
                    paid_count=Count('id'),
                    paid_value=Sum('total_amount')
                )
                .order_by('payment_date')
            )
            
            return Response({
                'summary': {
                    'total_invoices': total_invoices,
                    'paid_invoices': paid_invoices,
                    'pending_invoices': pending_invoices,
                    'overdue_invoices': overdue_invoices
                },
                'financial_statistics': financial_stats,
                'status_distribution': list(status_distribution),
                'overdue_analysis': list(overdue_analysis),
                'payment_trends': list(payment_trends),
                'period_days': days
            })
            
        except Exception as e:
            logger.error(f"Error getting invoice analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProContractViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProcurePro contracts.
    
    Provides read-only access to contract data with filtering,
    searching, and analytics capabilities.
    """
    
    queryset = ProcureProContract.objects.select_related('supplier').all()
    serializer_class = ProcureProContractSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'contract_type', 'currency', 'supplier']
    search_fields = ['contract_number', 'title', 'description']
    ordering_fields = ['start_date', 'end_date', 'contract_value', 'created_at']
    ordering = ['-start_date']
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get contract analytics and insights."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            # Basic counts
            total_contracts = ProcureProContract.objects.count()
            active_contracts = ProcureProContract.objects.filter(status='active').count()
            expired_contracts = ProcureProContract.objects.filter(
                end_date__lt=timezone.now().date()
            ).count()
            new_contracts = ProcureProContract.objects.filter(created_at__gte=start_date).count()
            
            # Financial statistics
            financial_stats = (
                ProcureProContract.objects
                .filter(start_date__gte=start_date)
                .aggregate(
                    total_value=Sum('contract_value'),
                    avg_value=Avg('contract_value'),
                    count=Count('id')
                )
            )
            
            # Status distribution
            status_distribution = (
                ProcureProContract.objects
                .values('status')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            # Contract type analysis
            type_analysis = (
                ProcureProContract.objects
                .values('contract_type')
                .annotate(
                    count=Count('id'),
                    total_value=Sum('contract_value'),
                    avg_value=Avg('contract_value')
                )
                .order_by('-total_value')
            )
            
            # Expiring contracts
            expiring_soon = (
                ProcureProContract.objects
                .filter(
                    end_date__gte=timezone.now().date(),
                    end_date__lte=timezone.now().date() + timedelta(days=90)
                )
                .order_by('end_date')[:10]
                .values('id', 'contract_number', 'title', 'supplier__name', 'end_date', 'contract_value')
            )
            
            return Response({
                'summary': {
                    'total_contracts': total_contracts,
                    'active_contracts': active_contracts,
                    'expired_contracts': expired_contracts,
                    'new_contracts': new_contracts
                },
                'financial_statistics': financial_stats,
                'status_distribution': list(status_distribution),
                'contract_type_analysis': list(type_analysis),
                'expiring_soon': list(expiring_soon),
                'period_days': days
            })
            
        except Exception as e:
            logger.error(f"Error getting contract analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProcurePro synchronization logs.
    
    Provides read-only access to sync log data for monitoring
    and troubleshooting synchronization activities.
    """
    
    queryset = ProcureProSyncLog.objects.all()
    serializer_class = ProcureProSyncLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sync_type', 'status']
    ordering_fields = ['started_at', 'completed_at', 'records_processed']
    ordering = ['-started_at']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get synchronization summary and statistics."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 7))
            start_date = timezone.now() - timedelta(days=days)
            
            # Recent sync activity
            recent_syncs = (
                ProcureProSyncLog.objects
                .filter(started_at__gte=start_date)
                .order_by('-started_at')
            )
            
            # Sync statistics by type
            sync_stats = (
                recent_syncs
                .values('sync_type', 'status')
                .annotate(count=Count('id'))
                .order_by('sync_type', 'status')
            )
            
            # Success rates
            success_rates = {}
            for sync_type in ['suppliers', 'purchase_orders', 'invoices', 'contracts']:
                type_syncs = recent_syncs.filter(sync_type=sync_type)
                total = type_syncs.count()
                successful = type_syncs.filter(status='success').count()
                success_rates[sync_type] = {
                    'total': total,
                    'successful': successful,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
            
            # Performance metrics
            performance_metrics = (
                recent_syncs
                .filter(duration_seconds__isnull=False)
                .aggregate(
                    avg_duration=Avg('duration_seconds'),
                    total_records_processed=Sum('records_processed'),
                    total_api_calls=Sum('api_calls_made')
                )
            )
            
            return Response({
                'period_days': days,
                'sync_statistics': list(sync_stats),
                'success_rates': success_rates,
                'performance_metrics': performance_metrics,
                'recent_syncs': ProcureProSyncLogSerializer(
                    recent_syncs[:10], many=True
                ).data
            })
            
        except Exception as e:
            logger.error(f"Error getting sync summary: {e}")
            return Response(
                {'error': 'Failed to retrieve summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProSyncViewSet(viewsets.ViewSet):
    """
    ViewSet for ProcurePro synchronization operations.
    
    Provides endpoints for manually triggering synchronization
    and monitoring sync status.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync_suppliers(self, request):
        """Manually trigger supplier synchronization."""
        try:
            incremental = request.data.get('incremental', True)
            max_records = request.data.get('max_records')
            initiated_by = request.user.username if request.user.is_authenticated else 'api'
            
            with ProcureProSyncService() as sync_service:
                sync_log = sync_service.sync_suppliers(
                    incremental=incremental,
                    max_records=max_records,
                    initiated_by=initiated_by
                )
            
            return Response({
                'message': 'Supplier synchronization completed',
                'sync_log_id': sync_log.id,
                'status': sync_log.status,
                'records_processed': sync_log.records_processed,
                'success_rate': sync_log.success_rate
            })
            
        except Exception as e:
            logger.error(f"Manual supplier sync failed: {e}")
            return Response(
                {'error': f'Synchronization failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Manually trigger full synchronization."""
        try:
            initiated_by = request.user.username if request.user.is_authenticated else 'api'
            
            with ProcureProSyncService() as sync_service:
                results = sync_service.full_sync(initiated_by=initiated_by)
            
            return Response({
                'message': 'Full synchronization completed',
                'results': {
                    entity_type: {
                        'status': log.status,
                        'records_processed': log.records_processed,
                        'success_rate': log.success_rate
                    }
                    for entity_type, log in results.items()
                }
            })
            
        except Exception as e:
            logger.error(f"Manual full sync failed: {e}")
            return Response(
                {'error': f'Synchronization failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current synchronization status."""
        try:
            with ProcureProSyncService() as sync_service:
                status_data = sync_service.get_sync_status()
            
            return Response(status_data)
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return Response(
                {'error': 'Failed to retrieve sync status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health_check(self, request):
        """Check ProcurePro API health."""
        try:
            with ProcureProSyncService() as sync_service:
                health_status = sync_service.client.health_check()
            
            return Response(health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response(
                {'status': 'unhealthy', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProAnalyticsView(APIView):
    """Comprehensive analytics view for all ProcurePro data."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive analytics across all ProcurePro entities."""
        try:
            # Get date range from query params
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            # Overall summary
            total_suppliers = ProcureProSupplier.objects.count()
            active_suppliers = ProcureProSupplier.objects.filter(status='active').count()
            total_pos = ProcureProPurchaseOrder.objects.count()
            total_invoices = ProcureProInvoice.objects.count()
            total_contracts = ProcureProContract.objects.count()
            
            # Financial summary
            total_purchase_value = ProcureProPurchaseOrder.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            total_invoice_value = ProcureProInvoice.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            total_contract_value = ProcureProContract.objects.aggregate(
                total=Sum('contract_value')
            )['total'] or 0
            
            # Status counts
            overdue_pos = ProcureProPurchaseOrder.objects.filter(
                expected_delivery_date__lt=timezone.now().date(),
                actual_delivery_date__isnull=True
            ).count()
            
            overdue_invoices = ProcureProInvoice.objects.filter(
                due_date__lt=timezone.now().date(),
                paid_date__isnull=True
            ).count()
            
            expiring_contracts = ProcureProContract.objects.filter(
                end_date__gte=timezone.now().date(),
                end_date__lte=timezone.now().date() + timedelta(days=90)
            ).count()
            
            # Recent sync activity
            last_sync = ProcureProSyncLog.objects.order_by('-started_at').first()
            last_sync_date = last_sync.started_at if last_sync else None
            
            # Calculate sync success rate
            recent_syncs = ProcureProSyncLog.objects.filter(
                started_at__gte=start_date
            )
            sync_success_rate = 0
            if recent_syncs.exists():
                successful = recent_syncs.filter(status='success').count()
                sync_success_rate = (successful / recent_syncs.count()) * 100
            
            analytics_data = {
                'summary': {
                    'total_suppliers': total_suppliers,
                    'active_suppliers': active_suppliers,
                    'total_purchase_orders': total_pos,
                    'total_invoices': total_invoices,
                    'total_contracts': total_contracts
                },
                'financial_summary': {
                    'total_purchase_value': total_purchase_value,
                    'total_invoice_value': total_invoice_value,
                    'total_contract_value': total_contract_value,
                    'total_value': total_purchase_value + total_invoice_value + total_contract_value
                },
                'status_counts': {
                    'overdue_purchase_orders': overdue_pos,
                    'overdue_invoices': overdue_invoices,
                    'expiring_contracts': expiring_contracts
                },
                'recent_activity': {
                    'last_sync_date': last_sync_date,
                    'sync_success_rate': sync_success_rate
                },
                'period': {
                    'days': days,
                    'start_date': start_date.date(),
                    'end_date': timezone.now().date()
                }
            }
            
            serializer = ProcureProAnalyticsSerializer(analytics_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProSearchView(APIView):
    """Advanced search across all ProcurePro entities."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Perform advanced search across all entities."""
        try:
            serializer = ProcureProSearchSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            query = serializer.validated_data.get('query', '')
            category = serializer.validated_data.get('category')
            status_filter = serializer.validated_data.get('status')
            min_rating = serializer.validated_data.get('min_rating')
            country = serializer.validated_data.get('country')
            
            # Search across suppliers
            supplier_results = []
            if query:
                supplier_qs = ProcureProSupplier.objects.filter(
                    Q(name__icontains=query) |
                    Q(legal_name__icontains=query) |
                    Q(trading_name__icontains=query) |
                    Q(email__icontains=query)
                )
                
                if category:
                    supplier_qs = supplier_qs.filter(category=category)
                if status_filter:
                    supplier_qs = supplier_qs.filter(status=status_filter)
                if min_rating:
                    supplier_qs = supplier_qs.filter(rating__gte=min_rating)
                if country:
                    supplier_qs = supplier_qs.filter(country=country)
                
                supplier_results = ProcureProSupplierSerializer(
                    supplier_qs[:10], many=True
                ).data
            
            # Search across purchase orders
            po_results = []
            if query:
                po_qs = ProcureProPurchaseOrder.objects.filter(
                    Q(po_number__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
                
                if status_filter:
                    po_qs = po_qs.filter(status=status_filter)
                
                po_results = ProcureProPurchaseOrderSerializer(
                    po_qs[:10], many=True
                ).data
            
            # Search across invoices
            invoice_results = []
            if query:
                invoice_qs = ProcureProInvoice.objects.filter(
                    Q(invoice_number__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
                
                if status_filter:
                    invoice_qs = invoice_qs.filter(status=status_filter)
                
                invoice_results = ProcureProInvoiceSerializer(
                    invoice_qs[:10], many=True
                ).data
            
            # Search across contracts
            contract_results = []
            if query:
                contract_qs = ProcureProContract.objects.filter(
                    Q(contract_number__icontains=query) |
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
                
                if status_filter:
                    contract_qs = contract_qs.filter(status=status_filter)
                
                contract_results = ProcureProContractSerializer(
                    contract_qs[:10], many=True
                ).data
            
            return Response({
                'query': query,
                'results': {
                    'suppliers': supplier_results,
                    'purchase_orders': po_results,
                    'invoices': invoice_results,
                    'contracts': contract_results
                },
                'total_results': len(supplier_results) + len(po_results) + len(invoice_results) + len(contract_results)
            })
            
        except Exception as e:
            logger.error(f"Error in comprehensive search: {e}")
            return Response(
                {'error': 'Search failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProDashboardView(APIView):
    """Dashboard view with key metrics and alerts."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard data with key metrics and alerts."""
        try:
            # Key metrics
            total_suppliers = ProcureProSupplier.objects.count()
            active_suppliers = ProcureProSupplier.objects.filter(status='active').count()
            total_pos = ProcureProPurchaseOrder.objects.count()
            total_invoices = ProcureProInvoice.objects.count()
            
            # Financial metrics
            total_purchase_value = ProcureProPurchaseOrder.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            total_invoice_value = ProcureProInvoice.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            # Alerts
            overdue_pos = ProcureProPurchaseOrder.objects.filter(
                expected_delivery_date__lt=timezone.now().date(),
                actual_delivery_date__isnull=True
            ).count()
            
            overdue_invoices = ProcureProInvoice.objects.filter(
                due_date__lt=timezone.now().date(),
                paid_date__isnull=True
            ).count()
            
            expiring_contracts = ProcureProContract.objects.filter(
                end_date__gte=timezone.now().date(),
                end_date__lte=timezone.now().date() + timedelta(days=30)
            ).count()
            
            # Recent activity
            recent_suppliers = ProcureProSupplier.objects.order_by('-created_at')[:5]
            recent_pos = ProcureProPurchaseOrder.objects.order_by('-created_at')[:5]
            
            # Sync status
            last_sync = ProcureProSyncLog.objects.order_by('-started_at').first()
            sync_status = 'unknown'
            if last_sync:
                if last_sync.status == 'success':
                    sync_status = 'healthy'
                elif last_sync.status == 'failed':
                    sync_status = 'failed'
                else:
                    sync_status = 'in_progress'
            
            return Response({
                'metrics': {
                    'suppliers': {
                        'total': total_suppliers,
                        'active': active_suppliers,
                        'inactive': total_suppliers - active_suppliers
                    },
                    'purchase_orders': {
                        'total': total_pos,
                        'overdue': overdue_pos
                    },
                    'invoices': {
                        'total': total_invoices,
                        'overdue': overdue_invoices
                    },
                    'contracts': {
                        'expiring_soon': expiring_contracts
                    },
                    'financial': {
                        'total_purchase_value': total_purchase_value,
                        'total_invoice_value': total_invoice_value
                    }
                },
                'alerts': {
                    'overdue_purchase_orders': overdue_pos,
                    'overdue_invoices': overdue_invoices,
                    'expiring_contracts': expiring_contracts
                },
                'recent_activity': {
                    'suppliers': ProcureProSupplierSerializer(recent_suppliers, many=True).data,
                    'purchase_orders': ProcureProPurchaseOrderSerializer(recent_pos, many=True).data
                },
                'sync_status': sync_status,
                'last_sync': ProcureProSyncLogSerializer(last_sync).data if last_sync else None
            })
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return Response(
                {'error': 'Failed to retrieve dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProHealthView(APIView):
    """Health check view for ProcurePro integration."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check overall health of ProcurePro integration."""
        try:
            # Check database connectivity
            db_healthy = True
            try:
                ProcureProSupplier.objects.count()
            except Exception:
                db_healthy = False
            
            # Check sync service health
            sync_healthy = True
            try:
                with ProcureProSyncService() as sync_service:
                    sync_healthy = sync_service.client.health_check().get('status') == 'healthy'
            except Exception:
                sync_healthy = False
            
            # Check data freshness
            last_sync = ProcureProSyncLog.objects.order_by('-started_at').first()
            data_fresh = True
            if last_sync:
                # Data is considered stale if last sync was more than 24 hours ago
                hours_since_sync = (timezone.now() - last_sync.started_at).total_seconds() / 3600
                data_fresh = hours_since_sync < 24
            
            # Overall health status
            overall_health = 'healthy' if all([db_healthy, sync_healthy, data_fresh]) else 'degraded'
            if not db_healthy:
                overall_health = 'critical'
            
            return Response({
                'status': overall_health,
                'checks': {
                    'database': {
                        'status': 'healthy' if db_healthy else 'unhealthy',
                        'details': 'Database connectivity check'
                    },
                    'sync_service': {
                        'status': 'healthy' if sync_healthy else 'unhealthy',
                        'details': 'ProcurePro API connectivity check'
                    },
                    'data_freshness': {
                        'status': 'fresh' if data_fresh else 'stale',
                        'details': 'Data synchronization freshness check'
                    }
                },
                'last_sync': ProcureProSyncLogSerializer(last_sync).data if last_sync else None,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return Response(
                {'status': 'critical', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcureProExportView(APIView):
    """Export ProcurePro data in various formats."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, entity_type):
        """Export data for specified entity type."""
        try:
            format_type = request.query_params.get('format', 'csv')
            
            if entity_type == 'suppliers':
                queryset = ProcureProSupplier.objects.all()
                filename = 'procurepro_suppliers'
            elif entity_type == 'purchase_orders':
                queryset = ProcureProPurchaseOrder.objects.select_related('supplier').all()
                filename = 'procurepro_purchase_orders'
            elif entity_type == 'invoices':
                queryset = ProcureProInvoice.objects.select_related('supplier', 'purchase_order').all()
                filename = 'procurepro_invoices'
            elif entity_type == 'contracts':
                queryset = ProcureProContract.objects.select_related('supplier').all()
                filename = 'procurepro_contracts'
            else:
                return Response(
                    {'error': 'Invalid entity type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if format_type == 'csv':
                return self._export_csv(queryset, entity_type, filename)
            elif format_type == 'json':
                return self._export_json(queryset, entity_type, filename)
            else:
                return Response(
                    {'error': 'Unsupported format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error exporting {entity_type}: {e}")
            return Response(
                {'error': f'Export failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _export_csv(self, queryset, entity_type, filename):
        """Export data as CSV."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        
        # Write headers based on entity type
        if entity_type == 'suppliers':
            headers = ['ID', 'Name', 'Email', 'Phone', 'Category', 'Status', 'Rating', 'Created']
            for row in queryset:
                writer.writerow([
                    row.id, row.name, row.email, row.phone, row.category,
                    row.status, row.rating, row.created_at
                ])
        elif entity_type == 'purchase_orders':
            headers = ['ID', 'PO Number', 'Title', 'Supplier', 'Amount', 'Status', 'Order Date']
            for row in queryset:
                writer.writerow([
                    row.id, row.po_number, row.title, row.supplier.name,
                    row.total_amount, row.status, row.order_date
                ])
        elif entity_type == 'invoices':
            headers = ['ID', 'Invoice Number', 'Title', 'Supplier', 'Amount', 'Status', 'Due Date']
            for row in queryset:
                writer.writerow([
                    row.id, row.invoice_number, row.title, row.supplier.name,
                    row.total_amount, row.status, row.due_date
                ])
        elif entity_type == 'contracts':
            headers = ['ID', 'Contract Number', 'Title', 'Supplier', 'Value', 'Status', 'End Date']
            for row in queryset:
                writer.writerow([
                    row.id, row.contract_number, row.title, row.supplier.name,
                    row.contract_value, row.status, row.end_date
                ])
        
        writer.writerow(headers)
        return response
    
    def _export_json(self, queryset, entity_type, filename):
        """Export data as JSON."""
        if entity_type == 'suppliers':
            serializer = ProcureProSupplierSerializer(queryset, many=True)
        elif entity_type == 'purchase_orders':
            serializer = ProcureProPurchaseOrderSerializer(queryset, many=True)
        elif entity_type == 'invoices':
            serializer = ProcureProInvoiceSerializer(queryset, many=True)
        elif entity_type == 'contracts':
            serializer = ProcureProContractSerializer(queryset, many=True)
        
        response = Response(serializer.data)
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response


# Additional specialized views for specific functionality
class ProcureProSupplierAnalyticsView(APIView):
    """Specialized analytics view for suppliers."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get supplier-specific analytics."""
        # Implementation similar to the analytics action in ProcureProSupplierViewSet
        pass


class ProcureProPurchaseOrderAnalyticsView(APIView):
    """Specialized analytics view for purchase orders."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get purchase order-specific analytics."""
        # Implementation similar to the analytics action in ProcureProPurchaseOrderViewSet
        pass


class ProcureProInvoiceAnalyticsView(APIView):
    """Specialized analytics view for invoices."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get invoice-specific analytics."""
        # Implementation similar to the analytics action in ProcureProInvoiceViewSet
        pass


class ProcureProContractAnalyticsView(APIView):
    """Specialized analytics view for contracts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get contract-specific analytics."""
        # Implementation similar to the analytics action in ProcureProContractViewSet
        pass


class ProcureProSupplierSearchView(APIView):
    """Specialized search view for suppliers."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search suppliers with advanced filters."""
        # Implementation for supplier-specific search
        pass


class ProcureProPurchaseOrderSearchView(APIView):
    """Specialized search view for purchase orders."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search purchase orders with advanced filters."""
        # Implementation for purchase order-specific search
        pass


class ProcureProInvoiceSearchView(APIView):
    """Specialized search view for invoices."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search invoices with advanced filters."""
        # Implementation for invoice-specific search
        pass


class ProcureProContractSearchView(APIView):
    """Specialized search view for contracts."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Search contracts with advanced filters."""
        # Implementation for contract-specific search
        pass


class ProcureProSupplierExportView(APIView):
    """Export view for suppliers."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export supplier data."""
        return ProcureProExportView().get(request, 'suppliers')


class ProcureProPurchaseOrderExportView(APIView):
    """Export view for purchase orders."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export purchase order data."""
        return ProcureProExportView().get(request, 'purchase_orders')


class ProcureProInvoiceExportView(APIView):
    """Export view for invoices."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export invoice data."""
        return ProcureProExportView().get(request, 'invoices')


class ProcureProContractExportView(APIView):
    """Export view for contracts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Export contract data."""
        return ProcureProExportView().get(request, 'contracts')


class ProcureProDashboardSummaryView(APIView):
    """Dashboard summary view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard summary data."""
        # Implementation for dashboard summary
        pass


class ProcureProDashboardAlertsView(APIView):
    """Dashboard alerts view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard alerts."""
        # Implementation for dashboard alerts
        pass


class ProcureProAPIHealthView(APIView):
    """API health check view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check ProcurePro API health."""
        # Implementation for API health check
        pass


class ProcureProSyncHealthView(APIView):
    """Sync health check view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check sync health."""
        # Implementation for sync health check
        pass


class ProcureProConfigView(APIView):
    """Configuration view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current configuration."""
        # Implementation for getting configuration
        pass
    
    def post(self, request):
        """Update configuration."""
        # Implementation for updating configuration
        pass


class ProcureProSyncScheduleView(APIView):
    """Sync schedule view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get sync schedule."""
        # Implementation for getting sync schedule
        pass
    
    def post(self, request):
        """Update sync schedule."""
        # Implementation for updating sync schedule
        pass


class ProcureProAPISettingsView(APIView):
    """API settings view."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get API settings."""
        # Implementation for getting API settings
        pass
    
    def post(self, request):
        """Update API settings."""
        # Implementation for updating API settings
        pass
