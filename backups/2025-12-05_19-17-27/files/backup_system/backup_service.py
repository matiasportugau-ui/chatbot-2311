#!/usr/bin/env python3
"""
Backup Service
Handles creation, verification, and management of backups
"""
import os
import json
import gzip
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from pymongo import MongoClient
from pymongo.database import Database
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mongodb_service import ensure_mongodb_connected, get_mongodb_service
except ImportError:
    # Fallback if mongodb_service not available
    def ensure_mongodb_connected():
        return False
    def get_mongodb_service():
        return None

logger = logging.getLogger(__name__)


@dataclass
class BackupResult:
    """Result of a backup operation"""
    backup_id: str
    success: bool
    timestamp: str
    size: int
    compressed_size: int
    collections: Dict[str, int]
    files: Dict[str, Any]
    error: Optional[str] = None
    metadata_path: str = ""


@dataclass
class VerificationResult:
    """Result of backup verification"""
    backup_id: str
    verified: bool
    checksum_match: bool
    integrity_check: bool
    error: Optional[str] = None


@dataclass
class BackupInfo:
    """Information about a backup"""
    backup_id: str
    timestamp: str
    type: str  # full or incremental
    size: int
    compressed_size: int
    collections: Dict[str, int]
    files_count: int
    verified: bool
    storage_location: str


class BackupService:
    """Service for creating and managing backups"""
    
    def __init__(self, storage_manager=None, config_path: str = "backup_config.json"):
        """
        Initialize BackupService
        
        Args:
            storage_manager: StorageManager instance
            config_path: Path to configuration file
        """
        self.storage_manager = storage_manager
        self.config = self._load_config(config_path)
        self.backup_metadata_dir = self.config.get("backup", {}).get("metadata_dir", "./backup_metadata")
        os.makedirs(self.backup_metadata_dir, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "backup": {
                "enabled": True,
                "compression": {
                    "enabled": True,
                    "algorithm": "gzip",
                    "level": 6
                },
                "encryption": {
                    "enabled": False,
                    "algorithm": "AES-256"
                },
                "metadata_dir": "./backup_metadata"
            },
            "storage": {
                "primary": "local",
                "local": {
                    "path": "./backups"
                }
            },
            "mongodb": {
                "collections": [
                    "conversations",
                    "conversaciones",
                    "quotes",
                    "cotizaciones",
                    "sessions",
                    "context",
                    "analytics",
                    "users"
                ]
            },
            "filesystem": {
                "patterns": [
                    "*.json",
                    "*.py",
                    "*.env",
                    "config.py",
                    "conocimiento_consolidado.json",
                    "base_conocimiento_*.json",
                    "kb_populated_*.json"
                ],
                "directories": [
                    "python-scripts",
                    "src",
                    "n8n_workflows",
                    "test_scenarios"
                ]
            }
        }
    
    def create_backup(self, backup_type: str = "full", scope: Optional[List[str]] = None) -> BackupResult:
        """
        Create a backup
        
        Args:
            backup_type: Type of backup (full or incremental)
            scope: List of scopes to backup (mongodb, filesystem, config)
        
        Returns:
            BackupResult object
        """
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Creating {backup_type} backup: {backup_id}")
        
        if scope is None:
            scope = ["mongodb", "filesystem", "config"]
        
        try:
            backup_data = {
                "backup_id": backup_id,
                "timestamp": timestamp,
                "type": backup_type,
                "scope": scope
            }
            
            collections = {}
            files_data = {"count": 0, "total_size": 0, "files": []}
            
            # Backup MongoDB
            if "mongodb" in scope:
                mongo_data = self._backup_mongodb()
                collections = mongo_data.get("collections", {})
                backup_data["mongodb"] = mongo_data
            
            # Backup filesystem
            if "filesystem" in scope or "config" in scope:
                fs_data = self._backup_filesystem(scope)
                files_data = fs_data
                backup_data["filesystem"] = fs_data
            
            # Calculate sizes
            backup_json = json.dumps(backup_data, default=str, indent=2)
            size = len(backup_json.encode('utf-8'))
            
            # Compress if enabled
            compressed_size = size
            if self.config.get("backup", {}).get("compression", {}).get("enabled", True):
                compressed = gzip.compress(backup_json.encode('utf-8'))
                compressed_size = len(compressed)
                backup_data["compressed_data"] = compressed.hex()
            
            # Calculate checksum
            checksum = hashlib.sha256(backup_json.encode('utf-8')).hexdigest()
            backup_data["verification"] = {
                "checksum": f"sha256:{checksum}",
                "verified": False,
                "verified_at": None
            }
            
            # Save backup
            if self.storage_manager:
                storage_path = self.storage_manager.save_backup(backup_data, backup_id)
                backup_data["storage"] = {
                    "location": self.config.get("storage", {}).get("primary", "local"),
                    "path": storage_path
                }
            
            # Save metadata
            metadata_path = self._save_metadata(backup_id, backup_data)
            
            result = BackupResult(
                backup_id=backup_id,
                success=True,
                timestamp=timestamp,
                size=size,
                compressed_size=compressed_size,
                collections=collections,
                files=files_data,
                metadata_path=metadata_path
            )
            
            logger.info(f"Backup created successfully: {backup_id}")
            return result
        
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return BackupResult(
                backup_id=backup_id,
                success=False,
                timestamp=timestamp,
                size=0,
                compressed_size=0,
                collections={},
                files={},
                error=str(e)
            )
    
    def _backup_mongodb(self) -> Dict:
        """Backup MongoDB collections"""
        logger.info("Backing up MongoDB collections...")
        
        if not ensure_mongodb_connected():
            logger.warning("MongoDB not connected, skipping MongoDB backup")
            return {"collections": {}, "error": "MongoDB not connected"}
        
        service = get_mongodb_service()
        if not service:
            return {"collections": {}, "error": "Could not get MongoDB service"}
        
        collections_data = {}
        collections_to_backup = self.config.get("mongodb", {}).get("collections", [])
        
        for collection_name in collections_to_backup:
            try:
                collection = service.get_collection(collection_name)
                documents = list(collection.find({}))
                collections_data[collection_name] = {
                    "count": len(documents),
                    "documents": documents
                }
                logger.info(f"Backed up {len(documents)} documents from {collection_name}")
            except Exception as e:
                logger.error(f"Error backing up collection {collection_name}: {e}")
                collections_data[collection_name] = {
                    "count": 0,
                    "error": str(e)
                }
        
        return {
            "collections": {k: v["count"] for k, v in collections_data.items()},
            "data": collections_data
        }
    
    def _backup_filesystem(self, scope: List[str]) -> Dict:
        """Backup filesystem files"""
        logger.info("Backing up filesystem files...")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        patterns = self.config.get("filesystem", {}).get("patterns", [])
        directories = self.config.get("filesystem", {}).get("directories", [])
        
        files_backed_up = []
        total_size = 0
        
        # Backup config files
        if "config" in scope:
            config_files = [".env", "config.py", "package.json", "requirements.txt"]
            for config_file in config_files:
                file_path = os.path.join(base_dir, config_file)
                if os.path.exists(file_path):
                    file_data = self._read_file(file_path)
                    if file_data:
                        files_backed_up.append({
                            "path": config_file,
                            "size": len(file_data),
                            "content": file_data
                        })
                        total_size += len(file_data)
        
        # Backup knowledge base files
        for pattern in patterns:
            if "*" in pattern:
                # Handle glob patterns
                import glob
                matches = glob.glob(os.path.join(base_dir, pattern))
                for match in matches:
                    rel_path = os.path.relpath(match, base_dir)
                    file_data = self._read_file(match)
                    if file_data:
                        files_backed_up.append({
                            "path": rel_path,
                            "size": len(file_data),
                            "content": file_data
                        })
                        total_size += len(file_data)
            else:
                # Direct file
                file_path = os.path.join(base_dir, pattern)
                if os.path.exists(file_path):
                    file_data = self._read_file(file_path)
                    if file_data:
                        files_backed_up.append({
                            "path": pattern,
                            "size": len(file_data),
                            "content": file_data
                        })
                        total_size += len(file_data)
        
        # Backup directories
        for directory in directories:
            dir_path = os.path.join(base_dir, directory)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_dir)
                        file_data = self._read_file(file_path)
                        if file_data:
                            files_backed_up.append({
                                "path": rel_path,
                                "size": len(file_data),
                                "content": file_data
                            })
                            total_size += len(file_data)
        
        return {
            "count": len(files_backed_up),
            "total_size": total_size,
            "files": files_backed_up
        }
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def _save_metadata(self, backup_id: str, metadata: Dict) -> str:
        """Save backup metadata"""
        metadata_path = os.path.join(self.backup_metadata_dir, f"{backup_id}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
        return metadata_path
    
    def verify_backup(self, backup_id: str) -> VerificationResult:
        """Verify backup integrity"""
        logger.info(f"Verifying backup: {backup_id}")
        
        try:
            metadata_path = os.path.join(self.backup_metadata_dir, f"{backup_id}.json")
            if not os.path.exists(metadata_path):
                return VerificationResult(
                    backup_id=backup_id,
                    verified=False,
                    checksum_match=False,
                    integrity_check=False,
                    error="Metadata file not found"
                )
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verify checksum if available
            checksum_match = True
            if "verification" in metadata:
                expected_checksum = metadata["verification"].get("checksum", "")
                # Recalculate checksum from metadata
                metadata_copy = metadata.copy()
                metadata_copy["verification"]["verified"] = False
                metadata_copy["verification"]["verified_at"] = None
                metadata_json = json.dumps(metadata_copy, default=str, sort_keys=True)
                actual_checksum = f"sha256:{hashlib.sha256(metadata_json.encode('utf-8')).hexdigest()}"
                checksum_match = expected_checksum == actual_checksum
            
            # Basic integrity check
            integrity_check = (
                "backup_id" in metadata and
                "timestamp" in metadata and
                "type" in metadata
            )
            
            # Update verification status
            if checksum_match and integrity_check:
                metadata["verification"]["verified"] = True
                metadata["verification"]["verified_at"] = datetime.now().isoformat()
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, default=str)
            
            return VerificationResult(
                backup_id=backup_id,
                verified=checksum_match and integrity_check,
                checksum_match=checksum_match,
                integrity_check=integrity_check
            )
        
        except Exception as e:
            logger.error(f"Verification failed: {e}", exc_info=True)
            return VerificationResult(
                backup_id=backup_id,
                verified=False,
                checksum_match=False,
                integrity_check=False,
                error=str(e)
            )
    
    def list_backups(self, filters: Optional[Dict] = None) -> List[BackupInfo]:
        """List all backups"""
        backups = []
        
        if not os.path.exists(self.backup_metadata_dir):
            return backups
        
        for filename in os.listdir(self.backup_metadata_dir):
            if filename.endswith('.json'):
                backup_id = filename[:-5]  # Remove .json
                metadata_path = os.path.join(self.backup_metadata_dir, filename)
                
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Apply filters
                    if filters:
                        if "type" in filters and metadata.get("type") != filters["type"]:
                            continue
                        if "after" in filters:
                            if metadata.get("timestamp", "") < filters["after"]:
                                continue
                    
                    backup_info = BackupInfo(
                        backup_id=metadata.get("backup_id", backup_id),
                        timestamp=metadata.get("timestamp", ""),
                        type=metadata.get("type", "unknown"),
                        size=metadata.get("size", 0),
                        compressed_size=metadata.get("compressed_size", 0),
                        collections=metadata.get("mongodb", {}).get("collections", {}),
                        files_count=metadata.get("filesystem", {}).get("count", 0),
                        verified=metadata.get("verification", {}).get("verified", False),
                        storage_location=metadata.get("storage", {}).get("path", "")
                    )
                    backups.append(backup_info)
                
                except Exception as e:
                    logger.warning(f"Error reading backup metadata {filename}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def get_backup_metadata(self, backup_id: str) -> Optional[Dict]:
        """Get backup metadata"""
        metadata_path = os.path.join(self.backup_metadata_dir, f"{backup_id}.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def create_incremental_backup(self) -> BackupResult:
        """Create incremental backup"""
        try:
            from incremental_backup import IncrementalBackupService, ChangeTracker
            incremental_service = IncrementalBackupService(self, ChangeTracker())
            result = incremental_service.create_incremental_backup()
            
            if result.get("backup_result"):
                backup_result = result["backup_result"]
                return BackupResult(
                    backup_id=backup_result.get("backup_id", ""),
                    success=backup_result.get("success", False),
                    timestamp=backup_result.get("timestamp", datetime.now().isoformat()),
                    size=0,
                    compressed_size=0,
                    collections={},
                    files={"count": result.get("total_changes", 0)}
                )
            else:
                # No changes, return success but with no backup
                return BackupResult(
                    backup_id="",
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    size=0,
                    compressed_size=0,
                    collections={},
                    files={}
                )
        except ImportError:
            # Fallback to full backup if incremental not available
            logger.warning("Incremental backup service not available, creating full backup")
            return self.create_backup(backup_type="incremental")
    
    def create_full_backup(self) -> BackupResult:
        """Create full backup"""
        return self.create_backup(backup_type="full")


