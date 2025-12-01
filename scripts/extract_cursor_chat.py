#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor AI Chat Extraction Script
Extracts AI chat history from Cursor's workspace storage (state.vscdb)

This script scans Cursor's workspaceStorage folder, opens SQLite databases,
and extracts AI chat history for recovery purposes.

Usage:
    python extract_cursor_chat.py --workspace-storage "~/Library/Application Support/Cursor/User/workspaceStorage"
    python extract_cursor_chat.py --backup-first --output ~/Desktop/chat_recovery
"""

import os
import sys
import json
import sqlite3
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class CursorChatExtractor:
    """Extract AI chat history from Cursor's workspace storage"""
    
    # Keys that may contain AI chat data
    CHAT_KEYS = [
        'aichat',
        'composer',
        'chat',
        'history',
        'aiChat',
        'cursorChat',
        'conversation',
        'assistant',
        'copilot',
        'workbench.panel.aichat',
        'workbench.panel.chat',
        'workbench.aichat.history',
    ]
    
    def __init__(self, workspace_storage_path: Optional[str] = None):
        """Initialize the extractor with workspace storage path"""
        self.workspace_storage = self._find_workspace_storage(workspace_storage_path)
        self.extracted_chats: List[Dict[str, Any]] = []
        self.extraction_report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_storage_path": str(self.workspace_storage) if self.workspace_storage else None,
            "databases_scanned": 0,
            "chats_found": 0,
            "errors": [],
            "workspaces": []
        }
    
    def _find_workspace_storage(self, provided_path: Optional[str]) -> Optional[Path]:
        """Find Cursor's workspace storage directory"""
        if provided_path:
            path = Path(provided_path).expanduser()
            if path.exists():
                return path
        
        # Common locations by OS
        possible_paths = [
            # macOS
            Path.home() / "Library/Application Support/Cursor/User/workspaceStorage",
            Path.home() / "Library/Application Support/cursor/User/workspaceStorage",
            # Linux
            Path.home() / ".config/Cursor/User/workspaceStorage",
            Path.home() / ".config/cursor/User/workspaceStorage",
            Path.home() / ".cursor/User/workspaceStorage",
            # Windows
            Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage",
            Path.home() / "AppData/Local/Cursor/User/workspaceStorage",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def backup_database(self, db_path: Path, backup_dir: Path) -> Optional[Path]:
        """Create a backup copy of the database before analysis"""
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{db_path.parent.name}_{db_path.name}"
            shutil.copy2(db_path, backup_path)
            return backup_path
        except Exception as e:
            self.extraction_report["errors"].append(f"Backup failed for {db_path}: {e}")
            return None
    
    def extract_from_database(self, db_path: Path, use_backup: bool = True, 
                              backup_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Extract chat data from a single state.vscdb database"""
        chats = []
        
        # Use backup if requested
        actual_path = db_path
        if use_backup and backup_dir:
            backup_path = self.backup_database(db_path, backup_dir)
            if backup_path:
                actual_path = backup_path
        
        try:
            # Open in read-only mode with URI
            conn = sqlite3.connect(f"file:{actual_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            
            # Check what tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Common table names in VSCode/Cursor
            target_tables = ['ItemTable', 'memento', 'state']
            
            for table in tables:
                if table not in target_tables:
                    continue
                
                try:
                    # Get all rows
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        key = row_dict.get('key', '')
                        value = row_dict.get('value', '')
                        
                        # Check if key matches any chat-related patterns
                        if any(chat_key.lower() in key.lower() for chat_key in self.CHAT_KEYS):
                            try:
                                # Try to parse JSON value
                                if isinstance(value, str):
                                    parsed_value = json.loads(value)
                                else:
                                    parsed_value = value
                                
                                chat_data = {
                                    "source_db": str(db_path),
                                    "workspace_id": db_path.parent.name,
                                    "key": key,
                                    "table": table,
                                    "data": parsed_value,
                                    "extracted_at": datetime.now().isoformat()
                                }
                                chats.append(chat_data)
                                
                            except json.JSONDecodeError:
                                # Store raw value if not JSON
                                if value and len(str(value)) > 10:
                                    chat_data = {
                                        "source_db": str(db_path),
                                        "workspace_id": db_path.parent.name,
                                        "key": key,
                                        "table": table,
                                        "data_raw": str(value)[:10000],  # Truncate large values
                                        "extracted_at": datetime.now().isoformat()
                                    }
                                    chats.append(chat_data)
                                    
                except sqlite3.Error as e:
                    self.extraction_report["errors"].append(f"Error reading table {table}: {e}")
            
            conn.close()
            
        except sqlite3.Error as e:
            self.extraction_report["errors"].append(f"Database error for {db_path}: {e}")
        except Exception as e:
            self.extraction_report["errors"].append(f"Error processing {db_path}: {e}")
        
        return chats
    
    def scan_all_workspaces(self, backup_dir: Optional[Path] = None, 
                            time_filter: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Scan all workspace storage folders for chat data"""
        if not self.workspace_storage:
            self.extraction_report["errors"].append("Workspace storage not found")
            return []
        
        all_chats = []
        
        # Find all state.vscdb files
        for workspace_dir in self.workspace_storage.iterdir():
            if not workspace_dir.is_dir():
                continue
            
            # Check modification time if filter provided
            if time_filter:
                start_time, end_time = time_filter
                mod_time = datetime.fromtimestamp(workspace_dir.stat().st_mtime)
                if not (start_time <= mod_time <= end_time):
                    continue
            
            workspace_info = {
                "id": workspace_dir.name,
                "path": str(workspace_dir),
                "modified": datetime.fromtimestamp(workspace_dir.stat().st_mtime).isoformat(),
                "chats_found": 0
            }
            
            state_db = workspace_dir / "state.vscdb"
            if state_db.exists():
                self.extraction_report["databases_scanned"] += 1
                chats = self.extract_from_database(state_db, backup_dir=backup_dir)
                workspace_info["chats_found"] = len(chats)
                all_chats.extend(chats)
            
            # Also check for workspace.json for project identification
            workspace_json = workspace_dir / "workspace.json"
            if workspace_json.exists():
                try:
                    with open(workspace_json, 'r') as f:
                        workspace_data = json.load(f)
                        workspace_info["project"] = workspace_data.get("folder", "unknown")
                except:
                    pass
            
            if workspace_info["chats_found"] > 0:
                self.extraction_report["workspaces"].append(workspace_info)
        
        self.extracted_chats = all_chats
        self.extraction_report["chats_found"] = len(all_chats)
        return all_chats
    
    def filter_by_keywords(self, chats: List[Dict[str, Any]], 
                           keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter chats by keywords"""
        if not keywords:
            return chats
        
        filtered = []
        for chat in chats:
            chat_str = json.dumps(chat, default=str).lower()
            if any(keyword.lower() in chat_str for keyword in keywords):
                filtered.append(chat)
        
        return filtered
    
    def filter_by_time(self, chats: List[Dict[str, Any]], 
                       start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Filter chats by time window"""
        filtered = []
        for chat in chats:
            # Try to find timestamp in chat data
            chat_str = json.dumps(chat, default=str)
            
            # Look for common timestamp patterns
            timestamp_patterns = [
                r'"timestamp":\s*(\d+)',
                r'"createdAt":\s*"([^"]+)"',
                r'"date":\s*"([^"]+)"',
                r'"time":\s*(\d+)',
            ]
            
            for pattern in timestamp_patterns:
                match = re.search(pattern, chat_str)
                if match:
                    try:
                        ts = match.group(1)
                        if ts.isdigit():
                            # Unix timestamp (milliseconds or seconds)
                            if len(ts) > 10:
                                ts = int(ts) / 1000
                            chat_time = datetime.fromtimestamp(int(ts))
                        else:
                            chat_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        
                        if start_time <= chat_time <= end_time:
                            filtered.append(chat)
                            break
                    except:
                        pass
            else:
                # If no timestamp found, include by default
                filtered.append(chat)
        
        return filtered
    
    def save_extracted_chats(self, output_path: Path, 
                             format: str = "json") -> str:
        """Save extracted chats to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "extraction_report": self.extraction_report,
                    "chats": self.extracted_chats
                }, f, ensure_ascii=False, indent=2, default=str)
        
        elif format == "markdown":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Cursor Chat Recovery\n\n")
                f.write(f"Extracted: {self.extraction_report['timestamp']}\n\n")
                f.write(f"## Summary\n\n")
                f.write(f"- Databases scanned: {self.extraction_report['databases_scanned']}\n")
                f.write(f"- Chats found: {self.extraction_report['chats_found']}\n\n")
                
                for i, chat in enumerate(self.extracted_chats, 1):
                    f.write(f"## Chat {i}\n\n")
                    f.write(f"**Workspace:** {chat.get('workspace_id', 'unknown')}\n\n")
                    f.write(f"**Key:** `{chat.get('key', 'unknown')}`\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(chat.get('data', chat.get('data_raw', {})), 
                                      indent=2, default=str)[:5000])
                    f.write("\n```\n\n")
        
        return str(output_path)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate extraction report"""
        return self.extraction_report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract AI chat history from Cursor's workspace storage"
    )
    parser.add_argument(
        "--workspace-storage", "-w",
        help="Path to Cursor's workspaceStorage folder"
    )
    parser.add_argument(
        "--output", "-o",
        default="chat_recovery",
        help="Output directory for extracted chats"
    )
    parser.add_argument(
        "--backup-first", "-b",
        action="store_true",
        help="Create backup copies of databases before reading"
    )
    parser.add_argument(
        "--keywords", "-k",
        nargs="+",
        help="Filter by keywords (e.g., function names, class names)"
    )
    parser.add_argument(
        "--start-time",
        help="Filter start time (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    parser.add_argument(
        "--end-time",
        help="Filter end time (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON to stdout"
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = CursorChatExtractor(args.workspace_storage)
    
    if not extractor.workspace_storage:
        print("❌ Could not find Cursor workspace storage.")
        print("\nTried these locations:")
        print("  - ~/Library/Application Support/Cursor/User/workspaceStorage (macOS)")
        print("  - ~/.config/Cursor/User/workspaceStorage (Linux)")
        print("  - ~/AppData/Roaming/Cursor/User/workspaceStorage (Windows)")
        print("\nPlease specify the path with --workspace-storage")
        sys.exit(1)
    
    print(f"🔍 Scanning workspace storage: {extractor.workspace_storage}")
    
    # Set up backup directory
    backup_dir = None
    if args.backup_first:
        backup_dir = Path(args.output) / "db_backups"
        print(f"📦 Creating database backups in: {backup_dir}")
    
    # Set up time filter
    time_filter = None
    if args.start_time and args.end_time:
        try:
            start = datetime.fromisoformat(args.start_time)
            end = datetime.fromisoformat(args.end_time)
            time_filter = (start, end)
            print(f"⏰ Filtering by time: {start} to {end}")
        except ValueError as e:
            print(f"⚠️ Invalid time format: {e}")
    
    # Scan all workspaces
    chats = extractor.scan_all_workspaces(backup_dir=backup_dir, time_filter=time_filter)
    
    # Apply keyword filter
    if args.keywords:
        print(f"🔎 Filtering by keywords: {args.keywords}")
        chats = extractor.filter_by_keywords(chats, args.keywords)
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"chat_recovery_{timestamp}.{args.format}"
    
    extractor.save_extracted_chats(output_file, format=args.format)
    
    # Print summary
    report = extractor.generate_report()
    
    if args.json_output:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"  Databases scanned: {report['databases_scanned']}")
        print(f"  Chats found: {report['chats_found']}")
        print(f"  Output saved to: {output_file}")
        
        if report['workspaces']:
            print("\n📁 Workspaces with chat data:")
            for ws in report['workspaces']:
                print(f"  - {ws['id']}: {ws['chats_found']} chats")
                if 'project' in ws:
                    print(f"    Project: {ws['project']}")
        
        if report['errors']:
            print("\n⚠️ Errors encountered:")
            for error in report['errors'][:5]:
                print(f"  - {error}")
        
        print("=" * 60)


if __name__ == "__main__":
    main()
