# 🔄 Backup & Lost Files Recovery System - Implementation Prompt

## Prompt for AI Assistant

You are tasked with implementing a comprehensive backup and recovery system for a conversational AI chatbot system (BMC Uruguay). The system handles conversations, quotes, and user sessions stored in MongoDB, with additional knowledge base files and configuration stored in the filesystem.

## Current System Context

**Existing Components:**
- MongoDB database (`bmc-cotizaciones`) with collections: `conversations`, `quotes`, `sessions`, `context`
- Python recovery scripts: `scripts/recover_conversations.py`, `scripts/recover_setup.py`
- Next.js API endpoint: `src/app/api/recovery/route.ts`
- Knowledge base files: `conocimiento_consolidado.json`, `base_conocimiento_exportada.json`
- Configuration files: `config.py`, `.env`
- Backup files scattered in root directory with patterns: `kb_populated*.json`, `backup*.json`

## Implementation Requirements

### 1. Automated Backup System

**Create a Python service (`scripts/automated_backup_service.py`) that:**

- Performs full MongoDB backups daily at 2:00 AM UTC
- Performs incremental backups every 6 hours
- Backs up critical collections: `conversations`, `quotes`, `sessions`, `context`, `analytics`
- Backs up filesystem files: knowledge base JSON files, config files, `.env` (encrypted)
- Stores backups in organized directory structure: `backups/YYYY-MM-DD/backup_<type>_<timestamp>.json`
- Implements backup rotation: keep daily backups for 30 days, weekly for 12 weeks, monthly for 12 months
- Compresses backups using gzip
- Encrypts sensitive data (AES-256)
- Generates checksums (SHA-256) for integrity verification
- Logs all operations with timestamps and status
- Sends notifications on backup success/failure (email/Slack)

**Backup Format:**
```json
{
  "backup_metadata": {
    "timestamp": "ISO-8601 timestamp",
    "backup_type": "full|incremental",
    "version": "1.0.0",
    "database": "bmc-cotizaciones",
    "backup_id": "unique_id"
  },
  "collections": {
    "conversations": [...],
    "quotes": [...]
  },
  "filesystem": {
    "knowledge_base": {...},
    "config": {...}
  },
  "checksums": {
    "conversations": "sha256:...",
    "filesystem": "sha256:..."
  }
}
```

### 2. Enhanced Recovery Scanner

**Enhance `scripts/recover_conversations.py` to:**

- Scan MongoDB collections with parallel processing for large datasets
- Scan filesystem recursively for backup files matching patterns:
  - `**/conversation*.json`
  - `**/backup*.json`
  - `**/export*.json`
  - `**/kb_populated*.json`
  - `**/recovery_report*.json`
- Search directories: `backups/`, `exportaciones/`, `exports/`, `data/`, `.whatsapp_temp/`, root directory
- Extract conversations from multiple JSON formats (arrays, nested objects, single objects)
- Generate comprehensive recovery report with:
  - MongoDB scan results (collection counts, sample data)
  - Filesystem scan results (file paths, sizes, conversation counts)
  - Data integrity analysis
  - Recommendations for recovery
- Support dry-run mode for safe testing
- Provide progress tracking for long operations
- Export recovery report as JSON and human-readable markdown

### 3. Data Restoration Engine

**Implement restoration functionality that:**

- Restores data from backup files to MongoDB collections
- Supports multiple conflict resolution strategies:
  - `skip_duplicates`: Skip records that already exist (default)
  - `overwrite`: Replace existing records with backup data
  - `merge`: Combine fields from both sources intelligently
  - `timestamp_based`: Keep the most recent version
- Validates data before restoration (required fields, data types)
- Performs post-restoration verification (count checks, integrity checks)
- Creates rollback backup before restoration
- Supports selective restoration (specific collections, date ranges, session IDs)
- Provides detailed restoration report (restored count, skipped count, errors)
- Handles large datasets efficiently (batch processing, progress updates)

**Restoration API:**
```python
def restore_from_backup(
    backup_file: str,
    target_collection: str,
    strategy: str = "skip_duplicates",
    dry_run: bool = False,
    filters: Dict = None  # e.g., {"date_range": {...}, "session_ids": [...]}
) -> Dict[str, Any]
```

### 4. Recovery API Endpoints

**Enhance `src/app/api/recovery/route.ts` with:**

**GET /api/recovery/scan**
- Scan for recoverable data from MongoDB and filesystem
- Query params: `source=mongodb|filesystem|all`, `collection=<name>`
- Returns comprehensive recovery report

**GET /api/recovery/backup**
- Create manual backup
- Query params: `type=full|incremental`, `collection=<name>`
- Returns backup ID, file path, timestamp, size

**POST /api/recovery/restore**
- Restore data from backup
- Body: `{backup_file, target_collection, strategy, dry_run, filters}`
- Returns restoration results and validation

**GET /api/recovery/backups**
- List available backups with metadata
- Query params: `limit=50`, `type=full|incremental`, `date_from`, `date_to`
- Returns paginated list of backups

**DELETE /api/recovery/backups/:id**
- Delete specific backup (with confirmation)
- Returns success status

**GET /api/recovery/validate/:backup_id**
- Validate backup file integrity
- Returns validation results (checksums, structure, data integrity)

### 5. Monitoring & Alerting

**Implement monitoring system:**

- Track backup success/failure rates
- Monitor backup durations and file sizes
- Track storage space usage
- Alert on:
  - Backup failure for 24+ hours (critical)
  - Recovery operation failure (critical)
  - Storage space below 10% (critical)
  - Backup delayed by > 2 hours (warning)
  - Data integrity check failure (critical)
- Send notifications via:
  - Email (SMTP)
  - Slack webhook
  - Discord webhook
  - Log file

**Metrics Dashboard:**
- Backup success rate over time
- Storage usage trends
- Recovery operation history
- System health status
- Alert timeline

### 6. Security & Access Control

**Implement security measures:**

- Require admin authentication for all backup/restore operations
- Rate limit API endpoints (10 GET requests/15min, 5 POST requests/15min)
- Encrypt sensitive data in backups (AES-256)
- Secure encryption key storage (environment variable or key file with restricted permissions)
- Use HTTPS for all API communications
- Implement audit logging for all operations
- Restrict file system permissions (backup directory: 755, backup files: 600)

### 7. Testing & Validation

**Create test suite:**

- Unit tests for backup creation, scanning, restoration
- Integration tests for end-to-end recovery workflows
- Load tests for large datasets (10K+ conversations)
- Data integrity tests
- Conflict resolution tests
- Rollback tests

**Test Scenarios:**
1. Create backup → Delete data → Restore → Verify
2. Restore with duplicate detection
3. Restore with conflict resolution (overwrite, merge)
4. Restore selective data (date range, session IDs)
5. Validate backup integrity
6. Test rollback functionality

### 8. Documentation

**Create comprehensive documentation:**

- User guide for backup/restore operations
- API documentation with examples
- Troubleshooting guide
- Runbook for common scenarios
- Architecture diagrams
- Configuration reference

## Implementation Guidelines

1. **Code Quality:**
   - Use type hints in Python
   - Follow PEP 8 style guide
   - Add comprehensive docstrings
   - Handle errors gracefully with meaningful messages
   - Log all operations with appropriate log levels

2. **Performance:**
   - Use parallel processing for large datasets
   - Implement batch processing for MongoDB operations
   - Compress backups to save storage
   - Optimize file scanning with efficient glob patterns
   - Cache frequently accessed data

3. **Reliability:**
   - Implement retry logic for transient failures
   - Validate data before operations
   - Create rollback capabilities
   - Test error scenarios
   - Handle edge cases (empty collections, corrupted files)

4. **Maintainability:**
   - Use configuration files for settings
   - Make code modular and reusable
   - Add comprehensive comments
   - Follow DRY principles
   - Create helper utilities for common operations

## Expected Deliverables

1. ✅ `scripts/automated_backup_service.py` - Automated backup service
2. ✅ Enhanced `scripts/recover_conversations.py` - Enhanced recovery scanner
3. ✅ `scripts/restore_data.py` - Data restoration engine
4. ✅ Enhanced `src/app/api/recovery/route.ts` - Recovery API endpoints
5. ✅ `scripts/monitor_backups.py` - Monitoring and alerting service
6. ✅ `tests/test_backup_recovery.py` - Test suite
7. ✅ `docs/BACKUP_RECOVERY_GUIDE.md` - User documentation
8. ✅ `backup_config.json` - Configuration file
9. ✅ `scripts/setup_backup_system.sh` - Setup script
10. ✅ Cron job configuration examples

## Success Criteria

- ✅ Automated backups run successfully on schedule
- ✅ Recovery operations restore data within acceptable timeframes (< 10 min for 10K records)
- ✅ Data integrity maintained throughout backup/restore cycles
- ✅ System can recover from data loss scenarios
- ✅ Monitoring provides timely notifications
- ✅ Security measures protect sensitive data
- ✅ Documentation enables effective system usage

## Constraints

- Must work with existing MongoDB setup
- Must not disrupt running chatbot services
- Must handle large datasets efficiently (10K+ conversations)
- Must be compatible with Python 3.8+ and Node.js 18+
- Must follow existing code patterns and conventions

## Questions to Consider

1. How should we handle partial backups if MongoDB connection fails mid-backup?
2. What's the best strategy for backing up large files (knowledge base JSON files)?
3. How should we handle version compatibility between backup formats?
4. What's the optimal backup frequency to balance data safety and performance?
5. How should we handle cloud storage integration (AWS S3, Google Cloud Storage)?

---

**Start implementing the backup and recovery system following these requirements. Begin with the automated backup service, then move to the recovery scanner, restoration engine, API endpoints, and finally monitoring and documentation.**
