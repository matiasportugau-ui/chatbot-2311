#!/bin/bash
# Install Auto-Start for Orchestrator
# This script sets up automatic execution of orchestrator in all sessions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ORCHESTRATOR_DIR="$SCRIPT_DIR"

echo "🚀 Installing Auto-Start for Orchestrator"
echo "=========================================="
echo ""

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    echo "⚠️  Unknown shell, using .bashrc"
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
fi

echo "📋 Detected shell: $SHELL_NAME"
echo "📝 Shell RC file: $SHELL_RC"
echo ""

# Create auto-start entry
AUTO_START_ENTRY="# Auto-Start Orchestrator (BMC Consolidation Plan)
# Added by install_auto_start.sh
if [ -f \"$ORCHESTRATOR_DIR/auto_start.py\" ]; then
    cd \"$REPO_ROOT\"
    python3 \"$ORCHESTRATOR_DIR/auto_start.py\" > /dev/null 2>&1 &
fi"

# Check if already installed
if grep -q "Auto-Start Orchestrator" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  Auto-start already installed in $SHELL_RC"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 0
    fi
    # Remove old entry
    sed -i.bak '/# Auto-Start Orchestrator/,/^fi$/d' "$SHELL_RC"
    echo "✅ Removed old auto-start entry"
fi

# Add auto-start entry
echo "$AUTO_START_ENTRY" >> "$SHELL_RC"
echo "✅ Added auto-start entry to $SHELL_RC"

# Make scripts executable
chmod +x "$ORCHESTRATOR_DIR/auto_start.py"
chmod +x "$ORCHESTRATOR_DIR/run_automated_execution.py"
echo "✅ Made scripts executable"

# Create config file if it doesn't exist
CONFIG_FILE="$ORCHESTRATOR_DIR/config/auto_start_config.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOF
{
  "enabled": true,
  "mode": "automated",
  "resume": true,
  "check_interval": 300,
  "auto_restart": true,
  "log_file": "consolidation/logs/auto_start.log"
}
EOF
    echo "✅ Created configuration file: $CONFIG_FILE"
fi

# Create log directory
mkdir -p "$REPO_ROOT/consolidation/logs"
echo "✅ Created log directory"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart your terminal or run: source $SHELL_RC"
echo "   2. Orchestrator will start automatically in new sessions"
echo "   3. Check logs at: consolidation/logs/auto_start.log"
echo ""
echo "⚙️  Configuration: $CONFIG_FILE"
echo "   - Set 'enabled: false' to disable auto-start"
echo "   - Set 'mode' to 'manual' or 'dry-run' to change execution mode"
echo ""

