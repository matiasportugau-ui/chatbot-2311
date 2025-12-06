#!/bin/bash
# Setup script for Cursor Multi-Agent Integration
# Supports OpenAI, Groq, Gemini, and Grok (xAI)

echo "🚀 Setting up Cursor Multi-Agent Integration"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from env.example..."
    cp env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GROQ_API_KEY (optional - free tier available)"
    echo "   - GEMINI_API_KEY"
    echo "   - GROK_API_KEY"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -q openai groq google-generativeai python-dotenv

echo ""
echo "✅ Dependencies installed"
echo ""

# Check for API keys
echo "🔑 Checking API keys in .env..."
source .env 2>/dev/null || true

if [ -z "$GROK_API_KEY" ]; then
    echo "⚠️  GROK_API_KEY not set in .env"
    echo "   Add: GROK_API_KEY=xai-your-key-here"
else
    echo "✅ GROK_API_KEY found"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set in .env"
else
    echo "✅ OPENAI_API_KEY found"
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set in .env"
else
    echo "✅ GEMINI_API_KEY found"
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set in .env (optional)"
else
    echo "✅ GROQ_API_KEY found"
fi

echo ""
echo "📋 Model Strategy: ${MODEL_STRATEGY:-balanced}"
echo ""
echo "✨ Setup complete!"
echo ""
echo "To test the integration, run:"
echo "   python3 test_grok_integration.py"
echo ""

