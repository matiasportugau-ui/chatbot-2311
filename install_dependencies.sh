#!/bin/bash
# Quick install script for dependencies

echo "📦 Installing dependencies..."
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install Python with pip."
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "Using: $PIP_CMD"
echo ""

# Install from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    $PIP_CMD install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing core packages..."
    $PIP_CMD install fastapi uvicorn[standard] pydantic requests pymongo openai python-dotenv
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Run: python verify_setup.py to verify"

