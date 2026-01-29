#!/bin/bash
# Gravity Agent - Quick Start Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🌌 Gravity Agent - Development Automation Orchestrator"
echo "========================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check orchestrator
if [ ! -f "scripts/orchestrator/main_orchestrator.py" ]; then
    echo "⚠️  Warning: Orchestrator not found at scripts/orchestrator/main_orchestrator.py"
fi

# Run gravity agent with provided arguments
python3 "$SCRIPT_DIR/gravity_agent.py" "$@"
