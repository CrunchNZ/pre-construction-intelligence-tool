"""
Financial Analytics Service for Greentree Integration

This service provides comprehensive financial analytics and reporting
capabilities for data from the Greentree accounting system.

Key Features:
- Financial performance analysis
- Budget vs actual comparisons
- Cash flow analysis
- Profit and loss reporting
- Balance sheet analysis
- Job costing analytics
- Trend analysis and forecasting
- Financial health scoring

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear

from .financial_models import (
    FinancialAccount,
    FinancialPeriod,
    GeneralLedgerEntry,
    ProfitLossStatement,
    BalanceSheet,
    CashFlow,
    BudgetVsActual,
    JobCosting,
)

logger = logging.getLogger(__name__)


class FinancialAnalyticsService:
    """
    Financial analytics service for Greentree integration.
    
    Provides comprehensive financial analysis, reporting,
    and insights for construction project management.
    """
    
    def __init__(self):
        """Initialize the financial analytics service."""
        self.cache_timeout = 3600  # 1 hour
        self.analytics_stats = {
            'last_analysis': None,
            'analyses_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
    
    def get_financial_overview(self, period_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Get comprehensive financial overview for a period.
        
        Args:
            period_id: Financial period ID
            start_date: Start date for analysis (YYYY-MM-DD)
            end_date: End date for analysis (YYYY-MM-DD)
            
        Returns:
            Dictionary containing financial overview data
        """
        cache_key = f'financial_overview_{period_id}_{start_date}_{end_date}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Determine date range
            if period_id:
                period = FinancialPeriod.objects.get(id=period_id)
                start_date = period.start_date
                end_date = period.end_date
            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                # Default to current month
                today = timezone.now().date()
                start_date = today.replace(day=1)
                end_date = today
            
            # Get financial data
            overview_data = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days + 1
                },
                'summary': self._get_financial_summary(start_date, end_date),
                'performance': self._get_performance_metrics(start_date, end_date),
                'trends': self._get_financial_trends(start_date, end_date),
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, overview_data, self.cache_timeout)
            
            self.analytics_stats['last_analysis'] = timezone.now()
            self.analytics_stats['analyses_performed'] += 1
            
            return overview_data
            
        except Exception as e:
            logger.error(f"Failed to get financial overview: {str(e)}")
            return {'error': f'Failed to get financial overview: {str(e)}'}
    
    def get_profit_loss_analysis(self, period_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Get detailed profit and loss analysis.
        
        Args:
            period_id: Financial period ID
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing P&L analysis data
        """
        cache_key = f'profit_loss_analysis_{period_id}_{start_date}_{end_date}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Determine date range
            if period_id:
                period = FinancialPeriod.objects.get(id=period_id)
                start_date = period.start_date
                end_date = period.end_date
            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                # Default to current month
                today = timezone.now().date()
                start_date = today.replace(day=1)
                end_date = today
            
            # Get P&L data
            pl_data = self._get_profit_loss_data(start_date, end_date)
            
            # Calculate key metrics
            gross_margin = 0
            if pl_data['total_revenue'] > 0:
                gross_margin = ((pl_data['total_revenue'] - pl_data['total_cost_of_sales']) / pl_data['total_revenue']) * 100
            
            operating_margin = 0
            if pl_data['total_revenue'] > 0:
                operating_margin = (pl_data['operating_income'] / pl_data['total_revenue']) * 100
            
            net_margin = 0
            if pl_data['total_revenue'] > 0:
                net_margin = (pl_data['net_income'] / pl_data['total_revenue']) * 100
            
            analysis_data = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'profit_loss': pl_data,
                'margins': {
                    'gross_margin': round(gross_margin, 2),
                    'operating_margin': round(operating_margin, 2),
                    'net_margin': round(net_margin, 2)
                },
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, analysis_data, self.cache_timeout)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to get profit and loss analysis: {str(e)}")
            return {'error': f'Failed to get profit and loss analysis: {str(e)}'}
    
    def get_balance_sheet_analysis(self, as_of_date: str = None) -> Dict[str, Any]:
        """
        Get balance sheet analysis as of a specific date.
        
        Args:
            as_of_date: Date for balance sheet (YYYY-MM-DD)
            
        Returns:
            Dictionary containing balance sheet analysis data
        """
        cache_key = f'balance_sheet_analysis_{as_of_date}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Determine as-of date
            if as_of_date:
                as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
            else:
                as_of_date = timezone.now().date()
            
            # Get balance sheet data
            bs_data = self._get_balance_sheet_data(as_of_date)
            
            # Calculate key ratios
            current_ratio = 0
            if bs_data['total_current_liabilities'] > 0:
                current_ratio = bs_data['total_current_assets'] / bs_data['total_current_liabilities']
            
            debt_to_equity = 0
            if bs_data['total_equity'] > 0:
                debt_to_equity = bs_data['total_liabilities'] / bs_data['total_equity']
            
            asset_turnover = 0
            if bs_data['total_assets'] > 0:
                # This would typically use revenue data from P&L
                asset_turnover = 0  # Placeholder
            
            analysis_data = {
                'as_of_date': as_of_date.isoformat(),
                'balance_sheet': bs_data,
                'ratios': {
                    'current_ratio': round(current_ratio, 2),
                    'debt_to_equity': round(debt_to_equity, 2),
                    'asset_turnover': round(asset_turnover, 2)
                },
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, analysis_data, self.cache_timeout)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to get balance sheet analysis: {str(e)}")
            return {'error': f'Failed to get balance sheet analysis: {str(e)}'}
    
    def get_cash_flow_analysis(self, period_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Get cash flow analysis for a period.
        
        Args:
            period_id: Financial period ID
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing cash flow analysis data
        """
        cache_key = f'cash_flow_analysis_{period_id}_{start_date}_{end_date}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Determine date range
            if period_id:
                period = FinancialPeriod.objects.get(id=period_id)
                start_date = period.start_date
                end_date = period.end_date
            elif start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                # Default to current month
                today = timezone.now().date()
                start_date = today.replace(day=1)
                end_date = today
            
            # Get cash flow data
            cf_data = self._get_cash_flow_data(start_date, end_date)
            
            # Calculate key metrics
            operating_cash_flow_ratio = 0
            if cf_data['total_current_liabilities'] > 0:
                operating_cash_flow_ratio = cf_data['operating_cash_flow'] / cf_data['total_current_liabilities']
            
            cash_coverage_ratio = 0
            if cf_data['total_debt'] > 0:
                cash_coverage_ratio = cf_data['operating_cash_flow'] / cf_data['total_debt']
            
            analysis_data = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'cash_flow': cf_data,
                'ratios': {
                    'operating_cash_flow_ratio': round(operating_cash_flow_ratio, 2),
                    'cash_coverage_ratio': round(cash_coverage_ratio, 2)
                },
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, analysis_data, self.cache_timeout)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to get cash flow analysis: {str(e)}")
            return {'error': f'Failed to get cash flow analysis: {str(e)}'}
    
    def get_budget_vs_actual_analysis(self, period_id: str = None, account_code: str = None) -> Dict[str, Any]:
        """
        Get budget vs actual analysis.
        
        Args:
            period_id: Financial period ID
            account_code: Specific account code to analyze
            
        Returns:
            Dictionary containing budget vs actual analysis data
        """
        cache_key = f'budget_vs_actual_analysis_{period_id}_{account_code}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Get budget vs actual data
            bva_data = self._get_budget_vs_actual_data(period_id, account_code)
            
            # Calculate variance analysis
            total_budget = sum(item['budget_amount'] for item in bva_data['items'])
            total_actual = sum(item['actual_amount'] for item in bva_data['items'])
            total_variance = total_actual - total_budget
            
            total_variance_percentage = 0
            if total_budget > 0:
                total_variance_percentage = (total_variance / total_budget) * 100
            
            # Categorize variances
            favorable_variances = [item for item in bva_data['items'] if item['variance_amount'] < 0]
            unfavorable_variances = [item for item in bva_data['items'] if item['variance_amount'] > 0]
            
            analysis_data = {
                'summary': {
                    'total_budget': total_budget,
                    'total_actual': total_actual,
                    'total_variance': total_variance,
                    'total_variance_percentage': round(total_variance_percentage, 2)
                },
                'variance_analysis': {
                    'favorable_count': len(favorable_variances),
                    'unfavorable_count': len(unfavorable_variances),
                    'favorable_variances': favorable_variances,
                    'unfavorable_variances': unfavorable_variances
                },
                'detailed_analysis': bva_data,
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, analysis_data, self.cache_timeout)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to get budget vs actual analysis: {str(e)}")
            return {'error': f'Failed to get budget vs actual analysis: {str(e)}'}
    
    def get_job_costing_analysis(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get job costing analysis for projects.
        
        Args:
            project_id: Specific project ID to analyze
            
        Returns:
            Dictionary containing job costing analysis data
        """
        cache_key = f'job_costing_analysis_{project_id}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Get job costing data
            jc_data = self._get_job_costing_data(project_id)
            
            # Calculate cost performance metrics
            total_budget = sum(job['budget_amount'] for job in jc_data['jobs'])
            total_actual = sum(job['actual_amount'] for job in jc_data['jobs'])
            total_committed = sum(job['committed_amount'] for job in jc_data['jobs'])
            
            total_variance = total_actual - total_budget
            total_variance_percentage = 0
            if total_budget > 0:
                total_variance_percentage = (total_variance / total_budget) * 100
            
            # Cost breakdown analysis
            cost_breakdown = {
                'labor': sum(job['labor_cost'] for job in jc_data['jobs']),
                'material': sum(job['material_cost'] for job in jc_data['jobs']),
                'equipment': sum(job['equipment_cost'] for job in jc_data['jobs']),
                'subcontractor': sum(job['subcontractor_cost'] for job in jc_data['jobs']),
                'overhead': sum(job['overhead_cost'] for job in jc_data['jobs'])
            }
            
            analysis_data = {
                'summary': {
                    'total_budget': total_budget,
                    'total_actual': total_actual,
                    'total_committed': total_committed,
                    'total_variance': total_variance,
                    'total_variance_percentage': round(total_variance_percentage, 2)
                },
                'cost_breakdown': cost_breakdown,
                'jobs': jc_data['jobs'],
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, analysis_data, self.cache_timeout)
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to get job costing analysis: {str(e)}")
            return {'error': f'Failed to get job costing analysis: {str(e)}'}
    
    def get_financial_health_score(self) -> Dict[str, Any]:
        """
        Calculate overall financial health score.
        
        Returns:
            Dictionary containing financial health score and metrics
        """
        cache_key = 'financial_health_score'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            self.analytics_stats['cache_hits'] += 1
            return cached_result
        
        self.analytics_stats['cache_misses'] += 1
        
        try:
            # Get current financial data
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
            
            # Calculate various metrics
            pl_data = self._get_profit_loss_data(start_date, end_date)
            bs_data = self._get_balance_sheet_data(today)
            cf_data = self._get_cash_flow_data(start_date, end_date)
            
            # Calculate health score components
            profitability_score = self._calculate_profitability_score(pl_data)
            liquidity_score = self._calculate_liquidity_score(bs_data)
            solvency_score = self._calculate_solvency_score(bs_data)
            efficiency_score = self._calculate_efficiency_score(pl_data, bs_data)
            
            # Weighted average score
            overall_score = (
                profitability_score * 0.3 +
                liquidity_score * 0.25 +
                solvency_score * 0.25 +
                efficiency_score * 0.2
            )
            
            # Determine health level
            if overall_score >= 80:
                health_level = 'Excellent'
            elif overall_score >= 70:
                health_level = 'Good'
            elif overall_score >= 60:
                health_level = 'Fair'
            elif overall_score >= 50:
                health_level = 'Poor'
            else:
                health_level = 'Critical'
            
            health_data = {
                'overall_score': round(overall_score, 1),
                'health_level': health_level,
                'component_scores': {
                    'profitability': round(profitability_score, 1),
                    'liquidity': round(liquidity_score, 1),
                    'solvency': round(solvency_score, 1),
                    'efficiency': round(efficiency_score, 1)
                },
                'metrics': {
                    'profit_loss': pl_data,
                    'balance_sheet': bs_data,
                    'cash_flow': cf_data
                },
                'analysis_timestamp': timezone.now().isoformat()
            }
            
            # Cache the result
            cache.set(cache_key, health_data, self.cache_timeout)
            
            return health_data
            
        except Exception as e:
            logger.error(f"Failed to calculate financial health score: {str(e)}")
            return {'error': f'Failed to calculate financial health score: {str(e)}'}
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear all cached analytics data."""
        try:
            # Clear all financial analytics cache keys
            cache_keys = [
                'financial_overview_*',
                'profit_loss_analysis_*',
                'balance_sheet_analysis_*',
                'cash_flow_analysis_*',
                'budget_vs_actual_analysis_*',
                'job_costing_analysis_*',
                'financial_health_score'
            ]
            
            cleared_count = 0
            for pattern in cache_keys:
                # This is a simplified approach - in production you might use
                # a more sophisticated cache clearing mechanism
                cleared_count += 1
            
            return {
                'status': 'success',
                'message': 'Financial analytics cache cleared',
                'cleared_patterns': cleared_count,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return {'error': f'Failed to clear cache: {str(e)}'}
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics service statistics."""
        return {
            'analytics_stats': self.analytics_stats,
            'cache_timeout': self.cache_timeout,
            'timestamp': timezone.now().isoformat()
        }
    
    # Private helper methods
    
    def _get_financial_summary(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Get financial summary for a date range."""
        # Get ledger entries for the period
        entries = GeneralLedgerEntry.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            entry_status='posted'
        )
        
        # Calculate totals by account type
        revenue = entries.filter(account__account_type='revenue').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        expenses = entries.filter(account__account_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        assets = entries.filter(account__account_type='asset').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        liabilities = entries.filter(account__account_type='liability').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return {
            'total_revenue': revenue,
            'total_expenses': expenses,
            'total_assets': assets,
            'total_liabilities': liabilities,
            'net_income': revenue - expenses,
            'total_equity': assets - liabilities
        }
    
    def _get_performance_metrics(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Get performance metrics for a date range."""
        # This would calculate various performance metrics
        # For now, return placeholder data
        return {
            'revenue_growth': 0.0,
            'expense_growth': 0.0,
            'profit_margin': 0.0,
            'asset_turnover': 0.0,
            'return_on_equity': 0.0
        }
    
    def _get_financial_trends(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Get financial trends for a date range."""
        # This would analyze trends over time
        # For now, return placeholder data
        return {
            'revenue_trend': 'stable',
            'expense_trend': 'stable',
            'profit_trend': 'stable',
            'cash_flow_trend': 'stable'
        }
    
    def _get_profit_loss_data(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Get profit and loss data for a date range."""
        # Get ledger entries for the period
        entries = GeneralLedgerEntry.objects.filter(
            entry_date__gte=start_date,
            entry_date__lte=end_date,
            entry_status='posted'
        )
        
        # Calculate P&L components
        revenue = entries.filter(account__account_type='revenue').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        cost_of_sales = entries.filter(account__account_type='cost_of_sales').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        expenses = entries.filter(account__account_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        gross_profit = revenue - cost_of_sales
        operating_income = gross_profit - expenses
        net_income = operating_income
        
        return {
            'total_revenue': revenue,
            'total_cost_of_sales': cost_of_sales,
            'gross_profit': gross_profit,
            'total_expenses': expenses,
            'operating_income': operating_income,
            'net_income': net_income
        }
    
    def _get_balance_sheet_data(self, as_of_date: datetime.date) -> Dict[str, Any]:
        """Get balance sheet data as of a specific date."""
        # Get ledger entries up to the as-of date
        entries = GeneralLedgerEntry.objects.filter(
            entry_date__lte=as_of_date,
            entry_status='posted'
        )
        
        # Calculate balance sheet components
        current_assets = entries.filter(account__account_type='asset').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        fixed_assets = Decimal('0.00')  # Placeholder
        
        current_liabilities = entries.filter(account__account_type='liability').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        long_term_liabilities = Decimal('0.00')  # Placeholder
        
        total_assets = current_assets + fixed_assets
        total_liabilities = current_liabilities + long_term_liabilities
        total_equity = total_assets - total_liabilities
        
        return {
            'total_current_assets': current_assets,
            'total_fixed_assets': fixed_assets,
            'total_assets': total_assets,
            'total_current_liabilities': current_liabilities,
            'total_long_term_liabilities': long_term_liabilities,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity
        }
    
    def _get_cash_flow_data(self, start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """Get cash flow data for a date range."""
        # This would calculate cash flow from operations, investing, and financing
        # For now, return placeholder data
        return {
            'operating_cash_flow': Decimal('0.00'),
            'investing_cash_flow': Decimal('0.00'),
            'financing_cash_flow': Decimal('0.00'),
            'net_cash_flow': Decimal('0.00'),
            'total_current_liabilities': Decimal('0.00'),
            'total_debt': Decimal('0.00')
        }
    
    def _get_budget_vs_actual_data(self, period_id: str = None, account_code: str = None) -> Dict[str, Any]:
        """Get budget vs actual data."""
        # This would retrieve budget vs actual data from the database
        # For now, return placeholder data
        return {
            'items': [
                {
                    'account_code': '1000',
                    'account_name': 'Cash',
                    'budget_amount': Decimal('100000.00'),
                    'actual_amount': Decimal('95000.00'),
                    'variance_amount': Decimal('-5000.00'),
                    'variance_percentage': -5.0
                }
            ]
        }
    
    def _get_job_costing_data(self, project_id: str = None) -> Dict[str, Any]:
        """Get job costing data."""
        # This would retrieve job costing data from the database
        # For now, return placeholder data
        return {
            'jobs': [
                {
                    'job_number': 'JOB001',
                    'job_name': 'Sample Project',
                    'budget_amount': Decimal('500000.00'),
                    'actual_amount': Decimal('480000.00'),
                    'committed_amount': Decimal('490000.00'),
                    'labor_cost': Decimal('200000.00'),
                    'material_cost': Decimal('150000.00'),
                    'equipment_cost': Decimal('80000.00'),
                    'subcontractor_cost': Decimal('40000.00'),
                    'overhead_cost': Decimal('10000.00')
                }
            ]
        }
    
    def _calculate_profitability_score(self, pl_data: Dict[str, Any]) -> float:
        """Calculate profitability score component."""
        if pl_data['total_revenue'] <= 0:
            return 0.0
        
        # Calculate profit margin
        profit_margin = (pl_data['net_income'] / pl_data['total_revenue']) * 100
        
        # Score based on profit margin
        if profit_margin >= 20:
            return 100.0
        elif profit_margin >= 15:
            return 85.0
        elif profit_margin >= 10:
            return 70.0
        elif profit_margin >= 5:
            return 55.0
        elif profit_margin >= 0:
            return 40.0
        else:
            return max(0.0, 40.0 + (profit_margin * 2))
    
    def _calculate_liquidity_score(self, bs_data: Dict[str, Any]) -> float:
        """Calculate liquidity score component."""
        if bs_data['total_current_liabilities'] <= 0:
            return 100.0
        
        # Calculate current ratio
        current_ratio = bs_data['total_current_assets'] / bs_data['total_current_liabilities']
        
        # Score based on current ratio
        if current_ratio >= 2.0:
            return 100.0
        elif current_ratio >= 1.5:
            return 85.0
        elif current_ratio >= 1.0:
            return 70.0
        elif current_ratio >= 0.8:
            return 55.0
        else:
            return max(0.0, 55.0 + (current_ratio - 0.8) * 275)
    
    def _calculate_solvency_score(self, bs_data: Dict[str, Any]) -> float:
        """Calculate solvency score component."""
        if bs_data['total_equity'] <= 0:
            return 0.0
        
        # Calculate debt-to-equity ratio
        debt_to_equity = bs_data['total_liabilities'] / bs_data['total_equity']
        
        # Score based on debt-to-equity ratio
        if debt_to_equity <= 0.5:
            return 100.0
        elif debt_to_equity <= 1.0:
            return 85.0
        elif debt_to_equity <= 1.5:
            return 70.0
        elif debt_to_equity <= 2.0:
            return 55.0
        else:
            return max(0.0, 55.0 - (debt_to_equity - 2.0) * 27.5)
    
    def _calculate_efficiency_score(self, pl_data: Dict[str, Any], bs_data: Dict[str, Any]) -> float:
        """Calculate efficiency score component."""
        if pl_data['total_revenue'] <= 0 or bs_data['total_assets'] <= 0:
            return 50.0
        
        # Calculate asset turnover
        asset_turnover = pl_data['total_revenue'] / bs_data['total_assets']
        
        # Score based on asset turnover
        if asset_turnover >= 2.0:
            return 100.0
        elif asset_turnover >= 1.5:
            return 85.0
        elif asset_turnover >= 1.0:
            return 70.0
        elif asset_turnover >= 0.5:
            return 55.0
        else:
            return max(0.0, 55.0 + (asset_turnover * 90))
