#!/usr/bin/env python3
"""
SQLite Database Deep Analysis
Performs deep analysis of Cursor databases to find deleted records,
WAL files, or journal entries that might contain lost data
"""
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

def check_wal_files(db_path):
    """Check for WAL (Write-Ahead Log) files"""
    wal_path = db_path + '-wal'
    shm_path = db_path + '-shm'
    
    results = {
        'wal_exists': os.path.exists(wal_path),
        'shm_exists': os.path.exists(shm_path),
        'wal_path': wal_path if os.path.exists(wal_path) else None,
        'shm_path': shm_path if os.path.exists(shm_path) else None
    }
    
    if results['wal_exists']:
        results['wal_size'] = os.path.getsize(wal_path)
        results['wal_mtime'] = datetime.fromtimestamp(os.path.getmtime(wal_path)).isoformat()
    
    return results

def check_journal_files(db_path):
    """Check for SQLite journal files"""
    journal_path = db_path + '-journal'
    
    results = {
        'journal_exists': os.path.exists(journal_path),
        'journal_path': journal_path if os.path.exists(journal_path) else None
    }
    
    if results['journal_exists']:
        results['journal_size'] = os.path.getsize(journal_path)
        results['journal_mtime'] = datetime.fromtimestamp(os.path.getmtime(journal_path)).isoformat()
    
    return results

def analyze_database_structure(db_path):
    """Analyze database structure and check for anomalies"""
    if not os.path.exists(db_path):
        return None
    
    analysis = {
        'db_path': db_path,
        'db_size': os.path.getsize(db_path),
        'db_mtime': datetime.fromtimestamp(os.path.getmtime(db_path)).isoformat(),
        'tables': [],
        'row_counts': {},
        'anomalies': []
    }
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        analysis['tables'] = tables
        
        # Count rows in each table
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                analysis['row_counts'][table] = count
            except sqlite3.Error as e:
                analysis['anomalies'].append(f"Error counting rows in {table}: {e}")
        
        # Check for uncommitted transactions (this is tricky, SQLite doesn't expose this easily)
        # We can check if WAL mode is enabled
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        analysis['journal_mode'] = journal_mode
        
        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        analysis['integrity_check'] = integrity
        
        # Get page count and size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        analysis['page_count'] = page_count
        
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        analysis['page_size'] = page_size
        
        conn.close()
    
    except Exception as e:
        analysis['error'] = str(e)
        analysis['anomalies'].append(f"Error analyzing database: {e}")
    
    return analysis

def search_for_deleted_patterns(db_path):
    """Search for patterns that might indicate deleted data"""
    # Note: SQLite doesn't easily expose deleted records without forensic tools
    # This is a basic check for common patterns
    
    patterns_found = []
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for tables with unusual row counts (might indicate deletions)
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Check if table has a deleted or removed column
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'deleted' in ' '.join(column_names).lower() or 'removed' in ' '.join(column_names).lower():
                    patterns_found.append({
                        'table': table,
                        'type': 'has_deleted_column',
                        'row_count': count
                    })
            except sqlite3.Error:
                pass
        
        conn.close()
    
    except Exception as e:
        patterns_found.append({
            'type': 'error',
            'message': str(e)
        })
    
    return patterns_found

def analyze_database(db_path):
    """Perform comprehensive analysis of a database"""
    print(f"\nAnalyzing: {os.path.basename(db_path)}")
    
    results = {
        'db_path': db_path,
        'analysis_time': datetime.now().isoformat(),
        'wal_files': check_wal_files(db_path),
        'journal_files': check_journal_files(db_path),
        'structure': analyze_database_structure(db_path),
        'deleted_patterns': search_for_deleted_patterns(db_path)
    }
    
    return results

def main():
    """Main analysis function"""
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
    
    print(f"Found {len(db_paths)} database files to analyze")
    
    all_analyses = []
    for db_path in db_paths:
        analysis = analyze_database(db_path)
        all_analyses.append(analysis)
    
    # Write JSON output
    output_json = os.path.join(workspace_path, "recovery_deep_analysis.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_databases': len(all_analyses),
            'analyses': all_analyses
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nAnalysis complete! Results written to: {output_json}")
    
    # Print summary
    print("\n=== Summary ===")
    for analysis in all_analyses:
        db_name = os.path.basename(analysis['db_path'])
        print(f"\n{db_name}:")
        if analysis['wal_files']['wal_exists']:
            print(f"  - WAL file found: {analysis['wal_files']['wal_size']} bytes")
        if analysis['journal_files']['journal_exists']:
            print(f"  - Journal file found: {analysis['journal_files']['journal_size']} bytes")
        if analysis['structure']:
            print(f"  - Tables: {len(analysis['structure']['tables'])}")
            print(f"  - Integrity: {analysis['structure'].get('integrity_check', 'unknown')}")
    
    return len(all_analyses)

if __name__ == "__main__":
    main()

