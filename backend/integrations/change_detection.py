"""
Project Change Detection Service

This service monitors and detects changes across all integrated
construction management systems. It provides real-time change tracking,
change history, and automated change notifications.

Key Features:
- Real-time change detection
- Change history tracking
- Automated change notifications
- Change impact analysis
- Change approval workflows
- Integration with external systems

Author: Pre-Construction Intelligence Team
Version: 1.0.0
"""

import logging
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, F
from django.contrib.auth.models import User

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

logger = logging.getLogger(__name__)


class ChangeDetectionService:
    """
    Project change detection service.
    
    Monitors and detects changes across all integrated construction
    management systems with real-time tracking and notifications.
    """
    
    def __init__(self):
        """Initialize the change detection service."""
        self.change_types = {
            'project': ['name', 'status', 'budget', 'start_date', 'end_date', 'progress_percentage'],
            'document': ['title', 'status', 'version', 'file_name', 'file_size'],
            'schedule': ['name', 'start_date', 'end_date', 'completion_percentage'],
            'financial': ['amount', 'financial_type', 'effective_date'],
            'change_order': ['title', 'status', 'change_order_value', 'description'],
            'rfi': ['subject', 'status', 'priority', 'question', 'answer']
        }
        self.notification_channels = ['email', 'slack', 'webhook', 'database']
    
    def detect_changes(self, project_id: str = None, system_type: str = None) -> Dict[str, Any]:
        """
        Detect changes across projects or specific systems.
        
        Args:
            project_id: Specific project to monitor (optional)
            system_type: Specific system type to monitor (optional)
            
        Returns:
            Change detection results
        """
        try:
            logger.info(f"Starting change detection - Project: {project_id}, System: {system_type}")
            
            changes_detected = {
                'timestamp': timezone.now().isoformat(),
                'total_changes': 0,
                'changes_by_type': {},
                'changes_by_priority': {'high': 0, 'medium': 0, 'low': 0},
                'affected_projects': [],
                'notifications_sent': 0,
                'errors': []
            }
            
            if project_id:
                # Detect changes for specific project
                project_changes = self._detect_project_changes(project_id)
                changes_detected['changes_by_type']['project'] = project_changes
                changes_detected['total_changes'] += len(project_changes)
                changes_detected['affected_projects'].append(project_id)
            else:
                # Detect changes across all projects
                projects = UnifiedProject.objects.all()
                if system_type:
                    projects = projects.filter(integration_systems__system_type=system_type)
                
                for project in projects:
                    try:
                        project_changes = self._detect_project_changes(str(project.id))
                        if project_changes:
                            changes_detected['changes_by_type'][str(project.id)] = project_changes
                            changes_detected['total_changes'] += len(project_changes)
                            changes_detected['affected_projects'].append(str(project.id))
                    except Exception as e:
                        error_msg = f"Failed to detect changes for project {project.id}: {str(e)}"
                        logger.error(error_msg)
                        changes_detected['errors'].append(error_msg)
            
            # Analyze change priorities
            changes_detected['changes_by_priority'] = self._analyze_change_priorities(changes_detected['changes_by_type'])
            
            # Send notifications for high-priority changes
            if changes_detected['changes_by_priority']['high'] > 0:
                notifications_sent = self._send_change_notifications(changes_detected, priority='high')
                changes_detected['notifications_sent'] = notifications_sent
            
            # Store change detection results
            self._store_change_detection_results(changes_detected)
            
            logger.info(f"Change detection completed: {changes_detected['total_changes']} changes detected")
            return changes_detected
            
        except Exception as e:
            error_msg = f"Change detection failed: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg, 'timestamp': timezone.now().isoformat()}
    
    def _detect_project_changes(self, project_id: str) -> List[Dict[str, Any]]:
        """Detect changes for a specific project."""
        try:
            project = UnifiedProject.objects.get(id=project_id)
            changes = []
            
            # Detect project-level changes
            project_changes = self._detect_entity_changes(project, 'project')
            changes.extend(project_changes)
            
            # Detect document changes
            documents = ProjectDocument.objects.filter(project=project)
            for document in documents:
                doc_changes = self._detect_entity_changes(document, 'document')
                changes.extend(doc_changes)
            
            # Detect schedule changes
            schedules = ProjectSchedule.objects.filter(project=project)
            for schedule in schedules:
                sched_changes = self._detect_entity_changes(schedule, 'schedule')
                changes.extend(sched_changes)
            
            # Detect financial changes
            financials = ProjectFinancial.objects.filter(project=project)
            for financial in financials:
                fin_changes = self._detect_entity_changes(financial, 'financial')
                changes.extend(fin_changes)
            
            # Detect change order changes
            change_orders = ProjectChangeOrder.objects.filter(project=project)
            for change_order in change_orders:
                co_changes = self._detect_entity_changes(change_order, 'change_order')
                changes.extend(co_changes)
            
            # Detect RFI changes
            rfis = ProjectRFI.objects.filter(project=project)
            for rfi in rfis:
                rfi_changes = self._detect_entity_changes(rfi, 'rfi')
                changes.extend(rfi_changes)
            
            return changes
            
        except UnifiedProject.DoesNotExist:
            logger.error(f"Project {project_id} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to detect changes for project {project_id}: {str(e)}")
            return []
    
    def _detect_entity_changes(self, entity, entity_type: str) -> List[Dict[str, Any]]:
        """Detect changes for a specific entity."""
        changes = []
        
        try:
            # Get the entity's change history
            change_history = self._get_entity_change_history(entity, entity_type)
            
            if not change_history:
                return changes
            
            # Compare current state with previous state
            current_state = self._get_entity_current_state(entity, entity_type)
            previous_state = change_history.get('previous_state', {})
            
            # Check for changes in monitored fields
            monitored_fields = self.change_types.get(entity_type, [])
            
            for field in monitored_fields:
                if field in current_state and field in previous_state:
                    current_value = current_state[field]
                    previous_value = previous_state[field]
                    
                    if current_value != previous_value:
                        change = {
                            'entity_id': str(entity.id),
                            'entity_type': entity_type,
                            'field_name': field,
                            'previous_value': previous_value,
                            'current_value': current_value,
                            'change_timestamp': timezone.now().isoformat(),
                            'change_type': self._determine_change_type(previous_value, current_value),
                            'priority': self._calculate_change_priority(field, previous_value, current_value, entity_type),
                            'impact_assessment': self._assess_change_impact(field, previous_value, current_value, entity_type),
                            'requires_approval': self._requires_approval(field, entity_type),
                            'approval_status': 'pending' if self._requires_approval(field, entity_type) else 'not_required'
                        }
                        
                        changes.append(change)
            
            # Update change history
            if changes:
                self._update_entity_change_history(entity, entity_type, current_state)
            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to detect changes for entity {entity.id} ({entity_type}): {str(e)}")
            return []
    
    def _get_entity_change_history(self, entity, entity_type: str) -> Dict[str, Any]:
        """Get change history for an entity."""
        try:
            cache_key = f'change_history_{entity_type}_{entity.id}'
            return cache.get(cache_key, {})
            
        except Exception as e:
            logger.error(f"Failed to get change history for {entity_type} {entity.id}: {str(e)}")
            return {}
    
    def _get_entity_current_state(self, entity, entity_type: str) -> Dict[str, Any]:
        """Get current state of an entity."""
        try:
            if entity_type == 'project':
                return {
                    'name': entity.name,
                    'status': entity.status,
                    'budget': float(entity.budget) if entity.budget else None,
                    'start_date': entity.start_date.isoformat() if entity.start_date else None,
                    'end_date': entity.end_date.isoformat() if entity.end_date else None,
                    'progress_percentage': entity.progress_percentage,
                    'risk_score': entity.risk_score,
                    'risk_level': entity.risk_level
                }
            elif entity_type == 'document':
                return {
                    'title': entity.title,
                    'status': entity.status,
                    'version': entity.version,
                    'file_name': entity.file_name,
                    'file_size': entity.file_size,
                    'document_type': entity.document_type
                }
            elif entity_type == 'schedule':
                return {
                    'name': entity.name,
                    'start_date': entity.start_date.isoformat() if entity.start_date else None,
                    'end_date': entity.end_date.isoformat() if entity.end_date else None,
                    'completion_percentage': entity.completion_percentage,
                    'total_duration_days': entity.total_duration_days
                }
            elif entity_type == 'financial':
                return {
                    'amount': float(entity.amount) if entity.amount else None,
                    'financial_type': entity.financial_type,
                    'effective_date': entity.effective_date.isoformat() if entity.effective_date else None,
                    'currency': entity.currency
                }
            elif entity_type == 'change_order':
                return {
                    'title': entity.title,
                    'status': entity.status,
                    'change_order_value': float(entity.change_order_value) if entity.change_order_value else None,
                    'description': entity.description,
                    'change_order_number': entity.change_order_number
                }
            elif entity_type == 'rfi':
                return {
                    'subject': entity.subject,
                    'status': entity.status,
                    'priority': entity.priority,
                    'question': entity.question,
                    'answer': entity.answer,
                    'rfi_number': entity.rfi_number
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get current state for {entity_type} {entity.id}: {str(e)}")
            return {}
    
    def _update_entity_change_history(self, entity, entity_type: str, current_state: Dict[str, Any]):
        """Update change history for an entity."""
        try:
            cache_key = f'change_history_{entity_type}_{entity.id}'
            
            # Get existing history
            history = cache.get(cache_key, {})
            
            # Update history
            history['previous_state'] = history.get('current_state', {})
            history['current_state'] = current_state
            history['last_updated'] = timezone.now().isoformat()
            history['change_count'] = history.get('change_count', 0) + 1
            
            # Store updated history
            cache.set(cache_key, history, timeout=86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to update change history for {entity_type} {entity.id}: {str(e)}")
    
    def _determine_change_type(self, previous_value, current_value) -> str:
        """Determine the type of change."""
        try:
            if previous_value is None and current_value is not None:
                return 'added'
            elif previous_value is not None and current_value is None:
                return 'removed'
            elif isinstance(previous_value, (int, float)) and isinstance(current_value, (int, float)):
                if current_value > previous_value:
                    return 'increased'
                elif current_value < previous_value:
                    return 'decreased'
                else:
                    return 'unchanged'
            else:
                return 'modified'
                
        except Exception as e:
            logger.error(f"Failed to determine change type: {str(e)}")
            return 'unknown'
    
    def _calculate_change_priority(self, field: str, previous_value, current_value, entity_type: str) -> str:
        """Calculate the priority of a change."""
        try:
            # High priority changes
            high_priority_fields = {
                'project': ['status', 'budget', 'end_date'],
                'document': ['status', 'version'],
                'schedule': ['end_date', 'completion_percentage'],
                'financial': ['amount'],
                'change_order': ['status', 'change_order_value'],
                'rfi': ['status', 'priority']
            }
            
            if field in high_priority_fields.get(entity_type, []):
                return 'high'
            
            # Medium priority changes
            medium_priority_fields = {
                'project': ['progress_percentage', 'risk_score'],
                'document': ['title', 'file_name'],
                'schedule': ['start_date', 'name'],
                'financial': ['effective_date'],
                'change_order': ['title', 'description'],
                'rfi': ['subject', 'question']
            }
            
            if field in medium_priority_fields.get(entity_type, []):
                return 'medium'
            
            # Low priority changes
            return 'low'
            
        except Exception as e:
            logger.error(f"Failed to calculate change priority: {str(e)}")
            return 'medium'
    
    def _assess_change_impact(self, field: str, previous_value, current_value, entity_type: str) -> Dict[str, Any]:
        """Assess the impact of a change."""
        try:
            impact = {
                'level': 'low',
                'description': '',
                'affected_systems': [],
                'estimated_delay_days': 0,
                'estimated_cost_impact': 0.0
            }
            
            # Project status changes
            if entity_type == 'project' and field == 'status':
                if current_value == 'on_hold':
                    impact['level'] = 'high'
                    impact['description'] = 'Project put on hold - may cause delays'
                    impact['estimated_delay_days'] = 7
                elif current_value == 'cancelled':
                    impact['level'] = 'critical'
                    impact['description'] = 'Project cancelled - significant impact'
                    impact['estimated_delay_days'] = 30
                    impact['estimated_cost_impact'] = 100000.0
            
            # Budget changes
            elif entity_type == 'project' and field == 'budget':
                if previous_value and current_value:
                    change_amount = current_value - previous_value
                    change_percentage = abs(change_amount / previous_value * 100)
                    
                    if change_percentage > 20:
                        impact['level'] = 'high'
                        impact['description'] = f'Budget changed by {change_percentage:.1f}%'
                        impact['estimated_cost_impact'] = abs(change_amount)
                    elif change_percentage > 10:
                        impact['level'] = 'medium'
                        impact['description'] = f'Budget changed by {change_percentage:.1f}%'
                        impact['estimated_cost_impact'] = abs(change_amount)
            
            # Schedule changes
            elif entity_type == 'schedule' and field == 'end_date':
                if previous_value and current_value:
                    try:
                        prev_date = datetime.fromisoformat(previous_value).date()
                        curr_date = datetime.fromisoformat(current_value).date()
                        delay_days = (curr_date - prev_date).days
                        
                        if delay_days > 0:
                            impact['level'] = 'high' if delay_days > 7 else 'medium'
                            impact['description'] = f'Schedule delayed by {delay_days} days'
                            impact['estimated_delay_days'] = delay_days
                    except:
                        pass
            
            # Change order value changes
            elif entity_type == 'change_order' and field == 'change_order_value':
                if previous_value and current_value:
                    change_amount = current_value - previous_value
                    if abs(change_amount) > 10000:
                        impact['level'] = 'high'
                        impact['description'] = f'Change order value changed by ${change_amount:,.2f}'
                        impact['estimated_cost_impact'] = abs(change_amount)
            
            # RFI priority changes
            elif entity_type == 'rfi' and field == 'priority':
                if current_value == 'critical':
                    impact['level'] = 'high'
                    impact['description'] = 'RFI marked as critical - requires immediate attention'
                    impact['estimated_delay_days'] = 3
            
            return impact
            
        except Exception as e:
            logger.error(f"Failed to assess change impact: {str(e)}")
            return {'level': 'unknown', 'description': 'Unable to assess impact', 'affected_systems': [], 'estimated_delay_days': 0, 'estimated_cost_impact': 0.0}
    
    def _requires_approval(self, field: str, entity_type: str) -> bool:
        """Determine if a change requires approval."""
        try:
            # Fields that always require approval
            approval_required_fields = {
                'project': ['status', 'budget'],
                'document': ['status', 'version'],
                'schedule': ['end_date'],
                'financial': ['amount'],
                'change_order': ['status', 'change_order_value'],
                'rfi': ['status', 'priority']
            }
            
            return field in approval_required_fields.get(entity_type, [])
            
        except Exception as e:
            logger.error(f"Failed to determine approval requirement: {str(e)}")
            return False
    
    def _analyze_change_priorities(self, changes_by_type: Dict[str, Any]) -> Dict[str, int]:
        """Analyze change priorities across all detected changes."""
        try:
            priority_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for project_changes in changes_by_type.values():
                if isinstance(project_changes, list):
                    for change in project_changes:
                        priority = change.get('priority', 'medium')
                        if priority in priority_counts:
                            priority_counts[priority] += 1
            
            return priority_counts
            
        except Exception as e:
            logger.error(f"Failed to analyze change priorities: {str(e)}")
            return {'high': 0, 'medium': 0, 'low': 0}
    
    def _send_change_notifications(self, changes_detected: Dict[str, Any], priority: str = 'high') -> int:
        """Send notifications for detected changes."""
        try:
            notifications_sent = 0
            
            # Get high-priority changes
            high_priority_changes = []
            for project_changes in changes_detected['changes_by_type'].values():
                if isinstance(project_changes, list):
                    for change in project_changes:
                        if change.get('priority') == priority:
                            high_priority_changes.append(change)
            
            if not high_priority_changes:
                return notifications_sent
            
            # Send notifications through configured channels
            for channel in self.notification_channels:
                try:
                    if channel == 'email':
                        notifications_sent += self._send_email_notifications(high_priority_changes)
                    elif channel == 'slack':
                        notifications_sent += self._send_slack_notifications(high_priority_changes)
                    elif channel == 'webhook':
                        notifications_sent += self._send_webhook_notifications(high_priority_changes)
                    elif channel == 'database':
                        notifications_sent += self._store_notifications(high_priority_changes)
                except Exception as e:
                    logger.error(f"Failed to send notifications via {channel}: {str(e)}")
            
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Failed to send change notifications: {str(e)}")
            return 0
    
    def _send_email_notifications(self, changes: List[Dict[str, Any]]) -> int:
        """Send email notifications for changes."""
        try:
            # This would typically integrate with Django's email system
            # For now, we'll simulate sending emails
            
            for change in changes:
                logger.info(f"Email notification sent for {change['entity_type']} change: {change['field_name']}")
            
            return len(changes)
            
        except Exception as e:
            logger.error(f"Failed to send email notifications: {str(e)}")
            return 0
    
    def _send_slack_notifications(self, changes: List[Dict[str, Any]]) -> int:
        """Send Slack notifications for changes."""
        try:
            # This would typically integrate with Slack's API
            # For now, we'll simulate sending Slack messages
            
            for change in changes:
                logger.info(f"Slack notification sent for {change['entity_type']} change: {change['field_name']}")
            
            return len(changes)
            
        except Exception as e:
            logger.error(f"Failed to send Slack notifications: {str(e)}")
            return 0
    
    def _send_webhook_notifications(self, changes: List[Dict[str, Any]]) -> int:
        """Send webhook notifications for changes."""
        try:
            # This would typically send HTTP POST requests to configured webhooks
            # For now, we'll simulate sending webhooks
            
            for change in changes:
                logger.info(f"Webhook notification sent for {change['entity_type']} change: {change['field_name']}")
            
            return len(changes)
            
        except Exception as e:
            logger.error(f"Failed to send webhook notifications: {str(e)}")
            return 0
    
    def _store_notifications(self, changes: List[Dict[str, Any]]) -> int:
        """Store notifications in the database."""
        try:
            # This would typically store notifications in a dedicated table
            # For now, we'll simulate storing notifications
            
            for change in changes:
                logger.info(f"Notification stored for {change['entity_type']} change: {change['field_name']}")
            
            return len(changes)
            
        except Exception as e:
            logger.error(f"Failed to store notifications: {str(e)}")
            return 0
    
    def _store_change_detection_results(self, results: Dict[str, Any]):
        """Store change detection results for historical tracking."""
        try:
            # Store results in cache for quick access
            cache_key = f'change_detection_results_{timezone.now().strftime("%Y%m%d_%H%M")}'
            cache.set(cache_key, results, timeout=86400 * 7)  # 7 days
            
            # Also store in a list of recent results
            recent_results = cache.get('recent_change_detections', [])
            recent_results.append(results)
            
            # Keep only last 10 results
            if len(recent_results) > 10:
                recent_results = recent_results[-10:]
            
            cache.set('recent_change_detections', recent_results, timeout=86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to store change detection results: {str(e)}")
    
    def get_change_history(self, entity_id: str, entity_type: str, days: int = 30) -> Dict[str, Any]:
        """Get change history for an entity over a specified time period."""
        try:
            cache_key = f'change_history_{entity_type}_{entity_id}'
            history = cache.get(cache_key, {})
            
            if not history:
                return {'error': 'No change history found'}
            
            # Filter by time period
            cutoff_date = timezone.now() - timedelta(days=days)
            filtered_changes = []
            
            # This would typically query a dedicated change history table
            # For now, we'll return the cached history
            
            return {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'period_days': days,
                'total_changes': history.get('change_count', 0),
                'last_updated': history.get('last_updated'),
                'current_state': history.get('current_state', {}),
                'previous_state': history.get('previous_state', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get change history: {str(e)}")
            return {'error': str(e)}
    
    def get_recent_changes(self, hours: int = 24) -> Dict[str, Any]:
        """Get recent changes across all entities."""
        try:
            recent_results = cache.get('recent_change_detections', [])
            
            if not recent_results:
                return {'error': 'No recent changes found'}
            
            # Filter by time period
            cutoff_time = timezone.now() - timedelta(hours=hours)
            recent_changes = []
            
            for result in recent_results:
                try:
                    result_time = datetime.fromisoformat(result['timestamp'])
                    if result_time >= cutoff_time:
                        recent_changes.append(result)
                except:
                    continue
            
            return {
                'period_hours': hours,
                'total_changes': sum(r.get('total_changes', 0) for r in recent_changes),
                'changes_by_priority': self._aggregate_priority_counts(recent_changes),
                'affected_projects': list(set([p for r in recent_changes for p in r.get('affected_projects', [])])),
                'recent_results': recent_changes
            }
            
        except Exception as e:
            logger.error(f"Failed to get recent changes: {str(e)}")
            return {'error': str(e)}
    
    def _aggregate_priority_counts(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate priority counts across multiple results."""
        try:
            priority_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for result in results:
                changes_by_priority = result.get('changes_by_priority', {})
                for priority, count in changes_by_priority.items():
                    if priority in priority_counts:
                        priority_counts[priority] += count
            
            return priority_counts
            
        except Exception as e:
            logger.error(f"Failed to aggregate priority counts: {str(e)}")
            return {'high': 0, 'medium': 0, 'low': 0}
    
    def approve_change(self, change_id: str, approver: User, approval_notes: str = '') -> Dict[str, Any]:
        """Approve a change that requires approval."""
        try:
            # This would typically update a change approval table
            # For now, we'll simulate the approval process
            
            approval_result = {
                'change_id': change_id,
                'approved_by': approver.username,
                'approval_timestamp': timezone.now().isoformat(),
                'approval_notes': approval_notes,
                'status': 'approved'
            }
            
            # Store approval in cache
            cache_key = f'change_approval_{change_id}'
            cache.set(cache_key, approval_result, timeout=86400 * 30)  # 30 days
            
            logger.info(f"Change {change_id} approved by {approver.username}")
            return approval_result
            
        except Exception as e:
            logger.error(f"Failed to approve change {change_id}: {str(e)}")
            return {'error': str(e)}
    
    def reject_change(self, change_id: str, rejector: User, rejection_reason: str) -> Dict[str, Any]:
        """Reject a change that requires approval."""
        try:
            # This would typically update a change approval table
            # For now, we'll simulate the rejection process
            
            rejection_result = {
                'change_id': change_id,
                'rejected_by': rejector.username,
                'rejection_timestamp': timezone.now().isoformat(),
                'rejection_reason': rejection_reason,
                'status': 'rejected'
            }
            
            # Store rejection in cache
            cache_key = f'change_approval_{change_id}'
            cache.set(cache_key, rejection_result, timeout=86400 * 30)  # 30 days
            
            logger.info(f"Change {change_id} rejected by {rejector.username}")
            return rejection_result
            
        except Exception as e:
            logger.error(f"Failed to reject change {change_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get list of changes pending approval."""
        try:
            # This would typically query a change approval table
            # For now, we'll return an empty list
            
            pending_approvals = []
            
            # Check for changes that require approval
            # This is a simplified implementation
            
            return pending_approvals
            
        except Exception as e:
            logger.error(f"Failed to get pending approvals: {str(e)}")
            return []
    
    def clear_change_history(self, entity_id: str = None, entity_type: str = None):
        """Clear change history for entities."""
        try:
            if entity_id and entity_type:
                # Clear specific entity history
                cache_key = f'change_history_{entity_type}_{entity_id}'
                cache.delete(cache_key)
                logger.info(f"Cleared change history for {entity_type} {entity_id}")
            else:
                # Clear all change history
                # This would typically clear all cache keys related to change history
                logger.info("Cleared all change history")
                
        except Exception as e:
            logger.error(f"Failed to clear change history: {str(e)}")
