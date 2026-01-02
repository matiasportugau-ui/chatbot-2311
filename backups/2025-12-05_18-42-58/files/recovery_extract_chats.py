#!/usr/bin/env python3
"""
RecoveryAgent: Extract chat history from Cursor's SQLite databases
"""
import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

def backup_database(db_path, backup_dir="/tmp"):
    """Create a backup of the database before reading"""
    if not os.path.exists(db_path):
        return None
    
    db_name = os.path.basename(db_path)
    db_hash = db_name.replace('.vscdb', '')[:16]
    backup_path = os.path.join(backup_dir, f"backup_{db_hash}.vscdb")
    
    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Warning: Could not backup {db_path}: {e}")
        return None

def extract_chat_data(db_path, output_file):
    """Extract chat-related data from a Cursor database"""
    if not os.path.exists(db_path):
        return []
    
    backup_path = backup_database(db_path)
    if backup_path:
        print(f"Backed up database to: {backup_path}")
    
    extracted_data = []
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Look for chat-related keys in ItemTable (common VS Code/Cursor pattern)
        chat_patterns = [
            'composerData',
            'aichat',
            'prompts',
            'chat',
            'fileActions',
            'cursor.chat',
            'cursor.composer'
        ]
        
        # Try to find ItemTable or similar
        for table in tables:
            if 'item' in table.lower() or 'key' in table.lower():
                try:
                    # Try different column name patterns
                    for col_pattern in ['key', 'name', 'id']:
                        try:
                            cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                            columns = [description[0] for description in cursor.description]
                            
                            key_col = None
                            value_col = None
                            
                            for col in columns:
                                if col.lower() in ['key', 'name', 'id']:
                                    key_col = col
                                if col.lower() in ['value', 'data', 'content', 'text']:
                                    value_col = col
                            
                            if key_col and value_col:
                                cursor.execute(f"SELECT {key_col}, {value_col} FROM {table}")
                                rows = cursor.fetchall()
                                
                                for key, value in rows:
                                    if not key or not value:
                                        continue
                                    
                                    key_str = str(key).lower()
                                    # Check if this key matches our patterns
                                    if any(pattern.lower() in key_str for pattern in chat_patterns):
                                        try:
                                            # Try to parse as JSON
                                            if isinstance(value, bytes):
                                                value = value.decode('utf-8', errors='ignore')
                                            
                                            parsed_value = json.loads(value) if isinstance(value, str) else value
                                            
                                            extracted_data.append({
                                                'key': key,
                                                'value': parsed_value,
                                                'table': table,
                                                'source': db_path
                                            })
                                        except (json.JSONDecodeError, UnicodeDecodeError):
                                            # Not JSON, but might still be relevant
                                            if any(pattern.lower() in key_str for pattern in chat_patterns):
                                                extracted_data.append({
                                                    'key': key,
                                                    'value': str(value)[:1000],  # Truncate long values
                                                    'table': table,
                                                    'source': db_path,
                                                    'raw': True
                                                })
                        except sqlite3.Error:
                            continue
                except sqlite3.Error:
                    continue
        
        # Also try direct queries for known patterns
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    for col, val in row_dict.items():
                        if val and isinstance(val, (str, bytes)):
                            val_str = str(val).lower() if isinstance(val, str) else val.decode('utf-8', errors='ignore').lower()
                            if any(pattern in val_str for pattern in ['chat', 'composer', 'prompt', 'ai']):
                                extracted_data.append({
                                    'key': f"{table}.{col}",
                                    'value': str(val)[:2000],
                                    'table': table,
                                    'source': db_path
                                })
            except sqlite3.Error:
                continue
        
        conn.close()
        
    except Exception as e:
        print(f"Error extracting from {db_path}: {e}")
        return []
    
    return extracted_data

def main():
    """Main recovery function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    output_file = os.path.join(workspace_path, "RecoveredChats.md")
    
    # Find all database files
    db_paths = []
    
    # Global storage
    global_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
    if os.path.exists(global_db):
        db_paths.append(global_db)
    
    # Workspace storage - check all
    workspace_storage = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage")
    if os.path.exists(workspace_storage):
        for root, dirs, files in os.walk(workspace_storage):
            if "state.vscdb" in files:
                db_paths.append(os.path.join(root, "state.vscdb"))
    
    print(f"Found {len(db_paths)} database files to scan")
    
    all_extracted = []
    for db_path in db_paths:
        print(f"\nScanning: {db_path}")
        extracted = extract_chat_data(db_path, output_file)
        all_extracted.extend(extracted)
        print(f"  Extracted {len(extracted)} items")
    
    # Write recovered chats to markdown
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Recovered Chat History\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Items Recovered:** {len(all_extracted)}\n\n")
        f.write("---\n\n")
        
        for i, item in enumerate(all_extracted, 1):
            f.write(f"## Item {i}\n\n")
            f.write(f"**Source:** `{item['source']}`\n\n")
            f.write(f"**Table:** `{item['table']}`\n\n")
            f.write(f"**Key:** `{item['key']}`\n\n")
            f.write("**Content:**\n\n")
            
            if isinstance(item['value'], dict):
                f.write("```json\n")
                f.write(json.dumps(item['value'], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
            elif isinstance(item['value'], list):
                f.write("```json\n")
                f.write(json.dumps(item['value'], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
            else:
                f.write("```\n")
                f.write(str(item['value']))
                f.write("\n```\n\n")
            
            f.write("---\n\n")
    
    print(f"\nRecovery complete! Wrote {len(all_extracted)} items to {output_file}")
    
    # Also save as JSON for machine-readable format
    json_file = os.path.join(workspace_path, "recovered_chats.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_extracted, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Also saved JSON format to: {json_file}")
    
    return len(all_extracted)

if __name__ == "__main__":
    main()

