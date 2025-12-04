#!/usr/bin/env python3
"""
RecoveryAgent - Autonomous forensic AI agent for recovering lost session data
Recovers: Git state, Cursor AI chats, Cursor History file versions
"""

import os
import json
import sqlite3
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import unquote, urlparse
import glob
import hashlib

# Configuration
PROJECT_ROOT = Path.cwd()
USER_HOME = Path.home()
CURSOR_SUPPORT = USER_HOME / "Library/Application Support/Cursor"
# Crash window: last 7 hours until now
CRASH_WINDOW_END = datetime.now()
CRASH_WINDOW_START = CRASH_WINDOW_END - timedelta(hours=7)

# Output directories
RESTORED_DIR = PROJECT_ROOT / "restored"
BACKUP_DIR = PROJECT_ROOT / "restored_from_backup"
RESTORED_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# Recovery data structures
recovery_data = {
    "git_recovery": False,
    "chat_recovered": False,
    "files_restored": [],
    "missing_files": [],
    "chat_records": [],
    "history_files": []
}


def safe_json_parse(text):
    """Attempt to parse JSON, return parsed object or original text."""
    if not isinstance(text, str):
        return text
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


def get_file_hash(filepath):
    """Generate a hash for a file path."""
    return hashlib.md5(str(filepath).encode()).hexdigest()[:8]


def phase1_git_check():
    """Phase 1: Baseline Git Check"""
    print("Phase 1: Git Baseline Check...")
    
    git_summary = []
    git_summary.append("# Git Recovery Summary\n")
    git_summary.append(f"Generated: {datetime.now().isoformat()}\n\n")
    
    if not (PROJECT_ROOT / ".git").exists():
        git_summary.append("## Status\n\n")
        git_summary.append("**Not a Git repository.**\n\n")
        git_summary.append("No Git recovery possible.\n")
        recovery_data["git_recovery"] = False
    else:
        recovery_data["git_recovery"] = True
        git_summary.append("## Status\n\n")
        git_summary.append("**Git repository detected.**\n\n")
        
        # Git status
        try:
            result = subprocess.run(
                ["git", "status", "--short", "--branch"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            git_summary.append("### Git Status\n\n")
            git_summary.append("```\n")
            git_summary.append(result.stdout)
            git_summary.append("```\n\n")
        except Exception as e:
            git_summary.append(f"Error getting git status: {e}\n\n")
        
        # Git log
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-20"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            git_summary.append("### Recent Commits (last 20)\n\n")
            git_summary.append("```\n")
            git_summary.append(result.stdout)
            git_summary.append("```\n\n")
        except Exception as e:
            git_summary.append(f"Error getting git log: {e}\n\n")
        
        # Git reflog
        try:
            result = subprocess.run(
                ["git", "reflog", "--date=iso", "-20"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            git_summary.append("### Git Reflog (last 20)\n\n")
            git_summary.append("```\n")
            git_summary.append(result.stdout)
            git_summary.append("```\n\n")
        except Exception as e:
            git_summary.append(f"Error getting git reflog: {e}\n\n")
        
        # Git stash
        try:
            result = subprocess.run(
                ["git", "stash", "list"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            git_summary.append("### Git Stash\n\n")
            if result.stdout.strip():
                git_summary.append("```\n")
                git_summary.append(result.stdout)
                git_summary.append("```\n\n")
            else:
                git_summary.append("No stashes found.\n\n")
        except Exception as e:
            git_summary.append(f"Error getting git stash: {e}\n\n")
        
        # Check for missing tracked files
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            tracked_files = result.stdout.strip().split('\n')
            for file_path in tracked_files:
                if file_path and not (PROJECT_ROOT / file_path).exists():
                    recovery_data["missing_files"].append(file_path)
        except Exception as e:
            print(f"Warning: Could not check for missing files: {e}")
    
    # Write git summary
    git_summary_path = PROJECT_ROOT / "recovery_git_summary.md"
    with open(git_summary_path, "w", encoding="utf-8") as f:
        f.write("".join(git_summary))
    
    print(f"✓ Git check complete. Summary: {git_summary_path}")


def phase2_chat_recovery():
    """Phase 2: Chat Recovery from Cursor SQLite Databases"""
    print("Phase 2: Chat Recovery from Cursor SQLite...")
    
    if not CURSOR_SUPPORT.exists():
        print(f"  Cursor support directory not found: {CURSOR_SUPPORT}")
        return
    
    # Find state databases
    db_patterns = [
        CURSOR_SUPPORT / "User/workspaceStorage/*/state.vscdb",
        CURSOR_SUPPORT / "User/globalStorage/state.vscdb",
    ]
    
    found_dbs = []
    for pattern in db_patterns:
        found_dbs.extend(glob.glob(str(pattern)))
    
    if not found_dbs:
        print("  No Cursor state databases found.")
        return
    
    print(f"  Found {len(found_dbs)} database(s)")
    
    chat_markdown = []
    chat_markdown.append("# Recovered AI Chat Logs\n\n")
    chat_markdown.append(f"Recovery Time: {datetime.now().isoformat()}\n\n")
    chat_markdown.append("---\n\n")
    
    for db_path in found_dbs:
        db_path = Path(db_path)
        if not db_path.exists():
            continue
        
        print(f"  Processing: {db_path}")
        
        # Create backup
        db_hash = get_file_hash(db_path)
        backup_path = Path(f"/tmp/backup_{db_hash}.vscdb")
        try:
            shutil.copy2(db_path, backup_path)
            print(f"    Backed up to: {backup_path}")
        except Exception as e:
            print(f"    Warning: Could not backup database: {e}")
            continue
        
        # Try to open and query
        try:
            # Use URI mode for read-only
            db_uri = f"file:{db_path}?mode=ro"
            conn = sqlite3.connect(db_uri, uri=True)
            cursor = conn.cursor()
            
            # Try to find tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Common table names
            target_tables = [t for t in tables if any(
                pattern in t.lower() for pattern in 
                ['itemtable', 'items', 'item']
            )]
            
            if not target_tables:
                # Try all tables
                target_tables = tables
            
            print(f"    Found {len(target_tables)} table(s) to scan")
            
            for table in target_tables:
                try:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    # Look for key/value columns
                    key_col = None
                    value_col = None
                    
                    for col in columns:
                        col_lower = col.lower()
                        if 'key' in col_lower and key_col is None:
                            key_col = col
                        if 'value' in col_lower and value_col is None:
                            value_col = col
                    
                    if not key_col or not value_col:
                        # Try common patterns
                        if len(columns) >= 2:
                            key_col = columns[0]
                            value_col = columns[1]
                        else:
                            continue
                    
                    # Query all rows
                    cursor.execute(f"SELECT {key_col}, {value_col} FROM {table}")
                    rows = cursor.fetchall()
                    
                    for key, value in rows:
                        if not key:
                            continue
                        
                        key_str = str(key)
                        # Filter by prefixes
                        if any(key_str.startswith(prefix) for prefix in [
                            "composerData:",
                            "aichat",
                            "prompts",
                            "chat",
                            "fileActions"
                        ]):
                            parsed_value = safe_json_parse(value)
                            
                            record = {
                                "source_db": str(db_path),
                                "backup_db": str(backup_path),
                                "table": table,
                                "key": key_str,
                                "raw_value": str(value),
                                "parsed_value": parsed_value
                            }
                            recovery_data["chat_records"].append(record)
                            
                            # Add to markdown
                            chat_markdown.append(f"## Entry: {key_str}\n\n")
                            chat_markdown.append(f"**Source DB:** `{db_path}`\n\n")
                            chat_markdown.append(f"**Backup DB:** `{backup_path}`\n\n")
                            chat_markdown.append(f"**Table:** `{table}`\n\n")
                            chat_markdown.append(f"**Key:** `{key_str}`\n\n")
                            chat_markdown.append("### Raw Value\n\n")
                            chat_markdown.append("```\n")
                            chat_markdown.append(str(value)[:5000])  # Limit length
                            if len(str(value)) > 5000:
                                chat_markdown.append("\n... (truncated)")
                            chat_markdown.append("\n```\n\n")
                            chat_markdown.append("### Parsed Value\n\n")
                            chat_markdown.append("```json\n")
                            chat_markdown.append(json.dumps(parsed_value, indent=2, ensure_ascii=False)[:10000])
                            if len(json.dumps(parsed_value)) > 10000:
                                chat_markdown.append("\n... (truncated)")
                            chat_markdown.append("\n```\n\n")
                            chat_markdown.append("---\n\n")
                
                except Exception as e:
                    print(f"    Warning: Error querying table {table}: {e}")
                    continue
            
            conn.close()
        
        except Exception as e:
            print(f"    Error processing database: {e}")
            continue
    
    if recovery_data["chat_records"]:
        recovery_data["chat_recovered"] = True
        print(f"  ✓ Recovered {len(recovery_data['chat_records'])} chat records")
    else:
        print("  No chat records found")
    
    # Write chat recovery markdown
    chat_md_path = PROJECT_ROOT / "RecoveredChats.md"
    with open(chat_md_path, "w", encoding="utf-8") as f:
        f.write("".join(chat_markdown))
    
    print(f"✓ Chat recovery complete. Log: {chat_md_path}")


def normalize_file_uri(uri):
    """Convert file:// URI to OS path."""
    if not uri:
        return None
    
    if uri.startswith("file://"):
        parsed = urlparse(uri)
        path = unquote(parsed.path)
        return Path(path)
    elif uri.startswith("/"):
        return Path(uri)
    else:
        return Path(uri)


def parse_timestamp(timestamp_str):
    """Parse various timestamp formats."""
    if not timestamp_str:
        return None
    
    # Try ISO format
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # Try Unix timestamp
    try:
        ts = float(timestamp_str)
        return datetime.fromtimestamp(ts)
    except (ValueError, TypeError):
        pass
    
    return None


def phase3_history_recovery():
    """Phase 3: Cursor History File Recovery"""
    print("Phase 3: Cursor History Recovery...")
    
    if not CURSOR_SUPPORT.exists():
        print(f"  Cursor support directory not found: {CURSOR_SUPPORT}")
        return
    
    history_pattern = CURSOR_SUPPORT / "User/History/**/entries.json"
    history_files = glob.glob(str(history_pattern), recursive=True)
    
    if not history_files:
        print("  No Cursor History files found.")
        return
    
    print(f"  Found {len(history_files)} history file(s)")
    
    restored_count = 0
    
    for hist_file in history_files:
        hist_path = Path(hist_file)
        print(f"  Processing: {hist_path}")
        
        try:
            with open(hist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Handle different JSON structures
            entries = []
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict):
                entries = data.get("entries", data.get("files", []))
            
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                
                # Extract file path
                file_path = None
                for key in ["uri", "fileUri", "filePath", "path"]:
                    if key in entry:
                        file_path = normalize_file_uri(entry[key])
                        break
                
                if not file_path:
                    continue
                
                # Check if path is within project root
                try:
                    file_path = file_path.resolve()
                    project_root_resolved = PROJECT_ROOT.resolve()
                    
                    if not str(file_path).startswith(str(project_root_resolved)):
                        continue
                except Exception:
                    continue
                
                # Extract timestamp
                timestamp = None
                for key in ["timestamp", "modifiedTime", "lastModified", "time"]:
                    if key in entry:
                        timestamp = parse_timestamp(str(entry[key]))
                        if timestamp:
                            break
                
                # Filter by crash window
                if timestamp:
                    if timestamp > CRASH_WINDOW_END:
                        continue  # Skip entries after crash window
                
                # Extract content
                content = None
                for key in ["content", "text", "snapshot", "data", "body"]:
                    if key in entry:
                        content = entry[key]
                        break
                
                if not content:
                    continue
                
                # Compute relative path
                try:
                    rel_path = file_path.relative_to(project_root_resolved)
                except ValueError:
                    continue
                
                # Store entry for later (we'll keep the latest version)
                if rel_path not in recovery_data["history_files"]:
                    recovery_data["history_files"].append({
                        "path": str(rel_path),
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "content": content
                    })
                else:
                    # Update if this version is newer
                    existing = next((f for f in recovery_data["history_files"] if f["path"] == str(rel_path)), None)
                    if existing and timestamp:
                        existing_ts = parse_timestamp(existing["timestamp"]) if existing["timestamp"] else None
                        if not existing_ts or timestamp > existing_ts:
                            existing["timestamp"] = timestamp.isoformat()
                            existing["content"] = content
        
        except Exception as e:
            print(f"    Error processing history file: {e}")
            continue
    
    # Write restored files
    for file_info in recovery_data["history_files"]:
        rel_path = Path(file_info["path"])
        restored_path = RESTORED_DIR / rel_path
        
        # Create parent directories
        restored_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        try:
            content = file_info["content"]
            if isinstance(content, str):
                with open(restored_path, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                # If content is not a string, try to serialize it
                with open(restored_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(content, indent=2, ensure_ascii=False))
            
            recovery_data["files_restored"].append(str(rel_path))
            restored_count += 1
        except Exception as e:
            print(f"    Warning: Could not restore {rel_path}: {e}")
    
    print(f"  ✓ Restored {restored_count} file(s) from History")


def phase4_backup_placeholder():
    """Phase 4: Backup/Time Machine Placeholder"""
    print("Phase 4: Backup Recovery Placeholder...")
    print("  Manual backup recovery not automated.")
    print("  User should copy older versions into restored_from_backup/ if available.")


def phase5_consolidated_output():
    """Phase 5: Generate Consolidated Reports"""
    print("Phase 5: Generating Consolidated Reports...")
    
    # Calculate final score
    score = 0
    if recovery_data["git_recovery"]:
        score += 20
    if recovery_data["chat_recovered"]:
        score += 30
    if recovery_data["files_restored"]:
        score += 30
    if not recovery_data["missing_files"]:
        score += 20
    else:
        # Subtract up to 20 points (2 per missing file, capped at 20)
        missing_penalty = min(len(recovery_data["missing_files"]) * 2, 20)
        score -= missing_penalty
    
    score = max(0, min(100, score))
    
    # Create summary JSON
    summary = {
        "recovery_timestamp": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "git_recovery": recovery_data["git_recovery"],
        "chat_recovered": recovery_data["chat_recovered"],
        "chat_records_count": len(recovery_data["chat_records"]),
        "files_restored": recovery_data["files_restored"],
        "files_restored_count": len(recovery_data["files_restored"]),
        "missing_files": recovery_data["missing_files"],
        "missing_files_count": len(recovery_data["missing_files"]),
        "final_score": score,
        "crash_window": {
            "start": CRASH_WINDOW_START.isoformat(),
            "end": CRASH_WINDOW_END.isoformat()
        }
    }
    
    # Write JSON summary
    summary_path = PROJECT_ROOT / "recovery_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Summary JSON: {summary_path}")
    
    # Create markdown report
    report = []
    report.append("# Recovery Report\n\n")
    report.append(f"Generated: {datetime.now().isoformat()}\n\n")
    report.append("---\n\n")
    
    report.append("## Overview\n\n")
    report.append(f"- **Chat Recovered:** {recovery_data['chat_recovered']}\n")
    report.append(f"- **Git Recovery:** {recovery_data['git_recovery']}\n")
    report.append(f"- **Files Restored:** {len(recovery_data['files_restored'])}\n")
    report.append(f"- **Missing Files:** {len(recovery_data['missing_files'])}\n")
    report.append(f"- **Final Score:** {score}/100\n\n")
    
    report.append("## Git State\n\n")
    report.append("See [recovery_git_summary.md](./recovery_git_summary.md) for details.\n\n")
    
    report.append("## Recovered AI Chat Log Summary\n\n")
    report.append(f"- **Databases Scanned:** Multiple Cursor state databases\n")
    report.append(f"- **Records Found:** {len(recovery_data['chat_records'])}\n")
    report.append(f"- **Details:** See [RecoveredChats.md](./RecoveredChats.md)\n\n")
    
    report.append("## Files Recovered from History\n\n")
    if recovery_data["files_restored"]:
        report.append("The following files were restored to `restored/`:\n\n")
        for file_path in recovery_data["files_restored"]:
            report.append(f"- `{file_path}`\n")
        report.append("\n")
    else:
        report.append("No files were recovered from Cursor History.\n\n")
    
    report.append("## Backup / Time Machine Recovery\n\n")
    report.append("**Status:** Not automated. Manual recovery required.\n\n")
    report.append("To recover from Time Machine or other backups:\n")
    report.append("1. Locate older versions of missing files\n")
    report.append("2. Copy them into `restored_from_backup/` directory\n")
    report.append("3. Review and merge as needed\n\n")
    
    report.append("## Remaining Missing Elements\n\n")
    if recovery_data["missing_files"]:
        report.append("The following Git-tracked files are missing from disk:\n\n")
        for file_path in recovery_data["missing_files"]:
            report.append(f"- `{file_path}`\n")
        report.append("\n")
        report.append("**Recovery Suggestions:**\n")
        report.append("- Restore from Git: `git checkout <file>`\n")
        report.append("- Check Cursor History (see restored/ directory)\n")
        report.append("- Restore from Time Machine or other backups\n")
        report.append("- Check if files were moved or renamed\n\n")
    else:
        report.append("No missing files detected.\n\n")
    
    report.append("## JSON Summary\n\n")
    report.append("```json\n")
    report.append(json.dumps(summary, indent=2, ensure_ascii=False))
    report.append("\n```\n")
    
    # Write report
    report_path = PROJECT_ROOT / "recovery_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("".join(report))
    
    print(f"  ✓ Recovery Report: {report_path}")
    print(f"\n✓ Recovery complete! Final score: {score}/100")


def main():
    """Main recovery pipeline"""
    print("=" * 60)
    print("RecoveryAgent - Autonomous Forensic Recovery")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Crash Window: {CRASH_WINDOW_START} to {CRASH_WINDOW_END}")
    print("=" * 60)
    print()
    
    try:
        phase1_git_check()
        print()
        phase2_chat_recovery()
        print()
        phase3_history_recovery()
        print()
        phase4_backup_placeholder()
        print()
        phase5_consolidated_output()
        print()
        print("=" * 60)
        print("Recovery pipeline completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

