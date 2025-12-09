#!/usr/bin/env python3
"""
Extract Composer/Unsaved Buffer Data from Cursor databases
Extracts data from Cursor's composer state that may contain unsaved code edits
"""
import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

def parse_timestamp(ts):
    """Parse various timestamp formats"""
    if isinstance(ts, (int, float)):
        if ts > 1e12:
            return datetime.fromtimestamp(ts / 1000)
        else:
            return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(ts, fmt)
                except:
                    continue
    return None

def extract_composer_data(db_path):
    """Extract composer-related data from database"""
    if not os.path.exists(db_path):
        return []
    
    composer_data = []
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Composer-related keys to search for
        composer_keys = [
            'composerData',
            'chat.composer',
            'composer.state',
            'composer.context',
            'composer.edits',
            'composer.unsaved',
            'workspace.unsaved',
            'editor.unsaved',
            'file.unsaved'
        ]
        
        # Search in ItemTable
        for table in tables:
            if 'item' in table.lower():
                try:
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
                        # Search for composer keys
                        for composer_key in composer_keys:
                            try:
                                cursor.execute(f"SELECT {key_col}, {value_col} FROM {table} WHERE {key_col} LIKE ?", 
                                             (f"%{composer_key}%",))
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
                                    
                                    composer_data.append({
                                        'key': key,
                                        'data': parsed,
                                        'source_db': db_path,
                                        'table': table,
                                        'extracted_at': datetime.now().isoformat()
                                    })
                            except sqlite3.Error:
                                continue
                
                except sqlite3.Error:
                    continue
        
        # Also search for any key containing "composer" or "unsaved"
        for table in tables:
            if 'item' in table.lower():
                try:
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
                        cursor.execute(f"SELECT {key_col}, {value_col} FROM {table} WHERE LOWER({key_col}) LIKE ? OR LOWER({key_col}) LIKE ?", 
                                     ('%composer%', '%unsaved%'))
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            key = row[key_col]
                            value = row[value_col]
                            
                            # Skip if already captured
                            if any(item['key'] == key for item in composer_data):
                                continue
                            
                            if not value:
                                continue
                            
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8')
                                except:
                                    continue
                            
                            try:
                                parsed = json.loads(value) if isinstance(value, str) else value
                            except:
                                parsed = value
                            
                            composer_data.append({
                                'key': key,
                                'data': parsed,
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
    
    return composer_data

def extract_code_from_composer(data, path=""):
    """Recursively extract code-like content from composer data"""
    code_items = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 20:
                # Check if it looks like code
                code_indicators = ['def ', 'function', 'class ', 'import ', 'export ', 
                                 'const ', 'let ', 'var ', '{', '}', '(', ')', 
                                 '=>', '->', 'return ', 'if ', 'for ', 'while ']
                
                if any(indicator in value for indicator in code_indicators):
                    code_items.append({
                        'path': f"{path}.{key}",
                        'code': value,
                        'length': len(value)
                    })
            
            # Recursively search
            code_items.extend(extract_code_from_composer(value, f"{path}.{key}"))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            code_items.extend(extract_code_from_composer(item, f"{path}[{i}]"))
    
    elif isinstance(data, str) and len(data) > 50:
        code_indicators = ['def ', 'function', 'class ', 'import ']
        if any(indicator in data for indicator in code_indicators):
            code_items.append({
                'path': path,
                'code': data,
                'length': len(data)
            })
    
    return code_items

def format_composer_markdown(item, index):
    """Format composer data as markdown"""
    md = f"## Composer Item {index + 1}\n\n"
    md += f"**Source Database:** `{os.path.basename(item['source_db'])}`\n\n"
    md += f"**Key:** `{item['key']}`\n\n"
    md += f"**Extracted At:** {item['extracted_at']}\n\n"
    
    # Extract code snippets
    code_items = extract_code_from_composer(item['data'])
    if code_items:
        md += f"**Found {len(code_items)} code-like content(s):**\n\n"
        for code_item in code_items[:5]:  # Limit to 5
            md += f"### From {code_item['path']}\n\n"
            md += f"*Length: {code_item['length']} characters*\n\n"
            md += "```\n"
            # Show first 1000 chars
            md += code_item['code'][:1000]
            if len(code_item['code']) > 1000:
                md += f"\n... (truncated, {len(code_item['code']) - 1000} more characters)"
            md += "\n```\n\n"
    
    # Full data
    md += "**Full Data:**\n\n"
    md += "```json\n"
    md += json.dumps(item['data'], indent=2, ensure_ascii=False, default=str)
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
    
    # Also check original locations
    global_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
    if os.path.exists(global_db):
        db_paths.append(global_db)
    
    workspace_storage = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage")
    if os.path.exists(workspace_storage):
        workspaces = []
        for root, dirs, files in os.walk(workspace_storage):
            if "state.vscdb" in files:
                db_path = os.path.join(root, "state.vscdb")
                mtime = os.path.getmtime(db_path)
                workspaces.append((mtime, db_path))
        
        workspaces.sort(reverse=True)
        for _, db_path in workspaces[:5]:
            db_paths.append(db_path)
    
    print(f"Found {len(db_paths)} database files to scan")
    
    all_composer_data = []
    for db_path in db_paths:
        print(f"\nScanning: {os.path.basename(db_path)}")
        composer_data = extract_composer_data(db_path)
        all_composer_data.extend(composer_data)
        print(f"  Extracted {len(composer_data)} composer items")
    
    print(f"\nTotal composer items found: {len(all_composer_data)}")
    
    # Write markdown output
    output_md = os.path.join(workspace_path, "recovery_composer_data.md")
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# Composer/Unsaved Buffer Data\n\n")
        f.write(f"**Extraction Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Items:** {len(all_composer_data)}\n\n")
        f.write("---\n\n")
        
        for i, item in enumerate(all_composer_data):
            f.write(format_composer_markdown(item, i))
    
    print(f"Markdown output written to: {output_md}")
    
    # Write JSON output
    output_json = os.path.join(workspace_path, "recovery_composer_data.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'extraction_date': datetime.now().isoformat(),
            'total_items': len(all_composer_data),
            'items': all_composer_data
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"JSON output written to: {output_json}")
    
    return len(all_composer_data)

if __name__ == "__main__":
    main()

