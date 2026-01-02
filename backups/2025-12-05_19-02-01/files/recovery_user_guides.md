# Recovery User Guides

This document provides step-by-step instructions for manual recovery tasks.

## Task 3.1: Check Cursor Local History (Timeline)

Cursor's Timeline feature allows you to view and restore previous versions of files.

### Steps:

1. **Open the file in Cursor** that you want to recover
   
2. **Access Timeline:**
   - **Method 1:** Right-click on the file in the Explorer → "Open Timeline"
   - **Method 2:** Use Command Palette (Cmd+Shift+P) → Type "Timeline: Open Timeline"
   - **Method 3:** Click the clock icon in the file editor tab

3. **Review versions:**
   - Timeline shows all saved versions of the file
   - Versions are sorted by date (most recent first)
   - Each version shows the date/time it was saved

4. **Restore a version:**
   - Click on a version to preview it
   - Click "Restore" or "Compare with Current" to see differences
   - Copy content manually or restore the entire file

5. **Files to check:**
   - All files listed in `recovery_git_status.txt` with status `M` (modified)
   - Open the file and check: `cat recovery_git_status.txt | grep "^ M"`

### Tips:
- Timeline only shows versions that were saved to disk
- Unsaved changes in editor buffers won't appear in Timeline
- Timeline data is stored locally by Cursor

---

## Task 3.4: Time Machine Recovery (If Available)

If Time Machine is enabled on your Mac, you can restore files from before the crash.

### Prerequisites:
- Time Machine must be enabled
- Backup disk must be connected (or network backup accessible)
- You need to know approximately when the crash occurred

### Steps:

1. **Open Time Machine:**
   - Click the Time Machine icon in the menu bar, OR
   - Open System Settings → Time Machine → "Enter Time Machine"

2. **Navigate to project folder:**
   - In Finder, navigate to: `/Users/matias/chatbot2511/chatbot-2311`
   - Enter Time Machine from this location

3. **Find the snapshot:**
   - Use the timeline on the right side to navigate to before the crash
   - Look for a snapshot from within the last 24 hours (or your crash time window)
   - Browse the folder to see files as they were at that time

4. **Restore files:**
   - **Option A: Restore entire folder**
     - Select the project folder
     - Click "Restore" (restores to a new location to avoid overwriting)
   
   - **Option B: Restore specific files**
     - Navigate to specific files you need
     - Select files and click "Restore"
     - Choose restore location (recommend a temporary folder first)

5. **Compare and merge:**
   - After restoring to a temporary location, compare with current files
   - Use `diff` or a merge tool to identify differences
   - Manually copy needed content to current files

6. **Restore Cursor workspaceStorage (if needed):**
   - Navigate to: `~/Library/Application Support/Cursor/User/workspaceStorage/`
   - Find the workspace folder (hash) for your project
   - Restore the `state.vscdb` file from before the crash
   - **Warning:** This will overwrite current workspace state. Make a backup first!

### Safety Tips:
- Always restore to a separate location first
- Compare restored files with current versions before overwriting
- Make backups of current state before restoring from Time Machine
- Test restored files in a separate branch before merging

### Alternative: Command Line Time Machine

If you prefer command line:

```bash
# List available backups
tmutil listbackups

# Restore a specific file
tmutil restore "/Users/matias/chatbot2511/chatbot-2311/path/to/file" /tmp/restored_file

# Restore entire directory
tmutil restore "/Users/matias/chatbot2511/chatbot-2311" /tmp/restored_project
```

---

## Additional Recovery Tips

### If Time Machine is Not Available:

1. **Check other backup solutions:**
   - iCloud Drive (if enabled)
   - Dropbox, Google Drive, or other cloud sync
   - External drive backups
   - Git remote repositories

2. **Check system caches:**
   - Some applications cache file versions
   - Check `~/Library/Caches/` for application-specific caches

3. **Check for auto-save features:**
   - Some editors create auto-save files
   - Check for files with `.autosave` or similar extensions

4. **Check version control:**
   - Review git history: `git log --all --oneline`
   - Check for uncommitted changes: `git status`
   - Review stashes: `git stash list`

---

## Recovery Checklist

Use this checklist to ensure you've tried all recovery methods:

- [ ] Reviewed `recovery_recent_chats.md` for chat history
- [ ] Reviewed `recovery_composer_data.json` for unsaved edits
- [ ] Checked git stashes (`recovery_stash_contents.txt`)
- [ ] Reviewed git diff (`recovery_git_diff_full.txt`)
- [ ] Checked Cursor Timeline for each modified file
- [ ] Checked Time Machine (if available)
- [ ] Reviewed `recovery_final_report.md` for summary
- [ ] Committed current work to prevent further loss

---

## Getting Help

If recovery is unsuccessful:

1. Review `recovery_final_report.md` for detailed findings
2. Check `recovery_final_report.json` for machine-readable data
3. Review individual recovery output files
4. Consider professional data recovery services for critical data

