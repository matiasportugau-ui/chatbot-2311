#!/usr/bin/env python3
"""
File Scanner
Scans filesystem and MongoDB for missing or corrupted files
"""
import os
import json
import glob
import hashlib
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mongodb_service import ensure_mongodb_connected, get_mongodb_service
except ImportError:
    def ensure_mongodb_connected():
        return False
    def get_mongodb_service():
        return None

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """Information about a file"""
    path: str
    size: int
    exists: bool
    corrupted: bool = False
    last_modified: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class CorruptedFile:
    """Information about a corrupted file"""
    path: str
    error: str
    expected_size: Optional[int] = None
    actual_size: Optional[int] = None


@dataclass
class DuplicateGroup:
    """Group of duplicate files"""
    files: List[str]
    checksum: str
    size: int


@dataclass
class ComparisonResult:
    """Result of comparing files with backup"""
    missing_files: List[str]
    changed_files: List[str]
    new_files: List[str]


class FileScanner:
    """Scans filesystem and MongoDB for issues"""
    
    def __init__(self, base_dir: str = None, config: Dict = None):
        """
        Initialize FileScanner
        
        Args:
            base_dir: Base directory to scan
            config: Configuration dictionary
        """
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = config or {}
    
    def scan_directory(self, path: str, patterns: List[str]) -> List[FileInfo]:
        """
        Scan directory for files matching patterns
        
        Args:
            path: Directory path to scan
            patterns: List of file patterns (glob)
        
        Returns:
            List of FileInfo objects
        """
        files = []
        full_path = os.path.join(self.base_dir, path) if not os.path.isabs(path) else path
        
        if not os.path.exists(full_path):
            return files
        
        for pattern in patterns:
            search_path = os.path.join(full_path, pattern)
            matches = glob.glob(search_path, recursive=True)
            
            for match in matches:
                if os.path.isfile(match):
                    rel_path = os.path.relpath(match, self.base_dir)
                    file_info = self._get_file_info(rel_path)
                    if file_info:
                        files.append(file_info)
        
        return files
    
    def _get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Get information about a file"""
        full_path = os.path.join(self.base_dir, file_path)
        
        if not os.path.exists(full_path):
            return FileInfo(
                path=file_path,
                size=0,
                exists=False
            )
        
        try:
            stat = os.stat(full_path)
            return FileInfo(
                path=file_path,
                size=stat.st_size,
                exists=True,
                last_modified=str(stat.st_mtime)
            )
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def detect_missing_files(self, expected_files: List[str]) -> List[str]:
        """
        Detect missing files from expected list
        
        Args:
            expected_files: List of expected file paths
        
        Returns:
            List of missing file paths
        """
        missing = []
        
        for file_path in expected_files:
            full_path = os.path.join(self.base_dir, file_path) if not os.path.isabs(file_path) else file_path
            if not os.path.exists(full_path):
                missing.append(file_path)
        
        return missing
    
    def detect_corrupted_files(self, files: List[str]) -> List[CorruptedFile]:
        """
        Detect corrupted files
        
        Args:
            files: List of file paths to check
        
        Returns:
            List of CorruptedFile objects
        """
        corrupted = []
        
        for file_path in files:
            full_path = os.path.join(self.base_dir, file_path) if not os.path.isabs(file_path) else file_path
            
            if not os.path.exists(full_path):
                continue
            
            try:
                # Try to read and parse JSON files
                if file_path.endswith('.json'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                
                # Try to read Python files
                elif file_path.endswith('.py'):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
            
            except json.JSONDecodeError as e:
                corrupted.append(CorruptedFile(
                    path=file_path,
                    error=f"Invalid JSON: {str(e)}"
                ))
            except SyntaxError as e:
                corrupted.append(CorruptedFile(
                    path=file_path,
                    error=f"Syntax error: {str(e)}"
                ))
            except Exception as e:
                corrupted.append(CorruptedFile(
                    path=file_path,
                    error=f"Read error: {str(e)}"
                ))
        
        return corrupted
    
    def compare_with_backup(self, files: List[str], backup_id: str) -> ComparisonResult:
        """
        Compare files with backup
        
        Args:
            files: List of file paths to compare
            backup_id: Backup ID to compare with
        
        Returns:
            ComparisonResult object
        """
        # Load backup metadata
        backup_metadata_dir = self.config.get("backup", {}).get("metadata_dir", "./backup_metadata")
        backup_metadata_path = os.path.join(backup_metadata_dir, f"{backup_id}.json")
        
        if not os.path.exists(backup_metadata_path):
            return ComparisonResult(
                missing_files=[],
                changed_files=[],
                new_files=files
            )
        
        with open(backup_metadata_path, 'r', encoding='utf-8') as f:
            backup_metadata = json.load(f)
        
        backup_files = {}
        if "filesystem" in backup_metadata:
            for file_info in backup_metadata["filesystem"].get("files", []):
                backup_files[file_info["path"]] = {
                    "size": file_info.get("size", 0),
                    "checksum": self._calculate_checksum(file_info.get("content", ""))
                }
        
        missing_files = []
        changed_files = []
        new_files = []
        
        for file_path in files:
            if file_path not in backup_files:
                new_files.append(file_path)
            else:
                # Check if file exists and compare
                full_path = os.path.join(self.base_dir, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
                else:
                    # Compare checksum
                    current_checksum = self._calculate_file_checksum(full_path)
                    if current_checksum != backup_files[file_path]["checksum"]:
                        changed_files.append(file_path)
        
        return ComparisonResult(
            missing_files=missing_files,
            changed_files=changed_files,
            new_files=new_files
        )
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate checksum of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def find_duplicates(self, files: List[str]) -> List[DuplicateGroup]:
        """
        Find duplicate files
        
        Args:
            files: List of file paths to check
        
        Returns:
            List of DuplicateGroup objects
        """
        checksum_map = {}
        
        for file_path in files:
            full_path = os.path.join(self.base_dir, file_path) if not os.path.isabs(file_path) else file_path
            if os.path.exists(full_path):
                checksum = self._calculate_file_checksum(full_path)
                if checksum not in checksum_map:
                    checksum_map[checksum] = []
                checksum_map[checksum].append(file_path)
        
        duplicates = []
        for checksum, file_list in checksum_map.items():
            if len(file_list) > 1:
                size = os.path.getsize(os.path.join(self.base_dir, file_list[0]))
                duplicates.append(DuplicateGroup(
                    files=file_list,
                    checksum=checksum,
                    size=size
                ))
        
        return duplicates
    
    def scan_mongodb(self) -> Dict:
        """
        Scan MongoDB collections
        
        Returns:
            Dictionary with collection information
        """
        if not ensure_mongodb_connected():
            return {
                "connected": False,
                "collections": {},
                "error": "MongoDB not connected"
            }
        
        service = get_mongodb_service()
        if not service:
            return {
                "connected": False,
                "collections": {},
                "error": "Could not get MongoDB service"
            }
        
        collections_info = {}
        expected_collections = self.config.get("mongodb", {}).get("collections", [])
        
        for collection_name in expected_collections:
            try:
                collection = service.get_collection(collection_name)
                count = collection.count_documents({})
                collections_info[collection_name] = {
                    "exists": True,
                    "count": count
                }
            except Exception as e:
                collections_info[collection_name] = {
                    "exists": False,
                    "error": str(e)
                }
        
        return {
            "connected": True,
            "collections": collections_info
        }


