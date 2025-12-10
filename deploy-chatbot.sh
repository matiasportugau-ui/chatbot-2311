#!/bin/bash

# ============================================================================
# BMC Chatbot - Complete Deployment Script
# ============================================================================
# This script helps you deploy your chatbot to various platforms
#
# Supported platforms:
#   1. Railway.app (Python API + MongoDB)
#   2. Vercel (Next.js Frontend)
#   3. cPanel (Static files)
#   4. Render.com (Alternative to Railway)
#
# Usage:
#   ./deploy-chatbot.sh [option]
#   
#   Options:
#     railway    - Deploy to Railway.app
#     vercel     - Deploy to Vercel
#     cpanel     - Prepare files for cPanel
#     render     - Deploy to Render.com
#     all        - Interactive full deployment
#
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    else
        print_success "$1 is installed"
        return 0
    fi
}

check_file() {
    if [ ! -f "$1" ]; then
        print_error "File not found: $1"
        return 1
    else
        print_success "File found: $1"
        return 0
    fi
}

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

preflight_checks() {
    print_header "Running Pre-flight Checks"
    
    local has_errors=0
    
    # Check Python
    if check_command python3 || check_command python; then
        PYTHON_CMD=$(command -v python3 || command -v python)
        print_info "Python: $($PYTHON_CMD --version)"
    else
        has_errors=1
    fi
    
    # Check Node.js
    if check_command node; then
        print_info "Node.js: $(node --version)"
    else
        print_warning "Node.js not found - required for Next.js deployment"
    fi
    
    # Check npm
    if check_command npm; then
        print_info "npm: $(npm --version)"
    else
        print_warning "npm not found - required for Next.js deployment"
    fi
    
    # Check Git
    if check_command git; then
        print_info "Git: $(git --version)"
    else
        print_warning "Git not found - required for Railway/Vercel deployment"
    fi
    
    # Check required files
    check_file "requirements.txt"
    check_file "sistema_completo_integrado.py"
    check_file "package.json"
    
    echo ""
    
    if [ $has_errors -eq 1 ]; then
        print_error "Pre-flight checks failed. Please install missing dependencies."
        exit 1
    else
        print_success "All pre-flight checks passed!"
    fi
}

# ============================================================================
# RAILWAY DEPLOYMENT
# ============================================================================

deploy_railway() {
    print_header "Deploying to Railway.app"
    
    # Check Railway CLI
    if ! check_command railway; then
        print_warning "Railway CLI not installed. Installing..."
        npm install -g @railway/cli
    fi
    
    # Create railway.json if doesn't exist
    if [ ! -f "railway.json" ]; then
        print_info "Creating railway.json configuration..."
        cat > railway.json <<EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port \$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
        print_success "railway.json created"
    fi
    
    # Create Procfile if doesn't exist
    if [ ! -f "Procfile" ]; then
        print_info "Creating Procfile..."
        echo "web: uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port \$PORT" > Procfile
        print_success "Procfile created"
    fi
    
    # Login to Railway
    print_info "Logging into Railway..."
    railway login
    
    # Initialize project
    print_info "Initializing Railway project..."
    railway init
    
    # Add MongoDB
    print_info "Add MongoDB to your project in Railway dashboard:"
    print_info "  1. Go to https://railway.app/dashboard"
    print_info "  2. Select your project"
    print_info "  3. Click 'New' → 'Database' → 'Add MongoDB'"
    echo ""
    read -p "Press Enter when MongoDB is added..."
    
    # Set environment variables
    print_info "Setting environment variables..."
    echo ""
    read -p "Enter your OpenAI API Key: " OPENAI_KEY
    railway variables set OPENAI_API_KEY="$OPENAI_KEY"
    railway variables set OPENAI_MODEL="gpt-4o-mini"
    railway variables set MONGODB_URI="\${{MongoDB.MONGO_URL}}"
    railway variables set PORT="8000"
    railway variables set HOST="0.0.0.0"
    
    print_success "Environment variables set"
    
    # Deploy
    print_info "Deploying to Railway..."
    railway up
    
    # Get deployment URL
    print_success "Deployment complete!"
    print_info "Your API URL:"
    railway domain
    
    echo ""
    print_success "Railway deployment complete!"
    print_info "Check your deployment at: https://railway.app/dashboard"
}

# ============================================================================
# VERCEL DEPLOYMENT
# ============================================================================

deploy_vercel() {
    print_header "Deploying to Vercel"
    
    # Check Vercel CLI
    if ! check_command vercel; then
        print_warning "Vercel CLI not installed. Installing..."
        npm install -g vercel
    fi
    
    # Navigate to Next.js app
    # cd nextjs-app
    
    # Install dependencies
    print_info "Installing dependencies..."
    npm install
    
    # Check next.config.ts
    print_info "Checking Next.js configuration..."
    if grep -q "output: 'export'" next.config.ts 2>/dev/null; then
        print_warning "Static export is configured - removing for Vercel deployment"
        # Vercel doesn't need static export
    fi
    
    # Get Railway URL
    echo ""
    read -p "Enter your Railway API URL (e.g., https://your-app.railway.app): " RAILWAY_URL
    
    # Deploy
    print_info "Deploying to Vercel..."
    vercel --prod -e NEXT_PUBLIC_API_URL="$RAILWAY_URL"
    
    # cd ..
    
    print_success "Vercel deployment complete!"
    print_info "Your app is now live!"
}

# ============================================================================
# CPANEL DEPLOYMENT
# ============================================================================

deploy_cpanel() {
    print_header "Preparing Files for cPanel"
    
    # Navigate to Next.js app
    # cd nextjs-app
    
    # Update next.config.ts for static export
    print_info "Configuring Next.js for static export..."
    
    cat > next.config.ts <<EOF
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
};

export default nextConfig;
EOF
    
    print_success "Next.js configured for static export"
    
    # Get Railway URL
    echo ""
    read -p "Enter your Railway API URL (e.g., https://your-app.railway.app): " RAILWAY_URL
    
    # Set environment variable for build
    export NEXT_PUBLIC_API_URL="$RAILWAY_URL"
    
    # Install dependencies
    print_info "Installing dependencies..."
    npm install
    
    # Build
    print_info "Building static files..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Build successful!"
    else
        print_error "Build failed"
        # cd ..
        return 1
    fi
    
    # cd ..
    
    # Create deployment directory
    print_info "Preparing deployment package..."
    mkdir -p deployment/cpanel
    cp -r out/* deployment/cpanel/
    
    # Create .htaccess for cPanel
    cat > deployment/cpanel/.htaccess <<EOF
# Enable HTTPS redirect
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Handle Next.js routing
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [L]

# Enable compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Enable browser caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType text/javascript "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
EOF
    
    print_success "Deployment package ready!"
    
    # Create upload instructions
    cat > deployment/UPLOAD_TO_CPANEL.txt <<EOF
============================================================================
cPanel Upload Instructions
============================================================================

Your files are ready in: deployment/cpanel/

OPTION 1: Upload via cPanel File Manager
-----------------------------------------
1. Log into cPanel at your hosting provider
2. Open 'File Manager'
3. Navigate to 'public_html/' directory
4. Upload all files from 'deployment/cpanel/' directory
5. Set file permissions to 644, directory permissions to 755

OPTION 2: Upload via FTP
-------------------------
Host: grow-importa.com.uy
User: growimpo
Password: [your-cpanel-password]
Directory: /public_html/

1. Connect using FileZilla or any FTP client
2. Navigate to /public_html/
3. Upload all files from 'deployment/cpanel/'

OPTION 3: Upload via SCP (if SSH is enabled)
---------------------------------------------
scp -r deployment/cpanel/* growimpo@grow-importa.com.uy:~/public_html/

After Upload:
-------------
1. Visit: https://grow-importa.com.uy
2. Test the chatbot functionality
3. Verify API connection to Railway

Your Railway API URL: $RAILWAY_URL

============================================================================
EOF
    
    print_success "Upload instructions created: deployment/UPLOAD_TO_CPANEL.txt"
    
    echo ""
    print_header "cPanel Deployment Package Ready!"
    print_info "Files location: deployment/cpanel/"
    print_info "Instructions: deployment/UPLOAD_TO_CPANEL.txt"
    echo ""
    print_info "Next steps:"
    print_info "  1. Upload files to cPanel (see instructions above)"
    print_info "  2. Configure SSL certificate in cPanel"
    print_info "  3. Test your application"
}

# ============================================================================
# RENDER DEPLOYMENT
# ============================================================================

deploy_render() {
    print_header "Deploying to Render.com"
    
    print_info "Render deployment requires:"
    print_info "  1. GitHub repository"
    print_info "  2. Render account (free tier available)"
    print_info "  3. MongoDB Atlas database"
    echo ""
    
    # Create render.yaml
    print_info "Creating render.yaml configuration..."
    
    cat > render.yaml <<EOF
services:
  - type: web
    name: bmc-chatbot-api
    runtime: python3
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn sistema_completo_integrado:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: OPENAI_API_KEY
        sync: false
      - key: OPENAI_MODEL
        value: gpt-4o-mini
      - key: MONGODB_URI
        sync: false
      - key: PORT
        value: 8000
      - key: HOST
        value: 0.0.0.0
EOF
    
    print_success "render.yaml created"
    
    # Commit changes
    print_info "Committing configuration files..."
    git add render.yaml Procfile railway.json 2>/dev/null
    git commit -m "Add deployment configuration" 2>/dev/null
    git push 2>/dev/null
    
    echo ""
    print_info "Manual steps for Render deployment:"
    print_info "  1. Go to https://render.com"
    print_info "  2. Click 'New +' → 'Web Service'"
    print_info "  3. Connect your GitHub repository"
    print_info "  4. Render will auto-detect Python and render.yaml"
    print_info "  5. Set environment variables in Render dashboard:"
    print_info "     - OPENAI_API_KEY"
    print_info "     - MONGODB_URI (from MongoDB Atlas)"
    print_info "  6. Click 'Create Web Service'"
    echo ""
    
    print_success "Configuration ready for Render deployment!"
}

# ============================================================================
# INTERACTIVE FULL DEPLOYMENT
# ============================================================================

interactive_deployment() {
    print_header "BMC Chatbot - Interactive Deployment"
    
    echo "This wizard will guide you through deploying your chatbot."
    echo ""
    echo "Deployment architecture:"
    echo "  1. Python API → Railway.app or Render.com"
    echo "  2. Next.js Frontend → Vercel or cPanel"
    echo "  3. Database → Railway MongoDB or MongoDB Atlas"
    echo ""
    
    # Step 1: Choose API platform
    echo "Step 1: Choose API hosting platform"
    echo "  1) Railway.app (Recommended - Free tier)"
    echo "  2) Render.com (Alternative - Free tier)"
    echo ""
    read -p "Enter your choice (1 or 2): " api_choice
    
    case $api_choice in
        1)
            deploy_railway
            ;;
        2)
            deploy_render
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue to frontend deployment..."
    
    # Step 2: Choose frontend platform
    echo ""
    echo "Step 2: Choose frontend hosting platform"
    echo "  1) Vercel (Recommended - Best for Next.js)"
    echo "  2) cPanel (Use your existing hosting)"
    echo ""
    read -p "Enter your choice (1 or 2): " frontend_choice
    
    case $frontend_choice in
        1)
            deploy_vercel
            ;;
        2)
            deploy_cpanel
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
    
    # Summary
    print_header "Deployment Complete! 🎉"
    
    echo "Your chatbot is now deployed!"
    echo ""
    echo "Next steps:"
    echo "  1. Test your API endpoints"
    echo "  2. Configure WhatsApp webhook"
    echo "  3. Set up Google Sheets integration"
    echo "  4. Monitor logs and performance"
    echo ""
    
    print_success "All done! Your chatbot is live!"
}

# ============================================================================
# MAIN MENU
# ============================================================================

show_menu() {
    print_header "BMC Chatbot Deployment Script"
    
    echo "Choose deployment option:"
    echo ""
    echo "  1) Railway.app - Deploy Python API"
    echo "  2) Vercel - Deploy Next.js Frontend"
    echo "  3) cPanel - Prepare static files"
    echo "  4) Render.com - Deploy Python API"
    echo "  5) Full deployment (Interactive)"
    echo "  6) Pre-flight checks only"
    echo "  7) Exit"
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Parse command line arguments
    if [ $# -eq 1 ]; then
        case $1 in
            railway)
                preflight_checks
                deploy_railway
                exit 0
                ;;
            vercel)
                preflight_checks
                deploy_vercel
                exit 0
                ;;
            cpanel)
                preflight_checks
                deploy_cpanel
                exit 0
                ;;
            render)
                preflight_checks
                deploy_render
                exit 0
                ;;
            all)
                preflight_checks
                interactive_deployment
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Usage: $0 [railway|vercel|cpanel|render|all]"
                exit 1
                ;;
        esac
    fi
    
    # Interactive menu
    while true; do
        show_menu
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                preflight_checks
                deploy_railway
                ;;
            2)
                preflight_checks
                deploy_vercel
                ;;
            3)
                preflight_checks
                deploy_cpanel
                ;;
            4)
                preflight_checks
                deploy_render
                ;;
            5)
                preflight_checks
                interactive_deployment
                ;;
            6)
                preflight_checks
                ;;
            7)
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to return to menu..."
    done
}

# Run main
main "$@"
