"""
Unified Project Data Models

This module contains unified data models that integrate project information
from multiple construction management systems including ProcurePro, Procore,
and Jobpac. These models provide a consistent interface for accessing
project data across all integrated platforms.

Key Features:
- Unified project representation across all systems
- Cross-platform data mapping and normalization
- Audit trail for data changes and synchronization
- Performance optimization with proper indexing
- Comprehensive data validation and constraints

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

User = get_user_model()


class IntegrationSystem(models.Model):
    """
    Represents an external integration system.
    
    This model tracks all integrated systems and their configuration
    details for proper data synchronization and management.
    """
    
    SYSTEM_CHOICES = [
        ('procurepro', 'ProcurePro'),
        ('procore', 'Procore'),
        ('jobpac', 'Jobpac'),
        ('greentree', 'Greentree'),
        ('bim', 'BIM'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    system_type = models.CharField(max_length=50, choices=SYSTEM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Configuration
    base_url = models.URLField(max_length=500)
    api_version = models.CharField(max_length=20, default='v1')
    credentials = JSONField(default=dict, blank=True)  # Encrypted credentials
    
    # Connection details
    last_connection = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=20, default='unknown')
    error_message = models.TextField(blank=True)
    
    # Performance metrics
    avg_response_time = models.FloatField(default=0.0)
    total_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'integration_systems'
        verbose_name = 'Integration System'
        verbose_name_plural = 'Integration Systems'
        ordering = ['name']
        indexes = [
            models.Index(fields=['system_type', 'status']),
            models.Index(fields=['status', 'last_connection']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_system_type_display()})"
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of API requests."""
        if self.total_requests == 0:
            return 0.0
        return ((self.total_requests - self.failed_requests) / self.total_requests) * 100
    
    def update_connection_status(self, status: str, error_message: str = '') -> None:
        """Update connection status and metrics."""
        self.connection_status = status
        self.last_connection = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save()


class UnifiedProject(models.Model):
    """
    Unified project model that integrates data from multiple systems.
    
    This model provides a single source of truth for project information
    across all integrated construction management platforms.
    """
    
    PROJECT_STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('pre_construction', 'Pre-Construction'),
        ('construction', 'Construction'),
        ('post_construction', 'Post-Construction'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROJECT_TYPE_CHOICES = [
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic project information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='planning')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='commercial')
    
    # Location and contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Project details
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_duration_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Financial information
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Project team
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    client = models.CharField(max_length=255, blank=True)
    architect = models.CharField(max_length=255, blank=True)
    contractor = models.CharField(max_length=255, blank=True)
    
    # Integration mapping
    integration_systems = models.ManyToManyField(IntegrationSystem, through='ProjectSystemMapping')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    
    class Meta:
        db_table = 'unified_projects'
        verbose_name = 'Unified Project'
        verbose_name_plural = 'Unified Projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'project_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['project_number']),
            models.Index(fields=['city', 'state']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project_number})"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate project progress based on dates."""
        if not self.start_date or not self.end_date:
            return 0.0
        
        today = timezone.now().date()
        if today < self.start_date:
            return 0.0
        elif today > self.end_date:
            return 100.0
        
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (today - self.start_date).days
        return min(100.0, (elapsed_days / total_days) * 100)
    
    @property
    def budget_variance(self) -> Optional[Decimal]:
        """Calculate budget variance."""
        if self.budget and self.actual_cost:
            return self.actual_cost - self.budget
        return None
    
    @property
    def is_over_budget(self) -> bool:
        """Check if project is over budget."""
        variance = self.budget_variance
        return variance is not None and variance > 0
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining in project."""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        remaining = (self.end_date - today).days
        return max(0, remaining)


class ProjectSystemMapping(models.Model):
    """
    Maps projects to their corresponding system IDs across different platforms.
    
    This model maintains the relationship between unified projects and
    their external system representations for proper data synchronization.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='system_mappings')
    system = models.ForeignKey(IntegrationSystem, on_delete=models.CASCADE, related_name='project_mappings')
    
    # External system identifiers
    external_project_id = models.CharField(max_length=100)
    external_project_number = models.CharField(max_length=100, blank=True)
    external_project_name = models.CharField(max_length=255, blank=True)
    
    # Synchronization status
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default='pending')
    sync_error = models.TextField(blank=True)
    
    # Data mapping
    field_mappings = JSONField(default=dict, blank=True)  # Maps external fields to unified fields
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_system_mappings'
        verbose_name = 'Project System Mapping'
        verbose_name_plural = 'Project System Mappings'
        unique_together = [['project', 'system'], ['system', 'external_project_id']]
        indexes = [
            models.Index(fields=['system', 'sync_status']),
            models.Index(fields=['last_sync', 'sync_status']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.system.name} ({self.external_project_id})"


class ProjectDocument(models.Model):
    """
    Unified document model for project documents across all systems.
    
    This model consolidates document information from multiple platforms
    into a single, searchable interface.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('drawing', 'Drawing'),
        ('specification', 'Specification'),
        ('contract', 'Contract'),
        ('permit', 'Permit'),
        ('report', 'Report'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('superseded', 'Superseded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Document information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    file_type = models.CharField(max_length=100, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    
    # Version control
    version = models.CharField(max_length=20, default='1.0')
    revision = models.CharField(max_length=20, blank=True)
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='documents')
    system_mapping = models.ForeignKey(ProjectSystemMapping, on_delete=models.CASCADE, related_name='documents')
    
    # External system data
    external_document_id = models.CharField(max_length=100)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'project_documents'
        verbose_name = 'Project Document'
        verbose_name_plural = 'Project Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'document_type']),
            models.Index(fields=['status', 'document_type']),
            models.Index(fields=['external_document_id']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.project.name}"


class ProjectSchedule(models.Model):
    """
    Unified project schedule model integrating data from multiple systems.
    
    This model consolidates scheduling information from Procore, Jobpac,
    and other project management platforms.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Schedule information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Schedule details
    total_duration_days = models.PositiveIntegerField()
    critical_path_length = models.PositiveIntegerField(null=True, blank=True)
    completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0.0
    )
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='schedules')
    system_mapping = models.ForeignKey(ProjectSystemMapping, on_delete=models.CASCADE, related_name='schedules')
    
    # External system data
    external_schedule_id = models.CharField(max_length=100)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_schedules'
        verbose_name = 'Project Schedule'
        verbose_name_plural = 'Project Schedules'
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['project', 'start_date']),
            models.Index(fields=['completion_percentage']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"


class ProjectFinancial(models.Model):
    """
    Unified project financial model integrating data from multiple systems.
    
    This model consolidates financial information from ProcurePro, Jobpac,
    and other financial management platforms.
    """
    
    FINANCIAL_TYPE_CHOICES = [
        ('budget', 'Budget'),
        ('actual', 'Actual'),
        ('forecast', 'Forecast'),
        ('commitment', 'Commitment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Financial information
    financial_type = models.CharField(max_length=20, choices=FINANCIAL_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Cost breakdown
    labor_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    material_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    equipment_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    subcontractor_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    overhead_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Date information
    effective_date = models.DateField()
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='financials')
    system_mapping = models.ForeignKey(ProjectSystemMapping, on_delete=models.CASCADE, related_name='financials')
    
    # External system data
    external_financial_id = models.CharField(max_length=100)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_financials'
        verbose_name = 'Project Financial'
        verbose_name_plural = 'Project Financials'
        ordering = ['-effective_date']
        indexes = [
            models.Index(fields=['project', 'financial_type']),
            models.Index(fields=['effective_date', 'financial_type']),
        ]
    
    def __str__(self):
        return f"{self.get_financial_type_display()} - {self.project.name} - {self.amount} {self.currency}"


class ProjectChangeOrder(models.Model):
    """
    Unified change order model integrating data from multiple systems.
    
    This model consolidates change order information from Procore, Jobpac,
    and other project management platforms.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Change order information
    change_order_number = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial impact
    original_contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    change_order_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    new_total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Schedule impact
    original_completion_date = models.DateField(null=True, blank=True)
    new_completion_date = models.DateField(null=True, blank=True)
    schedule_impact_days = models.IntegerField(null=True, blank=True)
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='change_orders')
    system_mapping = models.ForeignKey(ProjectSystemMapping, on_delete=models.CASCADE, related_name='change_orders')
    
    # External system data
    external_change_order_id = models.CharField(max_length=100)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'project_change_orders'
        verbose_name = 'Project Change Order'
        verbose_name_plural = 'Project Change Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['change_order_number']),
        ]
    
    def __str__(self):
        return f"{self.change_order_number} - {self.title}"


class ProjectRFI(models.Model):
    """
    Unified RFI model integrating data from multiple systems.
    
    This model consolidates RFI information from Procore, Jobpac,
    and other project management platforms.
    """
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
        ('pending_review', 'Pending Review'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # RFI information
    rfi_number = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    question = models.TextField()
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    date_submitted = models.DateField()
    date_answered = models.DateField(null=True, blank=True)
    date_closed = models.DateField(null=True, blank=True)
    
    # Relationships
    project = models.ForeignKey(UnifiedProject, on_delete=models.CASCADE, related_name='rfis')
    system_mapping = models.ForeignKey(ProjectSystemMapping, on_delete=models.CASCADE, related_name='rfis')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_rfis')
    answered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='answered_rfis')
    
    # External system data
    external_rfi_id = models.CharField(max_length=100)
    external_metadata = JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_rfis'
        verbose_name = 'Project RFI'
        verbose_name_plural = 'Project RFIs'
        ordering = ['-date_submitted']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['rfi_number']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.rfi_number} - {self.subject}"
    
    @property
    def days_open(self) -> int:
        """Calculate days the RFI has been open."""
        if self.status == 'closed' and self.date_closed:
            return (self.date_closed - self.date_submitted).days
        elif self.status == 'answered' and self.date_answered:
            return (self.date_answered - self.date_submitted).days
        else:
            return (timezone.now().date() - self.date_submitted).days
