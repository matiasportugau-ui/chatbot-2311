#!/bin/bash

# BMC Dashboard Setup Script
# This script sets up the development environment for the BMC Dashboard

echo "🚀 Setting up BMC Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create environment file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating environment file..."
    cp env.example .env.local
    echo "✅ Environment file created. Please update .env.local with your configuration."
else
    echo "✅ Environment file already exists"
fi

# Check if TypeScript is working
echo "🔍 Checking TypeScript configuration..."
npx tsc --noEmit

if [ $? -ne 0 ]; then
    echo "⚠️  TypeScript errors found. Please fix them before running the application."
else
    echo "✅ TypeScript configuration is valid"
fi

# Check if ESLint is working
echo "🔍 Checking ESLint configuration..."
npx eslint . --ext .ts,.tsx --max-warnings 0

if [ $? -ne 0 ]; then
    echo "⚠️  ESLint errors found. Please fix them before running the application."
else
    echo "✅ ESLint configuration is valid"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env.local with your configuration"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "For more information, see the README.md file."
