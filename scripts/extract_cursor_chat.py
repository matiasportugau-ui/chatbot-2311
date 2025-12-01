#!/usr/bin/env python3
"""
Extract AI chat history from Cursor's workspace storage databases.

This script searches for Cursor's workspaceStorage folders and extracts
chat/conversation data from state.vscdb SQLite databases.
"""

import os
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse


def find_cursor_workspace_storage() -> List[Path]:
    """
    Find Cursor workspaceStorage directories.
    
    Returns:
        List of paths to workspaceStorage directories
    """
    storage_paths = []
    
    # Common locations for Cursor workspace storage
    home = Path.home()
    possible_locations = [
        # macOS
        home / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage",
        # Linux
        home / ".config" / "Cursor" / "User" / "workspaceStorage",
        # Windows (if running on WSL)
        home / "AppData" / "Roaming" / "Cursor" / "User" / "workspaceStorage",
    ]
    
    for location in possible_locations:
        if location.exists():
            storage_paths.append(location)
            print(f"✓ Found workspaceStorage: {location}")
    
    return storage_paths


def find_project_workspace(workspace_storage: Path, project_path: str) -> Optional[Path]:
    """
    Find the workspace folder for a specific project.
    
    Args:
        workspace_storage: Path to workspaceStorage directory
        project_path: Path to the project folder
        
    Returns:
        Path to the workspace folder, or None if not found
    """
    project_name = Path(project_path).name
    
    # Each workspace has a hash-based folder name
    # We'll search by checking modification dates and workspace.json files
    for workspace_folder in workspace_storage.iterdir():
        if not workspace_folder.is_dir():
            continue
            
        workspace_json = workspace_folder / "workspace.json"
        if workspace_json.exists():
            try:
                with open(workspace_json, 'r') as f:
                    workspace_data = json.load(f)
                    folder = workspace_data.get('folder', '')
                    if project_path in folder or project_name in folder:
                        return workspace_folder
            except (json.JSONDecodeError, KeyError):
                continue
    
    # Fallback: return most recently modified workspace
    workspaces = sorted(
        [w for w in workspace_storage.iterdir() if w.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    if workspaces:
        return workspaces[0]
    
    return None


def extract_chat_data(db_path: Path, time_window: Optional[tuple] = None, 
                     keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract chat data from a state.vscdb SQLite database.
    
    Args:
        db_path: Path to state.vscdb file
        time_window: Optional tuple of (start_time, end_time) as datetime objects
        keywords: Optional list of keywords to filter by
        
    Returns:
        List of chat entries found
    """
    if not db_path.exists():
        return []
    
    chat_entries = []
    
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query ItemTable for chat-related keys
        # Cursor stores data in ItemTable with keys like:
        # - aichat.*
        # - composer.*
        # - history.*
        # - chat.*
        
        query = """
        SELECT key, value, timestamp 
        FROM ItemTable 
        WHERE key LIKE '%chat%' 
           OR key LIKE '%aichat%'
           OR key LIKE '%composer%'
           OR key LIKE '%history%'
           OR key LIKE '%conversation%'
           OR key LIKE '%message%'
        ORDER BY timestamp DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            key = row['key']
            value_str = row['value']
            timestamp = row.get('timestamp', 0)
            
            # Parse JSON value
            try:
                value = json.loads(value_str) if value_str else {}
            except json.JSONDecodeError:
                value = {"raw": value_str}
            
            # Filter by time window if provided
            if time_window:
                entry_time = datetime.fromtimestamp(timestamp / 1000) if timestamp else None
                if entry_time:
                    start, end = time_window
                    if not (start <= entry_time <= end):
                        continue
            
            # Filter by keywords if provided
            if keywords:
                value_str_lower = json.dumps(value).lower()
                if not any(kw.lower() in value_str_lower for kw in keywords):
                    continue
            
            entry = {
                "key": key,
                "value": value,
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp / 1000).isoformat() if timestamp else None
            }
            chat_entries.append(entry)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Error reading database {db_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
    
    return chat_entries


def main():
    parser = argparse.ArgumentParser(
        description="Extract AI chat history from Cursor workspace storage"
    )
    parser.add_argument(
        "--project-path",
        type=str,
        default=os.getcwd(),
        help="Path to the project folder (default: current directory)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path (default: chat_recovery_<timestamp>.json)"
    )
    parser.add_argument(
        "--time-window",
        type=str,
        help="Time window in format 'YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS'"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        help="Keywords to filter chat entries"
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        help="Directory to backup workspaceStorage before extraction"
    )
    
    args = parser.parse_args()
    
    # Parse time window if provided
    time_window = None
    if args.time_window:
        try:
            start_str, end_str = args.time_window.split(',')
            start = datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(end_str.strip(), "%Y-%m-%d %H:%M:%S")
            time_window = (start, end)
        except ValueError:
            print("Error: Invalid time window format. Use 'YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS'", file=sys.stderr)
            sys.exit(1)
    
    # Find workspace storage
    print("Searching for Cursor workspaceStorage...")
    storage_paths = find_cursor_workspace_storage()
    
    if not storage_paths:
        print("No Cursor workspaceStorage found.", file=sys.stderr)
        print("Checked locations:", file=sys.stderr)
        for loc in [
            Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage",
            Path.home() / ".config" / "Cursor" / "User" / "workspaceStorage",
        ]:
            print(f"  - {loc}", file=sys.stderr)
        sys.exit(1)
    
    all_chat_entries = []
    
    # Process each workspaceStorage location
    for storage_path in storage_paths:
        print(f"\nProcessing workspaceStorage: {storage_path}")
        
        # Find project workspace
        project_path = os.path.abspath(args.project_path)
        workspace_folder = find_project_workspace(storage_path, project_path)
        
        if workspace_folder:
            print(f"✓ Found workspace folder: {workspace_folder}")
            
            # Backup if requested
            if args.backup_dir:
                backup_path = Path(args.backup_dir) / workspace_folder.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copytree(workspace_folder, backup_path, dirs_exist_ok=True)
                print(f"✓ Backed up to: {backup_path}")
            
            # Extract from state.vscdb
            db_path = workspace_folder / "state.vscdb"
            if db_path.exists():
                print(f"Extracting from {db_path}...")
                entries = extract_chat_data(db_path, time_window, args.keywords)
                all_chat_entries.extend(entries)
                print(f"✓ Found {len(entries)} chat entries")
            else:
                print(f"⚠ No state.vscdb found in {workspace_folder}")
        else:
            print(f"⚠ Could not find workspace folder for project: {project_path}")
            print("  Searching all workspaces...")
            
            # Search all workspaces
            for workspace_folder in storage_path.iterdir():
                if not workspace_folder.is_dir():
                    continue
                db_path = workspace_folder / "state.vscdb"
                if db_path.exists():
                    entries = extract_chat_data(db_path, time_window, args.keywords)
                    if entries:
                        all_chat_entries.extend(entries)
                        print(f"✓ Found {len(entries)} entries in {workspace_folder.name}")
    
    # Output results
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"chat_recovery_{timestamp}.json"
    
    output_data = {
        "extraction_timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "time_window": {
            "start": time_window[0].isoformat() if time_window else None,
            "end": time_window[1].isoformat() if time_window else None,
        } if time_window else None,
        "keywords": args.keywords,
        "total_entries": len(all_chat_entries),
        "entries": all_chat_entries
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Extraction complete!")
    print(f"  Total entries: {len(all_chat_entries)}")
    print(f"  Output file: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
