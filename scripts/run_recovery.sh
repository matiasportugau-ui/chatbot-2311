#!/bin/bash
#
# Cursor Data Recovery Helper Script
# Executes recovery tasks in priority order
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$WORKSPACE_DIR/cursor_workspace_backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "Cursor Data Recovery Script"
echo "=========================================="
echo "Workspace: $WORKSPACE_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Task 1: Extract Cursor Chat Data
echo -e "${GREEN}[TASK 1]${NC} Extracting Cursor chat data..."
if python3 "$SCRIPT_DIR/extract_cursor_chat.py" \
    --project-path "$WORKSPACE_DIR" \
    --backup-dir "$BACKUP_DIR" \
    --output "$WORKSPACE_DIR/chat_recovery_$TIMESTAMP.json"; then
    echo -e "${GREEN}✓${NC} Chat extraction completed"
else
    echo -e "${YELLOW}⚠${NC} Chat extraction failed or no data found"
fi
echo ""

# Task 2: Review Existing Recovery Reports
echo -e "${GREEN}[TASK 2]${NC} Reviewing existing recovery reports..."
if [ -f "$WORKSPACE_DIR/RECOVERY_SUMMARY.md" ]; then
    echo "Found: RECOVERY_SUMMARY.md"
    echo "---"
    head -20 "$WORKSPACE_DIR/RECOVERY_SUMMARY.md"
    echo "---"
    echo -e "${GREEN}✓${NC} Recovery reports reviewed"
else
    echo -e "${YELLOW}⚠${NC} No existing recovery reports found"
fi
echo ""

# Task 3: Search for Temporary Files
echo -e "${GREEN}[TASK 3]${NC} Searching for temporary files..."
TEMP_FILES="$WORKSPACE_DIR/temp_files_found_$TIMESTAMP.txt"
find "$WORKSPACE_DIR" \
    -name "*~" -o \
    -name "*.bak" -o \
    -name "*.swp" -o \
    -name "*.tmp" -o \
    -name "*.autosave" \
    2>/dev/null > "$TEMP_FILES" || true

if [ -s "$TEMP_FILES" ]; then
    echo "Found temporary files:"
    cat "$TEMP_FILES"
    echo -e "${GREEN}✓${NC} Temporary files search completed"
else
    echo "No temporary files found"
    echo -e "${GREEN}✓${NC} Temporary files search completed (none found)"
fi
echo ""

# Task 5: Verify Git Stashes
echo -e "${GREEN}[TASK 5]${NC} Checking git stashes..."
cd "$WORKSPACE_DIR"
if git stash list | grep -q .; then
    echo "Found stashes:"
    git stash list
    echo -e "${GREEN}✓${NC} Git stashes found"
else
    echo "No git stashes found"
    echo -e "${GREEN}✓${NC} Git stashes check completed"
fi
echo ""

# Summary
echo "=========================================="
echo "Recovery Summary"
echo "=========================================="
echo "Chat recovery file: chat_recovery_$TIMESTAMP.json"
echo "Temporary files list: temp_files_found_$TIMESTAMP.txt"
echo "Backup directory: $BACKUP_DIR"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review chat_recovery_$TIMESTAMP.json for extracted conversations"
echo "2. Check Cursor Timeline for file versions (manual action)"
echo "3. Review temp_files_found_$TIMESTAMP.txt for backup files"
echo "4. Check system backups if available"
echo ""
echo "For detailed instructions, see: CURSOR_DATA_RECOVERY_PLAN.md"
