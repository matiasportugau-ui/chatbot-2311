#!/bin/bash

# BMC Dashboard Deploy Script
# This script deploys the BMC Dashboard to production

echo "🚀 Deploying BMC Dashboard..."

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
    echo "❌ TypeScript errors found. Please fix them before deploying."
    exit 1
fi

echo "✅ TypeScript check passed"

# Run ESLint check
echo "🔍 Running ESLint check..."
npx eslint . --ext .ts,.tsx --max-warnings 0

if [ $? -ne 0 ]; then
    echo "❌ ESLint errors found. Please fix them before deploying."
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

echo "✅ Build completed successfully"

# Check if deployment target is specified
if [ -z "$DEPLOY_TARGET" ]; then
    echo "⚠️  DEPLOY_TARGET environment variable not set."
    echo "Available deployment targets:"
    echo "  - vercel"
    echo "  - netlify"
    echo "  - aws"
    echo "  - docker"
    echo ""
    echo "Set DEPLOY_TARGET environment variable to specify deployment target."
    echo "Example: DEPLOY_TARGET=vercel ./scripts/deploy.sh"
    exit 1
fi

# Deploy based on target
case $DEPLOY_TARGET in
    "vercel")
        echo "🚀 Deploying to Vercel..."
        if command -v vercel &> /dev/null; then
            vercel --prod
        else
            echo "❌ Vercel CLI not installed. Please install it first: npm i -g vercel"
            exit 1
        fi
        ;;
    "netlify")
        echo "🚀 Deploying to Netlify..."
        if command -v netlify &> /dev/null; then
            netlify deploy --prod
        else
            echo "❌ Netlify CLI not installed. Please install it first: npm i -g netlify-cli"
            exit 1
        fi
        ;;
    "aws")
        echo "🚀 Deploying to AWS..."
        echo "❌ AWS deployment not implemented yet. Please deploy manually."
        exit 1
        ;;
    "docker")
        echo "🚀 Building Docker image..."
        if command -v docker &> /dev/null; then
            docker build -t bmc-dashboard .
            echo "✅ Docker image built successfully"
            echo "Run with: docker run -p 3000:3000 bmc-dashboard"
        else
            echo "❌ Docker not installed. Please install Docker first."
            exit 1
        fi
        ;;
    *)
        echo "❌ Unknown deployment target: $DEPLOY_TARGET"
        echo "Available targets: vercel, netlify, aws, docker"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Your BMC Dashboard is now live and ready to use."
