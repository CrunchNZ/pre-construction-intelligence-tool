"""
ProcurePro API URL Configuration

Defines URL patterns for ProcurePro integration endpoints including
suppliers, purchase orders, invoices, contracts, and synchronization.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from . import views

# Create main router for ProcurePro entities
router = DefaultRouter()
router.register(r'suppliers', views.ProcureProSupplierViewSet, basename='procurepro-supplier')
router.register(r'purchase-orders', views.ProcureProPurchaseOrderViewSet, basename='procurepro-purchase-order')
router.register(r'invoices', views.ProcureProInvoiceViewSet, basename='procurepro-invoice')
router.register(r'contracts', views.ProcureProContractViewSet, basename='procurepro-contract')
router.register(r'sync-logs', views.ProcureProSyncLogViewSet, basename='procurepro-sync-log')
router.register(r'sync', views.ProcureProSyncViewSet, basename='procurepro-sync')

# Create nested router for supplier-related data
supplier_router = routers.NestedDefaultRouter(router, r'suppliers', lookup='supplier')
supplier_router.register(r'purchase-orders', views.ProcureProPurchaseOrderViewSet, basename='supplier-purchase-orders')
supplier_router.register(r'invoices', views.ProcureProInvoiceViewSet, basename='supplier-invoices')
supplier_router.register(r'contracts', views.ProcureProContractViewSet, basename='supplier-contracts')

# Create nested router for purchase order-related data
po_router = routers.NestedDefaultRouter(router, r'purchase-orders', lookup='purchase_order')
po_router.register(r'invoices', views.ProcureProInvoiceViewSet, basename='po-invoices')

# Custom endpoint patterns for specialized functionality
custom_patterns = [
    # Analytics and reporting endpoints
    path('analytics/', views.ProcureProAnalyticsView.as_view(), name='procurepro-analytics'),
    path('analytics/suppliers/', views.ProcureProSupplierAnalyticsView.as_view(), name='supplier-analytics'),
    path('analytics/purchase-orders/', views.ProcureProPurchaseOrderAnalyticsView.as_view(), name='po-analytics'),
    path('analytics/invoices/', views.ProcureProInvoiceAnalyticsView.as_view(), name='invoice-analytics'),
    path('analytics/contracts/', views.ProcureProContractAnalyticsView.as_view(), name='contract-analytics'),
    
    # Search and filtering endpoints
    path('search/', views.ProcureProSearchView.as_view(), name='procurepro-search'),
    path('search/suppliers/', views.ProcureProSupplierSearchView.as_view(), name='supplier-search'),
    path('search/purchase-orders/', views.ProcureProPurchaseOrderSearchView.as_view(), name='po-search'),
    path('search/invoices/', views.ProcureProInvoiceSearchView.as_view(), name='invoice-search'),
    path('search/contracts/', views.ProcureProContractSearchView.as_view(), name='contract-search'),
    
    # Export endpoints
    path('export/suppliers/', views.ProcureProSupplierExportView.as_view(), name='supplier-export'),
    path('export/purchase-orders/', views.ProcureProPurchaseOrderExportView.as_view(), name='po-export'),
    path('export/invoices/', views.ProcureProInvoiceExportView.as_view(), name='invoice-export'),
    path('export/contracts/', views.ProcureProContractExportView.as_view(), name='contract-export'),
    
    # Dashboard endpoints
    path('dashboard/', views.ProcureProDashboardView.as_view(), name='procurepro-dashboard'),
    path('dashboard/summary/', views.ProcureProDashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/alerts/', views.ProcureProDashboardAlertsView.as_view(), name='dashboard-alerts'),
    
    # Health and monitoring endpoints
    path('health/', views.ProcureProHealthView.as_view(), name='procurepro-health'),
    path('health/api/', views.ProcureProAPIHealthView.as_view(), name='api-health'),
    path('health/sync/', views.ProcureProSyncHealthView.as_view(), name='sync-health'),
    
    # Configuration and settings endpoints
    path('config/', views.ProcureProConfigView.as_view(), name='procurepro-config'),
    path('config/sync-schedule/', views.ProcureProSyncScheduleView.as_view(), name='sync-schedule'),
    path('config/api-settings/', views.ProcureProAPISettingsView.as_view(), name='api-settings'),
]

# Combine all URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    path('', include(supplier_router.urls)),
    path('', include(po_router.urls)),
    
    # Include custom endpoint patterns
    *custom_patterns,
]

# Add app name for reverse URL resolution
app_name = 'procurepro'

