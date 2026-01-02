#!/usr/bin/env python3
"""
Incremental Backup Support
Tracks changes and creates incremental backups
"""
import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_service import BackupService
from storage_manager import StorageManager

logger = logging.getLogger(__name__)


@dataclass
class ChangeRecord:
    """Record of a change"""
    path: str
    type: str  # file or collection
    action: str  # created, modified, deleted
    timestamp: str
    checksum: Optional[str] = None
    size: Optional[int] = None


@dataclass
class IncrementalBackup:
    """Incremental backup information"""
    backup_id: str
    base_backup_id: str
    timestamp: str
    changes: List[ChangeRecord]
    total_changes: int


class ChangeTracker:
    """Tracks changes for incremental backups"""
    
    def __init__(self, state_file: str = "./backup_change_state.json"):
        """
        Initialize ChangeTracker
        
        Args:
            state_file: Path to state file
        """
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load change tracking state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading state file: {e}")
        
        return {
            "last_full_backup": None,
            "file_checksums": {},
            "collection_checksums": {},
            "last_update": None
        }
    
    def _save_state(self):
        """Save change tracking state"""
        self.state["last_update"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def record_full_backup(self, backup_id: str, files: List[Dict], collections: Dict):
        """
        Record a full backup for change tracking
        
        Args:
            backup_id: Backup ID
            files: List of file information
            collections: Dictionary of collection information
        """
        self.state["last_full_backup"] = backup_id
        
        # Record file checksums
        for file_info in files:
            file_path = file_info.get("path")
            content = file_info.get("content", "")
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
            self.state["file_checksums"][file_path] = {
                "checksum": checksum,
                "size": len(content),
                "backup_id": backup_id
            }
        
        # Record collection checksums
        for collection_name, collection_data in collections.items():
            collection_json = json.dumps(collection_data, default=str, sort_keys=True)
            checksum = hashlib.sha256(collection_json.encode('utf-8')).hexdigest()
            self.state["collection_checksums"][collection_name] = {
                "checksum": checksum,
                "count": collection_data.get("count", 0),
                "backup_id": backup_id
            }
        
        self._save_state()
    
    def detect_changes(self, files: List[Dict], collections: Dict) -> List[ChangeRecord]:
        """
        Detect changes since last backup
        
        Args:
            files: Current file information
            collections: Current collection information
        
        Returns:
            List of ChangeRecord objects
        """
        changes = []
        timestamp = datetime.now().isoformat()
        
        # Track current file checksums
        current_file_checksums = {}
        for file_info in files:
            file_path = file_info.get("path")
            content = file_info.get("content", "")
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
            current_file_checksums[file_path] = checksum
        
        # Detect file changes
        tracked_files = set(self.state["file_checksums"].keys())
        current_files = set(current_file_checksums.keys())
        
        # New files
        for file_path in current_files - tracked_files:
            changes.append(ChangeRecord(
                path=file_path,
                type="file",
                action="created",
                timestamp=timestamp,
                checksum=current_file_checksums[file_path]
            ))
        
        # Modified files
        for file_path in current_files & tracked_files:
            old_checksum = self.state["file_checksums"][file_path]["checksum"]
            new_checksum = current_file_checksums[file_path]
            if old_checksum != new_checksum:
                changes.append(ChangeRecord(
                    path=file_path,
                    type="file",
                    action="modified",
                    timestamp=timestamp,
                    checksum=new_checksum
                ))
        
        # Deleted files
        for file_path in tracked_files - current_files:
            changes.append(ChangeRecord(
                path=file_path,
                type="file",
                action="deleted",
                timestamp=timestamp
            ))
        
        # Detect collection changes
        tracked_collections = set(self.state["collection_checksums"].keys())
        current_collections = set(collections.keys())
        
        for collection_name in current_collections:
            collection_data = collections[collection_name]
            collection_json = json.dumps(collection_data, default=str, sort_keys=True)
            checksum = hashlib.sha256(collection_json.encode('utf-8')).hexdigest()
            
            if collection_name not in tracked_collections:
                changes.append(ChangeRecord(
                    path=collection_name,
                    type="collection",
                    action="created",
                    timestamp=timestamp,
                    checksum=checksum
                ))
            else:
                old_checksum = self.state["collection_checksums"][collection_name]["checksum"]
                if old_checksum != checksum:
                    changes.append(ChangeRecord(
                        path=collection_name,
                        type="collection",
                        action="modified",
                        timestamp=timestamp,
                        checksum=checksum
                    ))
        
        for collection_name in tracked_collections - current_collections:
            changes.append(ChangeRecord(
                path=collection_name,
                type="collection",
                action="deleted",
                timestamp=timestamp
            ))
        
        return changes
    
    def update_state(self, backup_id: str, changes: List[ChangeRecord], files: List[Dict], collections: Dict):
        """
        Update state after incremental backup
        
        Args:
            backup_id: Incremental backup ID
            changes: List of changes
            files: Current file information
            collections: Current collection information
        """
        # Update file checksums for changed files
        file_dict = {f.get("path"): f for f in files}
        for change in changes:
            if change.type == "file":
                if change.action == "created" or change.action == "modified":
                    if change.path in file_dict:
                        file_info = file_dict[change.path]
                        content = file_info.get("content", "")
                        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
                        self.state["file_checksums"][change.path] = {
                            "checksum": checksum,
                            "size": len(content),
                            "backup_id": backup_id
                        }
                elif change.action == "deleted":
                    self.state["file_checksums"].pop(change.path, None)
        
        # Update collection checksums for changed collections
        for change in changes:
            if change.type == "collection":
                if change.action == "created" or change.action == "modified":
                    if change.path in collections:
                        collection_data = collections[change.path]
                        collection_json = json.dumps(collection_data, default=str, sort_keys=True)
                        checksum = hashlib.sha256(collection_json.encode('utf-8')).hexdigest()
                        self.state["collection_checksums"][change.path] = {
                            "checksum": checksum,
                            "count": collection_data.get("count", 0),
                            "backup_id": backup_id
                        }
                elif change.action == "deleted":
                    self.state["collection_checksums"].pop(change.path, None)
        
        self._save_state()


class IncrementalBackupService:
    """Service for creating incremental backups"""
    
    def __init__(self, backup_service: BackupService, change_tracker: ChangeTracker = None):
        """
        Initialize IncrementalBackupService
        
        Args:
            backup_service: BackupService instance
            change_tracker: ChangeTracker instance
        """
        self.backup_service = backup_service
        self.change_tracker = change_tracker or ChangeTracker()
    
    def create_incremental_backup(self) -> Dict:
        """
        Create an incremental backup
        
        Returns:
            Dictionary with backup result and changes
        """
        # Get last full backup
        last_full_backup_id = self.change_tracker.state.get("last_full_backup")
        if not last_full_backup_id:
            logger.warning("No full backup found, creating full backup instead")
            result = self.backup_service.create_full_backup()
            # Record as full backup
            if result.success:
                self._record_full_backup(result)
            return {
                "backup_result": result,
                "incremental": False,
                "message": "Created full backup (no previous backup found)"
            }
        
        # Get current state
        current_files = self._get_current_files()
        current_collections = self._get_current_collections()
        
        # Detect changes
        changes = self.change_tracker.detect_changes(current_files, current_collections)
        
        if not changes:
            logger.info("No changes detected, skipping incremental backup")
            return {
                "backup_result": None,
                "incremental": True,
                "changes": [],
                "message": "No changes detected"
            }
        
        # Create backup with only changed items
        backup_data = self._create_incremental_backup_data(changes, current_files, current_collections)
        
        # Save incremental backup
        backup_id = f"backup_inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        if self.backup_service.storage_manager:
            storage_path = self.backup_service.storage_manager.save_backup(backup_data, backup_id)
            backup_data["storage"] = {
                "location": "local",
                "path": storage_path
            }
        
        # Save metadata
        incremental_metadata = {
            "backup_id": backup_id,
            "type": "incremental",
            "base_backup_id": last_full_backup_id,
            "timestamp": timestamp,
            "changes": [asdict(c) for c in changes],
            "total_changes": len(changes)
        }
        
        metadata_path = os.path.join(
            self.backup_service.backup_metadata_dir,
            f"{backup_id}.json"
        )
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(incremental_metadata, f, indent=2, default=str)
        
        # Update change tracker
        self.change_tracker.update_state(backup_id, changes, current_files, current_collections)
        
        logger.info(f"Incremental backup created: {backup_id} with {len(changes)} changes")
        
        return {
            "backup_result": {
                "backup_id": backup_id,
                "success": True,
                "timestamp": timestamp
            },
            "incremental": True,
            "changes": [asdict(c) for c in changes],
            "total_changes": len(changes)
        }
    
    def _get_current_files(self) -> List[Dict]:
        """Get current file state"""
        # This would get current files from the filesystem
        # For now, we'll use the backup service's method
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config = self.backup_service.config
        
        files = []
        patterns = config.get("filesystem", {}).get("patterns", [])
        directories = config.get("filesystem", {}).get("directories", [])
        
        # Similar to backup_service._backup_filesystem but return file info
        import glob
        for pattern in patterns:
            if "*" in pattern:
                matches = glob.glob(os.path.join(base_dir, pattern))
                for match in matches:
                    if os.path.isfile(match):
                        rel_path = os.path.relpath(match, base_dir)
                        try:
                            with open(match, 'r', encoding='utf-8') as f:
                                content = f.read()
                            files.append({
                                "path": rel_path,
                                "content": content,
                                "size": len(content)
                            })
                        except:
                            pass
        
        return files
    
    def _get_current_collections(self) -> Dict:
        """Get current MongoDB collection state"""
        mongo_data = self.backup_service._backup_mongodb()
        collections = {}
        
        if "data" in mongo_data:
            for collection_name, collection_data in mongo_data["data"].items():
                collections[collection_name] = {
                    "count": collection_data.get("count", 0),
                    "documents": collection_data.get("documents", [])
                }
        
        return collections
    
    def _create_incremental_backup_data(self, changes: List[ChangeRecord], files: List[Dict], collections: Dict) -> Dict:
        """Create backup data with only changed items"""
        backup_data = {
            "backup_id": f"backup_inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "incremental",
            "changes": [asdict(c) for c in changes]
        }
        
        # Include only changed files
        changed_file_paths = {c.path for c in changes if c.type == "file"}
        changed_files = [f for f in files if f.get("path") in changed_file_paths]
        backup_data["filesystem"] = {
            "count": len(changed_files),
            "total_size": sum(f.get("size", 0) for f in changed_files),
            "files": changed_files
        }
        
        # Include only changed collections
        changed_collection_names = {c.path for c in changes if c.type == "collection"}
        changed_collections = {
            name: data for name, data in collections.items()
            if name in changed_collection_names
        }
        backup_data["mongodb"] = {
            "collections": {name: data.get("count", 0) for name, data in changed_collections.items()},
            "data": changed_collections
        }
        
        return backup_data
    
    def _record_full_backup(self, backup_result):
        """Record a full backup in change tracker"""
        # Get backup metadata to extract files and collections
        metadata = self.backup_service.get_backup_metadata(backup_result.backup_id)
        if metadata:
            files = metadata.get("filesystem", {}).get("files", [])
            collections = metadata.get("mongodb", {}).get("data", {})
            self.change_tracker.record_full_backup(
                backup_result.backup_id,
                files,
                collections
            )


def main():
    """Main entry point for incremental backup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Incremental Backup Service')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    storage_manager = StorageManager(config.get("storage", {}))
    backup_service = BackupService(storage_manager, args.config)
    incremental_service = IncrementalBackupService(backup_service)
    
    result = incremental_service.create_incremental_backup()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()


