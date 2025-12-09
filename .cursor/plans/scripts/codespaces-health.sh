#!/bin/bash
# Health check script for Codespaces services

set -e

echo "🏥 BMC Chatbot - Service Health Check"
echo "======================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local port=$3
    
    echo -n "Checking $name... "
    
    if curl -s -f "$url" > /dev/null 2>&1 || nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Check services
echo ""
echo "🔍 Service Status:"
echo ""

# Docker services
if command -v docker &> /dev/null; then
    echo "🐳 Docker Services:"
    docker compose ps 2>/dev/null || echo "   Docker Compose not running"
    echo ""
fi

# Next.js
check_service "Next.js" "http://localhost:3000" 3000

# FastAPI
check_service "FastAPI" "http://localhost:8000/health" 8000

# MongoDB
check_service "MongoDB" "mongodb://localhost:27017" 27017

# Qdrant
check_service "Qdrant" "http://localhost:6333" 6333

# n8n
check_service "n8n" "http://localhost:5678" 5678

echo ""
echo "📊 Port Status:"
netstat -tuln 2>/dev/null | grep -E ":(3000|8000|5678|27017|6333)" || ss -tuln 2>/dev/null | grep -E ":(3000|8000|5678|27017|6333)" || echo "   (Port check not available)"

echo ""
echo "✅ Health check complete!"
echo ""

