# 🔄 Backup & Lost File Recovery Implementation Prompt

## Overview

This document provides a comprehensive prompt and implementation guide for developing backup and lost file recovery systems. Use this as a template for AI agents or developers implementing data recovery functionality.

---

## 🎯 Implementation Prompt Template

```
You are implementing a backup and lost file recovery system for a [APPLICATION_TYPE] application.
The system should:

1. **Detect Data Loss**
   - Scan database for missing or corrupted records
   - Check filesystem for backup files and exports
   - Identify partial or incomplete data

2. **Recovery Sources**
   - Database collections/tables
   - Filesystem backup files (JSON, CSV, etc.)
   - Export files from previous operations
   - Log files with embedded data

3. **Recovery Operations**
   - Scan: Detect and catalog recoverable data
   - Backup: Create snapshots of current state
   - Restore: Recover data from backups to database
   - Validate: Verify integrity of recovered data

4. **Data Structures to Recover**
   - [LIST YOUR DATA TYPES: conversations, sessions, quotes, users, etc.]

5. **Output**
   - Detailed recovery report (JSON format)
   - Summary with recommendations
   - Audit log of all recovery actions
```

---

## 📋 Core Recovery System Architecture

### 1. Python Recovery Script Pattern

```python
#!/usr/bin/env python3
"""
Template: Backup and Recovery System
Customize for your specific data types and sources
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class DataRecovery:
    """Universal data recovery system"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.db_uri = self.config.get('db_uri') or os.getenv('DATABASE_URI', '')
        self.backup_dir = Path(self.config.get('backup_dir', 'backups'))
        self.report = self._init_report()
        
    def _init_report(self) -> Dict[str, Any]:
        """Initialize recovery report structure"""
        return {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "connected": False,
                "name": "",
                "collections": {},
                "total_found": 0
            },
            "filesystem": {
                "backups": [],
                "exports": [],
                "total_found": 0
            },
            "summary": {
                "total_recovered": 0,
                "status": "pending",
                "recommendations": [],
                "errors": []
            }
        }
    
    def connect_database(self) -> bool:
        """Establish database connection"""
        # Implement for your database type
        raise NotImplementedError("Override for specific database")
    
    def scan_database(self) -> Dict[str, Any]:
        """Scan database for existing data"""
        raise NotImplementedError("Override for specific database")
    
    def scan_filesystem(self, patterns: List[str] = None) -> List[Dict]:
        """Scan filesystem for backup files"""
        patterns = patterns or [
            "**/backup*.json",
            "**/export*.json",
            "**/*_data.json"
        ]
        
        found_files = []
        search_paths = [
            Path.cwd(),
            self.backup_dir,
            Path.cwd() / "exports",
            Path.cwd() / "data"
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
            for pattern in patterns:
                for file_path in search_path.glob(pattern):
                    if file_path.is_file():
                        file_info = self._analyze_backup_file(file_path)
                        if file_info:
                            found_files.append(file_info)
                            
        return found_files
    
    def _analyze_backup_file(self, file_path: Path) -> Optional[Dict]:
        """Analyze a potential backup file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = self._extract_records(data)
            if records:
                return {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                    "record_count": len(records),
                    "sample": records[:3]
                }
        except (json.JSONDecodeError, Exception) as e:
            self.report["summary"]["errors"].append(
                f"Error reading {file_path.name}: {str(e)}"
            )
        return None
    
    def _extract_records(self, data: Any) -> List[Dict]:
        """Extract records from various data formats"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check common container keys
            for key in ['data', 'records', 'items', 'conversations', 
                       'messages', 'collections']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Check if dict has nested collections
            if 'collections' in data and isinstance(data['collections'], dict):
                all_records = []
                for collection_data in data['collections'].values():
                    if isinstance(collection_data, list):
                        all_records.extend(collection_data)
                return all_records
            # Single record format
            if 'id' in data or '_id' in data or 'session_id' in data:
                return [data]
        return []
    
    def create_backup(self, name_prefix: str = "backup") -> str:
        """Create backup of current database state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{name_prefix}_{timestamp}.json"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "source": "database",
            "collections": {}
        }
        
        # Collect data from database
        db_data = self.scan_database()
        for collection_name, records in db_data.items():
            backup_data["collections"][collection_name] = records
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(backup_file)
    
    def restore_from_backup(
        self, 
        backup_path: str, 
        target_collection: str = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Restore data from backup file"""
        result = {
            "success": False,
            "restored": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            records = self._extract_records(data)
            
            if dry_run:
                result["success"] = True
                result["restored"] = len(records)
                result["dry_run"] = True
                return result
            
            for record in records:
                try:
                    self._insert_record(record, target_collection)
                    result["restored"] += 1
                except Exception as e:
                    result["failed"] += 1
                    result["errors"].append(str(e))
            
            result["success"] = result["failed"] == 0
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def _insert_record(self, record: Dict, collection: str = None):
        """Insert a record into the database"""
        raise NotImplementedError("Override for specific database")
    
    def run_full_recovery(self, create_backup_first: bool = True) -> Dict:
        """Execute complete recovery scan"""
        print("=" * 70)
        print("🔍 DATA RECOVERY SYSTEM")
        print("=" * 70)
        
        # Optional: Create backup first
        if create_backup_first:
            try:
                backup_file = self.create_backup("pre_recovery")
                print(f"📦 Pre-recovery backup: {backup_file}")
            except Exception as e:
                print(f"⚠️ Backup failed: {e}")
        
        # Scan database
        print("\n🔍 Scanning database...")
        if self.connect_database():
            db_data = self.scan_database()
            for collection, records in db_data.items():
                count = len(records) if isinstance(records, list) else records
                print(f"  📊 {collection}: {count} records")
                self.report["database"]["total_found"] += count
        
        # Scan filesystem
        print("\n📁 Scanning filesystem...")
        backup_files = self.scan_filesystem()
        for backup in backup_files:
            print(f"  📁 {backup['name']}: {backup['record_count']} records")
        self.report["filesystem"]["backups"] = backup_files
        self.report["filesystem"]["total_found"] = sum(
            b["record_count"] for b in backup_files
        )
        
        # Generate summary
        self._generate_summary()
        self._print_summary()
        
        return self.report
    
    def _generate_summary(self):
        """Generate recovery summary and recommendations"""
        total = (
            self.report["database"]["total_found"] + 
            self.report["filesystem"]["total_found"]
        )
        self.report["summary"]["total_recovered"] = total
        
        if total > 0:
            self.report["summary"]["status"] = "success"
            if self.report["database"]["total_found"] == 0:
                self.report["summary"]["recommendations"].append(
                    "Data found in backups but not in database. "
                    "Consider restoring from backups."
                )
        else:
            self.report["summary"]["status"] = "failed"
            self.report["summary"]["recommendations"].append(
                "No recoverable data found. Check backup locations."
            )
    
    def _print_summary(self):
        """Print recovery summary"""
        print("\n" + "=" * 70)
        print("📋 RECOVERY SUMMARY")
        print("=" * 70)
        print(f"  Database: {self.report['database']['total_found']} records")
        print(f"  Filesystem: {self.report['filesystem']['total_found']} records")
        print(f"  Status: {self.report['summary']['status'].upper()}")
        
        if self.report["summary"]["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in self.report["summary"]["recommendations"]:
                print(f"  - {rec}")
        
        if self.report["summary"]["errors"]:
            print("\n⚠️ Errors:")
            for error in self.report["summary"]["errors"][:5]:
                print(f"  - {error}")
    
    def save_report(self, output_file: str = None) -> str:
        """Save recovery report to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"recovery_report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Report saved: {output_file}")
        return output_file
```

---

### 2. TypeScript/Next.js API Pattern

```typescript
// src/app/api/recovery/route.ts
export const dynamic = 'force-dynamic'

import { NextRequest, NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'

interface RecoveryResult {
  source: string
  collection?: string
  count: number
  data: any[]
  errors?: string[]
}

interface RecoveryReport {
  timestamp: string
  database: {
    connected: boolean
    name: string
    collections: RecoveryResult[]
    totalFound: number
  }
  filesystem: {
    backups: RecoveryResult[]
    totalFound: number
  }
  summary: {
    totalRecovered: number
    status: 'success' | 'partial' | 'failed'
    recommendations: string[]
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const action = searchParams.get('action') || 'scan'
  const dryRun = searchParams.get('dryRun') === 'true'

  const report: RecoveryReport = initReport()

  switch (action) {
    case 'scan':
      await scanDatabase(report)
      await scanFilesystem(report)
      generateSummary(report)
      break
    case 'backup':
      return await createBackup()
    default:
      return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
  }

  return NextResponse.json({ success: true, report, dryRun })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const { action, source, data, targetCollection } = body

  if (action === 'restore') {
    return await restoreData(data, targetCollection)
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 })
}

function initReport(): RecoveryReport {
  return {
    timestamp: new Date().toISOString(),
    database: { connected: false, name: '', collections: [], totalFound: 0 },
    filesystem: { backups: [], totalFound: 0 },
    summary: { totalRecovered: 0, status: 'pending', recommendations: [] }
  }
}

async function scanDatabase(report: RecoveryReport) {
  // Implement database scanning logic
  // Example for MongoDB:
  try {
    const db = await connectDB()
    report.database.connected = true
    report.database.name = db.databaseName

    const collections = ['conversations', 'sessions', 'quotes']
    for (const name of collections) {
      const count = await db.collection(name).countDocuments({})
      if (count > 0) {
        const data = await db.collection(name).find({}).limit(100).toArray()
        report.database.collections.push({ source: 'mongodb', collection: name, count, data })
        report.database.totalFound += count
      }
    }
  } catch (error: any) {
    report.summary.recommendations.push(`Database error: ${error.message}`)
  }
}

async function scanFilesystem(report: RecoveryReport) {
  const backupPatterns = [/backup.*\.json$/i, /export.*\.json$/i]
  const searchDirs = ['backups', 'exports', '.']

  for (const dir of searchDirs) {
    try {
      const dirPath = path.join(process.cwd(), dir)
      const files = await fs.readdir(dirPath, { withFileTypes: true })

      for (const file of files) {
        if (file.isFile() && backupPatterns.some(p => p.test(file.name))) {
          const content = await fs.readFile(path.join(dirPath, file.name), 'utf-8')
          const data = JSON.parse(content)
          const records = extractRecords(data)
          
          if (records.length > 0) {
            report.filesystem.backups.push({
              source: 'filesystem',
              count: records.length,
              data: records.slice(0, 50)
            })
            report.filesystem.totalFound += records.length
          }
        }
      }
    } catch (err) {
      // Directory might not exist
    }
  }
}

function extractRecords(data: any): any[] {
  if (Array.isArray(data)) return data
  if (data?.conversations) return data.conversations
  if (data?.data) return data.data
  if (data?.collections) {
    return Object.values(data.collections).flat()
  }
  if (data?.messages || data?.session_id) return [data]
  return []
}

function generateSummary(report: RecoveryReport) {
  const total = report.database.totalFound + report.filesystem.totalFound
  report.summary.totalRecovered = total

  if (total > 0) {
    report.summary.status = 'success'
    if (report.database.totalFound === 0) {
      report.summary.recommendations.push(
        'Data found in backups but not in database. Consider restoring.'
      )
    }
  } else {
    report.summary.status = 'failed'
    report.summary.recommendations.push('No recoverable data found.')
  }
}

async function createBackup() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const backupDir = path.join(process.cwd(), 'backups')
  await fs.mkdir(backupDir, { recursive: true })

  const db = await connectDB()
  const backupData = { timestamp: new Date().toISOString(), collections: {} }

  for (const name of ['conversations', 'sessions', 'quotes']) {
    const data = await db.collection(name).find({}).toArray()
    if (data.length > 0) {
      backupData.collections[name] = data
    }
  }

  const backupFile = path.join(backupDir, `backup_${timestamp}.json`)
  await fs.writeFile(backupFile, JSON.stringify(backupData, null, 2))

  return NextResponse.json({ success: true, file: backupFile, timestamp })
}

async function restoreData(data: any[], targetCollection: string = 'conversations') {
  const db = await connectDB()
  const collection = db.collection(targetCollection)
  let restored = 0, failed = 0

  for (const item of data) {
    try {
      const { _id, ...itemData } = item
      itemData.restoredAt = new Date()
      await collection.insertOne(itemData)
      restored++
    } catch (err) {
      failed++
    }
  }

  return NextResponse.json({ success: true, restored, failed })
}
```

---

## 📂 Data Format Specifications

### Backup File Structure

```json
{
  "timestamp": "2025-12-01T10:30:00.000Z",
  "version": "1.0",
  "source": "application-name",
  "collections": {
    "conversations": [
      {
        "session_id": "unique-session-id",
        "phone": "+1234567890",
        "started_at": "2025-12-01T09:00:00.000Z",
        "messages": [
          {
            "timestamp": "2025-12-01T09:00:00.000Z",
            "user_message": "Hello",
            "bot_response": {
              "message": "Hi! How can I help?",
              "type": "greeting",
              "confidence": 0.95
            }
          }
        ]
      }
    ],
    "sessions": [...],
    "quotes": [...]
  },
  "metadata": {
    "total_records": 100,
    "exported_by": "backup-system",
    "checksum": "sha256-hash"
  }
}
```

### Recovery Report Structure

```json
{
  "timestamp": "2025-12-01T10:30:00.000Z",
  "database": {
    "connected": true,
    "name": "app-database",
    "collections": {
      "conversations": 50,
      "sessions": 25
    },
    "total_found": 75
  },
  "filesystem": {
    "backups": [
      {
        "path": "/backups/backup_20251201.json",
        "name": "backup_20251201.json",
        "size": 15240,
        "record_count": 30,
        "modified": "2025-12-01T08:00:00.000Z"
      }
    ],
    "total_found": 30
  },
  "summary": {
    "total_recovered": 105,
    "status": "success",
    "recommendations": [
      "All data successfully recovered"
    ],
    "errors": []
  }
}
```

---

## 🔧 CLI Usage

### Python Script

```bash
# Full recovery scan
python scripts/recover_data.py

# Scan without creating backup first
python scripts/recover_data.py --no-backup

# Restore from specific backup
python scripts/recover_data.py --restore backups/backup_20251201.json

# Restore to specific collection
python scripts/recover_data.py --restore backup.json --target-collection conversations

# Output JSON report
python scripts/recover_data.py --output recovery_report.json
```

### API Endpoints

```bash
# Scan for recoverable data
curl http://localhost:3000/api/recovery?action=scan

# Create backup
curl http://localhost:3000/api/recovery?action=backup

# Dry run scan
curl http://localhost:3000/api/recovery?action=scan&dryRun=true

# Restore data
curl -X POST http://localhost:3000/api/recovery \
  -H "Content-Type: application/json" \
  -d '{
    "action": "restore",
    "source": "filesystem",
    "targetCollection": "conversations",
    "data": [...]
  }'
```

---

## ✅ Implementation Checklist

### Core Features
- [ ] Database connection handling with timeout
- [ ] Filesystem scanning with glob patterns
- [ ] Multiple data format support (JSON, CSV)
- [ ] Backup creation with timestamps
- [ ] Data restoration with validation
- [ ] Recovery report generation
- [ ] Error handling and logging

### Security
- [ ] Admin authentication for API endpoints
- [ ] Rate limiting for recovery operations
- [ ] Sensitive data handling (redact in logs)
- [ ] Backup file encryption (optional)
- [ ] Audit logging for all operations

### Data Integrity
- [ ] Checksum validation for backups
- [ ] Duplicate detection during restore
- [ ] Transaction support for batch operations
- [ ] Rollback capability on failure

### Monitoring
- [ ] Recovery operation metrics
- [ ] Alert on data loss detection
- [ ] Backup schedule verification
- [ ] Storage space monitoring

---

## 🚨 Common Issues & Solutions

### Issue: Database Connection Timeout
```python
# Solution: Configure timeout and retry
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
for attempt in range(3):
    try:
        client.admin.command('ping')
        break
    except Exception:
        time.sleep(1)
```

### Issue: Large Backup Files
```python
# Solution: Stream processing
def stream_backup(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)
```

### Issue: Duplicate Records During Restore
```python
# Solution: Upsert with unique key
collection.update_one(
    {"session_id": record["session_id"]},
    {"$set": record},
    upsert=True
)
```

---

## 📚 Related Files in This Project

| File | Purpose |
|------|---------|
| `scripts/recover_conversations.py` | Python recovery script |
| `scripts/recover_setup.py` | Setup recovery utility |
| `src/app/api/recovery/route.ts` | API recovery endpoint |
| `RECOVERY_SUMMARY.md` | Recovery documentation |
| `recovery_report_*.json` | Generated reports |

---

## 🔗 Quick Reference

```
# Recovery Workflow
1. SCAN    → Detect available data sources
2. BACKUP  → Create snapshot before changes
3. ANALYZE → Review report and recommendations
4. RESTORE → Recover data to target location
5. VERIFY  → Validate restored data integrity
```

---

*Last Updated: December 1, 2025*
