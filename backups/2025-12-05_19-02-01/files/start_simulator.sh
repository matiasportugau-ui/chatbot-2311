#!/bin/bash
# Quick start script for simulator mode

set -e

echo "🚀 Starting BMC Chatbot Simulator"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if API server is running
API_URL="${PY_CHAT_SERVICE_URL:-http://localhost:8000}"
if curl -s "${API_URL}/health" > /dev/null 2>&1; then
    echo "✅ API server is running at ${API_URL}"
else
    echo "⚠️  API server is not running"
    echo "   Starting API server in background..."
    python3 api_server.py > logs/api_server.log 2>&1 &
    API_PID=$!
    echo "   API server started (PID: $API_PID)"
    echo "   Waiting for server to be ready..."
    sleep 3
    
    # Check again
    if curl -s "${API_URL}/health" > /dev/null 2>&1; then
        echo "✅ API server is ready"
    else
        echo "❌ API server failed to start"
        echo "   Check logs/api_server.log for details"
        exit 1
    fi
fi

echo ""
echo "Choose an option:"
echo "1) Interactive CLI (Enhanced)"
echo "2) Simple Simulator"
echo "3) Populate Knowledge Base"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Enhanced CLI..."
        python3 simulate_chat_cli.py
        ;;
    2)
        echo ""
        echo "Starting Simple Simulator..."
        python3 simulate_chat.py
        ;;
    3)
        echo ""
        echo "Populating Knowledge Base..."
        python3 populate_kb.py
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

