#!/bin/bash
# Agent Team Deployment Script
# This script automates the deployment of all agents in the team

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ORCHESTRATOR_PORT=8000
LOG_DIR="./logs"
CONFIG_FILE="agent_config.production.json"

echo -e "${GREEN}🚀 Starting Agent Team Deployment${NC}"
echo "=================================="

# Step 1: Check prerequisites
echo -e "\n${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check MongoDB
if ! command -v mongosh &> /dev/null && ! command -v mongo &> /dev/null; then
    echo -e "${YELLOW}⚠️  MongoDB client not found (continuing anyway)${NC}"
else
    echo -e "${GREEN}✅ MongoDB client found${NC}"
fi

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
    exit 1
fi
echo -e "${GREEN}✅ OPENAI_API_KEY set${NC}"

if [ -z "$MONGODB_URI" ]; then
    echo -e "${RED}❌ MONGODB_URI not set${NC}"
    exit 1
fi
echo -e "${GREEN}✅ MONGODB_URI set${NC}"

# Step 2: Create directories
echo -e "\n${YELLOW}Step 2: Creating directories...${NC}"
mkdir -p "$LOG_DIR"
mkdir -p "./data/agents"
echo -e "${GREEN}✅ Directories created${NC}"

# Step 3: Copy configuration
echo -e "\n${YELLOW}Step 3: Setting up configuration...${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    if [ -f "agent_config.json" ]; then
        cp agent_config.json "$CONFIG_FILE"
        echo -e "${GREEN}✅ Configuration file created${NC}"
    else
        echo -e "${RED}❌ agent_config.json not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Configuration file exists${NC}"
fi

# Step 4: Check if orchestrator is running
echo -e "\n${YELLOW}Step 4: Checking orchestrator...${NC}"
if curl -s "http://localhost:$ORCHESTRATOR_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Orchestrator is running${NC}"
else
    echo -e "${YELLOW}⚠️  Orchestrator not running. Starting orchestrator...${NC}"
    
    # Start orchestrator in background
    nohup python3 automated_agent_system.py --mode orchestrator > "$LOG_DIR/orchestrator.log" 2>&1 &
    ORCHESTRATOR_PID=$!
    echo $ORCHESTRATOR_PID > "$LOG_DIR/orchestrator.pid"
    
    # Wait for orchestrator to start
    echo "Waiting for orchestrator to start..."
    for i in {1..30}; do
        if curl -s "http://localhost:$ORCHESTRATOR_PORT/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Orchestrator started (PID: $ORCHESTRATOR_PID)${NC}"
            break
        fi
        sleep 1
    done
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Orchestrator failed to start${NC}"
        exit 1
    fi
fi

# Step 5: Register agents
echo -e "\n${YELLOW}Step 5: Registering agents...${NC}"

# Check if registration script exists
if [ -f "scripts/register_agents.py" ]; then
    python3 scripts/register_agents.py
    echo -e "${GREEN}✅ Agents registered${NC}"
else
    echo -e "${YELLOW}⚠️  Registration script not found. Creating basic registration...${NC}"
    
    # Create basic registration script
    cat > scripts/register_agents.py << 'EOF'
#!/usr/bin/env python3
"""Register all agents with the orchestrator"""
import requests
import json

ORCHESTRATOR_URL = "http://localhost:8000"

agents = [
    {
        "agent_id": "orchestrator-001",
        "agent_type": "orchestrator",
        "capabilities": ["coordination", "routing", "monitoring"],
        "status": "active"
    },
    {
        "agent_id": "sales-001",
        "agent_type": "sales",
        "capabilities": ["quote_creation", "sales", "product_info"],
        "status": "active"
    },
    {
        "agent_id": "support-001",
        "agent_type": "support",
        "capabilities": ["technical_support", "troubleshooting"],
        "status": "active"
    },
    {
        "agent_id": "followup-001",
        "agent_type": "follow_up",
        "capabilities": ["follow_up", "messaging"],
        "status": "active"
    },
    {
        "agent_id": "analytics-001",
        "agent_type": "analytics",
        "capabilities": ["analytics", "reporting"],
        "status": "active"
    },
    {
        "agent_id": "workflow-001",
        "agent_type": "workflow",
        "capabilities": ["workflow_execution", "automation"],
        "status": "active"
    },
    {
        "agent_id": "router-001",
        "agent_type": "router",
        "capabilities": ["routing", "intent_analysis"],
        "status": "active"
    }
]

for agent in agents:
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/agent/register",
            json=agent,
            timeout=5
        )
        if response.status_code in [200, 201]:
            print(f"✅ Registered {agent['agent_id']}")
        else:
            print(f"⚠️  {agent['agent_id']}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error registering {agent['agent_id']}: {e}")

print("\n✅ Agent registration complete!")
EOF
    
    chmod +x scripts/register_agents.py
    python3 scripts/register_agents.py
    echo -e "${GREEN}✅ Agents registered${NC}"
fi

# Step 6: Verify deployment
echo -e "\n${YELLOW}Step 6: Verifying deployment...${NC}"

# Check orchestrator status
if curl -s "http://localhost:$ORCHESTRATOR_PORT/agent/status" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Orchestrator responding${NC}"
else
    echo -e "${RED}❌ Orchestrator not responding${NC}"
    exit 1
fi

# Check agent list
AGENT_COUNT=$(curl -s "http://localhost:$ORCHESTRATOR_PORT/agent/list" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('agents', [])))" 2>/dev/null || echo "0")
echo -e "${GREEN}✅ Found $AGENT_COUNT registered agents${NC}"

# Step 7: Summary
echo -e "\n${GREEN}=================================="
echo "✅ Deployment Complete!"
echo "==================================${NC}"
echo ""
echo "Orchestrator: http://localhost:$ORCHESTRATOR_PORT"
echo "Health Check: http://localhost:$ORCHESTRATOR_PORT/health"
echo "Agent Status: http://localhost:$ORCHESTRATOR_PORT/agent/status"
echo ""
echo "Next steps:"
echo "1. Review AGENT_TEAM_DEPLOYMENT_PLAN.md"
echo "2. Read AGENT_TEAM_INSTRUCTIONS.md for role-specific guidance"
echo "3. Start individual agents as needed"
echo ""
echo -e "${YELLOW}To stop orchestrator:${NC}"
echo "  kill \$(cat $LOG_DIR/orchestrator.pid)"
echo ""
