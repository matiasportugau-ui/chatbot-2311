#!/usr/bin/env python3
"""
Storage Manager
Handles storage operations for backups (local, cloud, etc.)
"""
import os
import json
import gzip
import logging
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StorageUsage:
    """Storage usage information"""
    total_size: int
    backup_count: int
    available_space: Optional[int] = None
    used_percentage: Optional[float] = None


class StorageManager:
    """Manages backup storage"""
    
    def __init__(self, config: Dict):
        """
        Initialize StorageManager
        
        Args:
            config: Storage configuration
        """
        self.config = config
        self.storage_type = config.get("primary", "local")
        self.local_path = config.get("local", {}).get("path", "./backups")
        
        # Create local backup directory if it doesn't exist
        if self.storage_type == "local":
            os.makedirs(self.local_path, exist_ok=True)
    
    def save_backup(self, backup_data: Dict, backup_id: str) -> str:
        """
        Save backup data to storage
        
        Args:
            backup_data: Backup data dictionary
            backup_id: Unique backup identifier
        
        Returns:
            Path where backup was saved
        """
        if self.storage_type == "local":
            return self._save_local(backup_data, backup_id)
        elif self.storage_type == "s3":
            return self._save_s3(backup_data, backup_id)
        elif self.storage_type == "gcs":
            return self._save_gcs(backup_data, backup_id)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _save_local(self, backup_data: Dict, backup_id: str) -> str:
        """Save backup to local filesystem"""
        # Save as JSON
        backup_file = os.path.join(self.local_path, f"{backup_id}.json")
        
        # Compress if enabled
        compression = self.config.get("backup", {}).get("compression", {})
        if compression.get("enabled", True):
            backup_file = backup_file.replace(".json", ".json.gz")
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
        else:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
        
        logger.info(f"Backup saved to: {backup_file}")
        return backup_file
    
    def _save_s3(self, backup_data: Dict, backup_id: str) -> str:
        """Save backup to S3 (placeholder - requires boto3)"""
        # TODO: Implement S3 storage
        logger.warning("S3 storage not yet implemented, saving locally")
        return self._save_local(backup_data, backup_id)
    
    def _save_gcs(self, backup_data: Dict, backup_id: str) -> str:
        """Save backup to Google Cloud Storage (placeholder)"""
        # TODO: Implement GCS storage
        logger.warning("GCS storage not yet implemented, saving locally")
        return self._save_local(backup_data, backup_id)
    
    def load_backup(self, backup_id: str) -> Optional[Dict]:
        """
        Load backup data from storage
        
        Args:
            backup_id: Unique backup identifier
        
        Returns:
            Backup data dictionary or None if not found
        """
        if self.storage_type == "local":
            return self._load_local(backup_id)
        elif self.storage_type == "s3":
            return self._load_s3(backup_id)
        elif self.storage_type == "gcs":
            return self._load_gcs(backup_id)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _load_local(self, backup_id: str) -> Optional[Dict]:
        """Load backup from local filesystem"""
        # Try compressed first
        backup_file = os.path.join(self.local_path, f"{backup_id}.json.gz")
        if os.path.exists(backup_file):
            with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                return json.load(f)
        
        # Try uncompressed
        backup_file = os.path.join(self.local_path, f"{backup_id}.json")
        if os.path.exists(backup_file):
            with open(backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def _load_s3(self, backup_id: str) -> Optional[Dict]:
        """Load backup from S3"""
        # TODO: Implement S3 loading
        logger.warning("S3 loading not yet implemented")
        return None
    
    def _load_gcs(self, backup_id: str) -> Optional[Dict]:
        """Load backup from GCS"""
        # TODO: Implement GCS loading
        logger.warning("GCS loading not yet implemented")
        return None
    
    def list_backups(self, location: Optional[str] = None) -> List[str]:
        """
        List all backups in storage
        
        Args:
            location: Optional location override
        
        Returns:
            List of backup IDs
        """
        if location:
            storage_path = location
        elif self.storage_type == "local":
            storage_path = self.local_path
        else:
            return []
        
        backups = []
        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                if filename.endswith('.json') or filename.endswith('.json.gz'):
                    backup_id = filename.replace('.json.gz', '').replace('.json', '')
                    backups.append(backup_id)
        
        return backups
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete backup from storage
        
        Args:
            backup_id: Unique backup identifier
        
        Returns:
            True if deleted successfully
        """
        if self.storage_type == "local":
            # Try compressed
            backup_file = os.path.join(self.local_path, f"{backup_id}.json.gz")
            if os.path.exists(backup_file):
                os.remove(backup_file)
                return True
            
            # Try uncompressed
            backup_file = os.path.join(self.local_path, f"{backup_id}.json")
            if os.path.exists(backup_file):
                os.remove(backup_file)
                return True
        
        return False
    
    def get_storage_usage(self) -> StorageUsage:
        """Get storage usage information"""
        if self.storage_type != "local":
            return StorageUsage(total_size=0, backup_count=0)
        
        total_size = 0
        backup_count = 0
        
        if os.path.exists(self.local_path):
            for filename in os.listdir(self.local_path):
                if filename.endswith('.json') or filename.endswith('.json.gz'):
                    file_path = os.path.join(self.local_path, filename)
                    total_size += os.path.getsize(file_path)
                    backup_count += 1
        
        return StorageUsage(
            total_size=total_size,
            backup_count=backup_count
        )
    
    def compress_backup(self, backup_id: str) -> str:
        """
        Compress a backup file
        
        Args:
            backup_id: Unique backup identifier
        
        Returns:
            Path to compressed backup
        """
        backup_file = os.path.join(self.local_path, f"{backup_id}.json")
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup not found: {backup_id}")
        
        compressed_file = f"{backup_file}.gz"
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original
        os.remove(backup_file)
        
        return compressed_file
    
    def encrypt_backup(self, backup_id: str, key: str) -> str:
        """
        Encrypt a backup file (placeholder)
        
        Args:
            backup_id: Unique backup identifier
            key: Encryption key
        
        Returns:
            Path to encrypted backup
        """
        # TODO: Implement encryption
        logger.warning("Encryption not yet implemented")
        return ""


