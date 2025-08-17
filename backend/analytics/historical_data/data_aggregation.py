"""
Data Aggregation Service

This module provides comprehensive data aggregation services for historical analysis,
including data collection, transformation, and consolidation across all integrated systems.

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Sum, Count, Min, Max, StdDev
from django.core.cache import cache
import pandas as pd
import numpy as np
from collections import defaultdict

from integrations.procurepro.models import (
    Supplier, PurchaseOrder, Invoice, Contract, Material
)
from integrations.procore.models import (
    Project, Subcontractor, ChangeOrder, RFI, Submittal
)
from integrations.jobpac.models import (
    Job, Task, Resource, TimeEntry, CostCode
)
from integrations.greentree.models import (
    FinancialTransaction, Budget, CostCenter, GLAccount
)
from integrations.bim.models import (
    BIMModel, Component, Clash, Coordination
)
from integrations.external_apis.models import (
    WeatherData, WeatherImpactAnalysis, DataQualityRecord
)

logger = logging.getLogger(__name__)


class DataAggregator:
    """Comprehensive data aggregation service for historical analysis."""
    
    def __init__(self):
        """Initialize the data aggregator."""
        self.cache_timeout = 3600  # 1 hour cache
        self.aggregation_methods = {
            'sum': Sum,
            'average': Avg,
            'count': Count,
            'min': Min,
            'max': Max,
            'stddev': StdDev
        }
    
    def aggregate_procurement_data(self, 
                                 start_date: datetime = None,
                                 end_date: datetime = None,
                                 supplier_ids: List[str] = None,
                                 material_categories: List[str] = None) -> Dict[str, Any]:
        """Aggregate procurement data across all systems."""
        try:
            cache_key = f"procurement_agg_{start_date}_{end_date}_{supplier_ids}_{material_categories}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now() - timedelta(days=365)
            if not end_date:
                end_date = timezone.now()
            
            # Build base queryset
            po_queryset = PurchaseOrder.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if supplier_ids:
                po_queryset = po_queryset.filter(supplier_id__in=supplier_ids)
            
            # Aggregate purchase orders
            po_aggregates = po_queryset.aggregate(
                total_count=Count('id'),
                total_value=Sum('total_amount'),
                avg_value=Avg('total_amount'),
                min_value=Min('total_amount'),
                max_value=Max('total_amount')
            )
            
            # Aggregate invoices
            invoice_queryset = Invoice.objects.filter(
                invoice_date__gte=start_date,
                invoice_date__lte=end_date
            )
            
            invoice_aggregates = invoice_queryset.aggregate(
                total_count=Count('id'),
                total_amount=Sum('amount'),
                avg_amount=Avg('amount'),
                paid_amount=Sum('paid_amount'),
                outstanding_amount=Sum('amount') - Sum('paid_amount')
            )
            
            # Aggregate by supplier
            supplier_breakdown = po_queryset.values('supplier__name').annotate(
                po_count=Count('id'),
                total_value=Sum('total_amount'),
                avg_value=Avg('total_amount')
            ).order_by('-total_value')
            
            # Aggregate by material category
            material_breakdown = po_queryset.values('materials__category').annotate(
                po_count=Count('id'),
                total_value=Sum('total_amount'),
                avg_value=Avg('total_amount')
            ).order_by('-total_value')
            
            # Calculate payment performance metrics
            payment_performance = self._calculate_payment_performance(
                po_queryset, invoice_queryset
            )
            
            result = {
                'summary': {
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_purchase_orders': po_aggregates['total_count'] or 0,
                    'total_po_value': float(po_aggregates['total_value'] or 0),
                    'average_po_value': float(po_aggregates['avg_value'] or 0),
                    'total_invoices': invoice_aggregates['total_count'] or 0,
                    'total_invoice_amount': float(invoice_aggregates['total_amount'] or 0),
                    'outstanding_amount': float(invoice_aggregates['outstanding_amount'] or 0)
                },
                'supplier_breakdown': list(supplier_breakdown),
                'material_breakdown': list(material_breakdown),
                'payment_performance': payment_performance,
                'trends': self._calculate_procurement_trends(start_date, end_date)
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating procurement data: {e}")
            return {'error': str(e)}
    
    def aggregate_project_data(self,
                             start_date: datetime = None,
                             end_date: datetime = None,
                             project_ids: List[str] = None,
                             project_types: List[str] = None) -> Dict[str, Any]:
        """Aggregate project data across all systems."""
        try:
            cache_key = f"project_agg_{start_date}_{end_date}_{project_ids}_{project_types}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now() - timedelta(days=365)
            if not end_date:
                end_date = timezone.now()
            
            # Build base queryset
            project_queryset = Project.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if project_ids:
                project_queryset = project_queryset.filter(id__in=project_ids)
            if project_types:
                project_queryset = project_queryset.filter(project_type__in=project_types)
            
            # Aggregate projects
            project_aggregates = project_queryset.aggregate(
                total_count=Count('id'),
                total_budget=Sum('budget'),
                avg_budget=Avg('budget'),
                completed_count=Count('id', filter=Q(status='completed')),
                in_progress_count=Count('id', filter=Q(status='in_progress')),
                delayed_count=Count('id', filter=Q(status='delayed'))
            )
            
            # Aggregate change orders
            change_order_queryset = ChangeOrder.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if project_ids:
                change_order_queryset = change_order_queryset.filter(project_id__in=project_ids)
            
            change_order_aggregates = change_order_queryset.aggregate(
                total_count=Count('id'),
                total_value=Sum('amount'),
                avg_value=Avg('amount'),
                approved_count=Count('id', filter=Q(status='approved')),
                pending_count=Count('id', filter=Q(status='pending'))
            )
            
            # Aggregate RFIs and Submittals
            rfi_queryset = RFI.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            if project_ids:
                rfi_queryset = rfi_queryset.filter(project_id__in=project_ids)
            
            submittal_queryset = Submittal.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            if project_ids:
                submittal_queryset = submittal_queryset.filter(project_id__in=project_ids)
            
            # Calculate project performance metrics
            project_performance = self._calculate_project_performance(
                project_queryset, change_order_queryset, rfi_queryset, submittal_queryset
            )
            
            result = {
                'summary': {
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_projects': project_aggregates['total_count'] or 0,
                    'total_budget': float(project_aggregates['total_budget'] or 0),
                    'average_budget': float(project_aggregates['avg_budget'] or 0),
                    'completed_projects': project_aggregates['completed_count'] or 0,
                    'in_progress_projects': project_aggregates['in_progress_count'] or 0,
                    'delayed_projects': project_aggregates['delayed_count'] or 0,
                    'total_change_orders': change_order_aggregates['total_count'] or 0,
                    'total_change_order_value': float(change_order_aggregates['total_value'] or 0),
                    'total_rfis': rfi_queryset.count(),
                    'total_submittals': submittal_queryset.count()
                },
                'project_performance': project_performance,
                'change_order_analysis': {
                    'total_value': float(change_order_aggregates['total_value'] or 0),
                    'average_value': float(change_order_aggregates['avg_value'] or 0),
                    'approved_count': change_order_aggregates['approved_count'] or 0,
                    'pending_count': change_order_aggregates['pending_count'] or 0
                },
                'trends': self._calculate_project_trends(start_date, end_date)
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating project data: {e}")
            return {'error': str(e)}
    
    def aggregate_financial_data(self,
                               start_date: datetime = None,
                               end_date: datetime = None,
                               cost_centers: List[str] = None,
                               gl_accounts: List[str] = None) -> Dict[str, Any]:
        """Aggregate financial data across all systems."""
        try:
            cache_key = f"financial_agg_{start_date}_{end_date}_{cost_centers}_{gl_accounts}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now() - timedelta(days=365)
            if not end_date:
                end_date = timezone.now()
            
            # Build base queryset
            transaction_queryset = FinancialTransaction.objects.filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )
            
            if cost_centers:
                transaction_queryset = transaction_queryset.filter(cost_center__in=cost_centers)
            if gl_accounts:
                transaction_queryset = transaction_queryset.filter(gl_account__in=gl_accounts)
            
            # Aggregate transactions
            transaction_aggregates = transaction_queryset.aggregate(
                total_count=Count('id'),
                total_debits=Sum('debit_amount'),
                total_credits=Sum('credit_amount'),
                net_amount=Sum('debit_amount') - Sum('credit_amount')
            )
            
            # Aggregate by cost center
            cost_center_breakdown = transaction_queryset.values('cost_center__name').annotate(
                transaction_count=Count('id'),
                total_debits=Sum('debit_amount'),
                total_credits=Sum('credit_amount'),
                net_amount=Sum('debit_amount') - Sum('credit_amount')
            ).order_by('-net_amount')
            
            # Aggregate by GL account
            gl_account_breakdown = transaction_queryset.values('gl_account__account_number', 'gl_account__name').annotate(
                transaction_count=Count('id'),
                total_debits=Sum('debit_amount'),
                total_credits=Sum('credit_amount'),
                net_amount=Sum('debit_amount') - Sum('credit_amount')
            ).order_by('-net_amount')
            
            # Calculate financial ratios and metrics
            financial_metrics = self._calculate_financial_metrics(
                transaction_queryset, start_date, end_date
            )
            
            result = {
                'summary': {
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_transactions': transaction_aggregates['total_count'] or 0,
                    'total_debits': float(transaction_aggregates['total_debits'] or 0),
                    'total_credits': float(transaction_aggregates['total_credits'] or 0),
                    'net_amount': float(transaction_aggregates['net_amount'] or 0)
                },
                'cost_center_breakdown': list(cost_center_breakdown),
                'gl_account_breakdown': list(gl_account_breakdown),
                'financial_metrics': financial_metrics,
                'trends': self._calculate_financial_trends(start_date, end_date)
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating financial data: {e}")
            return {'error': str(e)}
    
    def aggregate_bim_data(self,
                          start_date: datetime = None,
                          end_date: datetime = None,
                          model_ids: List[str] = None,
                          component_types: List[str] = None) -> Dict[str, Any]:
        """Aggregate BIM data across all systems."""
        try:
            cache_key = f"bim_agg_{start_date}_{end_date}_{model_ids}_{component_types}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now() - timedelta(days=365)
            if not end_date:
                end_date = timezone.now()
            
            # Build base queryset
            model_queryset = BIMModel.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if model_ids:
                model_queryset = model_queryset.filter(id__in=model_ids)
            
            # Aggregate BIM models
            model_aggregates = model_queryset.aggregate(
                total_count=Count('id'),
                total_file_size=Sum('file_size'),
                avg_file_size=Avg('file_size')
            )
            
            # Aggregate components
            component_queryset = Component.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            
            if component_types:
                component_queryset = component_queryset.filter(component_type__in=component_types)
            
            component_aggregates = component_queryset.aggregate(
                total_count=Count('id'),
                total_components=Count('id'),
                unique_types=Count('component_type', distinct=True)
            )
            
            # Aggregate clashes
            clash_queryset = Clash.objects.filter(
                detected_at__gte=start_date,
                detected_at__lte=end_date
            )
            
            clash_aggregates = clash_queryset.aggregate(
                total_count=Count('id'),
                resolved_count=Count('id', filter=Q(status='resolved')),
                pending_count=Count('id', filter=Q(status='pending')),
                critical_count=Count('id', filter=Q(severity='critical'))
            )
            
            # Calculate BIM performance metrics
            bim_performance = self._calculate_bim_performance(
                model_queryset, component_queryset, clash_queryset
            )
            
            result = {
                'summary': {
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_models': model_aggregates['total_count'] or 0,
                    'total_file_size': float(model_aggregates['total_file_size'] or 0),
                    'average_file_size': float(model_aggregates['avg_file_size'] or 0),
                    'total_components': component_aggregates['total_count'] or 0,
                    'unique_component_types': component_aggregates['unique_types'] or 0,
                    'total_clashes': clash_aggregates['total_count'] or 0,
                    'resolved_clashes': clash_aggregates['resolved_count'] or 0,
                    'critical_clashes': clash_aggregates['critical_count'] or 0
                },
                'bim_performance': bim_performance,
                'clash_analysis': {
                    'total_clashes': clash_aggregates['total_count'] or 0,
                    'resolved_clashes': clash_aggregates['resolved_count'] or 0,
                    'pending_clashes': clash_aggregates['pending_count'] or 0,
                    'critical_clashes': clash_aggregates['critical_count'] or 0,
                    'resolution_rate': (clash_aggregates['resolved_count'] or 0) / (clash_aggregates['total_count'] or 1) * 100
                },
                'trends': self._calculate_bim_trends(start_date, end_date)
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating BIM data: {e}")
            return {'error': str(e)}
    
    def aggregate_cross_system_data(self,
                                  start_date: datetime = None,
                                  end_date: datetime = None,
                                  systems: List[str] = None) -> Dict[str, Any]:
        """Aggregate data across all integrated systems."""
        try:
            cache_key = f"cross_system_agg_{start_date}_{end_date}_{systems}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Set default date range if not provided
            if not start_date:
                start_date = timezone.now() - timedelta(days=365)
            if not end_date:
                end_date = timezone.now()
            
            # Aggregate data from all systems
            procurement_data = self.aggregate_procurement_data(start_date, end_date)
            project_data = self.aggregate_project_data(start_date, end_date)
            financial_data = self.aggregate_financial_data(start_date, end_date)
            bim_data = self.aggregate_bim_data(start_date, end_date)
            
            # Calculate cross-system correlations and insights
            cross_system_insights = self._calculate_cross_system_insights(
                procurement_data, project_data, financial_data, bim_data
            )
            
            result = {
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'system_summaries': {
                    'procurement': procurement_data.get('summary', {}),
                    'projects': project_data.get('summary', {}),
                    'financial': financial_data.get('summary', {}),
                    'bim': bim_data.get('summary', {})
                },
                'cross_system_insights': cross_system_insights,
                'overall_metrics': self._calculate_overall_metrics(
                    procurement_data, project_data, financial_data, bim_data
                )
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating cross-system data: {e}")
            return {'error': str(e)}
    
    def _calculate_payment_performance(self, po_queryset, invoice_queryset) -> Dict[str, Any]:
        """Calculate payment performance metrics."""
        try:
            # Calculate average payment time
            paid_invoices = invoice_queryset.filter(paid_amount__gt=0)
            if paid_invoices.exists():
                avg_payment_days = paid_invoices.aggregate(
                    avg_days=Avg('payment_date' - 'invoice_date')
                )['avg_days']
            else:
                avg_payment_days = 0
            
            # Calculate payment rate
            total_invoiced = invoice_queryset.aggregate(total=Sum('amount'))['total'] or 0
            total_paid = invoice_queryset.aggregate(total=Sum('paid_amount'))['total'] or 0
            payment_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0
            
            return {
                'average_payment_days': avg_payment_days,
                'payment_rate_percentage': payment_rate,
                'total_invoiced': float(total_invoiced),
                'total_paid': float(total_paid),
                'outstanding_amount': float(total_invoiced - total_paid)
            }
        except Exception as e:
            logger.error(f"Error calculating payment performance: {e}")
            return {}
    
    def _calculate_project_performance(self, project_queryset, change_order_queryset, 
                                     rfi_queryset, submittal_queryset) -> Dict[str, Any]:
        """Calculate project performance metrics."""
        try:
            # Calculate project completion rate
            total_projects = project_queryset.count()
            completed_projects = project_queryset.filter(status='completed').count()
            completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            
            # Calculate change order impact
            total_change_order_value = change_order_queryset.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            total_project_budget = project_queryset.aggregate(
                total=Sum('budget')
            )['total'] or 0
            
            change_order_impact = (total_change_order_value / total_project_budget * 100) if total_project_budget > 0 else 0
            
            return {
                'completion_rate_percentage': completion_rate,
                'change_order_impact_percentage': change_order_impact,
                'total_change_order_value': float(total_change_order_value),
                'total_project_budget': float(total_project_budget),
                'rfi_count': rfi_queryset.count(),
                'submittal_count': submittal_queryset.count()
            }
        except Exception as e:
            logger.error(f"Error calculating project performance: {e}")
            return {}
    
    def _calculate_financial_metrics(self, transaction_queryset, start_date, end_date) -> Dict[str, Any]:
        """Calculate financial performance metrics."""
        try:
            # Calculate monthly averages
            months_diff = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            if months_diff == 0:
                months_diff = 1
            
            total_transactions = transaction_queryset.count()
            avg_monthly_transactions = total_transactions / months_diff
            
            # Calculate transaction volume trends
            monthly_breakdown = transaction_queryset.extra(
                select={'month': "EXTRACT(month FROM transaction_date)"}
            ).values('month').annotate(
                transaction_count=Count('id'),
                total_amount=Sum('debit_amount') - Sum('credit_amount')
            ).order_by('month')
            
            return {
                'average_monthly_transactions': avg_monthly_transactions,
                'monthly_breakdown': list(monthly_breakdown),
                'total_transactions': total_transactions
            }
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {e}")
            return {}
    
    def _calculate_bim_performance(self, model_queryset, component_queryset, clash_queryset) -> Dict[str, Any]:
        """Calculate BIM performance metrics."""
        try:
            # Calculate model complexity
            total_components = component_queryset.count()
            total_models = model_queryset.count()
            avg_components_per_model = total_components / total_models if total_models > 0 else 0
            
            # Calculate clash resolution efficiency
            total_clashes = clash_queryset.count()
            resolved_clashes = clash_queryset.filter(status='resolved').count()
            resolution_efficiency = (resolved_clashes / total_clashes * 100) if total_clashes > 0 else 0
            
            return {
                'average_components_per_model': avg_components_per_model,
                'clash_resolution_efficiency_percentage': resolution_efficiency,
                'total_components': total_components,
                'total_models': total_models
            }
        except Exception as e:
            logger.error(f"Error calculating BIM performance: {e}")
            return {}
    
    def _calculate_cross_system_insights(self, procurement_data, project_data, 
                                       financial_data, bim_data) -> Dict[str, Any]:
        """Calculate insights across different systems."""
        try:
            insights = {}
            
            # Procurement vs Project correlation
            if 'summary' in procurement_data and 'summary' in project_data:
                po_value = procurement_data['summary'].get('total_po_value', 0)
                project_budget = project_data['summary'].get('total_budget', 0)
                if project_budget > 0:
                    procurement_ratio = po_value / project_budget
                    insights['procurement_to_budget_ratio'] = procurement_ratio
            
            # Financial vs Project correlation
            if 'summary' in financial_data and 'summary' in project_data:
                financial_net = financial_data['summary'].get('net_amount', 0)
                project_budget = project_data['summary'].get('total_budget', 0)
                if project_budget > 0:
                    budget_variance = financial_net / project_budget
                    insights['budget_variance_ratio'] = budget_variance
            
            return insights
        except Exception as e:
            logger.error(f"Error calculating cross-system insights: {e}")
            return {}
    
    def _calculate_overall_metrics(self, procurement_data, project_data, 
                                 financial_data, bim_data) -> Dict[str, Any]:
        """Calculate overall performance metrics."""
        try:
            overall_metrics = {
                'total_projects': project_data.get('summary', {}).get('total_projects', 0),
                'total_procurement_value': procurement_data.get('summary', {}).get('total_po_value', 0),
                'total_financial_net': financial_data.get('summary', {}).get('net_amount', 0),
                'total_bim_models': bim_data.get('summary', {}).get('total_models', 0)
            }
            
            # Calculate overall health score
            health_scores = []
            if 'project_performance' in project_data:
                completion_rate = project_data['project_performance'].get('completion_rate_percentage', 0)
                health_scores.append(completion_rate)
            
            if 'clash_analysis' in bim_data:
                resolution_rate = bim_data['clash_analysis'].get('resolution_rate', 0)
                health_scores.append(resolution_rate)
            
            if health_scores:
                overall_metrics['overall_health_score'] = sum(health_scores) / len(health_scores)
            
            return overall_metrics
        except Exception as e:
            logger.error(f"Error calculating overall metrics: {e}")
            return {}
    
    def _calculate_procurement_trends(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate procurement trends over time."""
        try:
            # Monthly procurement trends
            monthly_data = PurchaseOrder.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).extra(
                select={'month': "EXTRACT(month FROM created_at)"}
            ).values('month').annotate(
                po_count=Count('id'),
                total_value=Sum('total_amount')
            ).order_by('month')
            
            return {
                'monthly_trends': list(monthly_data)
            }
        except Exception as e:
            logger.error(f"Error calculating procurement trends: {e}")
            return {}
    
    def _calculate_project_trends(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate project trends over time."""
        try:
            # Monthly project trends
            monthly_data = Project.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).extra(
                select={'month': "EXTRACT(month FROM created_at)"}
            ).values('month').annotate(
                project_count=Count('id'),
                total_budget=Sum('budget')
            ).order_by('month')
            
            return {
                'monthly_trends': list(monthly_data)
            }
        except Exception as e:
            logger.error(f"Error calculating project trends: {e}")
            return {}
    
    def _calculate_financial_trends(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate financial trends over time."""
        try:
            # Monthly financial trends
            monthly_data = FinancialTransaction.objects.filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            ).extra(
                select={'month': "EXTRACT(month FROM transaction_date)"}
            ).values('month').annotate(
                transaction_count=Count('id'),
                net_amount=Sum('debit_amount') - Sum('credit_amount')
            ).order_by('month')
            
            return {
                'monthly_trends': list(monthly_data)
            }
        except Exception as e:
            logger.error(f"Error calculating financial trends: {e}")
            return {}
    
    def _calculate_bim_trends(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate BIM trends over time."""
        try:
            # Monthly BIM trends
            monthly_data = BIMModel.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).extra(
                select={'month': "EXTRACT(month FROM created_at)"}
            ).values('month').annotate(
                model_count=Count('id'),
                total_file_size=Sum('file_size')
            ).order_by('month')
            
            return {
                'monthly_trends': list(monthly_data)
            }
        except Exception as e:
            logger.error(f"Error calculating BIM trends: {e}")
            return {}
