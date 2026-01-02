#!/bin/bash
# Port management script for Codespaces
# Lists forwarded ports and generates shareable URLs

echo "🌐 BMC Chatbot - Port Management"
echo "================================="

# Check if we're in Codespaces
if [ -z "${CODESPACE_NAME:-}" ]; then
    echo "⚠️  This script is designed for GitHub Codespaces"
    echo "   CODESPACE_NAME is not set"
    echo ""
fi

echo "📋 Forwarded Ports:"
echo ""

# List ports and their status
PORTS=(
    "3000:Next.js Dashboard"
    "8000:FastAPI Server"
    "5678:n8n Workflows"
    "27017:MongoDB"
    "6333:Qdrant REST API"
    "6334:Qdrant gRPC"
)

for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port name <<< "$port_info"
    
    if nc -z localhost $port 2>/dev/null; then
        echo "   ✅ Port $port ($name) - Active"
        
        # Generate public URL if in Codespaces
        if [ -n "${CODESPACE_NAME:-}" ]; then
            echo "      Public URL: https://${CODESPACE_NAME}-${port}.preview.app.github.dev"
        fi
    else
        echo "   ⚠️  Port $port ($name) - Not active"
    fi
done

echo ""
echo "💡 To change port visibility:"
echo "   1. Open 'Ports' tab in VS Code"
echo "   2. Right-click on port"
echo "   3. Select 'Change Port Visibility'"
echo "   4. Choose 'Public' or 'Private'"
echo ""

