#!/bin/bash
# Setup script for GitHub Codespaces
# Installs dependencies and configures the development environment

set -e

echo "🚀 Setting up BMC Chatbot development environment in Codespaces..."
echo "================================================================"

# Log file
LOG_FILE=".devcontainer/setup.log"
mkdir -p .devcontainer
exec > >(tee -a "$LOG_FILE") 2>&1

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Create Python virtual environment
echo -e "${BLUE}📦 Step 1: Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Step 2: Install Python dependencies
echo -e "${BLUE}📦 Step 2: Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Step 3: Install Node.js dependencies
echo -e "${BLUE}📦 Step 3: Installing Node.js dependencies...${NC}"
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  package.json not found${NC}"
fi

# Step 4: Load secrets from GitHub Codespaces
echo -e "${BLUE}🔐 Step 4: Loading secrets...${NC}"
if [ -f ".devcontainer/load-secrets.sh" ]; then
    bash .devcontainer/load-secrets.sh
else
    echo -e "${YELLOW}⚠️  load-secrets.sh not found, skipping${NC}"
fi

# Step 5: Create .env file if it doesn't exist
echo -e "${BLUE}⚙️  Step 5: Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${GREEN}✅ Created .env from env.example${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANT: Configure your API keys in .env file${NC}"
        echo -e "${YELLOW}   Or use GitHub Secrets (Settings → Secrets and variables → Codespaces)${NC}"
    else
        echo -e "${YELLOW}⚠️  env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Step 6: Make scripts executable
echo -e "${BLUE}🔧 Step 6: Making scripts executable...${NC}"
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true
chmod +x .devcontainer/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts are executable${NC}"

# Step 7: Verify Docker Compose
echo -e "${BLUE}🐳 Step 7: Verifying Docker Compose...${NC}"
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose is available${NC}"
else
    echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
fi

# Step 8: Verify Git
echo -e "${BLUE}📝 Step 8: Verifying Git configuration...${NC}"
if command -v git &> /dev/null; then
    git config --global --add safe.directory /workspaces/*
    echo -e "${GREEN}✅ Git configured${NC}"
else
    echo -e "${YELLOW}⚠️  Git not found${NC}"
fi

echo ""
echo -e "${GREEN}================================================================"
echo -e "✅ Setup complete!${NC}"
echo -e "${GREEN}================================================================"
echo ""
echo "📝 Next steps:"
echo "   1. Configure .env file with your API keys"
echo "   2. Or add secrets in: Settings → Secrets and variables → Codespaces"
echo "   3. Run: docker-compose up -d (to start services)"
echo "   4. Run: npm run dev (to start Next.js)"
echo "   5. Run: python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 (to start API)"
echo ""
echo "💡 Or use the automated launcher:"
echo "   bash scripts/codespaces-start.sh"
echo ""

