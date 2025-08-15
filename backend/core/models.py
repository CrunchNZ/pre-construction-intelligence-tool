"""
Core models for the Pre-Construction Intelligence Tool.

This module contains the main data models for projects, suppliers,
and historical data analysis.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Project(models.Model):
    """Model representing a construction project."""
    
    PROJECT_STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('bidding', 'Bidding'),
        ('execution', 'Execution'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROJECT_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    
    # Basic project information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='planning')
    
    # Location and timing
    location = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_duration_days = models.IntegerField(null=True, blank=True)
    
    # Financial information
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    cost_variance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    cost_variance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Project details
    square_footage = models.IntegerField(null=True, blank=True)
    floors = models.IntegerField(null=True, blank=True)
    complexity_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True
    )
    
    # External system references
    external_id = models.CharField(max_length=100, blank=True)
    source_system = models.CharField(max_length=50, blank=True)  # e.g., 'Procore', 'Jobpac'
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return self.name
    
    def calculate_cost_variance(self):
        """Calculate cost variance and percentage."""
        if self.estimated_budget and self.actual_budget:
            self.cost_variance = self.actual_budget - self.estimated_budget
            if self.estimated_budget > 0:
                self.cost_variance_percentage = (self.cost_variance / self.estimated_budget) * 100
            self.save()
        return self.cost_variance


class Supplier(models.Model):
    """Model representing a supplier or contractor."""
    
    SUPPLIER_TYPE_CHOICES = [
        ('general_contractor', 'General Contractor'),
        ('subcontractor', 'Subcontractor'),
        ('material_supplier', 'Material Supplier'),
        ('equipment_rental', 'Equipment Rental'),
        ('consultant', 'Consultant'),
        ('other', 'Other'),
    ]
    
    # Basic supplier information
    name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=SUPPLIER_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Business information
    tax_id = models.CharField(max_length=50, blank=True)
    insurance_info = models.TextField(blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    # Performance metrics
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    reliability_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    quality_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    cost_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    
    # External system references
    external_id = models.CharField(max_length=100, blank=True)
    source_system = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
    
    def __str__(self):
        return self.name
    
    def calculate_overall_score(self):
        """Calculate overall score based on individual metrics."""
        scores = []
        if self.reliability_score:
            scores.append(self.reliability_score)
        if self.quality_score:
            scores.append(self.quality_score)
        if self.cost_score:
            scores.append(self.cost_score)
        
        if scores:
            self.overall_score = sum(scores) / len(scores)
            self.save()
        return self.overall_score


class ProjectSupplier(models.Model):
    """Model representing the relationship between projects and suppliers."""
    
    RELATIONSHIP_TYPE_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('backup', 'Backup'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='suppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='projects')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPE_CHOICES, default='primary')
    
    # Contract information
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    
    # Performance tracking
    on_time_delivery = models.BooleanField(null=True, blank=True)
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    cost_variance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'supplier']
        verbose_name = 'Project Supplier'
        verbose_name_plural = 'Project Suppliers'
    
    def __str__(self):
        return f"{self.project.name} - {self.supplier.name}"


class HistoricalData(models.Model):
    """Model for storing historical project data from external systems."""
    
    DATA_TYPE_CHOICES = [
        ('cost', 'Cost Data'),
        ('schedule', 'Schedule Data'),
        ('quality', 'Quality Data'),
        ('safety', 'Safety Data'),
        ('weather', 'Weather Data'),
        ('supply_chain', 'Supply Chain Data'),
    ]
    
    # Data identification
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='historical_data')
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    source_system = models.CharField(max_length=50)  # e.g., 'Procore', 'Jobpac'
    external_record_id = models.CharField(max_length=100, blank=True)
    
    # Data content
    data = models.JSONField()  # Store the actual data
    data_date = models.DateField()
    
    # Processing metadata
    is_processed = models.BooleanField(default=False)
    processing_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_date', '-created_at']
        verbose_name = 'Historical Data'
        verbose_name_plural = 'Historical Data'
        indexes = [
            models.Index(fields=['project', 'data_type', 'data_date']),
            models.Index(fields=['source_system', 'data_date']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.data_type} - {self.data_date}"
    
    def get_data_value(self, key, default=None):
        """Get a specific value from the JSON data."""
        return self.data.get(key, default)


class RiskAssessment(models.Model):
    """Model for storing AI-generated risk assessments."""
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    RISK_CATEGORY_CHOICES = [
        ('cost', 'Cost Risk'),
        ('schedule', 'Schedule Risk'),
        ('quality', 'Quality Risk'),
        ('safety', 'Safety Risk'),
        ('supply_chain', 'Supply Chain Risk'),
        ('weather', 'Weather Risk'),
        ('regulatory', 'Regulatory Risk'),
    ]
    
    # Risk identification
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risk_assessments')
    risk_category = models.CharField(max_length=20, choices=RISK_CATEGORY_CHOICES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    
    # Risk details
    title = models.CharField(max_length=200)
    description = models.TextField()
    probability = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Risk probability as a percentage"
    )
    impact_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Risk impact score from 1-10"
    )
    
    # AI model information
    ai_model_version = models.CharField(max_length=50, blank=True)
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    factors = models.JSONField(default=list, help_text="Factors contributing to this risk")
    
    # Mitigation
    mitigation_strategy = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_mitigated = models.BooleanField(default=False)
    mitigation_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-probability', '-impact_score']
        verbose_name = 'Risk Assessment'
        verbose_name_plural = 'Risk Assessments'
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"
    
    @property
    def risk_score(self):
        """Calculate overall risk score based on probability and impact."""
        return (self.probability * self.impact_score) / 10
