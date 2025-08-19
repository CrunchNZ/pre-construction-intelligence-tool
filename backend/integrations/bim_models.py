"""
BIM Data Models for Autodesk Platform Services Integration

This module contains data models for storing BIM (Building Information Modeling)
information from Autodesk Platform Services integration.

Key Features:
- 3D model management and versioning
- Model metadata and properties
- Viewable formats and derivatives
- Model analysis and clash detection
- Quantity takeoffs and material data
- Project folder structure
- Model translation and processing status

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import uuid
from decimal import Decimal
from typing import Optional, List, Dict, Any
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class BIMProject(models.Model):
    """
    BIM project information from Autodesk BIM 360.
    
    Represents a project in the BIM 360 environment
    with its associated models and data.
    """
    
    PROJECT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Project identification
    project_name = models.CharField(max_length=255)
    project_number = models.CharField(max_length=100, blank=True)
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='active')
    
    # Autodesk identifiers
    hub_id = models.CharField(max_length=100)
    project_id = models.CharField(max_length=100, unique=True)
    
    # Project details
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Integration mapping
    unified_project = models.ForeignKey('integrations.UnifiedProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='bim_projects')
    
    # External metadata
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bim_projects')
    
    class Meta:
        db_table = 'bim_projects'
        verbose_name = 'BIM Project'
        verbose_name_plural = 'BIM Projects'
        ordering = ['project_name']
        indexes = [
            models.Index(fields=['project_id']),
            models.Index(fields=['hub_id']),
            models.Index(fields=['project_status']),
            models.Index(fields=['unified_project']),
        ]
    
    def __str__(self):
        return f"{self.project_name} ({self.project_id})"


class BIMFolder(models.Model):
    """
    BIM project folder structure.
    
    Represents the folder hierarchy within a BIM project
    for organizing models and documents.
    """
    
    FOLDER_TYPE_CHOICES = [
        ('project', 'Project'),
        ('document', 'Document'),
        ('model', 'Model'),
        ('reference', 'Reference'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Folder identification
    folder_name = models.CharField(max_length=255)
    folder_type = models.CharField(max_length=20, choices=FOLDER_TYPE_CHOICES, default='other')
    
    # Autodesk identifiers
    folder_id = models.CharField(max_length=100, unique=True)
    
    # Hierarchy
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_folders')
    project = models.ForeignKey(BIMProject, on_delete=models.CASCADE, related_name='folders')
    
    # Folder details
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # External metadata
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bim_folders')
    
    class Meta:
        db_table = 'bim_folders'
        verbose_name = 'BIM Folder'
        verbose_name_plural = 'BIM Folders'
        ordering = ['project', 'sort_order', 'folder_name']
        indexes = [
            models.Index(fields=['folder_id']),
            models.Index(fields=['project', 'parent_folder']),
            models.Index(fields=['folder_type']),
        ]
    
    def __str__(self):
        return f"{self.folder_name} ({self.folder_id})"
    
    @property
    def full_path(self) -> str:
        """Get the full folder path."""
        if self.parent_folder:
            return f"{self.parent_folder.full_path}/{self.folder_name}"
        return self.folder_name


class BIMModel(models.Model):
    """
    BIM 3D model information.
    
    Represents a 3D model file in the BIM project
    with its associated metadata and processing status.
    """
    
    MODEL_STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('translated', 'Translated'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    MODEL_TYPE_CHOICES = [
        ('revit', 'Revit'),
        ('autocad', 'AutoCAD'),
        ('civil3d', 'Civil 3D'),
        ('inventor', 'Inventor'),
        ('fusion360', 'Fusion 360'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Model identification
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPE_CHOICES, default='other')
    model_status = models.CharField(max_length=20, choices=MODEL_STATUS_CHOICES, default='uploading')
    
    # Autodesk identifiers
    item_id = models.CharField(max_length=100, unique=True)
    version_id = models.CharField(max_length=100, blank=True)
    urn = models.CharField(max_length=500, blank=True)  # Base64 encoded identifier
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True, blank=True)  # in bytes
    file_extension = models.CharField(max_length=20, blank=True)
    
    # Project relationships
    project = models.ForeignKey(BIMProject, on_delete=models.CASCADE, related_name='models')
    folder = models.ForeignKey(BIMFolder, on_delete=models.CASCADE, related_name='models')
    
    # Model details
    description = models.TextField(blank=True)
    version_number = models.PositiveIntegerField(default=1)
    version_comment = models.TextField(blank=True)
    
    # Processing information
    translation_job_id = models.CharField(max_length=100, blank=True)
    translation_status = models.CharField(max_length=50, blank=True)
    translation_progress = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0.0
    )
    
    # Model metadata
    model_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bim_models')
    
    class Meta:
        db_table = 'bim_models'
        verbose_name = 'BIM Model'
        verbose_name_plural = 'BIM Models'
        ordering = ['project', 'folder', '-version_number', 'model_name']
        indexes = [
            models.Index(fields=['item_id']),
            models.Index(fields=['urn']),
            models.Index(fields=['project', 'folder']),
            models.Index(fields=['model_status']),
            models.Index(fields=['model_type']),
        ]
    
    def __str__(self):
        return f"{self.model_name} v{self.version_number} ({self.item_id})"
    
    @property
    def is_translated(self) -> bool:
        """Check if the model has been successfully translated."""
        return self.model_status == 'translated' and self.urn
    
    @property
    def is_processing(self) -> bool:
        """Check if the model is currently being processed."""
        return self.model_status in ['uploading', 'processing']


class ModelDerivative(models.Model):
    """
    Model derivative information.
    
    Represents a processed/translated version of a BIM model
    that can be viewed in the browser.
    """
    
    DERIVATIVE_TYPE_CHOICES = [
        ('svf', 'SVF'),
        ('svf2', 'SVF2'),
        ('thumbnail', 'Thumbnail'),
        ('geometry', 'Geometry'),
        ('viewable', 'Viewable'),
    ]
    
    DERIVATIVE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Derivative identification
    derivative_name = models.CharField(max_length=255)
    derivative_type = models.CharField(max_length=20, choices=DERIVATIVE_TYPE_CHOICES)
    derivative_status = models.CharField(max_length=20, choices=DERIVATIVE_STATUS_CHOICES, default='pending')
    
    # Model relationship
    model = models.ForeignKey(BIMModel, on_delete=models.CASCADE, related_name='derivatives')
    
    # Derivative details
    derivative_id = models.CharField(max_length=100, blank=True)
    urn = models.CharField(max_length=500, blank=True)
    viewable_id = models.CharField(max_length=100, blank=True)
    
    # File information
    file_size = models.BigIntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # Processing information
    processing_started = models.DateTimeField(null=True, blank=True)
    processing_completed = models.DateTimeField(null=True, blank=True)
    processing_duration = models.PositiveIntegerField(null=True, blank=True)  # in seconds
    
    # Derivative metadata
    derivative_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_model_derivatives')
    
    class Meta:
        db_table = 'model_derivatives'
        verbose_name = 'Model Derivative'
        verbose_name_plural = 'Model Derivatives'
        ordering = ['model', 'derivative_type', '-created_at']
        indexes = [
            models.Index(fields=['model', 'derivative_type']),
            models.Index(fields=['derivative_status']),
            models.Index(fields=['urn']),
        ]
    
    def __str__(self):
        return f"{self.derivative_name} - {self.model.model_name} ({self.derivative_type})"
    
    @property
    def is_ready(self) -> bool:
        """Check if the derivative is ready for viewing."""
        return self.derivative_status == 'success' and self.urn
    
    @property
    def processing_time(self) -> Optional[int]:
        """Get processing time in seconds."""
        if self.processing_started and self.processing_completed:
            return int((self.processing_completed - self.processing_started).total_seconds())
        return None


class ModelViewable(models.Model):
    """
    Model viewable information.
    
    Represents a viewable component within a translated model
    that can be displayed in the viewer.
    """
    
    VIEWABLE_TYPE_CHOICES = [
        ('view', 'View'),
        ('geometry', 'Geometry'),
        ('2d', '2D'),
        ('3d', '3D'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Viewable identification
    viewable_name = models.CharField(max_length=255)
    viewable_type = models.CharField(max_length=20, choices=VIEWABLE_TYPE_CHOICES, default='view')
    
    # Model relationship
    model = models.ForeignKey(BIMModel, on_delete=models.CASCADE, related_name='viewables')
    derivative = models.ForeignKey(ModelDerivative, on_delete=models.CASCADE, related_name='viewables')
    
    # Viewable details
    viewable_id = models.CharField(max_length=100, blank=True)
    guid = models.CharField(max_length=100, blank=True)
    
    # Viewable properties
    has_thumbnail = models.BooleanField(default=False)
    thumbnail_url = models.URLField(blank=True)
    
    # Viewable metadata
    viewable_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_model_viewables')
    
    class Meta:
        db_table = 'model_viewables'
        verbose_name = 'Model Viewable'
        verbose_name_plural = 'Model Viewables'
        ordering = ['model', 'viewable_type', 'viewable_name']
        indexes = [
            models.Index(fields=['model', 'viewable_type']),
            models.Index(fields=['viewable_id']),
            models.Index(fields=['guid']),
        ]
    
    def __str__(self):
        return f"{self.viewable_name} - {self.model.model_name} ({self.viewable_type})"


class ModelProperty(models.Model):
    """
    Model property information.
    
    Represents properties of objects within a BIM model
    such as materials, dimensions, and specifications.
    """
    
    PROPERTY_TYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('array', 'Array'),
        ('object', 'Object'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Property identification
    property_name = models.CharField(max_length=255)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='string')
    
    # Model relationship
    model = models.ForeignKey(BIMModel, on_delete=models.CASCADE, related_name='properties')
    viewable = models.ForeignKey(ModelViewable, on_delete=models.CASCADE, related_name='properties', null=True, blank=True)
    
    # Property details
    property_value = models.TextField(blank=True)
    property_unit = models.CharField(max_length=50, blank=True)
    property_category = models.CharField(max_length=100, blank=True)
    
    # Property metadata
    property_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_model_properties')
    
    class Meta:
        db_table = 'model_properties'
        verbose_name = 'Model Property'
        verbose_name_plural = 'Model Properties'
        ordering = ['model', 'property_category', 'property_name']
        indexes = [
            models.Index(fields=['model', 'property_category']),
            models.Index(fields=['property_name']),
            models.Index(fields=['property_type']),
        ]
    
    def __str__(self):
        return f"{self.property_name} - {self.model.model_name}"


class ModelQuantity(models.Model):
    """
    Model quantity takeoff information.
    
    Represents extracted quantities from BIM models
    for cost estimation and material planning.
    """
    
    QUANTITY_TYPE_CHOICES = [
        ('area', 'Area'),
        ('volume', 'Volume'),
        ('length', 'Length'),
        ('count', 'Count'),
        ('weight', 'Weight'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Quantity identification
    quantity_name = models.CharField(max_length=255)
    quantity_type = models.CharField(max_length=20, choices=QUANTITY_TYPE_CHOICES)
    
    # Model relationship
    model = models.ForeignKey(BIMModel, on_delete=models.CASCADE, related_name='quantities')
    
    # Quantity details
    quantity_value = models.DecimalField(max_digits=15, decimal_places=4)
    quantity_unit = models.CharField(max_length=20)
    quantity_category = models.CharField(max_length=100, blank=True)
    
    # Material information
    material_name = models.CharField(max_length=255, blank=True)
    material_code = models.CharField(max_length=100, blank=True)
    
    # Location information
    location_level = models.CharField(max_length=100, blank=True)
    location_zone = models.CharField(max_length=100, blank=True)
    
    # Quantity metadata
    quantity_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_model_quantities')
    
    class Meta:
        db_table = 'model_quantities'
        verbose_name = 'Model Quantity'
        verbose_name_plural = 'Model Quantities'
        ordering = ['model', 'quantity_category', 'quantity_name']
        indexes = [
            models.Index(fields=['model', 'quantity_category']),
            models.Index(fields=['quantity_type']),
            models.Index(fields=['material_code']),
        ]
    
    def __str__(self):
        return f"{self.quantity_name} - {self.model.model_name} ({self.quantity_value} {self.quantity_unit})"


class ModelClash(models.Model):
    """
    Model clash detection information.
    
    Represents detected clashes between different
    building systems in BIM models.
    """
    
    CLASH_SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CLASH_STATUS_CHOICES = [
        ('open', 'Open'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Clash identification
    clash_name = models.CharField(max_length=255)
    clash_severity = models.CharField(max_length=20, choices=CLASH_SEVERITY_CHOICES, default='medium')
    clash_status = models.CharField(max_length=20, choices=CLASH_STATUS_CHOICES, default='open')
    
    # Model relationship
    model = models.ForeignKey(BIMModel, on_delete=models.CASCADE, related_name='clashes')
    
    # Clash details
    clash_description = models.TextField()
    clash_type = models.CharField(max_length=100, blank=True)
    
    # Location information
    location_x = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    location_y = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    location_z = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    
    # Clashing elements
    element_1_id = models.CharField(max_length=100, blank=True)
    element_1_name = models.CharField(max_length=255, blank=True)
    element_1_system = models.CharField(max_length=100, blank=True)
    
    element_2_id = models.CharField(max_length=100, blank=True)
    element_2_name = models.CharField(max_length=255, blank=True)
    element_2_system = models.CharField(max_length=100, blank=True)
    
    # Clash metadata
    clash_metadata = models.JSONField(default=dict, blank=True)
    external_metadata = models.JSONField(default=dict, blank=True)
    
    # Resolution information
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_clashes')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_model_clashes')
    
    class Meta:
        db_table = 'model_clashes'
        verbose_name = 'Model Clash'
        verbose_name_plural = 'Model Clashes'
        ordering = ['model', '-clash_severity', 'clash_status', 'clash_name']
        indexes = [
            models.Index(fields=['model', 'clash_severity']),
            models.Index(fields=['clash_status']),
            models.Index(fields=['element_1_system', 'element_2_system']),
        ]
    
    def __str__(self):
        return f"{self.clash_name} - {self.model.model_name} ({self.clash_severity})"
    
    @property
    def is_resolved(self) -> bool:
        """Check if the clash has been resolved."""
        return self.clash_status == 'resolved'
    
    @property
    def is_critical(self) -> bool:
        """Check if the clash is critical severity."""
        return self.clash_severity == 'critical'
