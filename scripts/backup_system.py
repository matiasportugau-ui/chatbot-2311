#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup System Implementation
Based on BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md

This is a starter implementation providing core backup functionality.
Extend and customize based on your specific requirements.
"""

import os
import sys
import json
import shutil
import hashlib
import gzip
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BackupManifest:
    """Backup manifest containing metadata about a backup"""
    backup_id: str
    timestamp: str
    backup_type: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    validation: Dict[str, Any]
    retention: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def save(self, path: Path):
        """Save manifest to file"""
        with open(path / f"{self.backup_id}_manifest.json", 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'BackupManifest':
        """Load manifest from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)


@dataclass
class BackupValidation:
    """Validation result for a backup"""
    backup_id: str
    integrity_check: str  # passed, failed, pending
    restore_test: str
    verified_at: str
    errors: List[str]


@dataclass
class RecoveryResult:
    """Result of a file recovery operation"""
    file_path: str
    success: bool
    strategy_used: str
    recovery_time_seconds: float
    data_age_hours: Optional[float]
    error: Optional[str] = None


class BackupSystem:
    """
    Comprehensive backup system for BMC chatbot application
    """
    
    # Backup source configuration
    BACKUP_SOURCES = {
        "conversations": {
            "patterns": [
                "kb_populated_*.json",
                "conocimiento_consolidado.json",
                "base_conocimiento_exportada.json",
                "ia_conversacional_demo.json"
            ],
            "priority": "critical",
            "backup_frequency": "hourly"
        },
        "configuration": {
            "patterns": [
                ".env",
                "config.py",
                "matriz_precios.json",
                "requirements.txt",
                "package.json"
            ],
            "priority": "high",
            "backup_frequency": "daily"
        },
        "data": {
            "patterns": [
                "data/**/*.json",
                "locales/**/*.json"
            ],
            "priority": "medium",
            "backup_frequency": "daily"
        }
    }
    
    def __init__(self, backup_root: Path, retention_days: int = 30):
        """
        Initialize backup system
        
        Args:
            backup_root: Root directory for backups
            retention_days: Number of days to retain backups
        """
        self.backup_root = Path(backup_root)
        self.retention_days = retention_days
        self.workspace_root = Path(__file__).parent.parent.resolve()
        
        # Create backup directories
        self.hot_storage = self.backup_root / "hot"
        self.warm_storage = self.backup_root / "warm"
        self.cold_storage = self.backup_root / "cold"
        
        for storage in [self.hot_storage, self.warm_storage, self.cold_storage]:
            storage.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Backup system initialized. Root: {self.backup_root}")
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return f"sha256:{sha256_hash.hexdigest()}"
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return "error"
    
    def find_files(self, patterns: List[str]) -> List[Path]:
        """Find files matching patterns"""
        found_files = []
        for pattern in patterns:
            if "**" in pattern:
                # Recursive glob
                matches = list(self.workspace_root.glob(pattern))
            else:
                # Simple glob
                matches = list(self.workspace_root.glob(pattern))
            found_files.extend(matches)
        
        # Return unique, existing files
        return [f for f in set(found_files) if f.is_file()]
    
    def create_backup(
        self,
        backup_type: str = "incremental",
        sources: Optional[List[str]] = None,
        compression: bool = True,
        encryption: bool = False
    ) -> BackupManifest:
        """
        Create a new backup
        
        Args:
            backup_type: Type of backup (full, incremental, differential, snapshot)
            sources: List of source categories to backup (None = all)
            compression: Enable compression
            encryption: Enable encryption (not yet implemented)
        
        Returns:
            BackupManifest with metadata about the backup
        """
        start_time = time.time()
        timestamp = datetime.now()
        backup_id = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}_{backup_type}"
        
        logger.info(f"Starting backup: {backup_id}")
        
        # Determine which sources to backup
        if sources is None:
            sources_to_backup = self.BACKUP_SOURCES.keys()
        else:
            sources_to_backup = sources
        
        # Create backup directory
        backup_dir = self.hot_storage / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup each source
        backed_up_sources = []
        for source_name in sources_to_backup:
            if source_name not in self.BACKUP_SOURCES:
                logger.warning(f"Unknown source: {source_name}")
                continue
            
            source_config = self.BACKUP_SOURCES[source_name]
            patterns = source_config["patterns"]
            
            # Find files
            files = self.find_files(patterns)
            logger.info(f"Found {len(files)} files for source '{source_name}'")
            
            if not files:
                continue
            
            # Create source directory in backup
            source_dir = backup_dir / source_name
            source_dir.mkdir(exist_ok=True)
            
            total_size = 0
            files_backed_up = 0
            
            # Copy files
            for file_path in files:
                try:
                    # Calculate relative path
                    rel_path = file_path.relative_to(self.workspace_root)
                    dest_path = source_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    if compression and file_path.suffix in ['.json', '.txt', '.md', '.csv']:
                        # Compress JSON/text files
                        with open(file_path, 'rb') as f_in:
                            with gzip.open(f"{dest_path}.gz", 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        total_size += dest_path.with_suffix(dest_path.suffix + '.gz').stat().st_size
                    else:
                        shutil.copy2(file_path, dest_path)
                        total_size += dest_path.stat().st_size
                    
                    files_backed_up += 1
                    
                except Exception as e:
                    logger.error(f"Error backing up {file_path}: {e}")
            
            # Calculate checksum of entire source directory
            source_checksum = self._calculate_directory_checksum(source_dir)
            
            backed_up_sources.append({
                "source": source_name,
                "files_backed_up": files_backed_up,
                "total_size_bytes": total_size,
                "checksum": source_checksum,
                "compression": compression
            })
        
        # Create manifest
        duration = time.time() - start_time
        manifest = BackupManifest(
            backup_id=backup_id,
            timestamp=timestamp.isoformat(),
            backup_type=backup_type,
            sources=backed_up_sources,
            metadata={
                "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown",
                "workspace_root": str(self.workspace_root),
                "backup_duration_seconds": round(duration, 2),
                "compression_enabled": compression,
                "encryption_enabled": encryption
            },
            validation={
                "integrity_check": "pending",
                "restore_test": "pending",
                "verified_at": None
            },
            retention={
                "expires_at": (timestamp + timedelta(days=self.retention_days)).isoformat(),
                "tier": "hot"
            }
        )
        
        # Save manifest
        manifest.save(backup_dir)
        
        logger.info(f"Backup completed: {backup_id} ({duration:.2f}s)")
        return manifest
    
    def _calculate_directory_checksum(self, directory: Path) -> str:
        """Calculate checksum of all files in directory"""
        sha256_hash = hashlib.sha256()
        
        # Get all files sorted for consistent hashing
        files = sorted(directory.rglob('*'))
        
        for file_path in files:
            if file_path.is_file():
                # Include file path in hash
                sha256_hash.update(str(file_path.relative_to(directory)).encode())
                
                # Include file content in hash
                with open(file_path, 'rb') as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
        
        return f"sha256:{sha256_hash.hexdigest()}"
    
    def verify_backup(self, backup_id: str) -> BackupValidation:
        """
        Verify integrity of a backup
        
        Args:
            backup_id: ID of backup to verify
        
        Returns:
            BackupValidation result
        """
        logger.info(f"Verifying backup: {backup_id}")
        
        errors = []
        
        # Find backup directory
        backup_dir = self.hot_storage / backup_id
        if not backup_dir.exists():
            backup_dir = self.warm_storage / backup_id
        if not backup_dir.exists():
            backup_dir = self.cold_storage / backup_id
        
        if not backup_dir.exists():
            return BackupValidation(
                backup_id=backup_id,
                integrity_check="failed",
                restore_test="failed",
                verified_at=datetime.now().isoformat(),
                errors=["Backup directory not found"]
            )
        
        # Load manifest
        manifest_path = backup_dir / f"{backup_id}_manifest.json"
        if not manifest_path.exists():
            errors.append("Manifest file not found")
            return BackupValidation(
                backup_id=backup_id,
                integrity_check="failed",
                restore_test="failed",
                verified_at=datetime.now().isoformat(),
                errors=errors
            )
        
        manifest = BackupManifest.load(manifest_path)
        
        # Verify checksums
        integrity_check = "passed"
        for source in manifest.sources:
            source_name = source["source"]
            expected_checksum = source["checksum"]
            
            source_dir = backup_dir / source_name
            if not source_dir.exists():
                errors.append(f"Source directory missing: {source_name}")
                integrity_check = "failed"
                continue
            
            actual_checksum = self._calculate_directory_checksum(source_dir)
            if actual_checksum != expected_checksum:
                errors.append(f"Checksum mismatch for source: {source_name}")
                integrity_check = "failed"
        
        # Restore test (sample a few files)
        restore_test = "passed"
        try:
            # Try to read a few files
            for source in manifest.sources:
                source_dir = backup_dir / source["source"]
                files = list(source_dir.rglob('*'))[:3]  # Sample 3 files
                
                for file_path in files:
                    if file_path.is_file():
                        with open(file_path, 'rb') as f:
                            f.read(1024)  # Read first 1KB
        except Exception as e:
            errors.append(f"Restore test failed: {e}")
            restore_test = "failed"
        
        validation = BackupValidation(
            backup_id=backup_id,
            integrity_check=integrity_check,
            restore_test=restore_test,
            verified_at=datetime.now().isoformat(),
            errors=errors
        )
        
        logger.info(f"Verification complete: {integrity_check}, {restore_test}")
        return validation
    
    def list_backups(
        self,
        filter_by: Optional[Dict[str, Any]] = None,
        sort_by: str = "timestamp_desc"
    ) -> List[BackupManifest]:
        """
        List all available backups with filtering
        
        Args:
            filter_by: Optional filters (e.g., {"backup_type": "full"})
            sort_by: Sort order (timestamp_desc, timestamp_asc, size_desc, size_asc)
        
        Returns:
            List of BackupManifest objects
        """
        manifests = []
        
        # Search all storage tiers
        for storage in [self.hot_storage, self.warm_storage, self.cold_storage]:
            for backup_dir in storage.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                manifest_path = backup_dir / f"{backup_dir.name}_manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = BackupManifest.load(manifest_path)
                        manifests.append(manifest)
                    except Exception as e:
                        logger.error(f"Error loading manifest {manifest_path}: {e}")
        
        # Apply filters
        if filter_by:
            filtered = []
            for manifest in manifests:
                match = True
                for key, value in filter_by.items():
                    if key == "backup_type" and manifest.backup_type != value:
                        match = False
                    elif key == "after_date":
                        manifest_date = datetime.fromisoformat(manifest.timestamp)
                        if manifest_date < datetime.fromisoformat(value):
                            match = False
                if match:
                    filtered.append(manifest)
            manifests = filtered
        
        # Sort
        if sort_by == "timestamp_desc":
            manifests.sort(key=lambda m: m.timestamp, reverse=True)
        elif sort_by == "timestamp_asc":
            manifests.sort(key=lambda m: m.timestamp)
        
        return manifests
    
    def cleanup_old_backups(self, retention_days: Optional[int] = None):
        """
        Remove backups older than retention period
        
        Args:
            retention_days: Override default retention days
        """
        if retention_days is None:
            retention_days = self.retention_days
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        logger.info(f"Cleaning up backups older than {cutoff_date.isoformat()}")
        
        removed_count = 0
        
        for storage in [self.hot_storage, self.warm_storage]:
            for backup_dir in storage.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                manifest_path = backup_dir / f"{backup_dir.name}_manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = BackupManifest.load(manifest_path)
                        backup_date = datetime.fromisoformat(manifest.timestamp)
                        
                        if backup_date < cutoff_date:
                            logger.info(f"Removing old backup: {backup_dir.name}")
                            shutil.rmtree(backup_dir)
                            removed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing {backup_dir}: {e}")
        
        logger.info(f"Cleanup complete. Removed {removed_count} backups")
    
    def restore_file(
        self,
        backup_id: str,
        file_path: str,
        target_path: Optional[Path] = None
    ) -> bool:
        """
        Restore a specific file from backup
        
        Args:
            backup_id: ID of backup to restore from
            file_path: Relative path of file to restore
            target_path: Where to restore (None = original location)
        
        Returns:
            True if successful
        """
        logger.info(f"Restoring {file_path} from backup {backup_id}")
        
        # Find backup
        backup_dir = None
        for storage in [self.hot_storage, self.warm_storage, self.cold_storage]:
            candidate = storage / backup_id
            if candidate.exists():
                backup_dir = candidate
                break
        
        if not backup_dir:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        # Find file in backup
        file_found = False
        for source_dir in backup_dir.iterdir():
            if not source_dir.is_dir() or source_dir.name.endswith("_manifest.json"):
                continue
            
            # Check for regular file
            source_file = source_dir / file_path
            if source_file.exists():
                file_found = True
                break
            
            # Check for compressed file
            source_file = source_dir / f"{file_path}.gz"
            if source_file.exists():
                file_found = True
                break
        
        if not file_found:
            logger.error(f"File not found in backup: {file_path}")
            return False
        
        # Restore file
        try:
            if target_path is None:
                target_path = self.workspace_root / file_path
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_file.suffix == '.gz':
                # Decompress
                with gzip.open(source_file, 'rb') as f_in:
                    with open(target_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(source_file, target_path)
            
            logger.info(f"File restored successfully: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring file: {e}")
            return False


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup System CLI")
    parser.add_argument(
        "action",
        choices=["create", "list", "verify", "restore", "cleanup"],
        help="Action to perform"
    )
    parser.add_argument(
        "--type",
        choices=["full", "incremental", "differential", "snapshot"],
        default="incremental",
        help="Backup type"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        help="Sources to backup"
    )
    parser.add_argument(
        "--backup-id",
        help="Backup ID for verify/restore operations"
    )
    parser.add_argument(
        "--file",
        help="File path for restore operation"
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=30,
        help="Retention period in days"
    )
    
    args = parser.parse_args()
    
    # Initialize backup system
    workspace_root = Path(__file__).parent.parent.resolve()
    backup_root = workspace_root / "backups" / "automated"
    backup_system = BackupSystem(backup_root, retention_days=args.retention_days)
    
    if args.action == "create":
        manifest = backup_system.create_backup(
            backup_type=args.type,
            sources=args.sources
        )
        print(f"✅ Backup created: {manifest.backup_id}")
        print(json.dumps(manifest.to_dict(), indent=2))
    
    elif args.action == "list":
        backups = backup_system.list_backups()
        print(f"Found {len(backups)} backups:")
        for backup in backups:
            print(f"  - {backup.backup_id} ({backup.backup_type}) - {backup.timestamp}")
    
    elif args.action == "verify":
        if not args.backup_id:
            print("❌ --backup-id required for verify")
            sys.exit(1)
        
        validation = backup_system.verify_backup(args.backup_id)
        print(f"Integrity: {validation.integrity_check}")
        print(f"Restore Test: {validation.restore_test}")
        if validation.errors:
            print(f"Errors: {validation.errors}")
    
    elif args.action == "restore":
        if not args.backup_id or not args.file:
            print("❌ --backup-id and --file required for restore")
            sys.exit(1)
        
        success = backup_system.restore_file(args.backup_id, args.file)
        if success:
            print(f"✅ File restored: {args.file}")
        else:
            print(f"❌ Failed to restore: {args.file}")
    
    elif args.action == "cleanup":
        backup_system.cleanup_old_backups()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    main()
