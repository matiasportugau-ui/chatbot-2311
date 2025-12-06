#!/bin/bash
# Complete setup and run script for BMC Chatbot
# Usage: ./run_chatbot_complete.sh

set -e

echo "========================================================================"
echo "  BMC Chatbot - Install, Configure & Run"
echo "========================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${YELLOW}Step 1: Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found, installing core packages...${NC}"
    python3 -m pip install openai python-dotenv pymongo fastapi uvicorn requests --quiet
    echo -e "${GREEN}✅ Core packages installed${NC}"
fi
echo ""

# Step 3: Verify configuration
echo -e "${YELLOW}Step 3: Verifying configuration...${NC}"
if [ -f ".env.local" ] || [ -f ".env" ]; then
    echo -e "${GREEN}✅ Configuration file found${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found (will use system environment variables)${NC}"
fi
echo ""

# Step 4: Check services
echo -e "${YELLOW}Step 4: Checking services...${NC}"
if command -v docker &> /dev/null; then
    if docker ps --format '{{.Names}}' | grep -qi mongo; then
        echo -e "${GREEN}✅ MongoDB detected${NC}"
    else
        echo -e "${YELLOW}⚠️  MongoDB not running (optional)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not available (optional)${NC}"
fi
echo ""

# Step 5: Run chatbot
echo "========================================================================"
echo -e "${GREEN}✅ Setup complete! Starting chatbot...${NC}"
echo "========================================================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run chatbot (prefer AI version)
if [ -f "chat_interactivo_ai.py" ]; then
    echo -e "${GREEN}🚀 Iniciando chatbot con IA completa...${NC}"
    python3 chat_interactivo_ai.py
elif [ -f "chat_interactivo.py" ]; then
    echo -e "${GREEN}🚀 Iniciando chatbot (con IA mejorada)...${NC}"
    python3 chat_interactivo.py
elif [ -f "unified_launcher.py" ]; then
    echo -e "${GREEN}🚀 Iniciando unified launcher...${NC}"
    python3 unified_launcher.py
else
    echo -e "${RED}❌ Chatbot script not found${NC}"
    exit 1
fi

