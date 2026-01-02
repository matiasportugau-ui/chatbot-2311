#!/bin/bash
# setup_new_computer.sh
# Quick setup script for syncing workspace to a new computer

set -e  # Exit on error

echo "🚀 Setting up chatbot-2311 on new computer..."
echo ""

# Check if we're in the right directory or need to clone
if [ ! -d ".git" ]; then
    echo "📥 Repository not found. Please provide the repository URL:"
    read -p "Git repository URL (or press Enter to skip): " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        echo "Cloning repository..."
        git clone "$REPO_URL" chatbot-2311
        cd chatbot-2311
    else
        echo "💡 Default repository: https://github.com/matiasportugau-ui/chatbot-2311.git"
        echo "⚠️  Skipping Git clone. Make sure you're in the project directory."
    fi
fi

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"

# Check Node.js
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Some features may not work."
    echo "   Install from: https://nodejs.org/"
else
    NODE_VERSION=$(node --version)
    echo "✅ Found: $NODE_VERSION"
fi

# Python setup
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi

# Node.js setup
if command -v npm &> /dev/null; then
    echo ""
    echo "📦 Setting up Node.js dependencies..."
    if [ -f "package.json" ]; then
        npm install
        echo "✅ Node.js dependencies installed"
    else
        echo "⚠️  package.json not found"
    fi
fi

# Environment setup
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
        echo "⚠️  IMPORTANT: Edit .env file with your actual credentials!"
        echo "   Use the .env.backup from your other computer (securely transferred)."
    else
        echo "⚠️  env.example not found. Create .env manually."
    fi
else
    echo "✅ .env file already exists"
fi

# Verify .env is not tracked by git
echo ""
echo "🔍 Verifying Git configuration..."
if git ls-files --error-unmatch .env &> /dev/null; then
    echo "⚠️  WARNING: .env is tracked by Git! This is a security risk."
    echo "   Run: git rm --cached .env"
    echo "   Then add .env to .gitignore"
else
    echo "✅ .env is not tracked by Git (good!)"
fi

# Check if .gitignore has .env
if grep -q "^\.env$" .gitignore 2>/dev/null || grep -q "\.env" .gitignore 2>/dev/null; then
    echo "✅ .env is in .gitignore (good!)"
else
    echo "⚠️  WARNING: .env might not be in .gitignore"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your credentials (from secure backup)"
echo "   2. Activate virtual environment: source venv/bin/activate"
echo "   3. Test Python: python -c \"import openai; print('OK')\""
if command -v npm &> /dev/null; then
    echo "   4. Test Node.js: npm run dev (if available)"
fi
echo "   5. Pull latest changes: git pull origin main"
echo ""
echo "💡 Tip: Always run 'git pull' before starting work and 'git push' when done!"

