"""
Financial Data Models for Greentree Integration

This module contains data models for storing financial information
from Greentree accounting system integration.

Key Features:
- General ledger entries and account management
- Financial periods and reporting
- Profit and loss statements
- Balance sheet data
- Cash flow tracking
- Budget vs actual comparisons
- Job costing and project financials
- Tax codes and currency management

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import uuid
from decimal import Decimal
from typing import Optional, List, Dict, Any
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class FinancialAccount(models.Model):
    """
    Chart of accounts from Greentree.
    
    Represents the general ledger accounts used for financial
    reporting and analysis.
    """
    
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
        ('cost_of_sales', 'Cost of Sales'),
    ]
    
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Account identification
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    
    # Account hierarchy
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_accounts')
    account_level = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Financial settings
    default_currency = models.CharField(max_length=3, default='USD')
    tax_code = models.CharField(max_length=20, blank=True)
    cost_centre = models.CharField(max_length=50, blank=True)
    
    # External system mapping
    external_account_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_accounts')
    
    class Meta:
        db_table = 'financial_accounts'
        verbose_name = 'Financial Account'
        verbose_name_plural = 'Financial Accounts'
        ordering = ['account_code']
        indexes = [
            models.Index(fields=['account_code']),
            models.Index(fields=['account_type', 'account_status']),
            models.Index(fields=['parent_account', 'sort_order']),
            models.Index(fields=['cost_centre']),
        ]
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    @property
    def is_parent(self) -> bool:
        """Check if this account has child accounts."""
        return self.child_accounts.exists()
    
    @property
    def is_leaf(self) -> bool:
        """Check if this account is a leaf account (no children)."""
        return not self.is_parent
    
    def get_balance(self, as_of_date: Optional[datetime] = None) -> Decimal:
        """Get account balance as of a specific date."""
        if as_of_date is None:
            as_of_date = timezone.now()
        
        # Calculate balance from ledger entries
        entries = self.ledger_entries.filter(
            entry_date__lte=as_of_date
        )
        
        balance = Decimal('0.00')
        for entry in entries:
            if entry.account_type == 'debit':
                balance += entry.amount
            else:
                balance -= entry.amount
        
        return balance


class FinancialPeriod(models.Model):
    """
    Financial periods for reporting and analysis.
    
    Represents accounting periods (months, quarters, years)
    used for financial reporting.
    """
    
    PERIOD_TYPE_CHOICES = [
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
        ('custom', 'Custom'),
    ]
    
    PERIOD_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('locked', 'Locked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Period identification
    period_name = models.CharField(max_length=100)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    period_status = models.CharField(max_length=20, choices=PERIOD_STATUS_CHOICES, default='open')
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Financial year
    financial_year = models.PositiveIntegerField()
    period_number = models.PositiveIntegerField()  # Month number, quarter number, etc.
    
    # External system mapping
    external_period_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_periods')
    
    class Meta:
        db_table = 'financial_periods'
        verbose_name = 'Financial Period'
        verbose_name_plural = 'Financial Periods'
        ordering = ['financial_year', 'period_number']
        indexes = [
            models.Index(fields=['financial_year', 'period_number']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['period_status']),
        ]
    
    def __str__(self):
        return f"{self.period_name} ({self.start_date} - {self.end_date})"
    
    @property
    def duration_days(self) -> int:
        """Calculate the duration of the period in days."""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_current(self) -> bool:
        """Check if this is the current period."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class GeneralLedgerEntry(models.Model):
    """
    General ledger entries from Greentree.
    
    Represents individual financial transactions recorded
    in the general ledger.
    """
    
    ENTRY_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    
    ENTRY_STATUS_CHOICES = [
        ('posted', 'Posted'),
        ('pending', 'Pending'),
        ('reversed', 'Reversed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Entry identification
    entry_number = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    entry_status = models.CharField(max_length=20, choices=ENTRY_STATUS_CHOICES, default='posted')
    
    # Financial details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.000000)
    
    # Account relationships
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name='ledger_entries')
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name='ledger_entries')
    
    # Transaction details
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    memo = models.TextField(blank=True)
    
    # Project and cost centre
    project = models.ForeignKey('integrations.UnifiedProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_entries')
    cost_centre = models.CharField(max_length=50, blank=True)
    
    # External system mapping
    external_entry_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_entries')
    
    class Meta:
        db_table = 'general_ledger_entries'
        verbose_name = 'General Ledger Entry'
        verbose_name_plural = 'General Ledger Entries'
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['entry_date']),
            models.Index(fields=['account', 'entry_date']),
            models.Index(fields=['period', 'entry_date']),
            models.Index(fields=['entry_status']),
            models.Index(fields=['project', 'entry_date']),
            models.Index(fields=['cost_centre']),
        ]
    
    def __str__(self):
        return f"{self.entry_number} - {self.account.account_code} - {self.amount} {self.currency}"
    
    @property
    def base_amount(self) -> Decimal:
        """Get the amount in base currency."""
        return self.amount * self.exchange_rate


class ProfitLossStatement(models.Model):
    """
    Profit and loss statement data.
    
    Stores calculated profit and loss information for
    reporting and analysis purposes.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Statement identification
    statement_name = models.CharField(max_length=255)
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name='profit_loss_statements')
    
    # Revenue and expenses
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_cost_of_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Calculated fields
    gross_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    operating_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Statement data
    statement_data = JSONField(default=dict)  # Detailed breakdown by account
    
    # External system mapping
    external_statement_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_profit_loss_statements')
    
    class Meta:
        db_table = 'profit_loss_statements'
        verbose_name = 'Profit and Loss Statement'
        verbose_name_plural = 'Profit and Loss Statements'
        ordering = ['-period__start_date']
        indexes = [
            models.Index(fields=['period', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.statement_name} - {self.period.period_name}"
    
    def calculate_totals(self):
        """Calculate all totals based on statement data."""
        # This would typically involve complex calculations based on statement_data
        # For now, we'll use the stored values
        self.gross_profit = self.total_revenue - self.total_cost_of_sales
        self.operating_income = self.gross_profit - self.total_expenses
        self.net_income = self.operating_income
        self.save()


class BalanceSheet(models.Model):
    """
    Balance sheet data.
    
    Stores calculated balance sheet information for
    reporting and analysis purposes.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Balance sheet identification
    balance_sheet_name = models.CharField(max_length=255)
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name='balance_sheets')
    as_of_date = models.DateField()
    
    # Asset categories
    total_current_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_fixed_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Liability categories
    total_current_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_long_term_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Equity
    total_equity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Balance sheet data
    balance_sheet_data = JSONField(default=dict)  # Detailed breakdown by account
    
    # External system mapping
    external_balance_sheet_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_balance_sheets')
    
    class Meta:
        db_table = 'balance_sheets'
        verbose_name = 'Balance Sheet'
        verbose_name_plural = 'Balance Sheets'
        ordering = ['-as_of_date']
        indexes = [
            models.Index(fields=['as_of_date']),
            models.Index(fields=['period', 'as_of_date']),
        ]
    
    def __str__(self):
        return f"{self.balance_sheet_name} - {self.as_of_date}"
    
    def calculate_totals(self):
        """Calculate all totals based on balance sheet data."""
        self.total_assets = self.total_current_assets + self.total_fixed_assets
        self.total_liabilities = self.total_current_liabilities + self.total_long_term_liabilities
        self.total_equity = self.total_assets - self.total_liabilities
        self.save()


class CashFlow(models.Model):
    """
    Cash flow statement data.
    
    Stores calculated cash flow information for
    reporting and analysis purposes.
    """
    
    CASH_FLOW_TYPE_CHOICES = [
        ('operating', 'Operating Activities'),
        ('investing', 'Investing Activities'),
        ('financing', 'Financing Activities'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Cash flow identification
    cash_flow_name = models.CharField(max_length=255)
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name='cash_flows')
    
    # Cash flow by type
    operating_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    investing_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    financing_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Net cash flow
    net_cash_flow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    beginning_cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ending_cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # Cash flow data
    cash_flow_data = JSONField(default=dict)  # Detailed breakdown by activity
    
    # External system mapping
    external_cash_flow_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_cash_flows')
    
    class Meta:
        db_table = 'cash_flows'
        verbose_name = 'Cash Flow Statement'
        verbose_name_plural = 'Cash Flow Statements'
        ordering = ['-period__start_date']
        indexes = [
            models.Index(fields=['period', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.cash_flow_name} - {self.period.period_name}"
    
    def calculate_totals(self):
        """Calculate all totals based on cash flow data."""
        self.net_cash_flow = self.operating_cash_flow + self.investing_cash_flow + self.financing_cash_flow
        self.ending_cash_balance = self.beginning_cash_balance + self.net_cash_flow
        self.save()


class BudgetVsActual(models.Model):
    """
    Budget vs actual comparison data.
    
    Stores budget and actual financial data for
    variance analysis and reporting.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Comparison identification
    comparison_name = models.CharField(max_length=255)
    period = models.ForeignKey(FinancialPeriod, on_delete=models.CASCADE, related_name='budget_vs_actual')
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name='budget_vs_actual')
    
    # Budget and actual amounts
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Variance calculations
    variance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    variance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # External system mapping
    external_comparison_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_budget_vs_actual')
    
    class Meta:
        db_table = 'budget_vs_actual'
        verbose_name = 'Budget vs Actual'
        verbose_name_plural = 'Budget vs Actual'
        ordering = ['period__start_date', 'account__account_code']
        indexes = [
            models.Index(fields=['period', 'account']),
            models.Index(fields=['variance_percentage']),
        ]
    
    def __str__(self):
        return f"{self.comparison_name} - {self.account.account_code}"
    
    def calculate_variance(self):
        """Calculate variance amounts and percentages."""
        self.variance_amount = self.actual_amount - self.budget_amount
        
        if self.budget_amount != 0:
            self.variance_percentage = (self.variance_amount / self.budget_amount) * 100
        else:
            self.variance_percentage = 0
        
        self.save()


class JobCosting(models.Model):
    """
    Job costing information from Greentree.
    
    Stores project-specific financial data for
    construction project cost tracking.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Job identification
    job_number = models.CharField(max_length=50, unique=True)
    job_name = models.CharField(max_length=255)
    project = models.ForeignKey('integrations.UnifiedProject', on_delete=models.CASCADE, related_name='job_costing')
    
    # Financial information
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    committed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Cost breakdown
    labor_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    equipment_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    subcontractor_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overhead_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Currency
    currency = models.CharField(max_length=3, default='USD')
    
    # External system mapping
    external_job_id = models.CharField(max_length=100, blank=True)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_job_costing')
    
    class Meta:
        db_table = 'job_costing'
        verbose_name = 'Job Costing'
        verbose_name_plural = 'Job Costing'
        ordering = ['job_number']
        indexes = [
            models.Index(fields=['job_number']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"{self.job_number} - {self.job_name}"
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total actual cost."""
        return (self.labor_cost + self.material_cost + self.equipment_cost + 
                self.subcontractor_cost + self.overhead_cost)
    
    @property
    def cost_variance(self) -> Decimal:
        """Calculate cost variance from budget."""
        return self.actual_amount - self.budget_amount
    
    @property
    def cost_variance_percentage(self) -> Decimal:
        """Calculate cost variance percentage."""
        if self.budget_amount != 0:
            return (self.cost_variance / self.budget_amount) * 100
        return Decimal('0.00')
