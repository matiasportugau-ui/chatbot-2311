#!/usr/bin/env python3
"""
RecoveryAgent: Extract file history from Cursor's History folder
"""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import re

def find_project_history(history_base, project_path):
    """Find history entries related to the current project"""
    project_name = os.path.basename(project_path)
    project_parent = os.path.basename(os.path.dirname(project_path))
    
    relevant_entries = []
    
    if not os.path.exists(history_base):
        return relevant_entries
    
    # Walk through history directories
    for root, dirs, files in os.walk(history_base):
        if "entries.json" in files:
            entries_path = os.path.join(root, "entries.json")
            try:
                with open(entries_path, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
                
                # Check each entry
                for entry in entries:
                    if isinstance(entry, dict):
                        # Check if path matches project
                        entry_path = entry.get('resource', {}).get('fsPath', '') or entry.get('path', '')
                        
                        if project_name.lower() in entry_path.lower() or project_parent.lower() in entry_path.lower():
                            # Get the history folder for this entry
                            history_folder = root
                            entry_id = entry.get('id') or entry.get('resource', {}).get('path', '')
                            
                            relevant_entries.append({
                                'entry': entry,
                                'history_folder': history_folder,
                                'entry_id': entry_id,
                                'path': entry_path
                            })
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not read {entries_path}: {e}")
                continue
    
    return relevant_entries

def restore_file_from_history(entry_info, project_path, restore_dir):
    """Restore a file from history to the restore directory"""
    history_folder = entry_info['history_folder']
    entry = entry_info['entry']
    entry_path = entry_info['path']
    
    # Find the actual file in history
    # History structure: History/{hash}/entries.json and files in subdirectories
    restored_files = []
    
    # Look for file versions in the history folder
    for root, dirs, files in os.walk(history_folder):
        for file in files:
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.txt', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                
                # Get relative path from project
                try:
                    rel_path = os.path.relpath(entry_path, project_path)
                    if rel_path.startswith('..'):
                        continue
                    
                    # Create restore path
                    restore_path = os.path.join(restore_dir, rel_path)
                    os.makedirs(os.path.dirname(restore_path), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(file_path, restore_path)
                    restored_files.append({
                        'original': entry_path,
                        'restored': restore_path,
                        'timestamp': os.path.getmtime(file_path)
                    })
                except Exception as e:
                    print(f"Warning: Could not restore {file_path}: {e}")
                    continue
    
    return restored_files

def main():
    """Main history recovery function"""
    project_path = "/Users/matias/chatbot2511/chatbot-2311"
    history_base = os.path.expanduser("~/Library/Application Support/Cursor/User/History")
    restore_dir = os.path.join(project_path, "restored")
    
    # Create restore directory
    os.makedirs(restore_dir, exist_ok=True)
    
    print(f"Searching for history entries related to: {project_path}")
    print(f"History base: {history_base}")
    
    relevant_entries = find_project_history(history_base, project_path)
    
    print(f"\nFound {len(relevant_entries)} relevant history entries")
    
    restored_files = []
    for entry_info in relevant_entries:
        files = restore_file_from_history(entry_info, project_path, restore_dir)
        restored_files.extend(files)
    
    # Write summary
    summary_file = os.path.join(project_path, "recovery_history_summary.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# File History Recovery Summary\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Project Path:** `{project_path}`\n\n")
        f.write(f"**History Entries Found:** {len(relevant_entries)}\n\n")
        f.write(f"**Files Restored:** {len(restored_files)}\n\n")
        f.write("---\n\n")
        
        if restored_files:
            f.write("## Restored Files\n\n")
            for file_info in restored_files:
                f.write(f"- **{file_info['restored']}**\n")
                f.write(f"  - Original: `{file_info['original']}`\n")
                f.write(f"  - Timestamp: {datetime.fromtimestamp(file_info['timestamp']).isoformat()}\n\n")
        else:
            f.write("## No Files Restored\n\n")
            f.write("No matching file versions found in history.\n\n")
        
        if relevant_entries:
            f.write("## History Entries Found\n\n")
            for i, entry_info in enumerate(relevant_entries[:20], 1):  # Limit to first 20
                f.write(f"### Entry {i}\n\n")
                f.write(f"**Path:** `{entry_info['path']}`\n\n")
                f.write(f"**History Folder:** `{entry_info['history_folder']}`\n\n")
                f.write("**Entry Data:**\n\n")
                f.write("```json\n")
                f.write(json.dumps(entry_info['entry'], indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
                f.write("---\n\n")
    
    print(f"\nHistory recovery complete!")
    print(f"  - Found {len(relevant_entries)} relevant entries")
    print(f"  - Restored {len(restored_files)} files to {restore_dir}")
    print(f"  - Summary written to {summary_file}")
    
    return len(restored_files)

if __name__ == "__main__":
    main()

