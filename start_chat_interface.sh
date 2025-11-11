#!/bin/bash
# Automatic Chat Interface Startup Script
# Starts API server, HTTP server, and opens browser to chat interface

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_URL="${PY_CHAT_SERVICE_URL:-http://localhost:8000}"
API_PORT="${API_PORT:-8000}"
HTTP_PORT="${HTTP_PORT:-8080}"
CHAT_HTML="chat-interface.html"
API_SERVER="api_server.py"

# PIDs for cleanup
API_PID=""
HTTP_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    
    if [ ! -z "$HTTP_PID" ]; then
        echo -e "${YELLOW}   Stopping HTTP server (PID: $HTTP_PID)...${NC}"
        kill $HTTP_PID 2>/dev/null || true
        wait $HTTP_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$API_PID" ]; then
        echo -e "${YELLOW}   Stopping API server (PID: $API_PID)...${NC}"
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

# Print header
echo -e "${BLUE}🚀 Starting BMC Chat Interface${NC}"
echo "=================================="
echo ""

# Step 1: Check Python
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "   Please install Python 3.8+ first"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"

# Step 2: Check required files
if [ ! -f "$API_SERVER" ]; then
    echo -e "${RED}❌ API server file not found: $API_SERVER${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API server file found${NC}"

if [ ! -f "$CHAT_HTML" ]; then
    echo -e "${RED}❌ Chat interface HTML not found: $CHAT_HTML${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Chat interface HTML found${NC}"

# Step 3: Check Python dependencies
echo -e "${YELLOW}📋 Checking Python dependencies...${NC}"
MISSING_DEPS=()
for dep in fastapi uvicorn; do
    if ! python3 -c "import ${dep}" 2>/dev/null; then
        MISSING_DEPS+=("${dep}")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${YELLOW}   Installing from requirements.txt...${NC}"
    if [ -f "requirements.txt" ]; then
        pip3 install -q -r requirements.txt || {
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            echo "   Try: pip3 install -r requirements.txt"
            exit 1
        }
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found, installing minimal dependencies...${NC}"
        pip3 install -q fastapi uvicorn || {
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            exit 1
        }
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
else
    echo -e "${GREEN}✅ All required dependencies installed${NC}"
fi

# Step 4: Check/Start API server
echo ""
echo -e "${YELLOW}📋 Checking API server...${NC}"
if curl -s "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running at ${API_URL}${NC}"
else
    echo -e "${YELLOW}⚠️  API server is not running${NC}"
    echo -e "${YELLOW}   Starting API server in background...${NC}"
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start API server in background
    python3 "$API_SERVER" > logs/api_server.log 2>&1 &
    API_PID=$!
    echo -e "${GREEN}✅ API server started (PID: $API_PID)${NC}"
    echo -e "${YELLOW}   Waiting for server to be ready...${NC}"
    
    # Wait for server to be ready (max 30 seconds)
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
    
    if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
        echo -e "${RED}❌ API server failed to start within ${MAX_WAIT} seconds${NC}"
        echo "   Check logs/api_server.log for details"
        cleanup
        exit 1
    fi
fi

# Step 5: Start HTTP server
echo ""
echo -e "${YELLOW}📋 Starting HTTP server...${NC}"

# Find available port
FOUND_PORT=""
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    elif command -v netstat &> /dev/null; then
        ! netstat -an 2>/dev/null | grep -q ":$port.*LISTEN"
    elif command -v ss &> /dev/null; then
        ! ss -lnt 2>/dev/null | grep -q ":$port "
    else
        # Fallback: try to bind to the port
        python3 -c "import socket; s=socket.socket(); s.bind(('', $port)); s.close()" 2>/dev/null
    fi
}

for port in $(seq $HTTP_PORT $((HTTP_PORT + 10))); do
    if check_port $port; then
        FOUND_PORT=$port
        break
    fi
done

if [ -z "$FOUND_PORT" ]; then
    echo -e "${RED}❌ Could not find available port (tried ${HTTP_PORT}-$((HTTP_PORT + 10)))${NC}"
    cleanup
    exit 1
fi

# Start HTTP server in background
python3 -m http.server $FOUND_PORT > logs/http_server.log 2>&1 &
HTTP_PID=$!
sleep 1

# Verify HTTP server started
if ! kill -0 $HTTP_PID 2>/dev/null; then
    echo -e "${RED}❌ HTTP server failed to start${NC}"
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ HTTP server started on port $FOUND_PORT${NC}"
CHAT_URL="http://localhost:${FOUND_PORT}/${CHAT_HTML}"

# Step 6: Open browser
echo ""
echo -e "${YELLOW}🌐 Opening browser...${NC}"

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$CHAT_URL" 2>/dev/null && echo -e "${GREEN}✅ Browser opened${NC}" || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "$CHAT_URL" 2>/dev/null && echo -e "${GREEN}✅ Browser opened${NC}" || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
    elif command -v firefox &> /dev/null; then
        firefox "$CHAT_URL" 2>/dev/null && echo -e "${GREEN}✅ Browser opened${NC}" || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
    elif command -v google-chrome &> /dev/null; then
        google-chrome "$CHAT_URL" 2>/dev/null && echo -e "${GREEN}✅ Browser opened${NC}" || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not find browser command${NC}"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start "$CHAT_URL" 2>/dev/null && echo -e "${GREEN}✅ Browser opened${NC}" || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"
else
    echo -e "${YELLOW}⚠️  Unknown OS, cannot open browser automatically${NC}"
fi

# Display information
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Chat interface is ready!${NC}"
echo ""
echo -e "${CYAN}📱 Chat Interface:${NC} ${CHAT_URL}"
echo -e "${CYAN}🔌 API Server:${NC} ${API_URL}"
echo ""
if [ ! -z "$API_PID" ]; then
    echo -e "${YELLOW}💡 API server is running in background (PID: $API_PID)${NC}"
fi
echo -e "${YELLOW}💡 HTTP server is running in background (PID: $HTTP_PID)${NC}"
echo ""
echo -e "${YELLOW}💡 To stop: Press Ctrl+C${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Keep script running
echo -e "${BLUE}Press Ctrl+C to stop all servers...${NC}"
# Wait for HTTP server process (or any background job)
if [ ! -z "$HTTP_PID" ]; then
    wait $HTTP_PID 2>/dev/null || true
else
    # If HTTP server wasn't started by us, wait for any background job
    wait 2>/dev/null || true
fi

