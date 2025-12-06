#!/bin/bash
# Start all services in Codespaces
# This script is called automatically when Codespace starts

set -e

echo "🚀 Starting BMC Chatbot services in Codespaces..."
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to check if a service is running
check_service() {
    local port=$1
    local name=$2
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅ $name is running on port $port${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name is not running on port $port${NC}"
        return 1
    fi
}

# Step 1: Start Docker Compose services
echo -e "${BLUE}🐳 Step 1: Starting Docker Compose services...${NC}"
if [ -f "docker-compose.yml" ]; then
    # Check if services are already running
    if docker compose ps | grep -q "Up"; then
        echo -e "${YELLOW}⚠️  Some services are already running${NC}"
        docker compose ps
    else
        echo "Starting services..."
        docker compose up -d
        
        echo "⏳ Waiting for services to be ready..."
        sleep 10
        
        # Check service status
        docker compose ps
        echo -e "${GREEN}✅ Docker services started${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  docker-compose.yml not found${NC}"
fi

# Step 2: Wait for MongoDB
echo -e "${BLUE}🍃 Step 2: Checking MongoDB...${NC}"
for i in {1..30}; do
    if check_service 27017 "MongoDB"; then
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ MongoDB failed to start${NC}"
    else
        echo "   Waiting for MongoDB... ($i/30)"
        sleep 2
    fi
done

# Step 3: Wait for Qdrant
echo -e "${BLUE}🔍 Step 3: Checking Qdrant...${NC}"
for i in {1..30}; do
    if check_service 6333 "Qdrant"; then
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Qdrant failed to start${NC}"
    else
        echo "   Waiting for Qdrant... ($i/30)"
        sleep 2
    fi
done

# Step 4: Check n8n
echo -e "${BLUE}🔄 Step 4: Checking n8n...${NC}"
check_service 5678 "n8n" || echo -e "${YELLOW}⚠️  n8n may still be starting...${NC}"

echo ""
echo -e "${GREEN}=================================================="
echo -e "✅ Services started!${NC}"
echo -e "${GREEN}=================================================="
echo ""
echo "🌐 Your services are available at:"
echo ""
echo "   📊 Next.js Dashboard:"
echo "      http://localhost:3000"
echo ""
echo "   🔌 FastAPI Server:"
echo "      http://localhost:8000"
echo "      Health: http://localhost:8000/health"
echo ""
echo "   🔄 n8n Workflows:"
echo "      http://localhost:5678"
echo ""
echo "💡 Ports are automatically forwarded in Codespaces!"
echo "   Check the 'Ports' tab for public URLs you can share."
echo ""
echo "📝 To start Next.js and FastAPI manually:"
echo "   Terminal 1: npm run dev"
echo "   Terminal 2: source venv/bin/activate && python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload"
echo ""

