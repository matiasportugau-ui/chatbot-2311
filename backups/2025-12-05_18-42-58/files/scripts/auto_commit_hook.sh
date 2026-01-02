#!/bin/bash
# Git Auto-Commit Hook
# Creates a backup branch before major changes or tags significant commits

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
COMMIT_MSG=$(cat "$1")

# Count changes
FILES_CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
LINES_ADDED=$(git diff --cached --numstat | awk '{sum+=$1} END {print sum}')
LINES_DELETED=$(git diff --cached --numstat | awk '{sum+=$2} END {print sum}')

# If significant changes, create backup branch
if [ "$FILES_CHANGED" -gt 10 ] || [ "$LINES_ADDED" -gt 500 ] || [ "$LINES_DELETED" -gt 500 ]; then
    BACKUP_BRANCH="backup-$(date +%Y-%m-%d-%H%M%S)-${BRANCH_NAME}"
    echo "Significant changes detected. Creating backup branch: $BACKUP_BRANCH"
    git branch "$BACKUP_BRANCH" HEAD
    echo "Backup branch created: $BACKUP_BRANCH"
fi

# Tag significant commits
if [ "$FILES_CHANGED" -gt 5 ] || [ "$LINES_ADDED" -gt 100 ]; then
    TAG_NAME="checkpoint-$(date +%Y%m%d-%H%M%S)"
    git tag -a "$TAG_NAME" -m "Auto-checkpoint: $COMMIT_MSG" HEAD
    echo "Checkpoint tag created: $TAG_NAME"
fi

exit 0

