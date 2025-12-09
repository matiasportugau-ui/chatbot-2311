#!/bin/bash

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}       BMC Chatbot System - Installer & Launcher               ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check for Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Check if python is version 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python 3 is required but not found.${NC}"
        echo "Please install Python 3.11 or higher."
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3 is required but not found.${NC}"
    echo "Please install Python 3.11 or higher."
    exit 1
fi

echo -e "${GREEN}Using Python: $PYTHON_CMD${NC}"
echo ""
echo -e "${BLUE}Starting Unified Launcher in Full Stack Mode...${NC}"
echo "This will:"
echo "1. Install/Update dependencies"
echo "2. Configure environment (.env)"
echo "3. Launch API Server"
echo "4. Launch Next.js Dashboard"
echo ""

# Execute unified launcher with fullstack mode
# The launcher handles all setup steps automatically
$PYTHON_CMD unified_launcher.py --mode fullstack

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}System exited with error code $EXIT_CODE${NC}"
    echo "Please check the logs in logs/launcher.log"
    read -p "Press Enter to exit..."
fi
