# 🔄 Backup & Lost Files Recovery System - Implementation Prompt

## Overview
Develop a comprehensive backup and recovery system for a chatbot application that handles conversation data, configuration files, knowledge base files, and system state. The system must be able to detect, backup, and restore lost or corrupted files across multiple storage locations (MongoDB, filesystem, cloud storage).

## System Requirements

### 1. Core Functionality

#### 1.1 Backup System
- **Automated Backups**: Schedule regular backups (daily, weekly, monthly)
- **On-Demand Backups**: Manual backup triggers via CLI and API
- **Incremental Backups**: Track changes and backup only modified data
- **Full Backups**: Complete system state snapshots
- **Backup Compression**: Compress backups to save storage space
- **Backup Encryption**: Encrypt sensitive data in backups
- **Backup Verification**: Verify backup integrity after creation
- **Backup Retention**: Configurable retention policies (keep last N backups, delete after X days)

#### 1.2 Recovery System
- **Scan for Lost Files**: Automatically detect missing or corrupted files
- **Multiple Source Scanning**: 
  - MongoDB collections
  - Filesystem (JSON, config files, knowledge base)
  - Cloud storage (if configured)
  - Git history (for version-controlled files)
- **Data Deduplication**: Avoid restoring duplicate data
- **Selective Recovery**: Restore specific files, collections, or time ranges
- **Point-in-Time Recovery**: Restore to specific backup timestamps
- **Dry-Run Mode**: Preview what would be restored without making changes
- **Conflict Resolution**: Handle conflicts when restoring over existing data

#### 1.3 Monitoring & Alerts
- **Backup Status Monitoring**: Track backup success/failure
- **Storage Usage Monitoring**: Monitor backup storage consumption
- **Recovery Success Tracking**: Log all recovery operations
- **Alert System**: Notify administrators of backup failures or data loss

### 2. Data Sources to Protect

#### 2.1 Database Collections (MongoDB)
- `conversations` / `conversaciones`: User conversation history
- `quotes` / `cotizaciones`: Quote requests and responses
- `sessions`: User session data
- `context`: Conversation context and state
- `analytics`: Usage analytics and metrics
- `users`: User profiles and preferences

#### 2.2 Configuration Files
- `.env`: Environment variables and secrets
- `config.py`: Application configuration
- `package.json` / `requirements.txt`: Dependencies
- Database connection strings
- API keys and credentials (encrypted)

#### 2.3 Knowledge Base Files
- `conocimiento_consolidado.json`: Consolidated knowledge base
- `base_conocimiento_*.json`: Knowledge base exports
- `kb_populated_*.json`: Populated knowledge base files
- Product catalogs and specifications

#### 2.4 Application Files
- Python scripts in `python-scripts/`
- TypeScript/React components in `src/`
- Workflow definitions in `n8n_workflows/`
- Test scenarios in `test_scenarios/`

#### 2.5 System State
- Log files
- Temporary files
- Cache data
- Session state

### 3. Architecture Components

#### 3.1 Backup Service (`backup_service.py`)
```python
class BackupService:
    - create_backup(backup_type: str, scope: List[str]) -> BackupResult
    - create_incremental_backup() -> BackupResult
    - create_full_backup() -> BackupResult
    - verify_backup(backup_id: str) -> VerificationResult
    - list_backups(filters: Dict) -> List[BackupInfo]
    - delete_backup(backup_id: str, retention_policy: str) -> bool
    - get_backup_metadata(backup_id: str) -> BackupMetadata
```

#### 3.2 Recovery Service (`recovery_service.py`)
```python
class RecoveryService:
    - scan_for_lost_files() -> ScanResult
    - scan_mongodb() -> MongoDBScanResult
    - scan_filesystem(patterns: List[str]) -> FilesystemScanResult
    - scan_cloud_storage() -> CloudScanResult
    - restore_from_backup(backup_id: str, options: RestoreOptions) -> RestoreResult
    - restore_file(file_path: str, source: str) -> RestoreResult
    - restore_collection(collection: str, backup_id: str) -> RestoreResult
    - preview_restore(backup_id: str, options: RestoreOptions) -> PreviewResult
    - resolve_conflicts(conflicts: List[Conflict]) -> ResolutionResult
```

#### 3.3 Storage Manager (`storage_manager.py`)
```python
class StorageManager:
    - save_backup(backup_data: Dict, location: str) -> str
    - load_backup(backup_id: str) -> Dict
    - list_backups(location: str) -> List[str]
    - delete_backup(backup_id: str) -> bool
    - get_storage_usage() -> StorageUsage
    - compress_backup(backup_id: str) -> str
    - encrypt_backup(backup_id: str, key: str) -> str
```

#### 3.4 Scanner Module (`file_scanner.py`)
```python
class FileScanner:
    - scan_directory(path: str, patterns: List[str]) -> List[FileInfo]
    - detect_missing_files(expected_files: List[str]) -> List[str]
    - detect_corrupted_files(files: List[str]) -> List[CorruptedFile]
    - compare_with_backup(files: List[str], backup_id: str) -> ComparisonResult
    - find_duplicates(files: List[str]) -> List[DuplicateGroup]
```

#### 3.5 API Endpoints (`/api/backup` and `/api/recovery`)
```typescript
// Backup endpoints
GET  /api/backup/list              - List all backups
POST /api/backup/create            - Create new backup
GET  /api/backup/:id               - Get backup details
POST /api/backup/:id/verify        - Verify backup integrity
DELETE /api/backup/:id             - Delete backup
GET  /api/backup/storage           - Get storage usage

// Recovery endpoints
GET  /api/recovery/scan            - Scan for lost files
GET  /api/recovery/preview         - Preview recovery operation
POST /api/recovery/restore         - Restore from backup
GET  /api/recovery/status/:id      - Get recovery operation status
GET  /api/recovery/history         - Get recovery history
```

### 4. Implementation Steps

#### Phase 1: Core Backup System
1. **Create Backup Service**
   - Implement `BackupService` class with MongoDB backup functionality
   - Add filesystem backup for configuration and knowledge base files
   - Implement backup metadata tracking
   - Add backup compression using gzip or similar
   - Create backup verification mechanism

2. **Storage Management**
   - Implement local filesystem storage
   - Add support for cloud storage (S3, Google Cloud Storage, Azure Blob)
   - Create storage abstraction layer
   - Implement storage quota management

3. **CLI Interface**
   - Create `backup.py` script with commands:
     - `backup create [--full|--incremental] [--scope SCOPE]`
     - `backup list [--filter FILTER]`
     - `backup verify <backup_id>`
     - `backup delete <backup_id>`
     - `backup restore <backup_id> [--dry-run]`

#### Phase 2: Recovery System
1. **File Scanner**
   - Implement filesystem scanning with pattern matching
   - Add MongoDB collection scanning
   - Create comparison logic to detect missing/corrupted files
   - Implement duplicate detection

2. **Recovery Service**
   - Build recovery engine with multiple source support
   - Implement selective restoration
   - Add conflict resolution strategies
   - Create dry-run/preview mode
   - Add recovery logging and audit trail

3. **Recovery CLI**
   - Create `recover.py` script with commands:
     - `recover scan [--source SOURCE]`
     - `recover preview <backup_id> [--target TARGET]`
     - `recover restore <backup_id> [--selective SELECTIVE] [--dry-run]`
     - `recover status <operation_id>`

#### Phase 3: API Integration
1. **Backup API**
   - Implement REST endpoints for backup operations
   - Add authentication and authorization
   - Create rate limiting
   - Add request validation

2. **Recovery API**
   - Implement REST endpoints for recovery operations
   - Add async job processing for long-running operations
   - Create WebSocket support for real-time status updates
   - Implement operation queuing

#### Phase 4: Automation & Scheduling
1. **Scheduler**
   - Implement cron-based scheduling
   - Add support for multiple backup schedules
   - Create backup rotation policies
   - Add notification system for backup failures

2. **Monitoring**
   - Create backup health dashboard
   - Implement alerting system
   - Add metrics collection (Prometheus/StatsD)
   - Create backup success/failure reporting

#### Phase 5: Advanced Features
1. **Incremental Backups**
   - Implement change tracking
   - Add diff calculation
   - Create incremental backup merging

2. **Point-in-Time Recovery**
   - Implement timestamp-based recovery
   - Add backup chain management
   - Create recovery point selection UI

3. **Cross-Platform Support**
   - Add support for multiple database systems
   - Implement cloud storage adapters
   - Create platform-specific optimizations

### 5. Data Structures

#### Backup Metadata
```json
{
  "backup_id": "backup_20251128_120000",
  "timestamp": "2025-11-28T12:00:00Z",
  "type": "full|incremental",
  "scope": ["mongodb", "filesystem", "config"],
  "size": 1048576,
  "compressed_size": 524288,
  "encrypted": true,
  "collections": {
    "conversations": 150,
    "quotes": 45
  },
  "files": {
    "count": 23,
    "total_size": 524288
  },
  "verification": {
    "checksum": "sha256:abc123...",
    "verified": true,
    "verified_at": "2025-11-28T12:05:00Z"
  },
  "storage": {
    "location": "local|s3|gcs",
    "path": "/backups/backup_20251128_120000.tar.gz"
  }
}
```

#### Recovery Operation
```json
{
  "operation_id": "recover_20251128_130000",
  "backup_id": "backup_20251128_120000",
  "status": "pending|in_progress|completed|failed",
  "started_at": "2025-11-28T13:00:00Z",
  "completed_at": null,
  "options": {
    "scope": ["conversations", "config"],
    "dry_run": false,
    "conflict_resolution": "skip|overwrite|merge"
  },
  "results": {
    "restored": 150,
    "failed": 0,
    "skipped": 5,
    "conflicts": 2
  },
  "errors": []
}
```

#### Scan Result
```json
{
  "scan_id": "scan_20251128_140000",
  "timestamp": "2025-11-28T14:00:00Z",
  "sources": {
    "mongodb": {
      "connected": true,
      "collections_found": 5,
      "collections_missing": 1,
      "total_documents": 195
    },
    "filesystem": {
      "files_scanned": 150,
      "files_found": 145,
      "files_missing": 5,
      "files_corrupted": 2
    }
  },
  "lost_files": [
    {
      "path": "conocimiento_consolidado.json",
      "type": "knowledge_base",
      "last_seen": "2025-11-27T10:00:00Z",
      "recoverable_from": ["backup_20251127_120000"]
    }
  ],
  "recommendations": [
    "Restore conocimiento_consolidado.json from backup_20251127_120000"
  ]
}
```

### 6. Error Handling & Edge Cases

#### 6.1 Backup Failures
- Handle MongoDB connection failures gracefully
- Retry failed backup operations with exponential backoff
- Partial backup recovery (save what was backed up before failure)
- Disk space exhaustion handling
- Network timeout handling for cloud storage

#### 6.2 Recovery Failures
- Handle corrupted backup files
- Manage missing backup dependencies
- Handle schema mismatches during restore
- Partial recovery (restore what's possible, report failures)
- Rollback mechanism for failed recoveries

#### 6.3 Data Integrity
- Verify data integrity before and after backup/restore
- Handle concurrent modifications during backup
- Manage backup consistency across distributed systems
- Detect and handle data corruption

### 7. Security Requirements

#### 7.1 Authentication & Authorization
- Require authentication for all backup/recovery operations
- Implement role-based access control (RBAC)
- Admin-only access for sensitive operations
- Audit logging for all operations

#### 7.2 Data Protection
- Encrypt backups containing sensitive data
- Secure storage of encryption keys
- Secure transmission of backup data
- Mask sensitive data in logs and reports

#### 7.3 Compliance
- Support data retention policies
- Implement secure deletion of old backups
- Maintain audit trails
- Support compliance reporting

### 8. Testing Requirements

#### 8.1 Unit Tests
- Test backup creation for each data source
- Test recovery operations with various scenarios
- Test file scanning and detection
- Test conflict resolution strategies
- Test error handling and edge cases

#### 8.2 Integration Tests
- Test end-to-end backup and restore workflows
- Test API endpoints with various inputs
- Test scheduled backup execution
- Test recovery from different backup sources
- Test concurrent backup/recovery operations

#### 8.3 Performance Tests
- Test backup performance with large datasets
- Test recovery performance and time
- Test storage efficiency (compression ratios)
- Test concurrent operation handling

#### 8.4 Disaster Recovery Tests
- Simulate data loss scenarios
- Test recovery from various failure points
- Test backup chain integrity
- Test cross-platform recovery

### 9. Documentation Requirements

#### 9.1 User Documentation
- Installation and setup guide
- Configuration reference
- CLI usage examples
- API documentation
- Troubleshooting guide

#### 9.2 Developer Documentation
- Architecture overview
- Code structure and organization
- Extension points for custom storage/scanning
- Testing guide
- Contribution guidelines

#### 9.3 Operations Documentation
- Deployment guide
- Monitoring and alerting setup
- Backup schedule recommendations
- Recovery procedures
- Disaster recovery playbook

### 10. Configuration

#### Configuration File (`backup_config.json`)
```json
{
  "backup": {
    "enabled": true,
    "schedule": {
      "full": "0 2 * * 0",
      "incremental": "0 3 * * *"
    },
    "retention": {
      "full": 30,
      "incremental": 7
    },
    "compression": {
      "enabled": true,
      "algorithm": "gzip",
      "level": 6
    },
    "encryption": {
      "enabled": true,
      "algorithm": "AES-256"
    }
  },
  "storage": {
    "primary": "local",
    "secondary": "s3",
    "local": {
      "path": "./backups",
      "max_size": "10GB"
    },
    "s3": {
      "bucket": "backup-bucket",
      "region": "us-east-1"
    }
  },
  "recovery": {
    "auto_scan": true,
    "scan_interval": "1h",
    "conflict_resolution": "prompt"
  },
  "monitoring": {
    "enabled": true,
    "alert_on_failure": true,
    "metrics_endpoint": "/metrics"
  }
}
```

### 11. Success Criteria

The implementation is considered successful when:

1. ✅ **Backup System**
   - Can create full and incremental backups of all data sources
   - Backups are verified and can be restored successfully
   - Backup scheduling works reliably
   - Storage management handles quotas and cleanup

2. ✅ **Recovery System**
   - Can detect lost or corrupted files across all sources
   - Can restore data from backups with high success rate
   - Handles conflicts and edge cases gracefully
   - Provides clear recovery reports and recommendations

3. ✅ **API & CLI**
   - All operations accessible via CLI and API
   - API endpoints are secure and performant
   - CLI is user-friendly with helpful error messages
   - Operations are logged and auditable

4. ✅ **Monitoring & Alerts**
   - Backup status is monitored and reported
   - Failures trigger appropriate alerts
   - Storage usage is tracked and reported
   - Recovery operations are logged

5. ✅ **Documentation**
   - Complete user and developer documentation
   - Clear examples and troubleshooting guides
   - Operations runbook for common scenarios

### 12. Implementation Priority

**High Priority (MVP)**
1. Basic backup system (MongoDB + filesystem)
2. Basic recovery system (scan + restore)
3. CLI interface
4. Local storage

**Medium Priority**
1. API endpoints
2. Incremental backups
3. Cloud storage support
4. Monitoring and alerts

**Low Priority (Nice to Have)**
1. Point-in-time recovery
2. Advanced conflict resolution
3. Web UI dashboard
4. Cross-platform optimizations

### 13. Example Usage

#### CLI Examples
```bash
# Create a full backup
python backup.py create --full

# Create incremental backup
python backup.py create --incremental

# List backups
python backup.py list --filter "last_7_days"

# Verify backup
python backup.py verify backup_20251128_120000

# Scan for lost files
python recover.py scan

# Preview recovery
python recover.py preview backup_20251128_120000 --target conversations

# Restore from backup
python recover.py restore backup_20251128_120000 --selective conversations,config
```

#### API Examples
```bash
# Create backup via API
curl -X POST http://localhost:3000/api/backup/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "full", "scope": ["mongodb", "filesystem"]}'

# Scan for lost files
curl http://localhost:3000/api/recovery/scan \
  -H "Authorization: Bearer $TOKEN"

# Restore from backup
curl -X POST http://localhost:3000/api/recovery/restore \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backup_id": "backup_20251128_120000", "scope": ["conversations"]}'
```

---

## Implementation Notes

- **Start Simple**: Begin with basic backup/restore functionality, then add advanced features
- **Test Thoroughly**: Recovery systems must be reliable - extensive testing is critical
- **Document Everything**: Recovery procedures must be clear and well-documented
- **Monitor Closely**: Backup failures can lead to data loss - monitor aggressively
- **Plan for Scale**: Design for growth in data volume and backup frequency
- **Security First**: Protect backups and recovery operations with proper authentication and encryption

---

**This prompt provides a comprehensive guide for implementing a robust backup and recovery system. Follow the phases sequentially, ensuring each phase is complete and tested before moving to the next.**
