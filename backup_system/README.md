# Backup & Recovery System

Comprehensive backup and recovery system for the chatbot application.

## Quick Start

### Installation

1. Install Python dependencies:
```bash
pip install pymongo schedule
```

2. Configure MongoDB connection (set `MONGODB_URI` environment variable or use default)

3. Review and customize `backup_config.json` if needed

### Create a Backup

```bash
# Full backup
python3 backup.py create --full

# Incremental backup
python3 backup.py create --incremental

# Custom scope
python3 backup.py create --scope mongodb,filesystem
```

### List Backups

```bash
# List all backups
python3 backup.py list

# Filter by type
python3 backup.py list --type full

# Filter by date
python3 backup.py list --filter last_7_days
```

### Verify Backup

```bash
python3 backup.py verify backup_20251201_120000
```

### Scan for Lost Files

```bash
# Scan all sources
python3 recover.py scan

# Scan specific source
python3 recover.py scan --source mongodb
python3 recover.py scan --source filesystem
```

### Restore from Backup

```bash
# Preview restore (dry-run)
python3 recover.py restore backup_20251201_120000 --dry-run

# Restore everything
python3 recover.py restore backup_20251201_120000

# Selective restore
python3 recover.py restore backup_20251201_120000 --selective config.py,conocimiento_consolidado.json

# Restore specific scope
python3 recover.py restore backup_20251201_120000 --scope filesystem
```

## Automated Backups

### Run Scheduler

```bash
# Start scheduler (runs in foreground)
python3 backup_system/scheduler.py

# Or run in background
nohup python3 backup_system/scheduler.py > backup_scheduler.log 2>&1 &
```

### Schedule with Cron

Add to crontab:
```bash
# Full backup every Sunday at 2 AM
0 2 * * 0 cd /path/to/project && python3 backup.py create --full

# Incremental backup daily at 3 AM
0 3 * * * cd /path/to/project && python3 backup.py create --incremental
```

## API Usage

### Create Backup
```bash
curl -X POST http://localhost:3000/api/backup \
  -H "Content-Type: application/json" \
  -d '{"action": "create", "type": "full", "scope": ["mongodb", "filesystem"]}'
```

### List Backups
```bash
curl http://localhost:3000/api/backup?action=list
```

### Scan for Lost Files
```bash
curl http://localhost:3000/api/recovery?action=scan&source=all
```

### Restore from Backup
```bash
curl -X POST http://localhost:3000/api/recovery \
  -H "Content-Type: application/json" \
  -d '{"action": "restore", "backup_id": "backup_20251201_120000", "scope": ["filesystem"]}'
```

## Configuration

Edit `backup_system/backup_config.json` to customize:

- Backup schedules
- Retention policies
- Compression settings
- MongoDB collections to backup
- Filesystem patterns to backup
- Storage locations

## File Structure

```
backup_system/
├── backup_config.json      # Configuration
├── backup_service.py        # Backup service
├── storage_manager.py       # Storage management
├── file_scanner.py          # File scanning
├── recovery_service.py      # Recovery service
└── scheduler.py             # Backup scheduler

backup.py                    # Backup CLI
recover.py                   # Recovery CLI
```

## Backup Locations

- **Backup files:** `./backups/`
- **Backup metadata:** `./backup_metadata/`
- **Configuration:** `backup_system/backup_config.json`

## Troubleshooting

### MongoDB Connection Issues
- Check `MONGODB_URI` environment variable
- Verify MongoDB is running
- Check network connectivity

### Permission Issues
- Ensure write permissions for backup directories
- Check file system permissions

### Backup Failures
- Check disk space
- Verify MongoDB collections exist
- Review logs for specific errors

## Support

For issues or questions, check:
- `BACKUP_RECOVERY_IMPLEMENTATION_STATUS.md` for implementation status
- `BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md` for full specification


