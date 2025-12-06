#!/usr/bin/env python3
"""
Automated Recovery Script
Unified recovery script that automates all recovery phases
"""
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Success: {description}")
            if result.stdout:
                print(result.stdout[:500])  # Show first 500 chars
            return True
        else:
            print(f"✗ Error: {description}")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def run_python_script(script_path, description):
    """Run a Python script"""
    if not os.path.exists(script_path):
        print(f"✗ Script not found: {script_path}")
        return False
    
    cmd = f"python3 {script_path}"
    return run_command(cmd, description)

def phase1_baseline(workspace_path):
    """Phase 1: Baseline & Repository State Analysis"""
    print("\n" + "="*60)
    print("PHASE 1: Baseline & Repository State Analysis")
    print("="*60)
    
    os.chdir(workspace_path)
    
    # Task 1.1: Git state assessment
    run_command(
        "git status --porcelain > recovery_git_status.txt",
        "Task 1.1: Document git status"
    )
    run_command(
        "git diff --stat > recovery_git_diff_stat.txt",
        "Task 1.1: Document git diff statistics"
    )
    run_command(
        "git diff > recovery_git_diff_full.txt",
        "Task 1.1: Document full git diff"
    )
    run_command(
        "git log --all --oneline --graph -20 > recovery_git_log.txt",
        "Task 1.1: Document git log"
    )
    run_command(
        "git reflog -20 > recovery_git_reflog.txt",
        "Task 1.1: Document git reflog"
    )
    
    # Task 1.2: Workspace mapping
    run_command(
        "cd ~/Library/Application\\ Support/Cursor/User/workspaceStorage/ && for dir in */; do if [ -f \"$dir/state.vscdb\" ]; then echo \"Workspace: $dir\"; ls -lT \"$dir/state.vscdb\" | awk '{print $6, $7, $8, $9}'; fi; done > " + workspace_path + "/recovery_workspace_mapping.txt",
        "Task 1.2: Map workspace storage"
    )

def phase2_chat_recovery(workspace_path):
    """Phase 2: Enhanced Cursor Chat & Context Recovery"""
    print("\n" + "="*60)
    print("PHASE 2: Enhanced Cursor Chat & Context Recovery")
    print("="*60)
    
    os.chdir(workspace_path)
    
    # Task 2.1: Backup databases
    backup_dir = f"$HOME/Desktop/cursor_workspace_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_command(
        f"mkdir -p {backup_dir} && find ~/Library/Application\\ Support/Cursor/User/workspaceStorage/ -name \"state.vscdb\" -exec sh -c 'cp \"$1\" \"$2/$(basename $(dirname \"$1\"))_state.vscdb\"' _ {{}} {backup_dir} \\; && cp ~/Library/Application\\ Support/Cursor/User/globalStorage/state.vscdb {backup_dir}/globalStorage_state.vscdb 2>/dev/null || true && echo {backup_dir} > recovery_backup_location.txt",
        "Task 2.1: Backup Cursor databases"
    )
    
    # Task 2.2: Extract recent chats
    run_python_script(
        os.path.join(workspace_path, "recovery_extract_recent_chats.py"),
        "Task 2.2: Extract recent chat history"
    )
    
    # Task 2.3: Extract composer data
    run_python_script(
        os.path.join(workspace_path, "recovery_extract_composer.py"),
        "Task 2.3: Extract composer/unsaved buffer data"
    )
    
    # Task 2.4: Reconstruct context
    run_python_script(
        os.path.join(workspace_path, "recovery_reconstruct_context.py"),
        "Task 2.4: Reconstruct conversation context"
    )

def phase3_file_recovery(workspace_path):
    """Phase 3: Local History & File-Level Recovery"""
    print("\n" + "="*60)
    print("PHASE 3: Local History & File-Level Recovery")
    print("="*60)
    
    os.chdir(workspace_path)
    
    # Task 3.2: Scan for temp files
    run_command(
        "find . -type f \\( -name \"*~\" -o -name \"*.bak\" -o -name \"*.swp\" -o -name \"*.tmp\" -o -name \"*#*#\" \\) -mtime -1 -ls > recovery_temp_files.txt 2>&1",
        "Task 3.2: Scan for temporary files"
    )
    
    # Task 3.3: Analyze git stashes
    run_command(
        "git stash list > recovery_stash_list.txt",
        "Task 3.3: List git stashes"
    )
    run_command(
        "STASH_COUNT=$(git stash list | wc -l | tr -d ' ') && if [ \"$STASH_COUNT\" -gt 0 ]; then for i in $(seq 0 $(($STASH_COUNT - 1))); do echo \"=== Stash $i ===\" >> recovery_stash_contents.txt; git stash show -p stash@{$i} >> recovery_stash_contents.txt 2>&1; echo \"\" >> recovery_stash_contents.txt; done; fi",
        "Task 3.3: Extract git stash contents"
    )

def phase4_advanced(workspace_path):
    """Phase 4: Advanced Recovery Methods"""
    print("\n" + "="*60)
    print("PHASE 4: Advanced Recovery Methods")
    print("="*60)
    
    os.chdir(workspace_path)
    
    # Task 4.1: Deep database analysis
    run_python_script(
        os.path.join(workspace_path, "recovery_deep_db_analysis.py"),
        "Task 4.1: Deep SQLite database analysis"
    )
    
    # Task 4.2: System log analysis
    run_command(
        "log show --predicate 'process == \"Cursor\"' --last 24h --info 2>/dev/null | grep -i \"chatbot-2311\" | head -50 > recovery_system_logs.txt 2>&1",
        "Task 4.2: Analyze system logs"
    )

def phase5_consolidation(workspace_path):
    """Phase 5: Recovery Consolidation & Enhancement"""
    print("\n" + "="*60)
    print("PHASE 5: Recovery Consolidation & Enhancement")
    print("="*60)
    
    os.chdir(workspace_path)
    
    # Task 5.1: Generate report
    run_python_script(
        os.path.join(workspace_path, "recovery_generate_report.py"),
        "Task 5.1: Generate recovery report"
    )

def main():
    """Main automated recovery function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Cursor Session Recovery')
    parser.add_argument('--workspace', default='/Users/matias/chatbot2511/chatbot-2311',
                       help='Workspace path')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3, 4, 5],
                       help='Run specific phase only')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip database backup (use with caution)')
    
    args = parser.parse_args()
    
    workspace_path = os.path.abspath(args.workspace)
    
    if not os.path.exists(workspace_path):
        print(f"Error: Workspace path does not exist: {workspace_path}")
        return 1
    
    print("="*60)
    print("CURSOR SESSION RECOVERY - AUTOMATED SCRIPT")
    print("="*60)
    print(f"Workspace: {workspace_path}")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    try:
        if args.phase:
            phases = {1: phase1_baseline, 2: phase2_chat_recovery, 
                     3: phase3_file_recovery, 4: phase4_advanced, 5: phase5_consolidation}
            phases[args.phase](workspace_path)
        else:
            # Run all phases
            phase1_baseline(workspace_path)
            phase2_chat_recovery(workspace_path)
            phase3_file_recovery(workspace_path)
            phase4_advanced(workspace_path)
            phase5_consolidation(workspace_path)
        
        print("\n" + "="*60)
        print("RECOVERY COMPLETE")
        print("="*60)
        print(f"Finished: {datetime.now().isoformat()}")
        print(f"\nCheck recovery_final_report.md for comprehensive results")
        print("="*60)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nRecovery interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nError during recovery: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

