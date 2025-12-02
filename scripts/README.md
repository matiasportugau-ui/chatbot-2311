# Recovery Prevention Scripts

This directory contains scripts to prevent future data loss.

## Scripts

### 1. `auto_commit_hook.sh`
Git pre-commit hook that creates backup branches and tags for significant changes.

**Installation:**
```bash
cp scripts/auto_commit_hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Features:**
- Creates backup branch before major changes (>10 files or >500 lines)
- Tags significant commits as checkpoints
- Automatic, no user intervention required

### 2. `export_chat_periodic.py`
Periodic export of Cursor chat history to prevent loss.

**Usage:**
```bash
# Manual export
python3 scripts/export_chat_periodic.py

# Export with custom time window
python3 scripts/export_chat_periodic.py --hours 48

# Schedule with cron (daily at 2 AM)
# Add to crontab: 0 2 * * * /path/to/scripts/export_chat_periodic.py
```

**Features:**
- Exports chat history to JSON files
- Automatic cleanup of old exports (keeps last 30 days)
- Configurable time window

### 3. `backup_workspace.sh`
Scheduled backup of Cursor workspaceStorage.

**Usage:**
```bash
# Manual backup
./scripts/backup_workspace.sh

# Schedule with cron (daily at 3 AM)
# Add to crontab: 0 3 * * * /path/to/scripts/backup_workspace.sh
```

**Features:**
- Backs up workspaceStorage and globalStorage
- Creates timestamped backup directories
- Automatic cleanup of old backups (keeps last 7 days)
- Creates manifest file for each backup

### 4. `monitor_file_changes.py`
Monitors workspace for file changes and creates snapshots.

**Usage:**
```bash
# Start monitoring
python3 scripts/monitor_file_changes.py

# Monitor with custom snapshot directory
python3 scripts/monitor_file_changes.py --snapshot-dir /path/to/snapshots
```

**Features:**
- Real-time file change monitoring
- Periodic snapshots of change log
- Lightweight, minimal disk usage

**Note:** Requires `watchdog` Python package:
```bash
pip install watchdog
```

## Setup Instructions

### Complete Setup (All Scripts)

1. **Install git hook:**
   ```bash
   cp scripts/auto_commit_hook.sh .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. **Setup cron jobs:**
   ```bash
   crontab -e
   ```
   
   Add these lines:
   ```
   # Daily chat export at 2 AM
   0 2 * * * cd /Users/matias/chatbot2511/chatbot-2311 && python3 scripts/export_chat_periodic.py >> /tmp/chat_export.log 2>&1
   
   # Daily workspace backup at 3 AM
   0 3 * * * /Users/matias/chatbot2511/chatbot-2311/scripts/backup_workspace.sh >> /tmp/workspace_backup.log 2>&1
   ```

3. **Optional: Start file monitor (runs in background):**
   ```bash
   nohup python3 scripts/monitor_file_changes.py > /tmp/file_monitor.log 2>&1 &
   ```

## Recommendations

- **Git Hook:** Install immediately for automatic backup branches
- **Chat Export:** Schedule daily to prevent chat history loss
- **Workspace Backup:** Schedule daily for complete workspace state backup
- **File Monitor:** Use during active development sessions

## Backup Locations

- Chat exports: `{workspace}/chat_exports/`
- Workspace backups: `~/Desktop/cursor_workspace_backups/`
- File change snapshots: `{workspace}/file_change_snapshots/`

