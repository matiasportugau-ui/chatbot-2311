#!/bin/bash

# BMC Dashboard Development Script
# This script starts the development server for the BMC Dashboard

echo "🚀 Starting BMC Dashboard development server..."

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

# Check if environment file exists
if [ ! -f .env.local ]; then
    echo "⚠️  Environment file .env.local not found. Creating from example..."
    if [ -f env.example ]; then
        cp env.example .env.local
        echo "✅ Environment file created. Please update .env.local with your configuration."
    else
        echo "❌ Environment example file not found. Please create .env.local manually."
        exit 1
    fi
fi

# Start the development server
echo "🚀 Starting development server..."
npm run dev
