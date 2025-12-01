# 🤖 AI Agent Prompt: Backup & Lost File Recovery Implementation

Use this prompt to instruct an AI agent to implement backup and data recovery functionality.

---

## 📋 PROMPT TEMPLATE

```
## Task: Implement Backup and Lost File Recovery System

### Context
I need a comprehensive backup and data recovery system for my [TECHNOLOGY_STACK] application.
The application stores [DATA_TYPES] that are critical and need recovery capabilities.

### Requirements

#### 1. Data Recovery Scanner
Create a recovery scanner that:
- Connects to [DATABASE_TYPE] and scans for existing data
- Searches filesystem for backup files matching patterns: [PATTERNS]
- Supports data formats: [JSON/CSV/other]
- Generates detailed recovery reports

#### 2. Backup System
Implement backup functionality that:
- Creates timestamped snapshots of database collections
- Stores backups in structured JSON format
- Supports incremental backups (optional)
- Validates backup integrity

#### 3. Restore Capability
Build restore functionality that:
- Parses backup files of various formats
- Validates data before restoration
- Handles duplicate records (upsert/skip/fail)
- Provides dry-run mode for preview
- Logs all restoration operations

#### 4. API Endpoints (if applicable)
Create REST API endpoints:
- GET /api/recovery?action=scan - Scan for recoverable data
- GET /api/recovery?action=backup - Create new backup
- POST /api/recovery - Restore from backup data

#### 5. CLI Interface (if applicable)
Provide command-line interface:
- `--scan` - Run recovery scan
- `--backup` - Create backup
- `--restore <file>` - Restore from backup
- `--dry-run` - Preview without changes
- `--output <file>` - Save report

### Data Structures

#### Collections to backup/recover:
[LIST YOUR COLLECTIONS/TABLES]
- conversations: {session_id, phone, messages[], timestamps}
- sessions: {id, user_id, context, state}
- quotes: {id, products[], pricing, status}

#### Backup file format:
{
  "timestamp": "ISO-8601",
  "version": "1.0",
  "source": "app-name",
  "collections": {
    "collection_name": [records...]
  },
  "metadata": {
    "total_records": number,
    "checksum": "hash"
  }
}

### Technical Constraints
- Database: [MongoDB/PostgreSQL/MySQL/etc]
- Language: [Python/TypeScript/etc]
- Framework: [Next.js/Express/Flask/etc]
- Must handle connection timeouts gracefully
- Must include error handling and logging
- Should support large datasets (streaming if needed)

### Security Requirements
- Admin-only access for recovery operations
- Rate limiting on API endpoints
- Audit logging for all operations
- No sensitive data in logs

### Output Expected
1. Recovery script/module with full implementation
2. API routes (if applicable)
3. CLI interface (if applicable)
4. Usage documentation
5. Example recovery report

### Success Criteria
- Successfully scans and detects all data sources
- Creates valid backup files
- Restores data without loss or corruption
- Handles edge cases (empty data, duplicates, large files)
- Provides clear status and error messages
```

---

## 🎯 QUICK PROMPTS

### Minimal Python Recovery Script
```
Create a Python script that:
1. Connects to MongoDB and scans for conversation data
2. Scans the local filesystem for JSON backup files
3. Can restore conversations from backup files to MongoDB
4. Generates a JSON report of all found data
Include error handling and command-line arguments.
```

### Minimal TypeScript API
```
Create a Next.js API route at /api/recovery that:
1. GET with action=scan: Scans MongoDB and filesystem for data
2. GET with action=backup: Creates backup of current data
3. POST: Restores data from provided JSON body
Include proper error handling and return structured responses.
```

### Add Recovery to Existing App
```
I have an existing [FRAMEWORK] application with [DATABASE] storing [DATA_TYPES].
Add backup and recovery functionality with:
- Automated daily backups
- Manual recovery scan command
- API endpoint for administrators
- Recovery report generation
Use the existing database connection from [CONNECTION_FILE].
```

---

## 📊 EXPECTED OUTPUTS

### Recovery Report Example
```json
{
  "timestamp": "2025-12-01T10:30:00.000Z",
  "database": {
    "connected": true,
    "name": "myapp-db",
    "collections": {
      "conversations": 150,
      "sessions": 75,
      "quotes": 42
    },
    "total_found": 267
  },
  "filesystem": {
    "backups": [
      {
        "path": "backups/backup_20251201_093000.json",
        "name": "backup_20251201_093000.json",
        "size": 245760,
        "record_count": 200,
        "modified": "2025-12-01T09:30:00.000Z"
      }
    ],
    "total_found": 200
  },
  "summary": {
    "total_recovered": 467,
    "status": "success",
    "recommendations": [
      "All data sources accessible",
      "Backup files are current"
    ],
    "errors": []
  }
}
```

### Console Output Example
```
======================================================================
🔍 DATA RECOVERY SYSTEM
======================================================================

📦 Creating pre-recovery backup...
✅ Backup created: backups/pre_recovery_20251201_103000.json

🔍 Scanning database...
✅ Connected to MongoDB: myapp-db
  📊 conversations: 150 documents
  📊 sessions: 75 documents
  📊 quotes: 42 documents

📁 Scanning filesystem for backup files...
  📁 Found: backup_20251130.json (200 records)
  📁 Found: export_conversations.json (50 records)

======================================================================
📋 RECOVERY SUMMARY
======================================================================
  Database: 267 records found
  Filesystem: 250 records found
  Status: SUCCESS

💡 Recommendations:
  - All systems operational
  - Consider archiving old backups

💾 Report saved: recovery_report_20251201_103000.json
======================================================================
```

---

## 🔧 CUSTOMIZATION VARIABLES

Replace these placeholders in the prompts:

| Variable | Description | Examples |
|----------|-------------|----------|
| `[TECHNOLOGY_STACK]` | Your tech stack | Node.js/Next.js, Python/FastAPI |
| `[DATABASE_TYPE]` | Database system | MongoDB, PostgreSQL, MySQL |
| `[DATA_TYPES]` | Types of data | conversations, user sessions, orders |
| `[PATTERNS]` | Backup file patterns | `**/backup*.json`, `exports/*.csv` |
| `[FRAMEWORK]` | Web framework | Next.js, Express, Django, Flask |
| `[CONNECTION_FILE]` | DB connection file | `src/lib/mongodb.ts`, `config/db.py` |

---

## ⚡ ONE-LINER PROMPTS

```
# Python: Quick MongoDB recovery script
"Create a Python script to scan MongoDB for conversations and recover from JSON backup files with CLI support"

# TypeScript: Next.js recovery API
"Add /api/recovery endpoint to scan MongoDB, create backups, and restore data with admin auth"

# Add to existing project
"Analyze my codebase and add backup/recovery for the main data collections with filesystem and database scanning"

# Fix data loss
"My MongoDB data was lost. Create a recovery system to find and restore from any backup files in the project"
```

---

*Use these prompts with Claude, GPT-4, or other AI assistants to generate complete backup/recovery implementations.*
