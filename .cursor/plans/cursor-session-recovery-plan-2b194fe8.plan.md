<!-- 2b194fe8-cd0a-443f-842e-b5a9fad554ef 56b56b6f-5166-465d-b864-6257151915ca -->
# Cursor Session Recovery Implementation Plan

## Overview

This plan provides a systematic approach to recover:

1. **AI chat/context** from recent Cursor sessions (within last 24 hours)
2. **Unsaved code** or transient editor buffers from crashed sessions
3. **Enhanced recovery capabilities** for future incidents

**Current State:**

- Git repository with 141+ modified files (uncommitted work is safe)
- Previous recovery extracted 65,972 chat items (saved to `RecoveredChats.md` and `recovered_chats.json`)
- Multiple Cursor workspace databases identified in `~/Library/Application Support/Cursor/User/workspaceStorage/`
- Recent commits show active development on streaming, WhatsApp integration

**Recovery Likelihood:**

- **Cursor Chat DB**: HIGH (databases accessible, previous extraction successful)
- **Git History**: HIGH (reflog available, recent commits present)
- **Local History/Timeline**: MEDIUM (depends on Cursor's local history feature)
- **Unsaved Buffers**: LOW (RAM contents lost, but may exist in Cursor's temp files)
- **Time Machine**: UNKNOWN (needs user verification)

---

## Phase 1: Baseline & Repository State Analysis

### Task 1.1: Complete Git State Assessment

**Type:** analysis

**Priority:** 1

**Description:** Document current git state, identify all modified/untracked files, and compare with HEAD to detect any missing work.

**Commands:**

```bash
cd /Users/matias/chatbot2511/chatbot-2311
git status --porcelain > recovery_git_status.txt
git diff --stat > recovery_git_diff_stat.txt
git diff > recovery_git_diff_full.txt
git log --all --oneline --graph -20 > recovery_git_log.txt
git reflog -20 > recovery_git_reflog.txt
```

**Prerequisites:** Git repository initialized

**Caution:** All operations are read-only, safe to run

**Status:** pending

### Task 1.2: Identify Workspace-Specific Files

**Type:** analysis

**Priority:** 1

**Description:** Map current workspace to Cursor's workspaceStorage hash to target the correct database.

**Commands:**

```bash
# Find workspace hash by matching project path or modification date
cd ~/Library/Application\ Support/Cursor/User/workspaceStorage/
for dir in */; do
  if [ -f "$dir/state.vscdb" ]; then
    echo "Workspace: $dir"
    ls -lT "$dir/state.vscdb" | awk '{print $6, $7, $8, $9}'
  fi
done
```

**Prerequisites:** Cursor workspaceStorage directory exists

**Caution:** Read-only operation

**Status:** pending

---

## Phase 2: Enhanced Cursor Chat & Context Recovery

### Task 2.1: Backup All Cursor Databases

**Type:** script

**Priority:** 1

**Description:** Create timestamped backups of all state.vscdb files before analysis to prevent data loss.

**Commands:**

```bash
BACKUP_DIR="$HOME/Desktop/cursor_workspace_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
find ~/Library/Application\ Support/Cursor/User/workspaceStorage/ -name "state.vscdb" -exec cp {} "$BACKUP_DIR/" \;
cp ~/Library/Application\ Support/Cursor/User/globalStorage/state.vscdb "$BACKUP_DIR/" 2>/dev/null || true
echo "Backups created in: $BACKUP_DIR"
```

**Prerequisites:** Cursor installed, workspaceStorage accessible

**Caution:** Creates copies, does not modify originals

**Status:** pending

### Task 2.2: Enhanced Chat Extraction with Time Filtering

**Type:** script

**Priority:** 1

**Description:** Create improved extraction script that filters chat data by time window (last 24 hours) and extracts full conversation context including code edits.

**Script Location:** `recovery_extract_recent_chats.py`

**Key Features:**

- Filter by timestamp (last 24 hours from current time)
- Extract full conversation threads with code context
- Parse composer data for unsaved edits
- Export to both JSON and markdown with better formatting
- Include session metadata (titles, timestamps, file contexts)

**Prerequisites:** Python 3, sqlite3 module

**Caution:** Operates on database copies from Task 2.1

**Status:** pending

### Task 2.3: Extract Composer/Unsaved Buffer Data

**Type:** script

**Priority:** 2

**Description:** Extract data from Cursor's composer state that may contain unsaved code edits or partial conversations.

**Script Location:** `recovery_extract_composer.py`

**Key Queries:**

- `composerData` keys in ItemTable
- `chat.composer.*` entries
- Recent edit history from workspace state
- File-specific unsaved changes

**Prerequisites:** Task 2.1 completed

**Caution:** Some data may be encrypted or in binary format

**Status:** pending

### Task 2.4: Reconstruct Conversation Context

**Type:** script

**Priority:** 2

**Description:** Parse extracted chat data to reconstruct full conversation threads, identify code changes discussed, and map to project files.

**Script Location:** `recovery_reconstruct_context.py`

**Output:**

- Conversation timeline with code references
- List of files mentioned or modified in conversations
- Code snippets extracted from chat history
- Session summaries with key decisions

**Prerequisites:** Task 2.2 completed

**Status:** pending

---

## Phase 3: Local History & File-Level Recovery

### Task 3.1: Check Cursor Local History (Timeline)

**Type:** user_action

**Priority:** 2

**Description:** For each modified file identified in Phase 1, use Cursor's Timeline feature to view local history and recover previous versions.

**Steps:**

1. Open each modified file in Cursor
2. Right-click → "Open Timeline" or use Command Palette → "Timeline: Open Timeline"
3. Review versions from last 24 hours
4. Restore or copy content from versions before crash

**Files to Check:** All files listed in `recovery_git_status.txt` with status `M` (modified)

**Prerequisites:** Cursor IDE open, files accessible

**Caution:** Timeline may not have all versions if file was never saved

**Status:** pending

### Task 3.2: Scan for Temporary/Backup Files

**Type:** script

**Priority:** 2

**Description:** Search for temporary files, backup files, or swap files that may contain unsaved code.

**Commands:**

```bash
cd /Users/matias/chatbot2511/chatbot-2311
# Find common backup patterns
find . -type f \( -name "*~" -o -name "*.bak" -o -name "*.swp" -o -name "*.tmp" -o -name "*#*#" \) -mtime -1 -ls > recovery_temp_files.txt

# Check macOS-specific temp locations
mdfind -name "chatbot-2311" -onlyin ~/Library/Caches 2>/dev/null | head -20
mdfind -name "chatbot-2311" -onlyin /tmp 2>/dev/null | head -20
```

**Prerequisites:** File system access

**Caution:** Some temp files may be locked or require special permissions

**Status:** pending

### Task 3.3: Analyze Git Stashes

**Type:** analysis

**Priority:** 2

**Description:** Review git stashes to identify any stashed work that might contain lost code.

**Commands:**

```bash
cd /Users/matias/chatbot2511/chatbot-2311
git stash list > recovery_stash_list.txt
for i in $(seq 0 $(($(git stash list | wc -l) - 1))); do
  echo "=== Stash $i ===" >> recovery_stash_contents.txt
  git stash show -p stash@{$i} >> recovery_stash_contents.txt
done
```

**Prerequisites:** Git repository, stashes may exist

**Caution:** Do not apply stashes without reviewing contents first

**Status:** pending

### Task 3.4: Time Machine Recovery (If Available)

**Type:** user_action

**Priority:** 3

**Description:** If Time Machine is enabled, guide user to restore project folder and Cursor workspaceStorage from snapshot just before crash.

**Steps:**

1. Open Time Machine
2. Navigate to `/Users/matias/chatbot2511/chatbot-2311`
3. Find snapshot from before crash (within last 24 hours)
4. Restore specific files or entire folder to a temporary location
5. Compare restored files with current versions

**Prerequisites:** Time Machine enabled and recent backups available

**Caution:** Restore to separate location first, compare before overwriting

**Status:** pending

---

## Phase 4: Advanced Recovery Methods

### Task 4.1: SQLite Database Deep Analysis

**Type:** script

**Priority:** 3

**Description:** Perform deep analysis of Cursor databases to find deleted records, WAL files, or journal entries that might contain lost data.

**Script Location:** `recovery_deep_db_analysis.py`

**Techniques:**

- Check for WAL (Write-Ahead Log) files
- Analyze SQLite journal files
- Query for deleted but not yet vacuumed records
- Check for uncommitted transactions

**Prerequisites:** Task 2.1 completed, SQLite tools available

**Caution:** Advanced operation, may require database locking knowledge

**Status:** pending

### Task 4.2: File System Event Log Analysis

**Type:** analysis

**Priority:** 3

**Description:** Check macOS file system event logs (if available) to identify files that were created/modified/deleted around crash time.

**Commands:**

```bash
# Check if fseventsd logs are accessible (usually requires admin)
# Note: This is read-only and may not be accessible on all systems
log show --predicate 'process == "Cursor"' --last 24h --info 2>/dev/null | grep -i "chatbot-2311" | head -50
```

**Prerequisites:** macOS system logs accessible, may require admin rights

**Caution:** Limited availability, may not contain useful data

**Status:** pending

---

## Phase 5: Recovery Consolidation & Enhancement

### Task 5.1: Generate Recovery Report

**Type:** script

**Priority:** 1

**Description:** Consolidate all recovery findings into a comprehensive report with recovery likelihood assessment.

**Script Location:** `recovery_generate_report.py`

**Output:**

- Summary of recovered items
- List of irrecoverable items with reasons
- Recovery statistics (files recovered, chat items found, etc.)
- Recommendations for next steps

**Prerequisites:** All previous phases completed

**Status:** pending

### Task 5.2: Create Automated Recovery Script

**Type:** script

**Priority:** 2

**Description:** Create a unified recovery script that automates all recovery phases for future use.

**Script Location:** `recovery_automated.py`

**Features:**

- Single command execution
- Configurable time windows
- Automatic backup creation
- Progress reporting
- Error handling and logging

**Prerequisites:** All individual recovery scripts tested

**Status:** pending

### Task 5.3: Implement Preventive Measures

**Type:** script

**Priority:** 2

**Description:** Create scripts and configurations to prevent future data loss.

**Components:**

1. **Git Auto-Commit Hook:** Script to auto-commit on significant changes
2. **Chat Export Automation:** Periodic export of Cursor chat to markdown
3. **Workspace Backup Script:** Scheduled backup of Cursor workspaceStorage
4. **File Change Monitor:** Watch for unsaved changes and create snapshots

**Script Locations:**

- `scripts/auto_commit_hook.sh`
- `scripts/export_chat_periodic.py`
- `scripts/backup_workspace.sh`

**Prerequisites:** User approval for automation setup

**Caution:** Some automation may require system permissions

**Status:** pending

---

## Recovery Likelihood Assessment

| Channel | Likelihood | Notes |

|---------|------------|-------|

| **Cursor Chat DB** | HIGH | Databases accessible, previous extraction successful (65,972 items found) |

| **Git History/Reflog** | HIGH | Active git repository with recent commits and reflog entries |

| **Local History/Timeline** | MEDIUM | Depends on Cursor's local history feature, may not have all versions |

| **Git Stashes** | MEDIUM | 2 stashes available, need to check contents |

| **Temporary Files** | LOW | OS temp files usually cleared, but worth checking |

| **Composer/Unsaved Buffers** | LOW | RAM contents lost, but may exist in Cursor's state DB |

| **Time Machine** | UNKNOWN | Requires user verification if enabled |

| **File System Logs** | LOW | Limited availability, may not contain useful data |

---

## Irrecoverable Items

Based on typical crash scenarios, the following are likely **irrecoverable**:

1. **Unsaved buffers never written to disk** - If code was typed but never saved and not captured in chat history
2. **RAM-only state** - Any in-memory state that wasn't persisted to disk
3. **Deleted files without git history** - Files deleted and not tracked by git
4. **Recent edits in crashed session** - Edits made in the crashed session that weren't auto-saved

---

## Suggested Enhancements

### Enhancement 1: Cursor Extension for Chat Export

**Description:** Create or recommend a Cursor extension that automatically exports chat history to markdown files on a schedule.

**Implementation:** Research existing Cursor extensions or create custom extension using Cursor's extension API.

**Benefit:** Prevents chat history loss by maintaining external backups.

### Enhancement 2: Git Auto-Save Hook

**Description:** Implement a git pre-commit hook that creates a backup branch before major changes, or a post-commit hook that tags significant commits.

**Implementation:** Create `.git/hooks/pre-commit` script that checks for large changes and creates backup branch.

**Benefit:** Provides git-level recovery points for significant work.

### Enhancement 3: Workspace State Monitor

**Description:** Background service that periodically snapshots Cursor's workspaceStorage to a backup location.

**Implementation:** Python script or shell script with cron/launchd scheduling.

**Benefit:** Enables point-in-time recovery of workspace state.

### Enhancement 4: Enhanced Error Handling

**Description:** Improve error handling in AI agent actions to prevent crashes and ensure state is saved before risky operations.

**Implementation:** Add try-catch blocks, state checkpoints, and rollback mechanisms in agent workflows.

**Benefit:** Reduces likelihood of data loss from crashes.

### Enhancement 5: Recovery Dashboard

**Description:** Create a simple dashboard or CLI tool to monitor recovery status and provide quick access to recovery functions.

**Implementation:** Next.js dashboard or Python CLI tool that displays recovery statistics and provides one-click recovery actions.

**Benefit:** Makes recovery more accessible and user-friendly.

---

## Risks & Limitations

1. **Database Locking:** Cursor may lock databases while running, requiring Cursor to be closed for some operations
2. **Encrypted Data:** Some Cursor data may be encrypted and require decryption keys
3. **Binary Formats:** Some state data may be in binary formats requiring specialized parsing
4. **Time Window Accuracy:** Timestamp filtering depends on accurate system clocks and Cursor's timestamp storage
5. **File System Permissions:** Some operations may require elevated permissions
6. **Data Corruption:** Crashed sessions may have left databases in inconsistent states

---

## Execution Order

1. **Immediate (Priority 1):** Tasks 1.1, 1.2, 2.1, 2.2 - Establish baseline and extract recent chat data
2. **Short-term (Priority 2):** Tasks 2.3, 2.4, 3.1, 3.2, 3.3 - Deep extraction and local history recovery
3. **Medium-term (Priority 3):** Tasks 3.4, 4.1, 4.2 - Advanced recovery methods
4. **Final (Priority 1-2):** Tasks 5.1, 5.2, 5.3 - Consolidation and prevention

---

## Next Steps

1. Review this plan and confirm priorities
2. Execute Phase 1 tasks to establish baseline
3. Execute Phase 2 tasks to extract recent chat data
4. Review recovered data and identify gaps
5. Execute Phase 3 tasks for file-level recovery
6. Implement preventive measures from Phase 5