#!/usr/bin/env python3
"""
Periodic Chat Export Automation
Exports Cursor chat history to markdown files on a schedule
"""
import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import recovery scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from recovery_extract_recent_chats import extract_chat_sessions
except ImportError:
    print("Warning: Could not import recovery_extract_recent_chats. Using basic extraction.")
    extract_chat_sessions = None

def export_chat_history(workspace_path, hours=24, output_dir=None):
    """Export chat history for the specified time window"""
    if output_dir is None:
        output_dir = os.path.join(workspace_path, "chat_exports")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"chat_export_{timestamp}.json")
    
    # Find databases
    db_paths = []
    
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
    
    all_sessions = []
    for db_path in db_paths:
        if extract_chat_sessions:
            sessions = extract_chat_sessions(db_path)
        else:
            # Basic extraction
            sessions = []
        all_sessions.extend(sessions)
    
    # Save export
    export_data = {
        'export_date': datetime.now().isoformat(),
        'time_window_hours': hours,
        'total_sessions': len(all_sessions),
        'sessions': all_sessions
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"Chat export saved to: {output_file}")
    print(f"Exported {len(all_sessions)} sessions")
    
    # Clean up old exports (keep last 30 days)
    cleanup_old_exports(output_dir, days=30)
    
    return output_file

def cleanup_old_exports(output_dir, days=30):
    """Remove exports older than specified days"""
    cutoff = datetime.now() - timedelta(days=days)
    
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if file.startswith("chat_export_") and file.endswith(".json"):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    os.remove(file_path)
                    print(f"Removed old export: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")

def main():
    """Main export function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export Cursor chat history')
    parser.add_argument('--workspace', default='/Users/matias/chatbot2511/chatbot-2311',
                       help='Workspace path')
    parser.add_argument('--hours', type=int, default=24,
                       help='Time window in hours')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory for exports')
    
    args = parser.parse_args()
    
    workspace_path = os.path.abspath(args.workspace)
    export_chat_history(workspace_path, hours=args.hours, output_dir=args.output_dir)

if __name__ == "__main__":
    main()

