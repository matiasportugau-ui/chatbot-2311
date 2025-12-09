#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Chat History Extractor
Extracts AI chat history and context from Cursor's state.vscdb SQLite database

Usage:
    python extract_cursor_chat.py --db-path <path_to_state.vscdb> --output chat.json
    python extract_cursor_chat.py --scan  # Auto-scan for workspace storage
"""

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class CursorChatExtractor:
    """Extract chat history from Cursor workspace storage"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.chat_data = {
            "extraction_time": datetime.now().isoformat(),
            "source_db": str(db_path) if db_path else None,
            "conversations": [],
            "context_items": [],
            "composer_history": [],
            "metadata": {}
        }
    
    def find_workspace_storage(self, project_path: Optional[str] = None) -> List[Path]:
        """Find Cursor workspace storage directories"""
        possible_locations = []
        
        # Standard locations by OS
        home = Path.home()
        
        # Linux/Ubuntu
        linux_storage = home / ".config" / "Cursor" / "User" / "workspaceStorage"
        if linux_storage.exists():
            possible_locations.append(linux_storage)
        
        # Alternative Linux location
        linux_alt = home / ".cursor" / "User" / "workspaceStorage"
        if linux_alt.exists():
            possible_locations.append(linux_alt)
        
        # macOS
        macos_storage = home / "Library" / "Application Support" / "Cursor" / "User" / "workspaceStorage"
        if macos_storage.exists():
            possible_locations.append(macos_storage)
        
        # Windows
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            if appdata:
                win_storage = Path(appdata) / "Cursor" / "User" / "workspaceStorage"
                if win_storage.exists():
                    possible_locations.append(win_storage)
        
        # Find workspaces
        found_dbs = []
        for location in possible_locations:
            for workspace_dir in location.iterdir():
                if workspace_dir.is_dir():
                    db_file = workspace_dir / "state.vscdb"
                    if db_file.exists():
                        # Try to match project if specified
                        if project_path:
                            workspace_json = workspace_dir / "workspace.json"
                            if workspace_json.exists():
                                try:
                                    with open(workspace_json) as f:
                                        ws_data = json.load(f)
                                        if project_path in str(ws_data.get("folder", "")):
                                            found_dbs.insert(0, db_file)
                                        else:
                                            found_dbs.append(db_file)
                                except:
                                    found_dbs.append(db_file)
                            else:
                                found_dbs.append(db_file)
                        else:
                            found_dbs.append(db_file)
        
        return found_dbs
    
    def connect_db(self, db_path: str) -> sqlite3.Connection:
        """Connect to SQLite database in read-only mode"""
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        # Connect in read-only mode
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    
    def extract_chat_items(
        self, 
        conn: sqlite3.Connection,
        keywords: Optional[List[str]] = None,
        since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract chat-related items from ItemTable"""
        cursor = conn.cursor()
        
        # Query for chat-related keys
        chat_patterns = [
            '%aichat%',
            '%composer%',
            '%chat%',
            '%conversation%',
            '%ai.history%',
            '%cursor.chat%',
            '%workbench.panel.aichat%'
        ]
        
        items = []
        
        for pattern in chat_patterns:
            cursor.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE ?",
                (pattern,)
            )
            
            for row in cursor.fetchall():
                try:
                    key = row['key']
                    value = row['value']
                    
                    # Try to parse as JSON
                    try:
                        value_json = json.loads(value)
                    except:
                        value_json = {"raw": value}
                    
                    item = {
                        "key": key,
                        "value": value_json,
                        "raw_value": value
                    }
                    
                    # Filter by keywords if specified
                    if keywords:
                        value_str = json.dumps(value_json).lower()
                        if any(kw.lower() in value_str for kw in keywords):
                            items.append(item)
                    else:
                        items.append(item)
                
                except Exception as e:
                    print(f"Warning: Failed to process row {row['key']}: {e}")
        
        return items
    
    def extract_all_items(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Extract all items from ItemTable for inspection"""
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM ItemTable")
        
        items = []
        for row in cursor.fetchall():
            items.append({
                "key": row['key'],
                "value_preview": row['value'][:200] if len(row['value']) > 200 else row['value']
            })
        
        return items
    
    def parse_chat_data(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse extracted items into structured chat data"""
        conversations = []
        context_items = []
        composer_history = []
        
        for item in items:
            key = item['key']
            value = item['value']
            
            # Classify by key pattern
            if 'composer' in key.lower():
                composer_history.append({
                    "key": key,
                    "data": value,
                    "extracted_at": datetime.now().isoformat()
                })
            elif 'chat' in key.lower() or 'conversation' in key.lower():
                conversations.append({
                    "key": key,
                    "data": value,
                    "extracted_at": datetime.now().isoformat()
                })
            else:
                context_items.append({
                    "key": key,
                    "data": value,
                    "extracted_at": datetime.now().isoformat()
                })
        
        return {
            "conversations": conversations,
            "context_items": context_items,
            "composer_history": composer_history
        }
    
    def extract(
        self,
        keywords: Optional[List[str]] = None,
        since: Optional[str] = None,
        inspect_all: bool = False
    ) -> Dict[str, Any]:
        """Main extraction method"""
        if not self.db_path:
            raise ValueError("No database path specified")
        
        print(f"📂 Opening database: {self.db_path}")
        conn = self.connect_db(str(self.db_path))
        
        if inspect_all:
            print("🔍 Inspecting all items in database...")
            all_items = self.extract_all_items(conn)
            print(f"✅ Found {len(all_items)} total items")
            self.chat_data["all_items"] = all_items
        
        print("🔍 Extracting chat-related items...")
        items = self.extract_chat_items(conn, keywords, since)
        print(f"✅ Found {len(items)} chat-related items")
        
        if not items:
            print("⚠️  No chat items found. Try --inspect-all to see all database keys.")
        
        print("📊 Parsing chat data...")
        parsed = self.parse_chat_data(items)
        
        self.chat_data.update(parsed)
        self.chat_data["metadata"] = {
            "total_items": len(items),
            "conversations_found": len(parsed["conversations"]),
            "context_items_found": len(parsed["context_items"]),
            "composer_items_found": len(parsed["composer_history"]),
            "keywords_used": keywords or [],
            "since_filter": since or None
        }
        
        conn.close()
        print("✅ Extraction complete")
        
        return self.chat_data
    
    def export_json(self, output_path: str):
        """Export to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.chat_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to: {output_path}")
    
    def export_markdown(self, output_path: str):
        """Export to Markdown file"""
        md_lines = [
            "# Cursor Chat History Recovery",
            "",
            f"**Extracted:** {self.chat_data['extraction_time']}",
            f"**Source:** `{self.chat_data['source_db']}`",
            "",
            "---",
            ""
        ]
        
        # Metadata
        meta = self.chat_data.get("metadata", {})
        md_lines.extend([
            "## Summary",
            "",
            f"- **Total Items:** {meta.get('total_items', 0)}",
            f"- **Conversations:** {meta.get('conversations_found', 0)}",
            f"- **Context Items:** {meta.get('context_items_found', 0)}",
            f"- **Composer History:** {meta.get('composer_items_found', 0)}",
            ""
        ])
        
        # Conversations
        if self.chat_data.get("conversations"):
            md_lines.extend([
                "## Conversations",
                ""
            ])
            
            for i, conv in enumerate(self.chat_data["conversations"], 1):
                md_lines.append(f"### Conversation {i}")
                md_lines.append(f"**Key:** `{conv['key']}`")
                md_lines.append("")
                md_lines.append("```json")
                md_lines.append(json.dumps(conv['data'], indent=2))
                md_lines.append("```")
                md_lines.append("")
        
        # Composer History
        if self.chat_data.get("composer_history"):
            md_lines.extend([
                "## Composer History",
                ""
            ])
            
            for i, item in enumerate(self.chat_data["composer_history"], 1):
                md_lines.append(f"### Item {i}")
                md_lines.append(f"**Key:** `{item['key']}`")
                md_lines.append("")
                md_lines.append("```json")
                md_lines.append(json.dumps(item['data'], indent=2))
                md_lines.append("```")
                md_lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        print(f"📝 Markdown saved to: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract Cursor chat history from state.vscdb",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from specific database
  python extract_cursor_chat.py --db-path ~/.config/Cursor/User/workspaceStorage/abc123/state.vscdb
  
  # Auto-scan for workspaces
  python extract_cursor_chat.py --scan
  
  # Extract with keyword filter
  python extract_cursor_chat.py --db-path <path> --keywords MongoDB fix error --output recovery.json
  
  # Extract to markdown
  python extract_cursor_chat.py --db-path <path> --format markdown --output chat.md
  
  # Inspect all database keys
  python extract_cursor_chat.py --db-path <path> --inspect-all
        """
    )
    
    parser.add_argument(
        "--db-path",
        help="Path to state.vscdb file"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for workspace storage directories"
    )
    parser.add_argument(
        "--project-path",
        help="Project path to match (for --scan)"
    )
    parser.add_argument(
        "--output",
        default=f"cursor_chat_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output file path"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Filter by keywords"
    )
    parser.add_argument(
        "--since",
        help="Filter by date (ISO format: 2025-12-01)"
    )
    parser.add_argument(
        "--inspect-all",
        action="store_true",
        help="Inspect all items in database (for debugging)"
    )
    
    args = parser.parse_args()
    
    # Scan mode
    if args.scan:
        print("🔍 Scanning for Cursor workspace storage...")
        extractor = CursorChatExtractor()
        found_dbs = extractor.find_workspace_storage(args.project_path)
        
        if not found_dbs:
            print("❌ No workspace storage found")
            print("\nSearched in:")
            print("  - ~/.config/Cursor/User/workspaceStorage/")
            print("  - ~/.cursor/User/workspaceStorage/")
            print("  - ~/Library/Application Support/Cursor/User/workspaceStorage/ (macOS)")
            print("  - %APPDATA%/Cursor/User/workspaceStorage/ (Windows)")
            sys.exit(1)
        
        print(f"\n✅ Found {len(found_dbs)} workspace(s):\n")
        for i, db_path in enumerate(found_dbs, 1):
            workspace_id = db_path.parent.name
            print(f"  {i}. {workspace_id}")
            print(f"     {db_path}")
            print()
        
        if len(found_dbs) == 1:
            selected = found_dbs[0]
            print(f"Using: {selected}\n")
        else:
            choice = input(f"Select workspace (1-{len(found_dbs)}, or 'all'): ")
            if choice.lower() == 'all':
                selected = found_dbs
            else:
                try:
                    idx = int(choice) - 1
                    selected = found_dbs[idx]
                except (ValueError, IndexError):
                    print("Invalid selection")
                    sys.exit(1)
        
        # Process selected workspace(s)
        if isinstance(selected, list):
            for db_path in selected:
                process_database(db_path, args)
        else:
            process_database(selected, args)
        
        return
    
    # Direct path mode
    if not args.db_path:
        print("❌ Error: Either --db-path or --scan is required")
        parser.print_help()
        sys.exit(1)
    
    process_database(args.db_path, args)


def process_database(db_path: Path, args):
    """Process a single database"""
    extractor = CursorChatExtractor(db_path=str(db_path))
    
    try:
        data = extractor.extract(
            keywords=args.keywords,
            since=args.since,
            inspect_all=args.inspect_all
        )
        
        # Export based on format
        if args.format in ["json", "both"]:
            output_path = args.output
            if not output_path.endswith(".json"):
                output_path += ".json"
            extractor.export_json(output_path)
        
        if args.format in ["markdown", "both"]:
            md_output = args.output.replace(".json", ".md")
            if not md_output.endswith(".md"):
                md_output += ".md"
            extractor.export_markdown(md_output)
        
        # Print summary
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"Conversations: {len(data['conversations'])}")
        print(f"Context Items: {len(data['context_items'])}")
        print(f"Composer History: {len(data['composer_history'])}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
