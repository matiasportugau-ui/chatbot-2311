#!/bin/bash
# Workspace Backup Script
# Scheduled backup of Cursor workspaceStorage to prevent data loss

BACKUP_BASE_DIR="$HOME/Desktop/cursor_workspace_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/backup_$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup workspaceStorage
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"
if [ -d "$CURSOR_STORAGE" ]; then
    echo "Backing up workspaceStorage..."
    cp -r "$CURSOR_STORAGE" "$BACKUP_DIR/workspaceStorage"
    echo "✓ WorkspaceStorage backed up"
fi

# Backup globalStorage
CURSOR_GLOBAL="$HOME/Library/Application Support/Cursor/User/globalStorage"
if [ -d "$CURSOR_GLOBAL" ]; then
    echo "Backing up globalStorage..."
    cp -r "$CURSOR_GLOBAL" "$BACKUP_DIR/globalStorage"
    echo "✓ GlobalStorage backed up"
fi

# Create backup manifest
MANIFEST_FILE="$BACKUP_DIR/manifest.json"
cat > "$MANIFEST_FILE" << EOF
{
  "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_timestamp": "$TIMESTAMP",
  "backup_location": "$BACKUP_DIR",
  "workspace_storage_backed_up": $([ -d "$BACKUP_DIR/workspaceStorage" ] && echo "true" || echo "false"),
  "global_storage_backed_up": $([ -d "$BACKUP_DIR/globalStorage" ] && echo "true" || echo "false")
}
EOF

echo "Backup complete: $BACKUP_DIR"
echo "Manifest: $MANIFEST_FILE"

# Clean up old backups (keep last 7 days)
find "$BACKUP_BASE_DIR" -type d -name "backup_*" -mtime +7 -exec rm -rf {} \; 2>/dev/null
echo "Cleaned up backups older than 7 days"

