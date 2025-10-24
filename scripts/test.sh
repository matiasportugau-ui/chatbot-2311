#!/bin/bash

# BMC Dashboard Test Script
# This script runs tests for the BMC Dashboard

echo "🧪 Running BMC Dashboard tests..."

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
    echo "❌ TypeScript errors found. Please fix them before running tests."
    exit 1
fi

echo "✅ TypeScript check passed"

# Run ESLint check
echo "🔍 Running ESLint check..."
npx eslint . --ext .ts,.tsx --max-warnings 0

if [ $? -ne 0 ]; then
    echo "❌ ESLint errors found. Please fix them before running tests."
    exit 1
fi

echo "✅ ESLint check passed"

# Run Next.js build check
echo "🔍 Running Next.js build check..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build check failed"
    exit 1
fi

echo "✅ Build check passed"

# Run linting
echo "🔍 Running linting..."
npm run lint

if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi

echo "✅ Linting passed"

echo ""
echo "🎉 All tests passed successfully!"
echo ""
echo "The application is ready for development and production deployment."
