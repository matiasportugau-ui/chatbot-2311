#!/bin/bash

# BMC Dashboard Build Script
# This script builds the production version of the BMC Dashboard

echo "🏗️  Building BMC Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Run TypeScript check
echo "🔍 Running TypeScript check..."
npx tsc --noEmit

if [ $? -ne 0 ]; then
    echo "❌ TypeScript errors found. Please fix them before building."
    exit 1
fi

echo "✅ TypeScript check passed"

# Run ESLint check
echo "🔍 Running ESLint check..."
npx eslint . --ext .ts,.tsx --max-warnings 0

if [ $? -ne 0 ]; then
    echo "❌ ESLint errors found. Please fix them before building."
    exit 1
fi

echo "✅ ESLint check passed"

# Build the application
echo "🏗️  Building application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build completed successfully!"
echo ""
echo "The production build is available in the 'out' directory."
echo "You can now deploy the application to your hosting platform."
