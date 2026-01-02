#!/bin/bash
# One-command setup for GitHub Codespaces
# Wrapper around .devcontainer/setup.sh with additional validation

set -e

echo "🚀 BMC Chatbot - Codespaces Setup"
echo "=================================="

# Check if we're in Codespaces
if [ -z "${CODESPACE_NAME:-}" ]; then
    echo "⚠️  Warning: This doesn't appear to be a Codespaces environment"
    echo "   CODESPACE_NAME is not set"
    echo "   Continuing anyway..."
    echo ""
fi

# Run the main setup script
if [ -f ".devcontainer/setup.sh" ]; then
    bash .devcontainer/setup.sh
else
    echo "❌ Error: .devcontainer/setup.sh not found"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure secrets in GitHub: Settings → Secrets and variables → Codespaces"
echo "   2. Or edit .env file manually"
echo "   3. Run: bash scripts/codespaces-start.sh"
echo ""

