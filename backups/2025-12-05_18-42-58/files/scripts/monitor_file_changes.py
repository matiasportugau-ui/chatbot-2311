#!/usr/bin/env python3
"""
File Change Monitor
Watches for unsaved changes and creates snapshots
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, workspace_path, snapshot_dir):
        self.workspace_path = workspace_path
        self.snapshot_dir = snapshot_dir
        self.changes_log = []
        os.makedirs(snapshot_dir, exist_ok=True)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        # Skip recovery and log files
        if any(skip in event.src_path for skip in ['recovery_', '.git/', 'node_modules/', '__pycache__']):
            return
        
        file_path = event.src_path
        rel_path = os.path.relpath(file_path, self.workspace_path)
        
        change_record = {
            'timestamp': datetime.now().isoformat(),
            'file': rel_path,
            'event': 'modified',
            'full_path': file_path
        }
        
        self.changes_log.append(change_record)
        
        # Log change (don't create snapshot for every change to avoid disk spam)
        if len(self.changes_log) % 10 == 0:  # Every 10 changes
            self.save_snapshot()
    
    def save_snapshot(self):
        """Save current changes log as snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = os.path.join(self.snapshot_dir, f"changes_snapshot_{timestamp}.json")
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump({
                'snapshot_date': datetime.now().isoformat(),
                'total_changes': len(self.changes_log),
                'changes': self.changes_log[-100:]  # Last 100 changes
            }, f, indent=2, ensure_ascii=False)
        
        # Clear log (keep last 100)
        self.changes_log = self.changes_log[-100:]

def monitor_workspace(workspace_path, snapshot_dir=None):
    """Monitor workspace for file changes"""
    if snapshot_dir is None:
        snapshot_dir = os.path.join(workspace_path, "file_change_snapshots")
    
    event_handler = FileChangeHandler(workspace_path, snapshot_dir)
    observer = Observer()
    observer.schedule(event_handler, workspace_path, recursive=True)
    observer.start()
    
    print(f"Monitoring workspace: {workspace_path}")
    print(f"Snapshots will be saved to: {snapshot_dir}")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped")
    
    observer.join()

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor workspace for file changes')
    parser.add_argument('--workspace', default='/Users/matias/chatbot2511/chatbot-2311',
                       help='Workspace path to monitor')
    parser.add_argument('--snapshot-dir', default=None,
                       help='Directory for change snapshots')
    
    args = parser.parse_args()
    
    workspace_path = os.path.abspath(args.workspace)
    
    if not os.path.exists(workspace_path):
        print(f"Error: Workspace path does not exist: {workspace_path}")
        return 1
    
    try:
        monitor_workspace(workspace_path, args.snapshot_dir)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

