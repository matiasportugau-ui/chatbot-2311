# Recovery Quick Start Guide

## Quick Recovery Steps

### 1. Run Automated Recovery Script

```bash
./scripts/run_recovery.sh
```

This will:
- Extract chat data from Cursor workspace storage
- Search for temporary files
- Check git stashes
- Create backups

### 2. Extract Chat Data Manually (if script fails)

```bash
python3 scripts/extract_cursor_chat.py \
  --project-path /workspace \
  --backup-dir ./cursor_workspace_backup \
  --output chat_recovery_$(date +%Y%m%d_%H%M%S).json
```

### 3. Review Extracted Data

```bash
# View the extracted chat data
cat chat_recovery_*.json | jq '.'

# Search for specific keywords
cat chat_recovery_*.json | jq '.entries[] | select(.value | tostring | contains("your_keyword"))'
```

### 4. Check Cursor Timeline (Manual)

1. Open Cursor
2. For each file that may have been modified:
   - Right-click → "Open Timeline"
   - Or: Command Palette → "Local History: Find Entry to Restore"
3. Restore versions from before the crash

### 5. Check System Backups

```bash
# Check for common backup locations
ls -la ~/backups/
ls -la ~/.backup/
ls -la ~/Documents/backups/

# Check for cloud sync folders
ls -la ~/Dropbox/
ls -la ~/Google\ Drive/
```

## Recovery Likelihood

| Source | Likelihood | Action |
|--------|-----------|--------|
| Cursor Chat DB | **HIGH** | Run extraction script |
| Cursor Timeline | **MEDIUM** | Check manually in Cursor |
| System Backups | **MEDIUM** | Check backup locations |
| Git History | **LOW** | Already checked (clean) |
| Temp Files | **LOW** | Script searches automatically |

## Files Created

- `chat_recovery_*.json` - Extracted chat data
- `temp_files_found_*.txt` - List of temporary files
- `cursor_workspace_backup/` - Backup of workspace storage

## Full Documentation

See `CURSOR_DATA_RECOVERY_PLAN.md` for complete details.

## Need Help?

1. Review `CURSOR_DATA_RECOVERY_PLAN.md` for detailed instructions
2. Check `recovery_plan.json` for structured task list
3. Review `RECOVERY_SUMMARY.md` for previous recovery context
