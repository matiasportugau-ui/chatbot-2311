# 🔄 Backup & Recovery System - Quick Implementation Prompt

## Objective
Implement a comprehensive backup and recovery system for a chatbot application that can:
1. Automatically backup conversation data, configuration files, and knowledge base
2. Detect and recover lost or corrupted files from multiple sources
3. Provide CLI and API interfaces for backup/recovery operations
4. Support scheduled backups, incremental backups, and point-in-time recovery

## Core Components to Build

### 1. Backup Service (`backup_service.py`)
- Create full/incremental backups of MongoDB collections
- Backup filesystem files (config, knowledge base, scripts)
- Compress and encrypt backups
- Verify backup integrity
- Manage backup retention policies

### 2. Recovery Service (`recovery_service.py`)
- Scan MongoDB and filesystem for missing/corrupted files
- Restore from backups with conflict resolution
- Support selective restoration (specific files/collections)
- Provide dry-run/preview mode
- Generate recovery reports

### 3. CLI Tools
- `backup.py`: Create, list, verify, delete backups
- `recover.py`: Scan, preview, restore operations

### 4. API Endpoints
- `/api/backup/*`: Backup management endpoints
- `/api/recovery/*`: Recovery operation endpoints

## Key Features

### Backup
- ✅ Full and incremental backups
- ✅ Scheduled automatic backups (cron)
- ✅ Compression (gzip) and encryption (AES-256)
- ✅ Backup verification (checksums)
- ✅ Retention policies (keep N backups, delete after X days)
- ✅ Multiple storage backends (local, S3, GCS)

### Recovery
- ✅ Multi-source scanning (MongoDB, filesystem, cloud)
- ✅ Lost file detection
- ✅ Corrupted file detection
- ✅ Selective restoration
- ✅ Conflict resolution (skip/overwrite/merge)
- ✅ Dry-run mode
- ✅ Recovery audit logging

## Data to Protect

**MongoDB Collections:**
- `conversations`, `quotes`, `sessions`, `context`, `analytics`

**Files:**
- `.env`, `config.py`, `conocimiento_consolidado.json`
- `kb_populated_*.json`, knowledge base files
- Python scripts, TypeScript components, workflows

## Implementation Checklist

### Phase 1: Core Backup
- [ ] Implement `BackupService` class
- [ ] MongoDB backup functionality
- [ ] Filesystem backup functionality
- [ ] Backup compression
- [ ] Backup verification
- [ ] Local storage manager

### Phase 2: Recovery
- [ ] Implement `RecoveryService` class
- [ ] File scanner with pattern matching
- [ ] MongoDB collection scanner
- [ ] Restore functionality
- [ ] Conflict resolution
- [ ] Recovery reporting

### Phase 3: CLI
- [ ] `backup.py` script with all commands
- [ ] `recover.py` script with all commands
- [ ] Error handling and user-friendly messages
- [ ] Progress indicators

### Phase 4: API
- [ ] Backup REST endpoints
- [ ] Recovery REST endpoints
- [ ] Authentication/authorization
- [ ] Async job processing for long operations
- [ ] WebSocket for real-time status

### Phase 5: Automation
- [ ] Cron scheduler for backups
- [ ] Backup rotation policies
- [ ] Monitoring and alerting
- [ ] Health dashboard

## Example Implementation Structure

```
backup_service.py
├── BackupService
│   ├── create_backup()
│   ├── create_incremental_backup()
│   ├── verify_backup()
│   └── list_backups()
│
recovery_service.py
├── RecoveryService
│   ├── scan_for_lost_files()
│   ├── restore_from_backup()
│   ├── preview_restore()
│   └── resolve_conflicts()
│
storage_manager.py
├── StorageManager
│   ├── save_backup()
│   ├── load_backup()
│   ├── compress_backup()
│   └── encrypt_backup()
│
file_scanner.py
├── FileScanner
│   ├── scan_directory()
│   ├── detect_missing_files()
│   └── detect_corrupted_files()
```

## Configuration

Create `backup_config.json`:
```json
{
  "backup": {
    "enabled": true,
    "schedule": {"full": "0 2 * * 0", "incremental": "0 3 * * *"},
    "retention": {"full": 30, "incremental": 7},
    "compression": {"enabled": true, "algorithm": "gzip"},
    "encryption": {"enabled": true, "algorithm": "AES-256"}
  },
  "storage": {
    "primary": "local",
    "local": {"path": "./backups", "max_size": "10GB"}
  }
}
```

## Success Criteria

✅ Can backup all MongoDB collections and critical files  
✅ Can detect lost/corrupted files automatically  
✅ Can restore data from backups successfully  
✅ CLI and API are functional and secure  
✅ Scheduled backups run reliably  
✅ Monitoring and alerts work correctly  

## Quick Start Commands

```bash
# Create backup
python backup.py create --full

# Scan for lost files
python recover.py scan

# Restore from backup
python recover.py restore backup_20251128_120000
```

---

**Reference the full prompt (`BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md`) for detailed specifications, data structures, error handling, and testing requirements.**
