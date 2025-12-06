#!/bin/bash

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}       BMC Chatbot - 24/7 Setup (PM2)                          ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Install PM2 locally (to avoid sudo password issues)
if ! command -v pm2 &> /dev/null; then
    echo -e "${BLUE}Installing PM2 (Process Manager) locally...${NC}"
    npm install pm2
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install PM2.${NC}"
        exit 1
    fi
    echo -e "${GREEN}PM2 installed successfully.${NC}"
else
    echo -e "${GREEN}PM2 is already installed.${NC}"
fi

echo ""
echo -e "${BLUE}Starting Chatbot System with PM2...${NC}"

# Start the application using ecosystem file and npx
npx pm2 start ecosystem.config.js

echo ""
echo -e "${GREEN}System is now running in the background!${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  ${GREEN}npx pm2 status${NC}       - Check running processes"
echo -e "  ${GREEN}npx pm2 logs${NC}         - View real-time logs"
echo -e "  ${GREEN}npx pm2 stop all${NC}     - Stop the chatbot"
echo -e "  ${GREEN}npx pm2 restart all${NC}  - Restart the chatbot"
echo ""
echo -e "${BLUE}To ensure it runs after restart:${NC}"
echo "Run: npx pm2 startup"
echo ""
