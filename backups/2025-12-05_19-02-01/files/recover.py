#!/usr/bin/env python3
"""
Recovery CLI
Command-line interface for recovery operations
"""
import argparse
import json
import sys
import os
from pathlib import Path

# Add backup_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backup_system'))

from recovery_service import RecoveryService, RestoreOptions
from storage_manager import StorageManager
from file_scanner import FileScanner

def load_config(config_path: str = "backup_system/backup_config.json"):
    """Load configuration"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def cmd_scan(args):
    """Scan for lost files command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    recovery_service = RecoveryService(storage_manager, config)
    
    if args.source == "mongodb":
        result = recovery_service.scan_mongodb()
        print(json.dumps(result, indent=2, default=str))
    elif args.source == "filesystem":
        result = recovery_service.scan_filesystem()
        print(json.dumps(result, indent=2, default=str))
    else:
        result = recovery_service.scan_for_lost_files()
        
        print(f"\nScan ID: {result.scan_id}")
        print(f"Timestamp: {result.timestamp}")
        print(f"\nSources:")
        print(f"  MongoDB: {result.sources.get('mongodb', {})}")
        print(f"  Filesystem: {result.sources.get('filesystem', {})}")
        
        if result.lost_files:
            print(f"\nLost Files ({len(result.lost_files)}):")
            for lost_file in result.lost_files:
                print(f"  - {lost_file['path']} ({lost_file['type']})")
                if lost_file.get('recoverable_from'):
                    print(f"    Recoverable from: {', '.join(lost_file['recoverable_from'])}")
        
        if result.recommendations:
            print(f"\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
    
    return 0


def cmd_preview(args):
    """Preview restore command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    recovery_service = RecoveryService(storage_manager, config)
    
    scope = None
    if args.target:
        scope = args.target.split(',')
    
    options = RestoreOptions(
        scope=scope,
        dry_run=True,
        conflict_resolution=args.conflict_resolution or "prompt",
        selective=args.selective.split(',') if args.selective else None
    )
    
    preview = recovery_service.preview_restore(args.backup_id, options)
    
    print(f"\nPreview Restore from: {args.backup_id}")
    print(f"\nFiles to restore: {len(preview.files_to_restore)}")
    for file_path in preview.files_to_restore[:10]:
        print(f"  - {file_path}")
    if len(preview.files_to_restore) > 10:
        print(f"  ... and {len(preview.files_to_restore) - 10} more")
    
    print(f"\nCollections to restore: {len(preview.collections_to_restore)}")
    for collection in preview.collections_to_restore:
        print(f"  - {collection}")
    
    if preview.conflicts:
        print(f"\nConflicts: {len(preview.conflicts)}")
        for conflict in preview.conflicts:
            print(f"  - {conflict['type']}: {conflict.get('name') or conflict.get('path')}")
    
    print(f"\nEstimated size: {preview.estimated_size:,} bytes")
    
    return 0


def cmd_restore(args):
    """Restore command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    recovery_service = RecoveryService(storage_manager, config)
    
    scope = None
    if args.scope:
        scope = args.scope.split(',')
    
    options = RestoreOptions(
        scope=scope,
        dry_run=args.dry_run,
        conflict_resolution=args.conflict_resolution or "overwrite",
        selective=args.selective.split(',') if args.selective else None
    )
    
    result = recovery_service.restore_from_backup(args.backup_id, options)
    
    if args.dry_run:
        print(f"\nDry-run completed:")
    else:
        print(f"\nRestore operation: {result.operation_id}")
        print(f"Status: {result.status}")
    
    print(f"  Restored: {result.restored}")
    print(f"  Failed: {result.failed}")
    print(f"  Skipped: {result.skipped}")
    print(f"  Conflicts: {result.conflicts}")
    
    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    return 0 if result.status == "completed" else 1


def cmd_status(args):
    """Get recovery operation status"""
    print("Status tracking not yet implemented")
    print(f"Operation ID: {args.operation_id}")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Recovery management CLI')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for lost files')
    scan_parser.add_argument('--source', choices=['mongodb', 'filesystem', 'all'],
                            default='all', help='Source to scan')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview restore operation')
    preview_parser.add_argument('backup_id', help='Backup ID to preview')
    preview_parser.add_argument('--target', help='Comma-separated list of targets (mongodb,filesystem,config)')
    preview_parser.add_argument('--selective', help='Comma-separated list of specific files/collections')
    preview_parser.add_argument('--conflict-resolution', choices=['skip', 'overwrite', 'merge'],
                               help='Conflict resolution strategy')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_id', help='Backup ID to restore from')
    restore_parser.add_argument('--scope', help='Comma-separated list of scopes (mongodb,filesystem,config)')
    restore_parser.add_argument('--selective', help='Comma-separated list of specific files/collections')
    restore_parser.add_argument('--dry-run', action='store_true', help='Preview restore without making changes')
    restore_parser.add_argument('--conflict-resolution', choices=['skip', 'overwrite', 'merge'],
                               help='Conflict resolution strategy')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get recovery operation status')
    status_parser.add_argument('operation_id', help='Operation ID to check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'scan': cmd_scan,
        'preview': cmd_preview,
        'restore': cmd_restore,
        'status': cmd_status
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


