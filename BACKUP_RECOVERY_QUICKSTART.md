# 🚀 Backup & Recovery System - Quick Start Guide

## Overview

This guide helps you quickly set up and use the backup and recovery system for the BMC Uruguay chatbot application.

## Prerequisites

- Python 3.7+
- Git (for Git history recovery)
- MongoDB (optional, for MongoDB recovery)

## Quick Setup

### 1. Initialize Backup System

```bash
# Create backup directories
python scripts/backup_system.py create --type full

# Verify the backup
python scripts/backup_system.py list
```

### 2. Test Recovery Capabilities

```bash
# Scan for missing files
python scripts/recovery_engine.py scan

# Recover a specific file
python scripts/recovery_engine.py recover --file "conocimiento_consolidado.json"
```

## Common Tasks

### Create a Backup

```bash
# Full backup of all sources
python scripts/backup_system.py create --type full

# Incremental backup (only changed files)
python scripts/backup_system.py create --type incremental

# Backup specific sources only
python scripts/backup_system.py create --sources conversations configuration
```

### List Backups

```bash
# List all available backups
python scripts/backup_system.py list
```

### Verify Backup Integrity

```bash
# Verify a specific backup
python scripts/backup_system.py verify --backup-id backup_20251201_143022_full
```

### Restore a File

```bash
# Restore specific file from latest backup
python scripts/backup_system.py restore \
  --backup-id backup_20251201_143022_full \
  --file "conocimiento_consolidado.json"
```

### Scan for Missing Files

```bash
# Detect missing or corrupted files
python scripts/recovery_engine.py scan
```

### Recover Missing Files

```bash
# Automatically recover a missing file
python scripts/recovery_engine.py recover --file "conocimiento_consolidado.json"

# Use specific recovery strategy
python scripts/recovery_engine.py recover \
  --file "conocimiento_consolidado.json" \
  --strategy git_history

# Batch recover all missing files
python scripts/recovery_engine.py batch
```

### Cleanup Old Backups

```bash
# Remove backups older than 30 days
python scripts/backup_system.py cleanup

# Custom retention period
python scripts/backup_system.py cleanup --retention-days 7
```

## Automated Backup Schedule

### Option 1: Cron (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Hourly incremental backup
0 * * * * cd /workspace && python scripts/backup_system.py create --type incremental

# Daily full backup at 2 AM
0 2 * * * cd /workspace && python scripts/backup_system.py create --type full

# Weekly cleanup on Sunday at 3 AM
0 3 * * 0 cd /workspace && python scripts/backup_system.py cleanup
```

### Option 2: systemd Timer (Linux)

Create `/etc/systemd/system/bmc-backup.service`:

```ini
[Unit]
Description=BMC Chatbot Backup Service

[Service]
Type=oneshot
WorkingDirectory=/workspace
ExecStart=/usr/bin/python3 /workspace/scripts/backup_system.py create --type incremental
User=your-user
```

Create `/etc/systemd/system/bmc-backup.timer`:

```ini
[Unit]
Description=BMC Chatbot Backup Timer

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable bmc-backup.timer
sudo systemctl start bmc-backup.timer
```

### Option 3: Windows Task Scheduler

Create a batch file `backup.bat`:

```batch
@echo off
cd /d C:\path\to\workspace
python scripts\backup_system.py create --type incremental
```

Schedule using Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., hourly)
4. Action: Start a program
5. Program: `C:\path\to\workspace\backup.bat`

## Recovery Strategies

The recovery engine tries multiple strategies automatically:

### 1. Latest Backup
- **Speed:** Fast (seconds)
- **Success Rate:** High
- **Data Loss:** Minimal (up to last backup)

### 2. MongoDB Export
- **Speed:** Medium (30s-2min)
- **Success Rate:** Medium
- **Data Loss:** Minimal (up to last sync)

### 3. Git History
- **Speed:** Medium (30s-5min)
- **Success Rate:** Medium-High
- **Data Loss:** Depends on last commit

### 4. Regenerate
- **Speed:** Slow (5-10min)
- **Success Rate:** High
- **Data Loss:** None (regenerated from sources)

### 5. Manual Recovery
- **Speed:** Varies
- **Success Rate:** Varies
- **Data Loss:** Depends on manual source

## Monitoring Backup Health

### Check Last Backup

```bash
# List recent backups
python scripts/backup_system.py list | head -5
```

### Verify Latest Backup

```bash
# Get latest backup ID
LATEST=$(python scripts/backup_system.py list | head -1 | awk '{print $2}')

# Verify it
python scripts/backup_system.py verify --backup-id $LATEST
```

### Check Storage Usage

```bash
# Check backup directory size
du -sh backups/automated/
```

## Troubleshooting

### Problem: Backup Creation Fails

**Solution:**
```bash
# Check permissions
ls -la backups/

# Create backup directory manually
mkdir -p backups/automated/hot

# Check disk space
df -h
```

### Problem: Recovery Fails for All Strategies

**Solution:**
```bash
# 1. Check if backups exist
python scripts/backup_system.py list

# 2. Try manual recovery
python scripts/recovery_engine.py recover --file "your-file.json" --strategy latest_backup

# 3. Check Git history
git log --all --full-history -- your-file.json

# 4. Regenerate if possible
python consolidar_conocimiento.py
```

### Problem: Corrupted Backup

**Solution:**
```bash
# Verify backup integrity
python scripts/backup_system.py verify --backup-id <backup-id>

# If corrupted, use an older backup
python scripts/backup_system.py list
python scripts/backup_system.py restore --backup-id <older-backup-id> --file "your-file.json"
```

### Problem: Out of Disk Space

**Solution:**
```bash
# Check disk usage
df -h

# Cleanup old backups aggressively
python scripts/backup_system.py cleanup --retention-days 3

# Consider compression or offsite storage
# (Implement cloud backup following BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md)
```

## Best Practices

### 1. Regular Backups
- ✅ Hourly incremental backups
- ✅ Daily full backups
- ✅ Weekly verification

### 2. Test Recovery Regularly
```bash
# Monthly recovery drill
python scripts/recovery_engine.py batch
```

### 3. Monitor Storage
```bash
# Set up alerts when storage > 80%
USAGE=$(df -h /workspace/backups | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 80 ]; then
    echo "⚠️ Backup storage > 80% full"
fi
```

### 4. Keep Multiple Recovery Options
- ✅ Local backups
- ✅ Git history
- ✅ MongoDB
- ✅ Offsite backups (recommended)

### 5. Document Manual Recovery Procedures
Keep a runbook for manual recovery procedures specific to your organization.

## Advanced Usage

### Create Custom Recovery Strategy

Edit `scripts/recovery_engine.py` and add your custom strategy:

```python
def recover_from_custom_source(
    self,
    file_path: Path,
    config: Dict[str, Any]
) -> Optional[str]:
    """
    Custom recovery strategy
    """
    # Your custom recovery logic here
    pass

# Register the strategy
self.strategy_handlers["custom_source"] = self.recover_from_custom_source
```

### Configure Recovery Priorities

Edit `RECOVERY_STRATEGIES` in `scripts/recovery_engine.py`:

```python
RECOVERY_STRATEGIES = {
    "your-critical-file.json": [
        {"strategy": "latest_backup", "max_age_hours": 0.5},  # 30 minutes
        {"strategy": "mongodb_export"},
        {"strategy": "custom_source"}
    ]
}
```

### Integrate with Monitoring Systems

```python
# Example: Send metrics to monitoring system
import requests

def send_backup_metrics(manifest):
    metrics = {
        "backup_id": manifest.backup_id,
        "duration_seconds": manifest.metadata["backup_duration_seconds"],
        "total_files": sum(s["files_backed_up"] for s in manifest.sources),
        "total_size_mb": sum(s["total_size_bytes"] for s in manifest.sources) / 1024 / 1024
    }
    
    requests.post("https://your-monitoring-system/metrics", json=metrics)
```

## Emergency Recovery Procedures

### Scenario 1: Critical File Lost

```bash
# 1. Immediate recovery attempt
python scripts/recovery_engine.py recover --file "conocimiento_consolidado.json"

# 2. If fails, try Git
python scripts/recovery_engine.py recover --file "conocimiento_consolidado.json" --strategy git_history

# 3. If still fails, regenerate
python consolidar_conocimiento.py
```

### Scenario 2: Multiple Files Lost

```bash
# Batch recovery
python scripts/recovery_engine.py batch

# Review recovery report
cat recovery_report_*.json
```

### Scenario 3: Full System Recovery

```bash
# 1. Clone repository
git clone <repo-url> workspace-recovery

# 2. Restore from latest backup
cd workspace-recovery
python scripts/backup_system.py list
python scripts/backup_system.py restore --backup-id <latest-backup-id>

# 3. Verify restoration
python scripts/recovery_engine.py scan

# 4. Test system
python ejecutar_sistema.py
```

## Getting Help

### Check Logs

```bash
# Backup system logs
tail -f /tmp/backup_system.log

# Recovery engine logs
tail -f /tmp/recovery_engine.log
```

### Generate Diagnostic Report

```bash
# Run full scan
python scripts/recovery_engine.py scan > diagnostic_report.txt

# Check backup health
python scripts/backup_system.py list >> diagnostic_report.txt
```

### Contact Support

For issues or questions:
1. Check `BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md` for detailed documentation
2. Review logs for error messages
3. Contact system administrator with diagnostic report

## Next Steps

1. **Read Full Documentation:** `BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md`
2. **Set Up Automated Backups:** Follow automation instructions above
3. **Test Recovery:** Run a recovery drill
4. **Monitor:** Set up monitoring and alerts
5. **Document:** Create organization-specific recovery procedures

## Appendix: Configuration Files

### Backup Configuration

Edit source patterns in `scripts/backup_system.py`:

```python
BACKUP_SOURCES = {
    "your_custom_source": {
        "patterns": [
            "your-files/**/*.json"
        ],
        "priority": "high",
        "backup_frequency": "daily"
    }
}
```

### Recovery Configuration

Edit recovery strategies in `scripts/recovery_engine.py`:

```python
RECOVERY_STRATEGIES = {
    "your-file.json": [
        {"strategy": "latest_backup", "max_age_hours": 24},
        {"strategy": "your_custom_strategy"}
    ]
}
```

---

**Last Updated:** December 1, 2025  
**Version:** 1.0  
**For:** BMC Uruguay Chatbot System
