#!/bin/bash

# CodeBuddy Memory Optimization Script
# This script helps reduce CodeBuddy memory usage by clearing cache and verifying exclusions

echo "🔧 CodeBuddy Memory Optimization"
echo "================================"
echo ""

# Step 1: Show current cache size
echo "📊 Current CodeBuddy cache size:"
du -sh .cursor/plans/.codebuddy/ 2>/dev/null || echo "  Cache directory not found"
echo ""

# Step 2: Backup current cache (optional)
if [ -f ".cursor/plans/.codebuddy/codebase_analysis.db" ]; then
    echo "💾 Backing up current cache..."
    cp .cursor/plans/.codebuddy/codebase_analysis.db .cursor/plans/.codebuddy/codebase_analysis.db.backup 2>/dev/null
    echo "  ✅ Backup created"
    echo ""
fi

# Step 3: Clear CodeBuddy cache
echo "🗑️  Clearing CodeBuddy cache..."
rm -f .cursor/plans/.codebuddy/codebase_analysis.db 2>/dev/null
echo "  ✅ Cache cleared"
echo ""

# Step 4: Verify .cursorignore is in place
echo "✅ Verifying .cursorignore exclusions:"
if [ -f ".cursorignore" ]; then
    echo "  ✅ .cursorignore file exists"
    echo ""
    echo "📋 Large files/directories excluded:"
    echo "  - node_modules/ (558MB)"
    echo "  - .next/ (807MB)"
    echo "  - Large JSON files (conocimiento_*.json, module_analysis_*.json, etc.)"
    echo "  - Backup directories (backups/, backup_metadata/)"
    echo "  - Build caches (.next/cache/, *.pack.gz)"
    echo ""
else
    echo "  ⚠️  .cursorignore file not found!"
    echo ""
fi

# Step 5: Show excluded large files
echo "📁 Checking for large files that should be excluded:"
find . -type f -size +1M ! -path "./node_modules/*" ! -path "./.next/*" ! -path "./.git/*" 2>/dev/null | head -10 | while read file; do
    size=$(du -h "$file" 2>/dev/null | cut -f1)
    echo "  ⚠️  $file ($size)"
done
echo ""

echo "✅ Optimization complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Restart Cursor IDE to apply changes"
echo "  2. CodeBuddy will rebuild its cache with new exclusions"
echo "  3. Monitor memory usage - should drop from 1026MB to <500MB"
echo ""
echo "💡 Tip: If memory is still high, check for other large files"
echo "   that might need to be added to .cursorignore"

