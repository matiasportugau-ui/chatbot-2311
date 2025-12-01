#!/usr/bin/env python3
"""
Extract AI chat history from Cursor's workspace storage databases.

This script searches for Cursor's state.vscdb files and extracts chat/conversation data.
Works on both Linux and macOS systems.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse


def find_cursor_workspace_storage() -> List[Path]:
    """
    Find Cursor workspace storage directories.
    Returns list of potential paths to check.
    """
    home = Path.home()
    potential_paths = []
    
    # Linux paths
    if sys.platform.startswith('linux'):
        # Common Linux locations
        potential_paths.extend([
            home / '.config' / 'Cursor' / 'User' / 'workspaceStorage',
            home / '.local' / 'share' / 'Cursor' / 'User' / 'workspaceStorage',
            home / '.cursor' / 'User' / 'workspaceStorage',
        ])
    
    # macOS paths
    elif sys.platform == 'darwin':
        potential_paths.extend([
            home / 'Library' / 'Application Support' / 'Cursor' / 'User' / 'workspaceStorage',
        ])
    
    # Windows paths (WSL)
    elif sys.platform.startswith('win'):
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            potential_paths.append(Path(appdata) / 'Cursor' / 'User' / 'workspaceStorage')
    
    # Filter to existing paths
    existing_paths = [p for p in potential_paths if p.exists()]
    
    return existing_paths


def find_state_databases(workspace_storage_path: Path) -> List[Path]:
    """Find all state.vscdb files in workspace storage."""
    databases = []
    if workspace_storage_path.exists():
        for workspace_dir in workspace_storage_path.iterdir():
            if workspace_dir.is_dir():
                db_path = workspace_dir / 'state.vscdb'
                if db_path.exists():
                    databases.append(db_path)
    return databases


def extract_chat_data(db_path: Path, workspace_id: str, 
                     time_filter: Optional[tuple] = None,
                     keyword_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract chat-related data from a state.vscdb file.
    
    Args:
        db_path: Path to state.vscdb
        workspace_id: Identifier for this workspace
        time_filter: Optional tuple (start_time, end_time) as datetime objects
        keyword_filter: Optional list of keywords to search for
    
    Returns:
        List of extracted chat entries
    """
    results = []
    
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Common table names for chat storage
        chat_tables = ['ItemTable', 'keyvalue', 'storage', 'chat', 'conversations']
        
        for table in tables:
            if any(chat_name.lower() in table.lower() for chat_name in chat_tables):
                try:
                    # Try to get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Common column patterns
                    key_col = None
                    value_col = None
                    timestamp_col = None
                    
                    for col in columns:
                        col_lower = col.lower()
                        if 'key' in col_lower or 'id' in col_lower:
                            key_col = col
                        if 'value' in col_lower or 'data' in col_lower or 'content' in col_lower:
                            value_col = col
                        if 'time' in col_lower or 'date' in col_lower or 'timestamp' in col_lower:
                            timestamp_col = col
                    
                    # Build query
                    if key_col and value_col:
                        query = f"SELECT * FROM {table}"
                        cursor.execute(query)
                        
                        for row in cursor.fetchall():
                            row_dict = dict(row)
                            
                            # Extract key and value
                            key = row_dict.get(key_col, '')
                            value = row_dict.get(value_col, '')
                            
                            # Check if this looks like chat data
                            key_lower = str(key).lower()
                            if any(term in key_lower for term in ['chat', 'composer', 'aichat', 'conversation', 'history', 'message']):
                                # Try to parse JSON value
                                parsed_value = None
                                if isinstance(value, str):
                                    try:
                                        parsed_value = json.loads(value)
                                    except:
                                        parsed_value = value
                                else:
                                    parsed_value = value
                                
                                entry = {
                                    'workspace_id': workspace_id,
                                    'database': str(db_path),
                                    'table': table,
                                    'key': key,
                                    'value': parsed_value,
                                    'raw_value': str(value)[:500] if len(str(value)) > 500 else str(value),
                                }
                                
                                # Add timestamp if available
                                if timestamp_col and timestamp_col in row_dict:
                                    entry['timestamp'] = str(row_dict[timestamp_col])
                                
                                # Apply filters
                                include = True
                                
                                if time_filter and timestamp_col:
                                    entry_time = row_dict.get(timestamp_col)
                                    if entry_time:
                                        # Simple string comparison (can be improved)
                                        pass  # TODO: Implement time filtering
                                
                                if keyword_filter:
                                    entry_text = json.dumps(entry).lower()
                                    if not any(kw.lower() in entry_text for kw in keyword_filter):
                                        include = False
                                
                                if include:
                                    results.append(entry)
                
                except Exception as e:
                    print(f"  Warning: Could not read table {table}: {e}", file=sys.stderr)
        
        conn.close()
    
    except Exception as e:
        print(f"Error reading database {db_path}: {e}", file=sys.stderr)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Extract AI chat history from Cursor workspace storage'
    )
    parser.add_argument(
        '--output', '-o',
        default='chat_recovery.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--workspace-id',
        help='Specific workspace ID to extract (optional)'
    )
    parser.add_argument(
        '--keywords', '-k',
        nargs='+',
        help='Keywords to filter chat entries'
    )
    parser.add_argument(
        '--backup-dir',
        default='./cursor_workspace_backup',
        help='Directory to backup databases before analysis'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backups'
    )
    
    args = parser.parse_args()
    
    print("🔍 Searching for Cursor workspace storage...")
    workspace_storage_paths = find_cursor_workspace_storage()
    
    if not workspace_storage_paths:
        print("❌ No Cursor workspace storage directories found.")
        print("\nTried locations:")
        for path in find_cursor_workspace_storage():
            print(f"  - {path}")
        print("\n💡 If Cursor is installed elsewhere, manually specify the path.")
        return 1
    
    print(f"✅ Found {len(workspace_storage_paths)} workspace storage location(s)")
    
    # Create backup if requested
    if not args.no_backup:
        backup_dir = Path(args.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📦 Creating backups in {backup_dir}...")
    
    all_results = []
    
    for storage_path in workspace_storage_paths:
        print(f"\n📂 Scanning {storage_path}...")
        databases = find_state_databases(storage_path)
        
        if not databases:
            print(f"  ⚠️  No state.vscdb files found in {storage_path}")
            continue
        
        print(f"  ✅ Found {len(databases)} workspace database(s)")
        
        for db_path in databases:
            workspace_id = db_path.parent.name
            print(f"\n  🔍 Extracting from workspace: {workspace_id}")
            
            # Backup database
            if not args.no_backup:
                backup_path = backup_dir / f"{workspace_id}_state.vscdb"
                try:
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    print(f"    💾 Backed up to {backup_path}")
                except Exception as e:
                    print(f"    ⚠️  Backup failed: {e}")
            
            # Extract data
            results = extract_chat_data(
                db_path,
                workspace_id,
                keyword_filter=args.keywords
            )
            
            print(f"    ✅ Extracted {len(results)} chat entries")
            all_results.extend(results)
    
    # Save results
    if all_results:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_timestamp': datetime.now().isoformat(),
                'total_entries': len(all_results),
                'entries': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(all_results)} entries to {output_path}")
        
        # Print summary
        print("\n📊 Summary:")
        print(f"  Total entries: {len(all_results)}")
        workspaces = set(e['workspace_id'] for e in all_results)
        print(f"  Workspaces: {len(workspaces)}")
        for ws_id in workspaces:
            count = sum(1 for e in all_results if e['workspace_id'] == ws_id)
            print(f"    - {ws_id}: {count} entries")
    else:
        print("\n⚠️  No chat data found. This could mean:")
        print("  1. No chat history exists in the databases")
        print("  2. Chat data is stored in a different format/location")
        print("  3. The workspace storage path is incorrect")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
