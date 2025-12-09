#!/usr/bin/env python3
"""
Backup CLI
Command-line interface for backup operations
"""
import argparse
import json
import sys
import os
from pathlib import Path

# Add backup_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backup_system'))

from backup_service import BackupService
from storage_manager import StorageManager

def load_config(config_path: str = "backup_system/backup_config.json"):
    """Load configuration"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def cmd_create(args):
    """Create backup command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    backup_service = BackupService(storage_manager, args.config)
    
    scope = None
    if args.scope:
        scope = args.scope.split(',')
    
    if args.full:
        result = backup_service.create_full_backup()
    elif args.incremental:
        result = backup_service.create_incremental_backup()
    else:
        result = backup_service.create_backup(
            backup_type=args.type or "full",
            scope=scope
        )
    
    if result.success:
        print(f"✓ Backup created successfully: {result.backup_id}")
        print(f"  Size: {result.size:,} bytes")
        print(f"  Compressed: {result.compressed_size:,} bytes")
        print(f"  Collections: {len(result.collections)}")
        print(f"  Files: {result.files.get('count', 0)}")
        return 0
    else:
        print(f"✗ Backup failed: {result.error}")
        return 1


def cmd_list(args):
    """List backups command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    backup_service = BackupService(storage_manager, args.config)
    
    filters = {}
    if args.filter:
        if "last_7_days" in args.filter:
            from datetime import datetime, timedelta
            filters["after"] = (datetime.now() - timedelta(days=7)).isoformat()
        elif "last_30_days" in args.filter:
            from datetime import datetime, timedelta
            filters["after"] = (datetime.now() - timedelta(days=30)).isoformat()
        if args.type:
            filters["type"] = args.type
    
    backups = backup_service.list_backups(filters)
    
    if not backups:
        print("No backups found")
        return 0
    
    print(f"\nFound {len(backups)} backup(s):\n")
    print(f"{'Backup ID':<30} {'Type':<12} {'Date':<20} {'Size':<15} {'Verified':<10}")
    print("-" * 90)
    
    for backup in backups:
        size_str = f"{backup.compressed_size:,} bytes"
        verified_str = "✓" if backup.verified else "✗"
        print(f"{backup.backup_id:<30} {backup.type:<12} {backup.timestamp[:19]:<20} {size_str:<15} {verified_str:<10}")
    
    return 0


def cmd_verify(args):
    """Verify backup command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    backup_service = BackupService(storage_manager, args.config)
    
    result = backup_service.verify_backup(args.backup_id)
    
    if result.verified:
        print(f"✓ Backup verified: {args.backup_id}")
        print(f"  Checksum: {'✓' if result.checksum_match else '✗'}")
        print(f"  Integrity: {'✓' if result.integrity_check else '✗'}")
        return 0
    else:
        print(f"✗ Backup verification failed: {args.backup_id}")
        if result.error:
            print(f"  Error: {result.error}")
        return 1


def cmd_delete(args):
    """Delete backup command"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    if storage_manager.delete_backup(args.backup_id):
        print(f"✓ Backup deleted: {args.backup_id}")
        return 0
    else:
        print(f"✗ Failed to delete backup: {args.backup_id}")
        return 1


def cmd_restore(args):
    """Restore backup command (preview only for now)"""
    print("Restore functionality is available via recover.py")
    print(f"Use: python recover.py restore {args.backup_id}")
    return 0


def cmd_storage(args):
    """Show storage usage"""
    config = load_config(args.config)
    storage_config = config.get("storage", {})
    storage_manager = StorageManager(storage_config)
    
    usage = storage_manager.get_storage_usage()
    
    print(f"\nStorage Usage:")
    print(f"  Total Size: {usage.total_size:,} bytes ({usage.total_size / 1024 / 1024:.2f} MB)")
    print(f"  Backup Count: {usage.backup_count}")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Backup management CLI')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument('--full', action='store_true', help='Create full backup')
    create_parser.add_argument('--incremental', action='store_true', help='Create incremental backup')
    create_parser.add_argument('--type', choices=['full', 'incremental'], help='Backup type')
    create_parser.add_argument('--scope', help='Comma-separated list of scopes (mongodb,filesystem,config)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all backups')
    list_parser.add_argument('--filter', help='Filter backups (last_7_days, last_30_days)')
    list_parser.add_argument('--type', choices=['full', 'incremental'], help='Filter by type')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify backup integrity')
    verify_parser.add_argument('backup_id', help='Backup ID to verify')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a backup')
    delete_parser.add_argument('backup_id', help='Backup ID to delete')
    
    # Restore command (redirects to recover.py)
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_id', help='Backup ID to restore')
    restore_parser.add_argument('--dry-run', action='store_true', help='Preview restore without making changes')
    
    # Storage command
    storage_parser = subparsers.add_parser('storage', help='Show storage usage')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'create': cmd_create,
        'list': cmd_list,
        'verify': cmd_verify,
        'delete': cmd_delete,
        'restore': cmd_restore,
        'storage': cmd_storage
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


