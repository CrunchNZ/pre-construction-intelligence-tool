"""
Data Backup and Recovery Service

This service provides automated data backup and recovery capabilities for external API data
and integrated system data, ensuring data integrity and business continuity.

Features:
- Automated data backup scheduling
- Incremental and full backup strategies
- Data recovery and restoration
- Backup verification and integrity checks
- Backup retention and cleanup
- Disaster recovery planning

Author: Pre-Construction Intelligence Team
Date: 2025
"""

import logging
import json
import os
import shutil
import zipfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import hashlib

logger = logging.getLogger(__name__)


class DataBackupRecovery:
    """Service for data backup and recovery operations."""
    
    def __init__(self):
        """Initialize the backup and recovery service."""
        self.backup_config = {}
        self.backup_history = []
        self.recovery_history = []
        
        # Default backup configuration
        self.default_config = {
            'backup_directory': getattr(settings, 'BACKUP_DIR', '/tmp/backups'),
            'retention_days': 30,
            'max_backup_size_mb': 1000,
            'compression_enabled': True,
            'encryption_enabled': False,
            'verification_enabled': True
        }
        
        # Initialize backup directory
        self._initialize_backup_directory()
    
    def configure_backup(self, system_name: str, config: Dict[str, Any]) -> bool:
        """
        Configure backup settings for a specific system.
        
        Args:
            system_name: Name of the system to configure
            config: Backup configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate configuration
            if not self._validate_backup_config(config):
                logger.error(f"Invalid backup configuration for {system_name}")
                return False
            
            # Merge with default configuration
            merged_config = self.default_config.copy()
            merged_config.update(config)
            
            self.backup_config[system_name] = merged_config
            
            # Create system-specific backup directory
            system_backup_dir = os.path.join(merged_config['backup_directory'], system_name)
            os.makedirs(system_backup_dir, exist_ok=True)
            
            logger.info(f"Backup configuration set for system: {system_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring backup for {system_name}: {e}")
            return False
    
    def create_backup(self, system_name: str, data: Any, 
                      backup_type: str = 'incremental') -> Dict[str, Any]:
        """
        Create a backup of system data.
        
        Args:
            system_name: Name of the system to backup
            data: Data to backup
            backup_type: Type of backup ('full' or 'incremental')
            
        Returns:
            Backup creation results
        """
        try:
            if system_name not in self.backup_config:
                raise ValueError(f"No backup configuration found for system: {system_name}")
            
            config = self.backup_config[system_name]
            timestamp = timezone.now()
            backup_id = f"{system_name}_{backup_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup record
            backup_record = {
                'backup_id': backup_id,
                'system_name': system_name,
                'backup_type': backup_type,
                'timestamp': timestamp,
                'status': 'in_progress',
                'size_bytes': 0,
                'checksum': None,
                'file_path': None
            }
            
            # Create backup file
            backup_file_path = self._create_backup_file(system_name, backup_id, data, config)
            
            # Calculate file size and checksum
            file_size = os.path.getsize(backup_file_path)
            checksum = self._calculate_file_checksum(backup_file_path)
            
            # Update backup record
            backup_record.update({
                'status': 'completed',
                'size_bytes': file_size,
                'checksum': checksum,
                'file_path': backup_file_path
            })
            
            # Add to backup history
            self.backup_history.append(backup_record)
            
            # Verify backup if enabled
            if config.get('verification_enabled', True):
                verification_result = self._verify_backup(backup_file_path, checksum)
                backup_record['verification'] = verification_result
            
            # Cleanup old backups
            self._cleanup_old_backups(system_name, config)
            
            logger.info(f"Backup created successfully: {backup_id}")
            return backup_record
            
        except Exception as e:
            logger.error(f"Error creating backup for {system_name}: {e}")
            return {
                'error': str(e),
                'status': 'failed',
                'system_name': system_name,
                'timestamp': timezone.now().isoformat()
            }
    
    def restore_backup(self, backup_id: str, target_system: str, 
                       restore_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Restore data from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            target_system: Target system for restoration
            restore_options: Optional restoration options
            
        Returns:
            Restoration results
        """
        try:
            # Find backup record
            backup_record = self._find_backup_record(backup_id)
            if not backup_record:
                raise ValueError(f"Backup not found: {backup_id}")
            
            if backup_record['status'] != 'completed':
                raise ValueError(f"Backup {backup_id} is not in completed status")
            
            # Create recovery record
            recovery_record = {
                'recovery_id': f"recovery_{int(timezone.now().timestamp())}",
                'backup_id': backup_id,
                'target_system': target_system,
                'timestamp': timezone.now(),
                'status': 'in_progress',
                'restore_options': restore_options or {}
            }
            
            # Verify backup integrity before restoration
            if not self._verify_backup(backup_record['file_path'], backup_record['checksum']):
                raise ValueError(f"Backup integrity check failed for {backup_id}")
            
            # Perform restoration
            restored_data = self._perform_restoration(backup_record, target_system, restore_options)
            
            # Update recovery record
            recovery_record.update({
                'status': 'completed',
                'restored_data_size': len(str(restored_data)),
                'restored_data': restored_data
            })
            
            # Add to recovery history
            self.recovery_history.append(recovery_record)
            
            logger.info(f"Backup restored successfully: {backup_id}")
            return recovery_record
            
        except Exception as e:
            logger.error(f"Error restoring backup {backup_id}: {e}")
            return {
                'error': str(e),
                'status': 'failed',
                'backup_id': backup_id,
                'timestamp': timezone.now().isoformat()
            }
    
    def list_backups(self, system_name: Optional[str] = None, 
                     backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            system_name: Optional filter by system name
            backup_type: Optional filter by backup type
            
        Returns:
            List of backup records
        """
        backups = self.backup_history
        
        if system_name:
            backups = [b for b in backups if b['system_name'] == system_name]
        
        if backup_type:
            backups = [b for b in backups if b['backup_type'] == backup_type]
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific backup.
        
        Args:
            backup_id: ID of the backup
            
        Returns:
            Backup information or None if not found
        """
        return self._find_backup_record(backup_id)
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a specific backup.
        
        Args:
            backup_id: ID of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_record = self._find_backup_record(backup_id)
            if not backup_record:
                logger.warning(f"Backup not found for deletion: {backup_id}")
                return False
            
            # Remove backup file
            if backup_record.get('file_path') and os.path.exists(backup_record['file_path']):
                os.remove(backup_record['file_path'])
                logger.info(f"Backup file deleted: {backup_record['file_path']}")
            
            # Remove from history
            self.backup_history = [b for b in self.backup_history if b['backup_id'] != backup_id]
            
            logger.info(f"Backup deleted successfully: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting backup {backup_id}: {e}")
            return False
    
    def _initialize_backup_directory(self):
        """Initialize the backup directory structure."""
        try:
            backup_dir = self.default_config['backup_directory']
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create subdirectories for different backup types
            for backup_type in ['full', 'incremental']:
                type_dir = os.path.join(backup_dir, backup_type)
                os.makedirs(type_dir, exist_ok=True)
            
            logger.info(f"Backup directory initialized: {backup_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing backup directory: {e}")
    
    def _validate_backup_config(self, config: Dict[str, Any]) -> bool:
        """Validate backup configuration."""
        required_fields = ['backup_directory']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field '{field}' in backup configuration")
                return False
        
        # Validate retention days
        if 'retention_days' in config:
            retention = config['retention_days']
            if not isinstance(retention, int) or retention < 1:
                logger.error("Retention days must be a positive integer")
                return False
        
        return True
    
    def _create_backup_file(self, system_name: str, backup_id: str, 
                            data: Any, config: Dict[str, Any]) -> str:
        """Create the actual backup file."""
        # Create system backup directory
        system_backup_dir = os.path.join(config['backup_directory'], system_name)
        os.makedirs(system_backup_dir, exist_ok=True)
        
        # Create backup file path
        backup_file_path = os.path.join(system_backup_dir, f"{backup_id}.json")
        
        # Serialize data to JSON
        backup_data = {
            'metadata': {
                'backup_id': backup_id,
                'system_name': system_name,
                'timestamp': timezone.now().isoformat(),
                'version': '1.0'
            },
            'data': data
        }
        
        # Write backup file
        with open(backup_file_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        # Compress if enabled
        if config.get('compression_enabled', True):
            compressed_path = self._compress_backup_file(backup_file_path)
            # Remove uncompressed file
            os.remove(backup_file_path)
            backup_file_path = compressed_path
        
        return backup_file_path
    
    def _compress_backup_file(self, file_path: str) -> str:
        """Compress a backup file."""
        compressed_path = f"{file_path}.zip"
        
        with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
        
        return compressed_path
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _verify_backup(self, file_path: str, expected_checksum: str) -> Dict[str, Any]:
        """Verify backup file integrity."""
        try:
            if not os.path.exists(file_path):
                return {
                    'verified': False,
                    'error': 'Backup file not found'
                }
            
            actual_checksum = self._calculate_file_checksum(file_path)
            verified = actual_checksum == expected_checksum
            
            return {
                'verified': verified,
                'expected_checksum': expected_checksum,
                'actual_checksum': actual_checksum,
                'verification_timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }
    
    def _cleanup_old_backups(self, system_name: str, config: Dict[str, Any]):
        """Clean up old backups based on retention policy."""
        try:
            retention_days = config.get('retention_days', 30)
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            
            # Find old backups
            old_backups = [
                b for b in self.backup_history
                if (b['system_name'] == system_name and 
                    b['timestamp'] < cutoff_date and
                    b['status'] == 'completed')
            ]
            
            # Delete old backups
            for backup in old_backups:
                self.delete_backup(backup['backup_id'])
            
            if old_backups:
                logger.info(f"Cleaned up {len(old_backups)} old backups for {system_name}")
                
        except Exception as e:
            logger.error(f"Error cleaning up old backups for {system_name}: {e}")
    
    def _find_backup_record(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Find a backup record by ID."""
        for backup in self.backup_history:
            if backup['backup_id'] == backup_id:
                return backup
        return None
    
    def _perform_restoration(self, backup_record: Dict[str, Any], 
                            target_system: str, 
                            restore_options: Dict[str, Any]) -> Any:
        """Perform the actual data restoration."""
        backup_file_path = backup_record['file_path']
        
        # Decompress if needed
        if backup_file_path.endswith('.zip'):
            backup_file_path = self._decompress_backup_file(backup_file_path)
        
        # Read backup data
        with open(backup_file_path, 'r') as f:
            backup_data = json.load(f)
        
        # Extract data
        restored_data = backup_data.get('data', {})
        
        # Clean up temporary decompressed file
        if backup_file_path != backup_record['file_path']:
            os.remove(backup_file_path)
        
        return restored_data
    
    def _decompress_backup_file(self, compressed_path: str) -> str:
        """Decompress a backup file."""
        extract_dir = os.path.dirname(compressed_path)
        
        with zipfile.ZipFile(compressed_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        # Return path to extracted file
        extracted_files = [f for f in os.listdir(extract_dir) if f.endswith('.json')]
        if extracted_files:
            return os.path.join(extract_dir, extracted_files[0])
        
        raise ValueError("No JSON file found in compressed backup")
