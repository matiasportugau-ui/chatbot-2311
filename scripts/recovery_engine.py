#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recovery Engine Implementation
Based on BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md

Intelligent recovery system for lost or corrupted files with multiple recovery strategies.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backup_system import BackupSystem, RecoveryResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MissingFile:
    """Information about a missing file"""
    path: Path
    expected_location: str
    last_seen: Optional[datetime]
    priority: str
    file_type: str


@dataclass
class CorruptedFile:
    """Information about a corrupted file"""
    path: Path
    corruption_type: str
    detected_at: datetime
    error_message: str


class RecoveryEngine:
    """
    Intelligent recovery system for lost or corrupted files
    """
    
    # Recovery strategies configuration
    RECOVERY_STRATEGIES = {
        "conversations/*.json": [
            {"strategy": "latest_backup", "max_age_hours": 1},
            {"strategy": "mongodb_export", "collection": "conversations"},
            {"strategy": "git_history", "max_commits": 100},
            {"strategy": "reconstruct_from_logs", "log_dir": "logs/"}
        ],
        ".env": [
            {"strategy": "latest_backup", "max_age_hours": 24},
            {"strategy": "git_history"},
            {"strategy": "manual_recovery", "alert": True}
        ],
        "conocimiento_consolidado.json": [
            {"strategy": "latest_backup", "max_age_hours": 6},
            {"strategy": "regenerate", "script": "consolidar_conocimiento.py"},
            {"strategy": "mongodb_export", "aggregate": True}
        ],
        "matriz_precios.json": [
            {"strategy": "latest_backup", "max_age_hours": 24},
            {"strategy": "git_history"},
            {"strategy": "web_fetch", "url": "bmcuruguay.com.uy"}
        ]
    }
    
    def __init__(self, backup_system: BackupSystem):
        """
        Initialize recovery engine
        
        Args:
            backup_system: BackupSystem instance to use for recovery
        """
        self.backup_system = backup_system
        self.workspace_root = backup_system.workspace_root
        
        # Map strategy names to methods
        self.strategy_handlers = {
            "latest_backup": self.recover_from_latest_backup,
            "mongodb_export": self.recover_from_mongodb,
            "git_history": self.recover_from_git_history,
            "reconstruct_from_logs": self.reconstruct_from_logs,
            "regenerate": self.regenerate_file,
            "manual_recovery": self.manual_recovery
        }
        
        logger.info("Recovery engine initialized")
    
    def detect_missing_files(self) -> List[MissingFile]:
        """
        Detect files that should exist but are missing
        
        Returns:
            List of MissingFile objects
        """
        logger.info("Scanning for missing files...")
        missing_files = []
        
        # Define expected files
        expected_files = [
            {
                "path": "conocimiento_consolidado.json",
                "priority": "critical",
                "file_type": "knowledge_base"
            },
            {
                "path": "base_conocimiento_exportada.json",
                "priority": "high",
                "file_type": "knowledge_base"
            },
            {
                "path": "matriz_precios.json",
                "priority": "high",
                "file_type": "configuration"
            },
            {
                "path": ".env",
                "priority": "critical",
                "file_type": "configuration"
            },
            {
                "path": "requirements.txt",
                "priority": "high",
                "file_type": "dependency"
            }
        ]
        
        for expected in expected_files:
            file_path = self.workspace_root / expected["path"]
            if not file_path.exists():
                missing_files.append(MissingFile(
                    path=file_path,
                    expected_location=expected["path"],
                    last_seen=None,
                    priority=expected["priority"],
                    file_type=expected["file_type"]
                ))
                logger.warning(f"Missing file detected: {expected['path']} (priority: {expected['priority']})")
        
        logger.info(f"Found {len(missing_files)} missing files")
        return missing_files
    
    def detect_corrupted_files(self) -> List[CorruptedFile]:
        """
        Detect corrupted or damaged files
        
        Returns:
            List of CorruptedFile objects
        """
        logger.info("Scanning for corrupted files...")
        corrupted_files = []
        
        # Check JSON files
        json_patterns = [
            "*.json",
            "data/**/*.json",
            "locales/**/*.json"
        ]
        
        for pattern in json_patterns:
            for file_path in self.workspace_root.glob(pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    corrupted_files.append(CorruptedFile(
                        path=file_path,
                        corruption_type="json_decode_error",
                        detected_at=datetime.now(),
                        error_message=str(e)
                    ))
                    logger.warning(f"Corrupted JSON file: {file_path}")
                except Exception as e:
                    corrupted_files.append(CorruptedFile(
                        path=file_path,
                        corruption_type="read_error",
                        detected_at=datetime.now(),
                        error_message=str(e)
                    ))
        
        logger.info(f"Found {len(corrupted_files)} corrupted files")
        return corrupted_files
    
    def recover_file(
        self,
        file_path: Path,
        recovery_strategy: str = "auto",
        target_timestamp: Optional[datetime] = None
    ) -> RecoveryResult:
        """
        Recover a lost or corrupted file
        
        Args:
            file_path: Path to the lost file
            recovery_strategy: Strategy to use (auto, backup, mongodb, git, etc.)
            target_timestamp: Recover to specific point in time
        
        Returns:
            RecoveryResult with status and recovered data
        """
        start_time = time.time()
        logger.info(f"Attempting to recover: {file_path}")
        
        # Convert to relative path
        if file_path.is_absolute():
            try:
                file_path = file_path.relative_to(self.workspace_root)
            except ValueError:
                pass
        
        # Determine strategies to use
        if recovery_strategy == "auto":
            strategies = self._get_strategies_for_file(file_path)
        else:
            strategies = [{"strategy": recovery_strategy}]
        
        # Try each strategy in order
        for strategy_config in strategies:
            strategy_name = strategy_config["strategy"]
            
            if strategy_name not in self.strategy_handlers:
                logger.warning(f"Unknown strategy: {strategy_name}")
                continue
            
            logger.info(f"Trying strategy: {strategy_name}")
            
            try:
                handler = self.strategy_handlers[strategy_name]
                data = handler(file_path, strategy_config)
                
                if data is not None:
                    # Recovery successful
                    target_file = self.workspace_root / file_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    if isinstance(data, bytes):
                        with open(target_file, 'wb') as f:
                            f.write(data)
                    else:
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(data)
                    
                    recovery_time = time.time() - start_time
                    
                    logger.info(f"✅ File recovered using {strategy_name}: {file_path}")
                    
                    return RecoveryResult(
                        file_path=str(file_path),
                        success=True,
                        strategy_used=strategy_name,
                        recovery_time_seconds=round(recovery_time, 2),
                        data_age_hours=None
                    )
                    
            except Exception as e:
                logger.error(f"Strategy {strategy_name} failed: {e}")
                continue
        
        # All strategies failed
        recovery_time = time.time() - start_time
        logger.error(f"❌ Failed to recover: {file_path}")
        
        return RecoveryResult(
            file_path=str(file_path),
            success=False,
            strategy_used="none",
            recovery_time_seconds=round(recovery_time, 2),
            data_age_hours=None,
            error="All recovery strategies failed"
        )
    
    def _get_strategies_for_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get appropriate recovery strategies for a file"""
        file_str = str(file_path)
        
        # Check if file matches any configured pattern
        for pattern, strategies in self.RECOVERY_STRATEGIES.items():
            if self._matches_pattern(file_str, pattern):
                return strategies
        
        # Default strategies
        return [
            {"strategy": "latest_backup", "max_age_hours": 24},
            {"strategy": "git_history"}
        ]
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        from fnmatch import fnmatch
        return fnmatch(file_path, pattern)
    
    def recover_from_latest_backup(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Strategy 1: Recover from latest backup
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            File data as bytes or None
        """
        logger.info(f"Searching backups for: {file_path}")
        
        # Get all backups sorted by timestamp
        backups = self.backup_system.list_backups(sort_by="timestamp_desc")
        
        max_age_hours = config.get("max_age_hours", 24)
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for backup in backups:
            backup_time = datetime.fromisoformat(backup.timestamp)
            
            # Skip if too old
            if backup_time < cutoff_time:
                logger.debug(f"Backup {backup.backup_id} too old, skipping")
                continue
            
            # Try to restore file
            temp_target = self.workspace_root / ".recovery_temp" / file_path
            temp_target.parent.mkdir(parents=True, exist_ok=True)
            
            success = self.backup_system.restore_file(
                backup.backup_id,
                str(file_path),
                temp_target
            )
            
            if success and temp_target.exists():
                with open(temp_target, 'rb') as f:
                    data = f.read()
                
                # Cleanup temp file
                temp_target.unlink()
                
                return data
        
        return None
    
    def recover_from_mongodb(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Strategy 2: Recover from MongoDB if data is stored there
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            File data as string or None
        """
        logger.info(f"Attempting MongoDB recovery for: {file_path}")
        
        try:
            from pymongo import MongoClient
            
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                logger.warning("MONGODB_URI not configured")
                return None
            
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            db = client.get_database()
            
            collection_name = config.get("collection", "conversations")
            collection = db[collection_name]
            
            # Export collection to JSON
            documents = list(collection.find())
            
            if documents:
                # Remove MongoDB _id fields
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                return json.dumps(documents, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"MongoDB recovery failed: {e}")
        
        return None
    
    def recover_from_git_history(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Strategy 3: Recover from Git history
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            File data as bytes or None
        """
        logger.info(f"Searching Git history for: {file_path}")
        
        try:
            # Check if file exists in Git history
            result = subprocess.run(
                ["git", "log", "--all", "--full-history", "--", str(file_path)],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                logger.warning(f"File not found in Git history: {file_path}")
                return None
            
            # Get the most recent version
            result = subprocess.run(
                ["git", "show", f"HEAD:{file_path}"],
                cwd=self.workspace_root,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            
            # Try finding in other branches
            result = subprocess.run(
                ["git", "log", "--all", "--pretty=format:%H", "--", str(file_path)],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                max_commits = config.get("max_commits", 100)
                
                for commit in commits[:max_commits]:
                    result = subprocess.run(
                        ["git", "show", f"{commit}:{file_path}"],
                        cwd=self.workspace_root,
                        capture_output=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"Found file in commit: {commit}")
                        return result.stdout
            
        except subprocess.TimeoutExpired:
            logger.error("Git command timed out")
        except Exception as e:
            logger.error(f"Git recovery failed: {e}")
        
        return None
    
    def reconstruct_from_logs(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Strategy 4: Reconstruct from application logs
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            Reconstructed file data as string or None
        """
        logger.info(f"Attempting log reconstruction for: {file_path}")
        
        log_dir = self.workspace_root / config.get("log_dir", "logs")
        if not log_dir.exists():
            return None
        
        # This is a placeholder - actual implementation would parse logs
        # and reconstruct data based on logged operations
        
        logger.warning("Log reconstruction not yet implemented")
        return None
    
    def regenerate_file(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Strategy 5: Regenerate file using a script
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            Generated file data as string or None
        """
        logger.info(f"Attempting regeneration for: {file_path}")
        
        script_name = config.get("script")
        if not script_name:
            return None
        
        script_path = self.workspace_root / script_name
        if not script_path.exists():
            logger.warning(f"Regeneration script not found: {script_name}")
            return None
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Check if file was generated
                if (self.workspace_root / file_path).exists():
                    with open(self.workspace_root / file_path, 'r') as f:
                        return f.read()
            
        except Exception as e:
            logger.error(f"Regeneration failed: {e}")
        
        return None
    
    def manual_recovery(
        self,
        file_path: Path,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """
        Strategy 6: Manual recovery (alert only)
        
        Args:
            file_path: File to recover
            config: Strategy configuration
        
        Returns:
            None (manual intervention required)
        """
        logger.warning(f"Manual recovery required for: {file_path}")
        
        if config.get("alert", False):
            # Send alert (placeholder)
            print(f"\n⚠️  ALERT: Manual recovery required for {file_path}")
            print(f"   Please restore this file manually.\n")
        
        return None
    
    def batch_recovery(
        self,
        missing_files: List[MissingFile],
        parallel: bool = False
    ) -> Dict[Path, RecoveryResult]:
        """
        Recover multiple files in batch
        
        Args:
            missing_files: List of missing files
            parallel: Whether to recover in parallel (not yet implemented)
        
        Returns:
            Dictionary mapping file paths to recovery results
        """
        logger.info(f"Starting batch recovery of {len(missing_files)} files")
        
        results = {}
        
        for missing_file in missing_files:
            result = self.recover_file(missing_file.path)
            results[missing_file.path] = result
        
        # Summary
        successful = sum(1 for r in results.values() if r.success)
        failed = len(results) - successful
        
        logger.info(f"Batch recovery complete: {successful} successful, {failed} failed")
        
        return results
    
    def create_recovery_report(
        self,
        recovery_results: Dict[Path, RecoveryResult]
    ) -> Path:
        """
        Generate comprehensive recovery report
        
        Args:
            recovery_results: Dictionary of recovery results
        
        Returns:
            Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.workspace_root / f"recovery_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(recovery_results),
            "successful": sum(1 for r in recovery_results.values() if r.success),
            "failed": sum(1 for r in recovery_results.values() if not r.success),
            "results": [
                {
                    "file_path": str(path),
                    **asdict(result)
                }
                for path, result in recovery_results.items()
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Recovery report saved: {report_path}")
        return report_path


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Recovery Engine CLI")
    parser.add_argument(
        "action",
        choices=["scan", "recover", "batch"],
        help="Action to perform"
    )
    parser.add_argument(
        "--file",
        help="File to recover"
    )
    parser.add_argument(
        "--strategy",
        default="auto",
        help="Recovery strategy to use"
    )
    
    args = parser.parse_args()
    
    # Initialize systems
    workspace_root = Path(__file__).parent.parent.resolve()
    backup_root = workspace_root / "backups" / "automated"
    backup_system = BackupSystem(backup_root)
    recovery_engine = RecoveryEngine(backup_system)
    
    if args.action == "scan":
        print("\n🔍 Scanning for missing files...")
        missing = recovery_engine.detect_missing_files()
        
        print(f"\n📊 Found {len(missing)} missing files:")
        for file in missing:
            print(f"  ❌ {file.expected_location} (priority: {file.priority})")
        
        print("\n🔍 Scanning for corrupted files...")
        corrupted = recovery_engine.detect_corrupted_files()
        
        print(f"\n📊 Found {len(corrupted)} corrupted files:")
        for file in corrupted:
            print(f"  ⚠️  {file.path}")
            print(f"     Error: {file.error_message}")
    
    elif args.action == "recover":
        if not args.file:
            print("❌ --file required for recover action")
            sys.exit(1)
        
        file_path = Path(args.file)
        result = recovery_engine.recover_file(file_path, recovery_strategy=args.strategy)
        
        if result.success:
            print(f"\n✅ File recovered successfully!")
            print(f"   Strategy: {result.strategy_used}")
            print(f"   Time: {result.recovery_time_seconds}s")
        else:
            print(f"\n❌ Recovery failed")
            print(f"   Error: {result.error}")
    
    elif args.action == "batch":
        print("\n🔍 Detecting missing files...")
        missing = recovery_engine.detect_missing_files()
        
        if not missing:
            print("✅ No missing files detected")
            sys.exit(0)
        
        print(f"\n📦 Starting batch recovery of {len(missing)} files...")
        results = recovery_engine.batch_recovery(missing)
        
        report_path = recovery_engine.create_recovery_report(results)
        print(f"\n📄 Recovery report saved: {report_path}")
        
        successful = sum(1 for r in results.values() if r.success)
        print(f"\n✅ Recovery complete: {successful}/{len(results)} files recovered")


if __name__ == "__main__":
    main()
