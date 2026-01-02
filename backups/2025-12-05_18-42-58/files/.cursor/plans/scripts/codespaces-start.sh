#!/bin/bash
# One-command service startup for Codespaces
# Starts all services and displays public URLs

set -e

echo "🚀 Starting BMC Chatbot Services"
echo "================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Docker services
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Starting Docker services..."
    docker compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    docker compose ps
fi

# Start Next.js in background (if not already running)
if ! nc -z localhost 3000 2>/dev/null; then
    echo "📦 Starting Next.js..."
    if [ -f "package.json" ]; then
        npm run dev > /tmp/nextjs.log 2>&1 &
        echo "✅ Next.js starting (check /tmp/nextjs.log for output)"
    fi
else
    echo "✅ Next.js already running on port 3000"
fi

# Start FastAPI in background (if not already running)
if ! nc -z localhost 8000 2>/dev/null; then
    echo "🐍 Starting FastAPI..."
    if [ -f "api_server.py" ]; then
        source venv/bin/activate
        python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload > /tmp/fastapi.log 2>&1 &
        echo "✅ FastAPI starting (check /tmp/fastapi.log for output)"
    fi
else
    echo "✅ FastAPI already running on port 8000"
fi

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Check the 'Ports' tab in VS Code for public URLs:"
echo ""
echo "   📊 Next.js: http://localhost:3000"
echo "   🔌 FastAPI: http://localhost:8000"
echo "   🔄 n8n: http://localhost:5678"
echo ""
echo "💡 To view logs:"
echo "   tail -f /tmp/nextjs.log"
echo "   tail -f /tmp/fastapi.log"
echo "   docker compose logs -f"
echo ""

