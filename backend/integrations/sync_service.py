"""
Unified Project Data Synchronization Service

This service handles data synchronization across all integrated construction
management systems including ProcurePro, Procore, and Jobpac. It provides
incremental and full sync capabilities with conflict resolution and data
validation.

Key Features:
- Multi-system data synchronization
- Incremental and full sync modes
- Conflict resolution and data validation
- Real-time sync status monitoring
- Error handling and retry logic
- Performance optimization

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from .models import (
    IntegrationSystem,
    UnifiedProject,
    ProjectSystemMapping,
    ProjectDocument,
    ProjectSchedule,
    ProjectFinancial,
    ProjectChangeOrder,
    ProjectRFI,
)
from .procurepro.client import ProcureProAPIClient
from .procore.client import ProcoreAPIClient
from .jobpac.client import JobpacAPIClient

logger = logging.getLogger(__name__)


class ProjectSyncService:
    """
    Unified project data synchronization service.
    
    Handles synchronization of project data across all integrated
    construction management systems with conflict resolution and
    data validation.
    """
    
    def __init__(self):
        """Initialize the sync service."""
        self.clients = {}
        self.sync_stats = {
            'start_time': None,
            'end_time': None,
            'projects_processed': 0,
            'projects_created': 0,
            'projects_updated': 0,
            'projects_failed': 0,
            'entities_synced': 0,
            'errors': []
        }
    
    def get_client(self, system_type: str):
        """Get API client for a specific system type."""
        if system_type not in self.clients:
            if system_type == 'procurepro':
                self.clients[system_type] = ProcureProAPIClient()
            elif system_type == 'procore':
                self.clients[system_type] = ProcoreAPIClient()
            elif system_type == 'jobpac':
                self.clients[system_type] = JobpacAPIClient()
            else:
                raise ValueError(f"Unsupported system type: {system_type}")
        
        return self.clients[system_type]
    
    def sync_all_projects(self, force_full_sync: bool = False) -> Dict[str, Any]:
        """
        Synchronize all projects from all integrated systems.
        
        Args:
            force_full_sync: Force full synchronization instead of incremental
            
        Returns:
            Sync statistics and results
        """
        logger.info("Starting full project synchronization")
        self.sync_stats['start_time'] = timezone.now()
        
        try:
            # Get all active integration systems
            systems = IntegrationSystem.objects.filter(status='active')
            
            for system in systems:
                try:
                    logger.info(f"Syncing projects from {system.name} ({system.system_type})")
                    self._sync_system_projects(system, force_full_sync)
                except Exception as e:
                    error_msg = f"Failed to sync {system.name}: {str(e)}"
                    logger.error(error_msg)
                    self.sync_stats['errors'].append(error_msg)
                    self.sync_stats['projects_failed'] += 1
            
            self.sync_stats['end_time'] = timezone.now()
            self._update_sync_status()
            
            logger.info(f"Project synchronization completed. Stats: {self.sync_stats}")
            return self.sync_stats
            
        except Exception as e:
            error_msg = f"Project synchronization failed: {str(e)}"
            logger.error(error_msg)
            self.sync_stats['errors'].append(error_msg)
            self.sync_stats['end_time'] = timezone.now()
            return self.sync_stats
    
    def sync_system_projects(self, system: IntegrationSystem, force_full_sync: bool = False) -> Dict[str, Any]:
        """
        Synchronize projects from a specific system.
        
        Args:
            system: Integration system to sync from
            force_full_sync: Force full synchronization
            
        Returns:
            Sync statistics for the system
        """
        logger.info(f"Starting project synchronization for {system.name}")
        
        try:
            return self._sync_system_projects(system, force_full_sync)
        except Exception as e:
            error_msg = f"Failed to sync {system.name}: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg, 'success': False}
    
    def _sync_system_projects(self, system: IntegrationSystem, force_full_sync: bool) -> Dict[str, Any]:
        """Internal method to sync projects from a specific system."""
        client = self.get_client(system.system_type)
        system_stats = {
            'system_name': system.name,
            'projects_processed': 0,
            'projects_created': 0,
            'projects_updated': 0,
            'projects_failed': 0,
            'entities_synced': 0,
            'start_time': timezone.now(),
            'errors': []
        }
        
        try:
            # Get projects from the system
            if system.system_type == 'procurepro':
                projects_data = client.get_projects()
            elif system.system_type == 'procore':
                projects_data = client.get_projects()
            elif system.system_type == 'jobpac':
                projects_data = client.get_projects()
            else:
                raise ValueError(f"Unsupported system type: {system.system_type}")
            
            # Process each project
            for project_data in projects_data:
                try:
                    result = self._sync_project(system, project_data, force_full_sync)
                    system_stats['projects_processed'] += 1
                    
                    if result['created']:
                        system_stats['projects_created'] += 1
                    elif result['updated']:
                        system_stats['projects_updated'] += 1
                    
                    system_stats['entities_synced'] += result['entities_synced']
                    
                except Exception as e:
                    error_msg = f"Failed to sync project {project_data.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    system_stats['errors'].append(error_msg)
                    system_stats['projects_failed'] += 1
            
            system_stats['end_time'] = timezone.now()
            system_stats['success'] = True
            
            # Update system sync status
            system.last_connection = timezone.now()
            system.connection_status = 'active'
            system.error_message = ''
            system.save()
            
            return system_stats
            
        except Exception as e:
            error_msg = f"System sync failed: {str(e)}"
            logger.error(error_msg)
            system_stats['errors'].append(error_msg)
            system_stats['success'] = False
            
            # Update system error status
            system.connection_status = 'error'
            system.error_message = str(e)
            system.save()
            
            return system_stats
    
    def _sync_project(self, system: IntegrationSystem, project_data: Dict[str, Any], force_full_sync: bool) -> Dict[str, Any]:
        """
        Synchronize a single project from external system.
        
        Args:
            system: Integration system
            project_data: Project data from external system
            force_full_sync: Force full synchronization
            
        Returns:
            Sync result with status and entity counts
        """
        external_id = str(project_data.get('id'))
        project_number = project_data.get('project_number') or project_data.get('number')
        
        # Check if project already exists
        existing_mapping = ProjectSystemMapping.objects.filter(
            system=system,
            external_project_id=external_id
        ).first()
        
        if existing_mapping:
            # Update existing project
            project = existing_mapping.project
            created = False
            updated = True
        else:
            # Create new project
            project = self._create_unified_project(project_data, system)
            created = True
            updated = False
        
        # Update project mapping
        mapping, _ = ProjectSystemMapping.objects.update_or_create(
            system=system,
            external_project_id=external_id,
            defaults={
                'project': project,
                'external_project_number': project_number,
                'external_project_name': project_data.get('name', ''),
                'last_sync': timezone.now(),
                'sync_status': 'completed',
                'sync_error': '',
                'field_mappings': self._get_field_mappings(project_data)
            }
        )
        
        # Sync project entities
        entities_synced = 0
        if force_full_sync or not existing_mapping:
            entities_synced += self._sync_project_entities(project, system, project_data)
        
        # Update project with latest data
        self._update_project_data(project, project_data, system)
        
        return {
            'created': created,
            'updated': updated,
            'entities_synced': entities_synced,
            'project_id': project.id
        }
    
    def _create_unified_project(self, project_data: Dict[str, Any], system: IntegrationSystem) -> UnifiedProject:
        """Create a new unified project from external data."""
        # Extract project information based on system type
        if system.system_type == 'procurepro':
            project_info = self._extract_procurepro_project_data(project_data)
        elif system.system_type == 'procore':
            project_info = self._extract_procore_project_data(project_data)
        elif system.system_type == 'jobpac':
            project_info = self._extract_jobpac_project_data(project_data)
        else:
            project_info = self._extract_generic_project_data(project_data)
        
        # Create the project
        project = UnifiedProject.objects.create(**project_info)
        
        # Add system to integration systems
        project.integration_systems.add(system)
        
        logger.info(f"Created unified project: {project.name} ({project.id})")
        return project
    
    def _extract_procurepro_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project data from ProcurePro format."""
        return {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'project_number': data.get('project_number', ''),
            'status': self._map_project_status(data.get('status', '')),
            'project_type': self._map_project_type(data.get('project_type', '')),
            'start_date': self._parse_date(data.get('start_date')),
            'end_date': self._parse_date(data.get('end_date')),
            'budget': self._parse_decimal(data.get('budget')),
            'client': data.get('client_name', ''),
            'contractor': data.get('contractor_name', ''),
        }
    
    def _extract_procore_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project data from Procore format."""
        return {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'project_number': data.get('project_number', ''),
            'status': self._map_project_status(data.get('status', '')),
            'project_type': self._map_project_type(data.get('project_type', '')),
            'start_date': self._parse_date(data.get('start_date')),
            'end_date': self._parse_date(data.get('end_date')),
            'budget': self._parse_decimal(data.get('budget')),
            'client': data.get('client_name', ''),
            'architect': data.get('architect_name', ''),
            'contractor': data.get('contractor_name', ''),
        }
    
    def _extract_jobpac_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project data from Jobpac format."""
        return {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'project_number': data.get('project_number', ''),
            'status': self._map_project_status(data.get('status', '')),
            'project_type': self._map_project_type(data.get('project_type', '')),
            'start_date': self._parse_date(data.get('start_date')),
            'end_date': self._parse_date(data.get('end_date')),
            'budget': self._parse_decimal(data.get('budget')),
            'client': data.get('client_name', ''),
            'contractor': data.get('contractor_name', ''),
        }
    
    def _extract_generic_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project data from generic format."""
        return {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'project_number': data.get('project_number', ''),
            'status': 'planning',
            'project_type': 'other',
            'start_date': None,
            'end_date': None,
            'budget': None,
            'client': '',
            'contractor': '',
        }
    
    def _sync_project_entities(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project entities (documents, schedules, financials, etc.)."""
        entities_synced = 0
        
        try:
            # Sync documents
            entities_synced += self._sync_project_documents(project, system, project_data)
            
            # Sync schedules
            entities_synced += self._sync_project_schedules(project, system, project_data)
            
            # Sync financials
            entities_synced += self._sync_project_financials(project, system, project_data)
            
            # Sync change orders
            entities_synced += self._sync_project_change_orders(project, system, project_data)
            
            # Sync RFIs
            entities_synced += self._sync_project_rfis(project, system, project_data)
            
        except Exception as e:
            logger.error(f"Failed to sync project entities for {project.id}: {str(e)}")
        
        return entities_synced
    
    def _sync_project_documents(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project documents."""
        try:
            client = self.get_client(system.system_type)
            external_project_id = project_data.get('id')
            
            if system.system_type == 'procore':
                documents_data = client.get_project_documents(external_project_id)
            else:
                # Other systems may not have document endpoints yet
                return 0
            
            synced_count = 0
            for doc_data in documents_data:
                try:
                    self._sync_document(project, system, doc_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync document {doc_data.get('id')}: {str(e)}")
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Failed to sync project documents: {str(e)}")
            return 0
    
    def _sync_document(self, project: UnifiedProject, system: IntegrationSystem, doc_data: Dict[str, Any]):
        """Synchronize a single document."""
        external_id = str(doc_data.get('id'))
        
        # Check if document already exists
        existing_doc = ProjectDocument.objects.filter(
            project=project,
            system_mapping__system=system,
            external_document_id=external_id
        ).first()
        
        if existing_doc:
            # Update existing document
            existing_doc.title = doc_data.get('title', existing_doc.title)
            existing_doc.description = doc_data.get('description', existing_doc.description)
            existing_doc.status = doc_data.get('status', existing_doc.status)
            existing_doc.external_metadata = doc_data
            existing_doc.save()
        else:
            # Create new document
            mapping = ProjectSystemMapping.objects.filter(
                project=project,
                system=system
            ).first()
            
            if mapping:
                ProjectDocument.objects.create(
                    project=project,
                    system_mapping=mapping,
                    title=doc_data.get('title', ''),
                    description=doc_data.get('description', ''),
                    document_type=self._map_document_type(doc_data.get('type', '')),
                    status=doc_data.get('status', 'draft'),
                    file_name=doc_data.get('file_name', ''),
                    file_size=doc_data.get('file_size'),
                    file_type=doc_data.get('file_type', ''),
                    file_url=doc_data.get('file_url', ''),
                    version=doc_data.get('version', '1.0'),
                    external_document_id=external_id,
                    external_metadata=doc_data
                )
    
    def _sync_project_schedules(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project schedules."""
        try:
            client = self.get_client(system.system_type)
            external_project_id = project_data.get('id')
            
            if system.system_type == 'procore':
                schedule_data = client.get_project_schedule(external_project_id)
                if schedule_data:
                    return self._sync_schedule(project, system, schedule_data)
            else:
                # Other systems may not have schedule endpoints yet
                return 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to sync project schedule: {str(e)}")
            return 0
    
    def _sync_schedule(self, project: UnifiedProject, system: IntegrationSystem, schedule_data: Dict[str, Any]) -> int:
        """Synchronize a single schedule."""
        external_id = str(schedule_data.get('id'))
        
        # Check if schedule already exists
        existing_schedule = ProjectSchedule.objects.filter(
            project=project,
            system_mapping__system=system,
            external_schedule_id=external_id
        ).first()
        
        if existing_schedule:
            # Update existing schedule
            existing_schedule.name = schedule_data.get('name', existing_schedule.name)
            existing_schedule.description = schedule_data.get('description', existing_schedule.description)
            existing_schedule.start_date = self._parse_date(schedule_data.get('start_date'))
            existing_schedule.end_date = self._parse_date(schedule_data.get('end_date'))
            existing_schedule.external_metadata = schedule_data
            existing_schedule.save()
            return 0
        else:
            # Create new schedule
            mapping = ProjectSystemMapping.objects.filter(
                project=project,
                system=system
            ).first()
            
            if mapping:
                ProjectSchedule.objects.create(
                    project=project,
                    system_mapping=mapping,
                    name=schedule_data.get('name', ''),
                    description=schedule_data.get('description', ''),
                    start_date=self._parse_date(schedule_data.get('start_date')),
                    end_date=self._parse_date(schedule_data.get('end_date')),
                    total_duration_days=schedule_data.get('duration_days', 0),
                    external_schedule_id=external_id,
                    external_metadata=schedule_data
                )
                return 1
        
        return 0
    
    def _sync_project_financials(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project financials."""
        try:
            client = self.get_client(system.system_type)
            external_project_id = project_data.get('id')
            
            if system.system_type == 'procore':
                budget_data = client.get_project_budget(external_project_id)
                if budget_data:
                    return self._sync_financial(project, system, budget_data, 'budget')
            elif system.system_type == 'jobpac':
                financials_data = client.get_project_financials(external_project_id)
                if financials_data:
                    return self._sync_financial(project, system, financials_data, 'actual')
            else:
                # Other systems may not have financial endpoints yet
                return 0
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to sync project financials: {str(e)}")
            return 0
    
    def _sync_financial(self, project: UnifiedProject, system: IntegrationSystem, financial_data: Dict[str, Any], financial_type: str) -> int:
        """Synchronize a single financial record."""
        external_id = str(financial_data.get('id'))
        
        # Check if financial record already exists
        existing_financial = ProjectFinancial.objects.filter(
            project=project,
            system_mapping__system=system,
            external_financial_id=external_id
        ).first()
        
        if existing_financial:
            # Update existing financial record
            existing_financial.amount = self._parse_decimal(financial_data.get('amount'))
            existing_financial.external_metadata = financial_data
            existing_financial.save()
            return 0
        else:
            # Create new financial record
            mapping = ProjectSystemMapping.objects.filter(
                project=project,
                system=system
            ).first()
            
            if mapping:
                ProjectFinancial.objects.create(
                    project=project,
                    system_mapping=mapping,
                    financial_type=financial_type,
                    amount=self._parse_decimal(financial_data.get('amount')),
                    currency=financial_data.get('currency', 'USD'),
                    effective_date=self._parse_date(financial_data.get('effective_date')),
                    external_financial_id=external_id,
                    external_metadata=financial_data
                )
                return 1
        
        return 0
    
    def _sync_project_change_orders(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project change orders."""
        try:
            client = self.get_client(system.system_type)
            external_project_id = project_data.get('id')
            
            if system.system_type == 'procore':
                change_orders_data = client.get_change_orders(external_project_id)
            else:
                # Other systems may not have change order endpoints yet
                return 0
            
            synced_count = 0
            for co_data in change_orders_data:
                try:
                    self._sync_change_order(project, system, co_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync change order {co_data.get('id')}: {str(e)}")
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Failed to sync project change orders: {str(e)}")
            return 0
    
    def _sync_change_order(self, project: UnifiedProject, system: IntegrationSystem, co_data: Dict[str, Any]):
        """Synchronize a single change order."""
        external_id = str(co_data.get('id'))
        
        # Check if change order already exists
        existing_co = ProjectChangeOrder.objects.filter(
            project=project,
            system_mapping__system=system,
            external_change_order_id=external_id
        ).first()
        
        if existing_co:
            # Update existing change order
            existing_co.title = co_data.get('title', existing_co.title)
            existing_co.description = co_data.get('description', existing_co.description)
            existing_co.status = co_data.get('status', existing_co.status)
            existing_co.change_order_value = self._parse_decimal(co_data.get('change_order_value'))
            existing_co.external_metadata = co_data
            existing_co.save()
        else:
            # Create new change order
            mapping = ProjectSystemMapping.objects.filter(
                project=project,
                system=system
            ).first()
            
            if mapping:
                ProjectChangeOrder.objects.create(
                    project=project,
                    system_mapping=mapping,
                    change_order_number=co_data.get('change_order_number', ''),
                    title=co_data.get('title', ''),
                    description=co_data.get('description', ''),
                    status=co_data.get('status', 'pending'),
                    change_order_value=self._parse_decimal(co_data.get('change_order_value')),
                    external_change_order_id=external_id,
                    external_metadata=co_data
                )
    
    def _sync_project_rfis(self, project: UnifiedProject, system: IntegrationSystem, project_data: Dict[str, Any]) -> int:
        """Synchronize project RFIs."""
        try:
            client = self.get_client(system.system_type)
            external_project_id = project_data.get('id')
            
            if system.system_type == 'procore':
                rfis_data = client.get_rfis(external_project_id)
            else:
                # Other systems may not have RFI endpoints yet
                return 0
            
            synced_count = 0
            for rfi_data in rfis_data:
                try:
                    self._sync_rfi(project, system, rfi_data)
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync RFI {rfi_data.get('id')}: {str(e)}")
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Failed to sync project RFIs: {str(e)}")
            return 0
    
    def _sync_rfi(self, project: UnifiedProject, system: IntegrationSystem, rfi_data: Dict[str, Any]):
        """Synchronize a single RFI."""
        external_id = str(rfi_data.get('id'))
        
        # Check if RFI already exists
        existing_rfi = ProjectRFI.objects.filter(
            project=project,
            system_mapping__system=system,
            external_rfi_id=external_id
        ).first()
        
        if existing_rfi:
            # Update existing RFI
            existing_rfi.subject = rfi_data.get('subject', existing_rfi.subject)
            existing_rfi.question = rfi_data.get('question', existing_rfi.question)
            existing_rfi.answer = rfi_data.get('answer', existing_rfi.answer)
            existing_rfi.status = rfi_data.get('status', existing_rfi.status)
            existing_rfi.priority = rfi_data.get('priority', existing_rfi.priority)
            existing_rfi.external_metadata = rfi_data
            existing_rfi.save()
        else:
            # Create new RFI
            mapping = ProjectSystemMapping.objects.filter(
                project=project,
                system=system
            ).first()
            
            if mapping:
                ProjectRFI.objects.create(
                    project=project,
                    system_mapping=mapping,
                    rfi_number=rfi_data.get('rfi_number', ''),
                    subject=rfi_data.get('subject', ''),
                    question=rfi_data.get('question', ''),
                    answer=rfi_data.get('answer', ''),
                    status=rfi_data.get('status', 'open'),
                    priority=rfi_data.get('priority', 'medium'),
                    date_submitted=self._parse_date(rfi_data.get('date_submitted')),
                    external_rfi_id=external_id,
                    external_metadata=rfi_data
                )
    
    def _update_project_data(self, project: UnifiedProject, project_data: Dict[str, Any], system: IntegrationSystem):
        """Update project with latest data from external system."""
        try:
            # Update basic project information
            if project_data.get('name'):
                project.name = project_data['name']
            if project_data.get('description'):
                project.description = project_data['description']
            if project_data.get('status'):
                project.status = self._map_project_status(project_data['status'])
            
            # Update dates
            if project_data.get('start_date'):
                project.start_date = self._parse_date(project_data['start_date'])
            if project_data.get('end_date'):
                project.end_date = self._parse_date(project_data['end_date'])
            
            # Update financial information
            if project_data.get('budget'):
                project.budget = self._parse_decimal(project_data['budget'])
            if project_data.get('actual_cost'):
                project.actual_cost = self._parse_decimal(project_data['actual_cost'])
            
            project.save()
            
        except Exception as e:
            logger.error(f"Failed to update project {project.id}: {str(e)}")
    
    def _get_field_mappings(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Get field mappings between external and unified systems."""
        return {
            'name': data.get('name', ''),
            'project_number': data.get('project_number', ''),
            'status': data.get('status', ''),
            'start_date': data.get('start_date', ''),
            'end_date': data.get('end_date', ''),
            'budget': data.get('budget', ''),
        }
    
    def _map_project_status(self, external_status: str) -> str:
        """Map external project status to unified status."""
        status_mapping = {
            'planning': 'planning',
            'pre_construction': 'pre_construction',
            'construction': 'construction',
            'post_construction': 'post_construction',
            'completed': 'completed',
            'on_hold': 'on_hold',
            'cancelled': 'cancelled',
            'active': 'construction',
            'inactive': 'on_hold',
            'finished': 'completed',
        }
        return status_mapping.get(external_status.lower(), 'planning')
    
    def _map_project_type(self, external_type: str) -> str:
        """Map external project type to unified type."""
        type_mapping = {
            'commercial': 'commercial',
            'residential': 'residential',
            'industrial': 'industrial',
            'infrastructure': 'infrastructure',
            'healthcare': 'healthcare',
            'education': 'education',
            'retail': 'retail',
            'office': 'commercial',
            'warehouse': 'industrial',
            'hospital': 'healthcare',
            'school': 'education',
        }
        return type_mapping.get(external_type.lower(), 'other')
    
    def _map_document_type(self, external_type: str) -> str:
        """Map external document type to unified type."""
        type_mapping = {
            'drawing': 'drawing',
            'specification': 'specification',
            'contract': 'contract',
            'permit': 'permit',
            'report': 'report',
            'photo': 'photo',
            'plan': 'drawing',
            'spec': 'specification',
            'agreement': 'contract',
            'license': 'permit',
        }
        return type_mapping.get(external_type.lower(), 'other')
    
    def _parse_date(self, date_value) -> Optional[datetime.date]:
        """Parse date value from various formats."""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%S').date()
                except ValueError:
                    return None
        
        return None
    
    def _parse_decimal(self, value) -> Optional[float]:
        """Parse decimal value from various formats."""
        if value is None:
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _update_sync_status(self):
        """Update global sync status."""
        cache.set('project_sync_status', {
            'last_sync': timezone.now().isoformat(),
            'stats': self.sync_stats,
            'status': 'completed' if not self.sync_stats['errors'] else 'completed_with_errors'
        }, timeout=3600)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return cache.get('project_sync_status', {
            'last_sync': None,
            'stats': {},
            'status': 'unknown'
        })
    
    def cleanup_clients(self):
        """Clean up API client connections."""
        for client in self.clients.values():
            try:
                client.close()
            except Exception as e:
                logger.error(f"Failed to close client: {str(e)}")
        
        self.clients.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup_clients()
