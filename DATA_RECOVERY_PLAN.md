# Data Recovery Implementation Plan

**Generated:** 2025-12-01T20:21:54Z  
**Agent:** RecoveryPlanAgent  
**Environment:** Linux (Remote/Container)  
**Workspace:** /workspace (chatbot-2311)

---

## Overview

This document provides a comprehensive, actionable plan to recover:
1. **AI chat/context** from the last Cursor sessions for this project
2. **Unsaved code or transient editor buffers** accessible via local files, history, or backups

The plan also proposes enhancements to improve recovery success in future incidents.

---

## Phase 1 — Baseline & Repository State

### Findings

| Check | Result |
|-------|--------|
| Git Repository | ✅ Yes (`/workspace`) |
| Current Branch | `cursor/design-data-recovery-implementation-plan-claude-4.5-opus-high-thinking-5192` |
| Working Tree | ✅ Clean (no uncommitted changes) |
| Untracked Files | None |
| Git Stashes | None |
| Remote | `origin` → `github.com/matiasportugau-ui/chatbot-2311` |

### Recent Commits (Last 5)

| Hash | Description | Files Changed |
|------|-------------|---------------|
| `907d957` | feat: Complete setup and installation enhancement | 10 files (+3,562 lines) |
| `666f21a` | feat: Add knowledge consolidation step to unified launcher | 3 files (+242 lines) |
| `377cfa1` | docs: Add documentation update summary | 1 file (+105 lines) |
| `1c68b53` | docs: Add QUICK_ACCESS.md for easy reference | 1 file (+137 lines) |
| `068ce69` | docs: Update all documentation to feature Unified Launcher | 11 files (+586 lines) |

### Baseline Summary

- ✅ **All code is safely committed** — No uncommitted changes detected
- ✅ **No deleted files** in working tree
- ✅ **No pending modifications** — Clean working directory
- ⚠️ **Git reflog** shows only clone and checkout operations (new workspace)

**Conclusion:** From a Git perspective, no code recovery is needed. All work has been committed.

---

## Phase 2 — Cursor-Specific Storage (Chat & Context)

### Goal
Extract AI chat history from Cursor's workspace storage.

### Environment Analysis

| Location | Status |
|----------|--------|
| `~/.cursor/` | ❌ Not found |
| `~/.config/Cursor/` | ❌ Not found |
| `/home/ubuntu/.cursor/` | ❌ Not found |
| `state.vscdb` files | ❌ None found in filesystem |

**Key Finding:** This is a **remote/containerized environment** (devcontainer) that does not have standard Cursor workspace storage. The Cursor application's persistent storage is on the **local machine** (macOS/Windows) where Cursor is running, not in this remote workspace.

### Recovery Strategy for Chat Data

#### For macOS (User's Local Machine)

```bash
# 1. Locate workspace storage
CURSOR_STORAGE=~/Library/Application\ Support/Cursor/User/workspaceStorage

# 2. Find the workspace folder for this project (by modification time or content)
ls -lt "$CURSOR_STORAGE" | head -20

# 3. Create backup before analysis
mkdir -p ~/Desktop/cursor_workspace_backup
cp -r "$CURSOR_STORAGE" ~/Desktop/cursor_workspace_backup/

# 4. Run extraction script (copy to local machine first)
python scripts/extract_cursor_chat.py \
  --workspace-storage "$CURSOR_STORAGE" \
  --output ~/Desktop/chat_recovery \
  --backup-first \
  --keywords "chatbot" "WhatsApp" "n8n" \
  --format markdown
```

#### For Linux (Local Machine)

```bash
CURSOR_STORAGE=~/.config/Cursor/User/workspaceStorage
# Same commands as above
```

#### For Windows (Local Machine)

```powershell
$CURSOR_STORAGE = "$env:APPDATA\Cursor\User\workspaceStorage"
# Adapt commands for PowerShell
```

### Extraction Script Location

A Python script has been created for extracting chat data:

```
/workspace/scripts/extract_cursor_chat.py
```

**Features:**
- Scans all workspaceStorage folders
- Extracts data from `state.vscdb` SQLite databases
- Searches for keys containing: `aichat`, `composer`, `chat`, `history`, etc.
- Filters by keywords and time window
- Creates backups before analysis
- Outputs JSON or Markdown

---

## Phase 3 — Local History, Backups & File-Level Recovery

### Cursor Timeline (Local History)

The Cursor/VS Code Timeline feature stores local history for edited files. Access on the **local machine**:

1. Open any file in Cursor
2. Click **Timeline** in the Explorer panel
3. View and restore previous versions

**Note:** Timeline data is stored in Cursor's local storage, not in the remote workspace.

### Git Reflog Recovery

```bash
# View reflog
git reflog -20

# If you find a relevant commit, checkout to inspect
git checkout <commit-hash>

# Or create a branch from it
git branch recovery-branch <commit-hash>
```

### Git Stash Check

```bash
# List stashes
git stash list

# Apply a stash if found
git stash apply stash@{0}
```

### Temporary/Backup Files Scan

```bash
# Search for backup files
find /workspace -name "*~" -o -name "*.bak" -o -name "*.swp" -o -name ".#*" 2>/dev/null

# Search for recent JSON files (conversation backups)
ls -latr /workspace/*.json | tail -20
```

### Existing Recovery Reports Found

| File | Timestamp | Contents |
|------|-----------|----------|
| `recovery_report_20251128_010159.json` | 2025-11-28 | MongoDB + filesystem scan results |
| `recovery_report_20251128_010201.json` | 2025-11-28 | Similar recovery scan |
| `recovery_report_20251128_010136.json` | 2025-11-28 | Similar recovery scan |
| `recovery_report_20251128_010119.json` | 2025-11-28 | Similar recovery scan |

### Conversation Backup Files Found

13 `kb_populated_*.json` files containing conversation backups from 2025-11-09:

| File | Conversations |
|------|---------------|
| `kb_populated_Multi-turn_Conversation_20251109_234035.json` | 1 (11 messages) |
| `kb_populated_Quote_with_Questions_20251109_235129.json` | 1 (8 messages) |
| `kb_populated_Complete_Quote_Request_Flow_20251109_234648.json` | 1 (6 messages) |
| `kb_populated_Conversation_with_Objections_20251109_234342.json` | 1 (6 messages) |
| ... and 9 more files | ... |

### Time Machine / System Backups

**User Action Required:**

If Time Machine is enabled on macOS:

1. Open Time Machine
2. Navigate to `~/Library/Application Support/Cursor/User/workspaceStorage`
3. Go back to the time before the crash
4. Restore the relevant workspace folder

---

## Phase 4 — Advanced / Last-Resort Options

### RAM Recovery
❌ **Not Feasible** — After a hard crash, RAM contents are lost and cannot be recovered.

### Raw Disk Forensics

If mission-critical data is missing:

1. **Stop writing to the disk immediately** to prevent overwriting deleted data
2. Create a **full disk clone** using `dd` or specialized tools
3. Use file carving tools like:
   - `photorec` (open source)
   - `testdisk` (open source)
   - Commercial forensic tools

⚠️ **Caution:** This requires specialized skills and is typically only worthwhile for truly irreplaceable data.

---

## Phase 5 — Feasibility Assessment & Implementation Plan

### Recovery Likelihood Assessment

| Channel | Likelihood | Notes |
|---------|------------|-------|
| `cursor_chat_db` | **MEDIUM** | Requires access to local machine's Cursor storage. Script provided. |
| `git_history` | **HIGH** | All code appears committed. Clean working tree. |
| `local_backups` | **MEDIUM** | Timeline data on local machine. 13 conversation backups in workspace. |
| `temp_files` | **LOW** | No temp/backup files found in workspace. |
| `mongodb_data` | **HIGH** | Previous recovery found 14 conversations in MongoDB (if accessible). |

### Prioritized Task List

#### Task 1: Extract Cursor Chat from Local Machine
- **ID:** `task-1`
- **Type:** `user_action`
- **Priority:** 1 (High)
- **Description:** Run the chat extraction script on the local machine where Cursor is installed to recover AI chat history.
- **Commands:**
  ```bash
  # Copy script to local machine, then run:
  python extract_cursor_chat.py \
    --workspace-storage ~/Library/Application\ Support/Cursor/User/workspaceStorage \
    --output ~/Desktop/chat_recovery \
    --backup-first \
    --keywords "chatbot" "recovery" "MongoDB" \
    --format markdown
  ```
- **Prerequisites:** Script copied to local machine, Python 3 installed
- **Caution:** Always use `--backup-first` flag
- **Status:** `pending`

#### Task 2: Review Existing Recovery Reports
- **ID:** `task-2`
- **Type:** `analysis`
- **Priority:** 1 (High)
- **Description:** Analyze the existing recovery reports to understand what data was previously recovered and identify gaps.
- **Commands:**
  ```bash
  cat /workspace/recovery_report_20251128_010159.json | python -m json.tool
  ```
- **Prerequisites:** None
- **Caution:** None
- **Status:** `pending`

#### Task 3: Run Conversation Recovery Script
- **ID:** `task-3`
- **Type:** `script`
- **Priority:** 1 (High)
- **Description:** Execute the existing conversation recovery script to scan MongoDB and filesystem for conversation data.
- **Commands:**
  ```bash
  cd /workspace
  python scripts/recover_conversations.py --no-backup --output recovery_latest.json
  ```
- **Prerequisites:** MongoDB accessible (optional)
- **Caution:** May fail if MongoDB is not running
- **Status:** `pending`

#### Task 4: Check Cursor Timeline on Local Machine
- **ID:** `task-4`
- **Type:** `user_action`
- **Priority:** 2 (Medium)
- **Description:** Use Cursor's Timeline feature to check local history for any files that may have been edited but not saved.
- **Commands:** Manual action in Cursor UI
- **Prerequisites:** Cursor open on local machine
- **Caution:** None
- **Status:** `pending`

#### Task 5: Check Time Machine Backup
- **ID:** `task-5`
- **Type:** `user_action`
- **Priority:** 2 (Medium)
- **Description:** If Time Machine is enabled, restore Cursor workspace storage from backup.
- **Commands:**
  ```bash
  # On macOS, enter Time Machine and navigate to:
  # ~/Library/Application Support/Cursor/User/workspaceStorage
  ```
- **Prerequisites:** Time Machine enabled
- **Caution:** Restore to a different location first
- **Status:** `pending`

#### Task 6: Export Conversation Backups
- **ID:** `task-6`
- **Type:** `script`
- **Priority:** 2 (Medium)
- **Description:** Consolidate all kb_populated_*.json files into a single recovery archive.
- **Commands:**
  ```bash
  mkdir -p /workspace/recovery_archive
  cp /workspace/kb_populated_*.json /workspace/recovery_archive/
  python -c "
  import json, glob, os
  files = glob.glob('/workspace/recovery_archive/kb_populated_*.json')
  all_convs = []
  for f in files:
      with open(f) as fp:
          data = json.load(fp)
          if isinstance(data, list):
              all_convs.extend(data)
          elif 'conversations' in data:
              all_convs.extend(data['conversations'])
  with open('/workspace/recovery_archive/all_conversations.json', 'w') as fp:
      json.dump(all_convs, fp, indent=2)
  print(f'Consolidated {len(all_convs)} conversations')
  "
  ```
- **Prerequisites:** None
- **Caution:** None
- **Status:** `pending`

#### Task 7: Git Reflog Inspection
- **ID:** `task-7`
- **Type:** `analysis`
- **Priority:** 3 (Low)
- **Description:** Inspect git reflog for any unreachable commits that might contain lost code.
- **Commands:**
  ```bash
  git reflog --all
  git fsck --unreachable
  ```
- **Prerequisites:** None
- **Caution:** None
- **Status:** `pending`

#### Task 8: Setup Automated Chat Export
- **ID:** `task-8`
- **Type:** `script`
- **Priority:** 3 (Low)
- **Description:** Configure automated periodic export of chat data to prevent future data loss.
- **Commands:** See "Suggested Enhancements" section
- **Prerequisites:** Implementation of enhancement
- **Caution:** None
- **Status:** `pending`

### Irrecoverable Items

| Type | Reason |
|------|--------|
| `unsaved_buffer` | New files never written to disk or included in git are irrecoverable after crash |
| `ram_contents` | In-memory editor state lost on crash, cannot be recovered |
| `realtime_chat` | Chat messages not yet persisted to state.vscdb are lost |

---

## Suggested Enhancements

### Enhancement 1: Automated Chat Export Extension

**ID:** `enh-1`

Install or develop a Cursor extension that periodically exports AI chat history to markdown files within the project.

```javascript
// Conceptual implementation for Cursor extension
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function exportChatHistory() {
  const chatHistory = vscode.workspace.getConfiguration('cursor').get('chatHistory');
  const exportPath = path.join(vscode.workspace.rootPath, '.cursor-chats');
  
  fs.mkdirSync(exportPath, { recursive: true });
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `chat-export-${timestamp}.md`;
  
  fs.writeFileSync(path.join(exportPath, filename), formatChatAsMarkdown(chatHistory));
}

// Run every 30 minutes
setInterval(exportChatHistory, 30 * 60 * 1000);
```

### Enhancement 2: Git Pre-Commit Hook for Unsaved Changes

**ID:** `enh-2`

Add a git hook that warns about unsaved files before committing.

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for common unsaved file patterns in editor state
if [ -d ".vscode" ]; then
  echo "Warning: Check for unsaved files before committing"
fi
```

### Enhancement 3: Periodic State Backup Script

**ID:** `enh-3`

Create a cron job or scheduled task to backup Cursor's workspace storage.

```bash
#!/bin/bash
# backup_cursor_state.sh

CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"
BACKUP_DIR="$HOME/.cursor_backups"

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

rsync -a "$CURSOR_STORAGE" "$BACKUP_DIR/workspace_$TIMESTAMP/"

# Keep only last 10 backups
ls -dt "$BACKUP_DIR"/* | tail -n +11 | xargs rm -rf
```

Add to crontab:
```bash
# Run every 2 hours
0 */2 * * * /path/to/backup_cursor_state.sh
```

### Enhancement 4: MongoDB Auto-Backup

**ID:** `enh-4`

Configure MongoDB to create automatic backups of conversation data.

```bash
# Add to docker-compose.yml
services:
  mongodb-backup:
    image: mongo:latest
    volumes:
      - ./backups:/backups
    command: >
      bash -c "while true; do
        mongodump --uri='mongodb://mongodb:27017' --out=/backups/$(date +%Y%m%d_%H%M%S);
        sleep 3600;
      done"
```

### Enhancement 5: Recovery Dashboard

**ID:** `enh-5`

Create a simple web dashboard to monitor recovery status and available backups.

```python
# recovery_dashboard.py
from flask import Flask, render_template, jsonify
import glob
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    backups = glob.glob('backups/*.json')
    recovery_reports = glob.glob('recovery_report_*.json')
    return render_template('dashboard.html', 
                          backups=backups, 
                          reports=recovery_reports)

@app.route('/api/status')
def status():
    return jsonify({
        'backups': len(glob.glob('backups/*.json')),
        'conversations': len(glob.glob('kb_populated_*.json')),
        'last_recovery': os.path.getmtime('recovery_report_20251128_010159.json')
    })
```

---

## Risks & Limitations

### Current Limitations

1. **Remote Environment:** This workspace runs in a container/remote environment. Cursor's persistent storage (including chat history) is on the local machine, not accessible from here.

2. **No Direct Database Access:** The `state.vscdb` files are SQLite databases on the local machine. The extraction script must be run locally.

3. **MongoDB Availability:** The conversation recovery script requires MongoDB to be running. If it's not available, only filesystem backups can be recovered.

4. **Time Sensitivity:** The longer the wait before recovery, the higher the risk of data being overwritten or garbage collected.

### Mitigation Strategies

1. **Immediate Action:** Run recovery tasks as soon as possible
2. **Work on Copies:** Always backup databases before analysis
3. **Multiple Sources:** Check all possible data sources (chat DB, timeline, backups, MongoDB)
4. **Document Findings:** Record all recovery attempts and results

---

## Execution Checklist

- [ ] **Task 1:** Run chat extraction script on local machine
- [ ] **Task 2:** Review existing recovery reports in workspace
- [ ] **Task 3:** Run conversation recovery script
- [ ] **Task 4:** Check Cursor Timeline for unsaved changes
- [ ] **Task 5:** Check Time Machine backup (if available)
- [ ] **Task 6:** Export and consolidate conversation backups
- [ ] **Task 7:** Inspect git reflog for unreachable commits
- [ ] **Task 8:** Implement automated backup enhancements

---

## Appendix: Quick Commands Reference

```bash
# Check git status
git status && git log -3 --oneline

# Find recovery files
ls -la /workspace/recovery_report_*.json

# Run existing recovery script
python scripts/recover_conversations.py --no-backup

# Extract Cursor chat (on local machine)
python scripts/extract_cursor_chat.py --workspace-storage ~/Library/Application\ Support/Cursor/User/workspaceStorage --output ~/Desktop/chat_recovery --backup-first

# Consolidate conversation backups
cp /workspace/kb_populated_*.json /workspace/recovery_archive/
```

---

*Generated by RecoveryPlanAgent*
