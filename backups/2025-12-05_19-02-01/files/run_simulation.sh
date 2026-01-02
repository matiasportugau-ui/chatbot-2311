#!/bin/bash
# One-Command Simulation Runner
# Automatically sets up and runs the chatbot simulator

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 BMC Chatbot Simulator - One-Command Setup${NC}"
echo "=============================================="
echo ""

# Step 1: Check Python
echo -e "${YELLOW}📋 Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "   Please install Python 3.8+ first"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Step 2: Check/create .env file
echo -e "${YELLOW}📋 Step 2: Checking environment configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo -e "${YELLOW}⚠️  .env file not found, creating from template...${NC}"
        cp env.example .env
        echo -e "${GREEN}✅ .env file created (using defaults)${NC}"
        echo -e "${YELLOW}   Note: Edit .env if you need custom configuration${NC}"
    else
        echo -e "${YELLOW}⚠️  No .env file, using defaults${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Step 3: Install dependencies
echo -e "${YELLOW}📋 Step 3: Checking Python dependencies...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt not found, skipping dependency check${NC}"
else
    # Check if key packages are installed
    MISSING_DEPS=()
    for dep in fastapi uvicorn pymongo requests; do
        if ! python3 -c "import ${dep}" 2>/dev/null; then
            MISSING_DEPS+=("${dep}")
        fi
    done
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
        echo -e "${YELLOW}   Installing from requirements.txt...${NC}"
        pip3 install -q -r requirements.txt || {
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            echo "   Try: pip3 install -r requirements.txt"
            exit 1
        }
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ All required dependencies installed${NC}"
    fi
fi

# Step 4: Check MongoDB
echo -e "${YELLOW}📋 Step 4: Checking MongoDB...${NC}"
MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017/bmc_chat}"
MONGODB_HOST=$(echo $MONGODB_URI | sed -n 's|mongodb://\([^/]*\)/.*|\1|p' | cut -d: -f1)
MONGODB_PORT=$(echo $MONGODB_URI | sed -n 's|mongodb://[^:]*:\([0-9]*\)/.*|\1|p' || echo "27017")

# Check if MongoDB is accessible
if python3 -c "from pymongo import MongoClient; MongoClient('$MONGODB_URI', serverSelectionTimeoutMS=2000).admin.command('ping')" 2>/dev/null; then
    echo -e "${GREEN}✅ MongoDB is accessible${NC}"
    MONGODB_RUNNING=true
else
    echo -e "${YELLOW}⚠️  MongoDB not accessible at ${MONGODB_URI}${NC}"
    
    # Try to start MongoDB with Docker
    if command -v docker &> /dev/null; then
        # Check if Docker daemon is running
        if docker info > /dev/null 2>&1; then
            echo -e "${YELLOW}   Attempting to start MongoDB with Docker...${NC}"
            if docker ps -a 2>/dev/null | grep -q bmc-mongodb; then
                echo -e "${YELLOW}   Starting existing container...${NC}"
                docker start bmc-mongodb > /dev/null 2>&1
                sleep 2
            else
                echo -e "${YELLOW}   Creating new MongoDB container...${NC}"
                docker run -d -p 27017:27017 --name bmc-mongodb mongo:7.0 > /dev/null 2>&1
                sleep 3
            fi
            
            # Check again
            if python3 -c "from pymongo import MongoClient; MongoClient('$MONGODB_URI', serverSelectionTimeoutMS=2000).admin.command('ping')" 2>/dev/null; then
                echo -e "${GREEN}✅ MongoDB started successfully${NC}"
                MONGODB_RUNNING=true
            else
                echo -e "${YELLOW}⚠️  MongoDB not available, continuing without persistence${NC}"
                MONGODB_RUNNING=false
            fi
        else
            echo -e "${YELLOW}⚠️  Docker daemon is not running${NC}"
            echo -e "${YELLOW}   To start MongoDB: start Docker Desktop or run 'docker start bmc-mongodb'${NC}"
            echo -e "${YELLOW}   Continuing without MongoDB (no conversation persistence)${NC}"
            MONGODB_RUNNING=false
        fi
    else
        echo -e "${YELLOW}⚠️  Docker not found, continuing without MongoDB${NC}"
        echo -e "${YELLOW}   System will work but won't save conversations${NC}"
        MONGODB_RUNNING=false
    fi
fi

# Step 5: Create logs directory
echo -e "${YELLOW}📋 Step 5: Setting up logs...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ Logs directory ready${NC}"

# Step 6: Check if API server is running
echo -e "${YELLOW}📋 Step 6: Checking API server...${NC}"
API_URL="${PY_CHAT_SERVICE_URL:-http://localhost:8000}"

if curl -s "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is already running at ${API_URL}${NC}"
    API_PID=""
else
    echo -e "${YELLOW}⚠️  API server not running, starting it...${NC}"
    
    # Check if port is in use
    if lsof -ti :8000 > /dev/null 2>&1; then
        echo -e "${YELLOW}   Port 8000 is in use, attempting to free it...${NC}"
        kill -9 $(lsof -ti :8000) 2>/dev/null || true
        sleep 1
    fi
    
    # Start API server in background
    python3 api_server.py > logs/api_server.log 2>&1 &
    API_PID=$!
    echo -e "${GREEN}✅ API server started (PID: $API_PID)${NC}"
    
    # Wait for server to be ready
    echo -e "${YELLOW}   Waiting for server to be ready...${NC}"
    MAX_WAIT=30
    WAIT_COUNT=0
    while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
        if curl -s "${API_URL}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API server is ready!${NC}"
            break
        fi
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        echo -n "."
    done
    echo ""
    
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ API server failed to start${NC}"
        echo "   Check logs/api_server.log for details"
        if [ ! -z "$API_PID" ]; then
            kill $API_PID 2>/dev/null || true
        fi
        exit 1
    fi
fi

# Step 7: Verify setup
echo -e "${YELLOW}📋 Step 7: Verifying setup...${NC}"
if python3 -c "import api_server" 2>/dev/null; then
    echo -e "${GREEN}✅ API server module can be imported${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not import api_server module${NC}"
fi

# Step 8: Launch simulator
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Starting Interactive CLI Simulator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   - Type messages to chat with the bot"
echo "   - Use /help to see all commands"
echo "   - Use /exit to quit"
echo ""
echo -e "${YELLOW}📊 Status:${NC}"
echo "   API Server: ${API_URL}"
echo "   MongoDB: $([ "$MONGODB_RUNNING" = true ] && echo -e "${GREEN}Connected${NC}" || echo -e "${YELLOW}Not available (no persistence)${NC}")"
if [ ! -z "$API_PID" ]; then
    echo "   API PID: $API_PID (will stop when you exit)"
fi
echo ""

# Cleanup function
cleanup() {
    if [ ! -z "$API_PID" ]; then
        echo ""
        echo -e "${YELLOW}🛑 Stopping API server (PID: $API_PID)...${NC}"
        kill $API_PID 2>/dev/null || true
        echo -e "${GREEN}✅ API server stopped${NC}"
    fi
    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Launch CLI simulator
python3 simulate_chat_cli.py
