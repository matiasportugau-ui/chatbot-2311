#!/usr/bin/env python3
"""
Recovery Service
Handles recovery operations from backups
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_scanner import FileScanner
from storage_manager import StorageManager

try:
    from mongodb_service import ensure_mongodb_connected, get_mongodb_service
except ImportError:
    def ensure_mongodb_connected():
        return False
    def get_mongodb_service():
        return None

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result of a scan operation"""
    scan_id: str
    timestamp: str
    sources: Dict[str, Any]
    lost_files: List[Dict]
    recommendations: List[str]


@dataclass
class RestoreResult:
    """Result of a restore operation"""
    operation_id: str
    backup_id: str
    status: str  # pending, in_progress, completed, failed
    started_at: str
    completed_at: Optional[str]
    restored: int
    failed: int
    skipped: int
    conflicts: int
    errors: List[str]


@dataclass
class RestoreOptions:
    """Options for restore operation"""
    scope: List[str] = None
    dry_run: bool = False
    conflict_resolution: str = "prompt"  # skip, overwrite, merge
    selective: List[str] = None  # Specific files/collections to restore


@dataclass
class PreviewResult:
    """Result of preview operation"""
    backup_id: str
    files_to_restore: List[str]
    collections_to_restore: List[str]
    conflicts: List[Dict]
    estimated_size: int


@dataclass
class Conflict:
    """Information about a restore conflict"""
    path: str
    type: str  # file or collection
    existing_size: int
    backup_size: int
    resolution: Optional[str] = None


class RecoveryService:
    """Service for recovering data from backups"""
    
    def __init__(self, storage_manager: StorageManager = None, config: Dict = None):
        """
        Initialize RecoveryService
        
        Args:
            storage_manager: StorageManager instance
            config: Configuration dictionary
        """
        self.storage_manager = storage_manager
        self.config = config or {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_scanner = FileScanner(self.base_dir, self.config)
        self.backup_metadata_dir = self.config.get("backup", {}).get("metadata_dir", "./backup_metadata")
    
    def scan_for_lost_files(self) -> ScanResult:
        """
        Scan for lost or corrupted files
        
        Returns:
            ScanResult object
        """
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Starting scan: {scan_id}")
        
        sources = {}
        lost_files = []
        recommendations = []
        
        # Scan MongoDB
        mongo_scan = self.scan_mongodb()
        sources["mongodb"] = mongo_scan
        
        # Scan filesystem
        fs_scan = self.scan_filesystem()
        sources["filesystem"] = fs_scan
        
        # Identify lost files
        if "filesystem" in fs_scan:
            missing = fs_scan.get("files_missing", [])
            corrupted = fs_scan.get("files_corrupted", [])
            
            for file_path in missing:
                lost_files.append({
                    "path": file_path,
                    "type": "missing",
                    "recoverable_from": self._find_backups_with_file(file_path)
                })
            
            for file_path in corrupted:
                lost_files.append({
                    "path": file_path,
                    "type": "corrupted",
                    "recoverable_from": self._find_backups_with_file(file_path)
                })
        
        # Generate recommendations
        for lost_file in lost_files:
            if lost_file["recoverable_from"]:
                backup_id = lost_file["recoverable_from"][0]
                recommendations.append(
                    f"Restore {lost_file['path']} from {backup_id}"
                )
        
        return ScanResult(
            scan_id=scan_id,
            timestamp=timestamp,
            sources=sources,
            lost_files=lost_files,
            recommendations=recommendations
        )
    
    def scan_mongodb(self) -> Dict:
        """Scan MongoDB collections"""
        return self.file_scanner.scan_mongodb()
    
    def scan_filesystem(self, patterns: Optional[List[str]] = None) -> Dict:
        """
        Scan filesystem for issues
        
        Args:
            patterns: Optional list of file patterns to scan
        """
        if patterns is None:
            patterns = self.config.get("filesystem", {}).get("patterns", [])
        
        files_scanned = []
        files_found = []
        files_missing = []
        files_corrupted = []
        
        # Scan directories
        directories = self.config.get("filesystem", {}).get("directories", [])
        for directory in directories:
            scanned = self.file_scanner.scan_directory(directory, patterns)
            files_scanned.extend([f.path for f in scanned])
            files_found.extend([f.path for f in scanned if f.exists])
            files_missing.extend([f.path for f in scanned if not f.exists])
        
        # Check for corruption
        corrupted = self.file_scanner.detect_corrupted_files(files_found)
        files_corrupted = [c.path for c in corrupted]
        
        return {
            "files_scanned": len(files_scanned),
            "files_found": len(files_found),
            "files_missing": len(files_missing),
            "files_corrupted": len(files_corrupted),
            "missing_files": files_missing,
            "corrupted_files": files_corrupted
        }
    
    def _find_backups_with_file(self, file_path: str) -> List[str]:
        """Find backups that contain a specific file"""
        backups_with_file = []
        
        if not os.path.exists(self.backup_metadata_dir):
            return backups_with_file
        
        for filename in os.listdir(self.backup_metadata_dir):
            if filename.endswith('.json'):
                backup_id = filename[:-5]
                metadata_path = os.path.join(self.backup_metadata_dir, filename)
                
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Check filesystem backup
                    if "filesystem" in metadata:
                        files = metadata["filesystem"].get("files", [])
                        for file_info in files:
                            if file_info.get("path") == file_path:
                                backups_with_file.append(backup_id)
                                break
                except Exception as e:
                    logger.warning(f"Error reading backup metadata {filename}: {e}")
        
        return backups_with_file
    
    def restore_from_backup(self, backup_id: str, options: RestoreOptions) -> RestoreResult:
        """
        Restore data from backup
        
        Args:
            backup_id: Backup ID to restore from
            options: RestoreOptions object
        """
        operation_id = f"recover_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now().isoformat()
        
        logger.info(f"Starting restore operation: {operation_id} from backup: {backup_id}")
        
        # Load backup
        if not self.storage_manager:
            return RestoreResult(
                operation_id=operation_id,
                backup_id=backup_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                restored=0,
                failed=0,
                skipped=0,
                conflicts=0,
                errors=["Storage manager not initialized"]
            )
        
        backup_data = self.storage_manager.load_backup(backup_id)
        if not backup_data:
            return RestoreResult(
                operation_id=operation_id,
                backup_id=backup_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                restored=0,
                failed=0,
                skipped=0,
                conflicts=0,
                errors=[f"Backup not found: {backup_id}"]
            )
        
        if options.dry_run:
            # Preview mode
            preview = self.preview_restore(backup_id, options)
            return RestoreResult(
                operation_id=operation_id,
                backup_id=backup_id,
                status="completed",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                restored=len(preview.files_to_restore) + len(preview.collections_to_restore),
                failed=0,
                skipped=0,
                conflicts=len(preview.conflicts),
                errors=[]
            )
        
        # Perform actual restore
        restored = 0
        failed = 0
        skipped = 0
        conflicts = 0
        errors = []
        
        # Restore MongoDB collections
        if "mongodb" in backup_data and ("mongodb" in (options.scope or [])):
            mongo_result = self._restore_mongodb(backup_data["mongodb"], options)
            restored += mongo_result["restored"]
            failed += mongo_result["failed"]
            conflicts += mongo_result["conflicts"]
            errors.extend(mongo_result["errors"])
        
        # Restore filesystem files
        if "filesystem" in backup_data and ("filesystem" in (options.scope or []) or "config" in (options.scope or [])):
            fs_result = self._restore_filesystem(backup_data["filesystem"], options)
            restored += fs_result["restored"]
            failed += fs_result["failed"]
            skipped += fs_result["skipped"]
            conflicts += fs_result["conflicts"]
            errors.extend(fs_result["errors"])
        
        completed_at = datetime.now().isoformat()
        
        return RestoreResult(
            operation_id=operation_id,
            backup_id=backup_id,
            status="completed",
            started_at=started_at,
            completed_at=completed_at,
            restored=restored,
            failed=failed,
            skipped=skipped,
            conflicts=conflicts,
            errors=errors
        )
    
    def _restore_mongodb(self, mongo_data: Dict, options: RestoreOptions) -> Dict:
        """Restore MongoDB collections"""
        restored = 0
        failed = 0
        conflicts = 0
        errors = []
        
        if not ensure_mongodb_connected():
            return {
                "restored": 0,
                "failed": 0,
                "conflicts": 0,
                "errors": ["MongoDB not connected"]
            }
        
        service = get_mongodb_service()
        if not service:
            return {
                "restored": 0,
                "failed": 0,
                "conflicts": 0,
                "errors": ["Could not get MongoDB service"]
            }
        
        collections_data = mongo_data.get("data", {})
        
        for collection_name, collection_data in collections_data.items():
            # Check if selective restore
            if options.selective and collection_name not in options.selective:
                continue
            
            try:
                collection = service.get_collection(collection_name)
                
                # Check for conflicts
                existing_count = collection.count_documents({})
                if existing_count > 0:
                    conflicts += 1
                    if options.conflict_resolution == "skip":
                        continue
                    elif options.conflict_resolution == "overwrite":
                        collection.delete_many({})
                
                # Restore documents
                documents = collection_data.get("documents", [])
                if documents:
                    collection.insert_many(documents)
                    restored += len(documents)
                    logger.info(f"Restored {len(documents)} documents to {collection_name}")
            
            except Exception as e:
                failed += 1
                error_msg = f"Error restoring {collection_name}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "restored": restored,
            "failed": failed,
            "conflicts": conflicts,
            "errors": errors
        }
    
    def _restore_filesystem(self, fs_data: Dict, options: RestoreOptions) -> Dict:
        """Restore filesystem files"""
        restored = 0
        failed = 0
        skipped = 0
        conflicts = 0
        errors = []
        
        files = fs_data.get("files", [])
        
        for file_info in files:
            file_path = file_info.get("path")
            
            # Check if selective restore
            if options.selective and file_path not in options.selective:
                skipped += 1
                continue
            
            full_path = os.path.join(self.base_dir, file_path)
            
            # Check for conflicts
            if os.path.exists(full_path):
                conflicts += 1
                if options.conflict_resolution == "skip":
                    skipped += 1
                    continue
                elif options.conflict_resolution == "overwrite":
                    # Will overwrite below
                    pass
            
            try:
                # Create directory if needed
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file
                content = file_info.get("content", "")
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                restored += 1
                logger.info(f"Restored file: {file_path}")
            
            except Exception as e:
                failed += 1
                error_msg = f"Error restoring {file_path}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "restored": restored,
            "failed": failed,
            "skipped": skipped,
            "conflicts": conflicts,
            "errors": errors
        }
    
    def preview_restore(self, backup_id: str, options: RestoreOptions) -> PreviewResult:
        """
        Preview what would be restored
        
        Args:
            backup_id: Backup ID to preview
            options: RestoreOptions object
        """
        if not self.storage_manager:
            return PreviewResult(
                backup_id=backup_id,
                files_to_restore=[],
                collections_to_restore=[],
                conflicts=[],
                estimated_size=0
            )
        
        backup_data = self.storage_manager.load_backup(backup_id)
        if not backup_data:
            return PreviewResult(
                backup_id=backup_id,
                files_to_restore=[],
                collections_to_restore=[],
                conflicts=[],
                estimated_size=0
            )
        
        files_to_restore = []
        collections_to_restore = []
        conflicts = []
        estimated_size = 0
        
        # Preview MongoDB restore
        if "mongodb" in backup_data:
            collections_data = backup_data["mongodb"].get("data", {})
            for collection_name, collection_data in collections_data.items():
                if options.selective and collection_name not in options.selective:
                    continue
                
                collections_to_restore.append(collection_name)
                
                # Check for conflicts
                if ensure_mongodb_connected():
                    service = get_mongodb_service()
                    if service:
                        collection = service.get_collection(collection_name)
                        if collection.count_documents({}) > 0:
                            conflicts.append({
                                "type": "collection",
                                "name": collection_name,
                                "resolution": options.conflict_resolution
                            })
        
        # Preview filesystem restore
        if "filesystem" in backup_data:
            files = backup_data["filesystem"].get("files", [])
            for file_info in files:
                file_path = file_info.get("path")
                
                if options.selective and file_path not in options.selective:
                    continue
                
                files_to_restore.append(file_path)
                estimated_size += file_info.get("size", 0)
                
                # Check for conflicts
                full_path = os.path.join(self.base_dir, file_path)
                if os.path.exists(full_path):
                    conflicts.append({
                        "type": "file",
                        "path": file_path,
                        "resolution": options.conflict_resolution
                    })
        
        return PreviewResult(
            backup_id=backup_id,
            files_to_restore=files_to_restore,
            collections_to_restore=collections_to_restore,
            conflicts=conflicts,
            estimated_size=estimated_size
        )
    
    def restore_file(self, file_path: str, source: str) -> Dict:
        """
        Restore a specific file from backup
        
        Args:
            file_path: Path of file to restore
            source: Backup ID or source identifier
        """
        # Find backup with file
        backups = self._find_backups_with_file(file_path)
        if not backups:
            return {
                "success": False,
                "error": f"No backup found containing {file_path}"
            }
        
        backup_id = source if source in backups else backups[0]
        
        options = RestoreOptions(
            scope=["filesystem"],
            selective=[file_path],
            conflict_resolution="overwrite"
        )
        
        result = self.restore_from_backup(backup_id, options)
        
        return {
            "success": result.status == "completed",
            "backup_id": backup_id,
            "restored": result.restored,
            "errors": result.errors
        }
    
    def restore_collection(self, collection: str, backup_id: str) -> Dict:
        """
        Restore a specific MongoDB collection
        
        Args:
            collection: Collection name to restore
            backup_id: Backup ID to restore from
        """
        options = RestoreOptions(
            scope=["mongodb"],
            selective=[collection],
            conflict_resolution="overwrite"
        )
        
        result = self.restore_from_backup(backup_id, options)
        
        return {
            "success": result.status == "completed",
            "collection": collection,
            "restored": result.restored,
            "errors": result.errors
        }


