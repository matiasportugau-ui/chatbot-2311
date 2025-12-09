#!/usr/bin/env python3
"""
Enhanced Chat Extraction with Time Filtering
Extracts chat history from Cursor databases filtered by time window (last 24 hours)
"""
import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

def parse_timestamp(ts):
    """Parse various timestamp formats from Cursor data"""
    if isinstance(ts, (int, float)):
        # Unix timestamp in milliseconds
        if ts > 1e12:
            return datetime.fromtimestamp(ts / 1000)
        else:
            return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        # Try ISO format
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except:
            # Try other formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(ts, fmt)
                except:
                    continue
    return None

def extract_timestamp_from_data(data, path=""):
    """Recursively search for timestamps in data structure"""
    timestamps = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if 'time' in key.lower() or 'date' in key.lower() or 'timestamp' in key.lower():
                ts = parse_timestamp(value)
                if ts:
                    timestamps.append(ts)
            timestamps.extend(extract_timestamp_from_data(value, f"{path}.{key}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            timestamps.extend(extract_timestamp_from_data(item, f"{path}[{i}]"))
    
    return timestamps

def is_within_time_window(data, hours=24):
    """Check if data is within the specified time window"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Extract all timestamps from the data
    timestamps = extract_timestamp_from_data(data)
    
    if not timestamps:
        # If no timestamp found, include it (better safe than sorry)
        return True
    
    # Check if any timestamp is within the window
    for ts in timestamps:
        if ts >= cutoff_time:
            return True
    
    return False

def extract_chat_sessions(db_path):
    """Extract chat session data from database"""
    if not os.path.exists(db_path):
        return []
    
    sessions = []
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Look for ItemTable (VS Code/Cursor pattern)
        for table in tables:
            if 'item' in table.lower():
                try:
                    # Get column names
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                    columns = [desc[0] for desc in cursor.description]
                    
                    key_col = None
                    value_col = None
                    
                    for col in columns:
                        if col.lower() in ['key', 'name', 'id']:
                            key_col = col
                        if col.lower() in ['value', 'data', 'content', 'text']:
                            value_col = col
                    
                    if key_col and value_col:
                        # Query chat-related keys
                        chat_keys = [
                            'chat.ChatSessionStore',
                            'chat.ChatSessionStore.index',
                            'chat.composer',
                            'composerData',
                            'chat.customModes',
                            'chat.terminalSessions'
                        ]
                        
                        for chat_key in chat_keys:
                            try:
                                cursor.execute(f"SELECT {key_col}, {value_col} FROM {table} WHERE {key_col} LIKE ?", 
                                             (f"%{chat_key}%",))
                                rows = cursor.fetchall()
                                
                                for row in rows:
                                    key = row[key_col]
                                    value = row[value_col]
                                    
                                    if not value:
                                        continue
                                    
                                    # Decode if bytes
                                    if isinstance(value, bytes):
                                        try:
                                            value = value.decode('utf-8')
                                        except:
                                            continue
                                    
                                    # Parse JSON
                                    try:
                                        parsed = json.loads(value) if isinstance(value, str) else value
                                    except:
                                        parsed = value
                                    
                                    # Check time window
                                    if is_within_time_window(parsed, hours=24):
                                        sessions.append({
                                            'key': key,
                                            'data': parsed,
                                            'source_db': db_path,
                                            'table': table,
                                            'extracted_at': datetime.now().isoformat()
                                        })
                            except sqlite3.Error as e:
                                continue
                
                except sqlite3.Error:
                    continue
        
        # Also look for session data in other formats
        for table in tables:
            if 'session' in table.lower() or 'chat' in table.lower():
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        row_dict = dict(row)
                        if is_within_time_window(row_dict, hours=24):
                            sessions.append({
                                'key': f"{table}.row",
                                'data': row_dict,
                                'source_db': db_path,
                                'table': table,
                                'extracted_at': datetime.now().isoformat()
                            })
                except sqlite3.Error:
                    continue
        
        conn.close()
    
    except Exception as e:
        print(f"Error extracting from {db_path}: {e}")
        return []
    
    return sessions

def extract_code_context(session_data):
    """Extract code snippets and file references from session data"""
    code_snippets = []
    file_refs = []
    
    def search_for_code(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                if 'code' in key.lower() or 'content' in key.lower() or 'text' in key.lower():
                    if isinstance(value, str) and len(value) > 20:
                        # Check if it looks like code
                        if any(char in value for char in ['{', '(', 'def ', 'function', 'import', 'class ']):
                            code_snippets.append({
                                'path': f"{path}.{key}",
                                'code': value[:500]  # First 500 chars
                            })
                
                if 'file' in key.lower() or 'path' in key.lower():
                    if isinstance(value, str):
                        file_refs.append(value)
                
                search_for_code(value, f"{path}.{key}")
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                search_for_code(item, f"{path}[{i}]")
        
        elif isinstance(data, str) and len(data) > 50:
            # Check for file paths in strings
            path_pattern = r'[\/\w\-\.]+\.(py|js|ts|tsx|jsx|json|md|txt|yml|yaml)'
            matches = re.findall(path_pattern, data)
            file_refs.extend(matches)
    
    search_for_code(session_data)
    
    return {
        'code_snippets': code_snippets[:10],  # Limit to 10
        'file_references': list(set(file_refs))[:20]  # Unique, limit to 20
    }

def format_session_markdown(session, index):
    """Format a session as markdown"""
    md = f"## Session {index + 1}\n\n"
    md += f"**Source Database:** `{os.path.basename(session['source_db'])}`\n\n"
    md += f"**Key:** `{session['key']}`\n\n"
    md += f"**Extracted At:** {session['extracted_at']}\n\n"
    
    # Extract metadata
    data = session['data']
    if isinstance(data, dict):
        if 'title' in data:
            md += f"**Title:** {data['title']}\n\n"
        if 'sessionId' in data:
            md += f"**Session ID:** `{data['sessionId']}`\n\n"
        if 'lastMessageDate' in data:
            ts = parse_timestamp(data['lastMessageDate'])
            if ts:
                md += f"**Last Message:** {ts.isoformat()}\n\n"
    
    # Extract code context
    context = extract_code_context(data)
    if context['file_references']:
        md += "**File References:**\n\n"
        for ref in context['file_references']:
            md += f"- `{ref}`\n"
        md += "\n"
    
    if context['code_snippets']:
        md += "**Code Snippets:**\n\n"
        for snippet in context['code_snippets']:
            md += f"*From {snippet['path']}:*\n\n"
            md += "```\n"
            md += snippet['code']
            md += "\n```\n\n"
    
    # Full data
    md += "**Full Data:**\n\n"
    md += "```json\n"
    md += json.dumps(data, indent=2, ensure_ascii=False, default=str)
    md += "\n```\n\n"
    md += "---\n\n"
    
    return md

def main():
    """Main extraction function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    backup_dir = "/Users/matias/Desktop/cursor_workspace_backup_20251201_175806"
    
    # Read backup location if available
    backup_location_file = os.path.join(workspace_path, "recovery_backup_location.txt")
    if os.path.exists(backup_location_file):
        with open(backup_location_file, 'r') as f:
            backup_dir = f.read().strip()
    
    print(f"Using backup directory: {backup_dir}")
    
    # Find all backup databases
    db_paths = []
    
    if os.path.exists(backup_dir):
        for file in os.listdir(backup_dir):
            if file.endswith('.vscdb'):
                db_paths.append(os.path.join(backup_dir, file))
    
    # Also check original locations for most recent data
    global_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
    if os.path.exists(global_db):
        db_paths.append(global_db)
    
    workspace_storage = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage")
    if os.path.exists(workspace_storage):
        # Get most recently modified workspace (likely current project)
        workspaces = []
        for root, dirs, files in os.walk(workspace_storage):
            if "state.vscdb" in files:
                db_path = os.path.join(root, "state.vscdb")
                mtime = os.path.getmtime(db_path)
                workspaces.append((mtime, db_path))
        
        # Sort by modification time, get most recent
        workspaces.sort(reverse=True)
        for _, db_path in workspaces[:5]:  # Top 5 most recent
            db_paths.append(db_path)
    
    print(f"Found {len(db_paths)} database files to scan")
    
    all_sessions = []
    for db_path in db_paths:
        print(f"\nScanning: {os.path.basename(db_path)}")
        sessions = extract_chat_sessions(db_path)
        all_sessions.extend(sessions)
        print(f"  Extracted {len(sessions)} sessions within last 24 hours")
    
    print(f"\nTotal sessions found: {len(all_sessions)}")
    
    # Write markdown output
    output_md = os.path.join(workspace_path, "recovery_recent_chats.md")
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# Recent Chat History (Last 24 Hours)\n\n")
        f.write(f"**Extraction Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Sessions:** {len(all_sessions)}\n\n")
        f.write("---\n\n")
        
        for i, session in enumerate(all_sessions):
            f.write(format_session_markdown(session, i))
    
    print(f"Markdown output written to: {output_md}")
    
    # Write JSON output
    output_json = os.path.join(workspace_path, "recovery_recent_chats.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'extraction_date': datetime.now().isoformat(),
            'time_window_hours': 24,
            'total_sessions': len(all_sessions),
            'sessions': all_sessions
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"JSON output written to: {output_json}")
    
    return len(all_sessions)

if __name__ == "__main__":
    main()

