#!/bin/bash

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}       BMC Chatbot - Internet Access Setup                     ${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js first.${NC}"
    exit 1
fi

echo -e "${BLUE}This script will use 'localtunnel' to temporarily expose your${NC}"
echo -e "${BLUE}local server to the internet so you can access it from any device.${NC}"
echo ""
echo -e "${GREEN}1. Exposing Dashboard (Port 3000)...${NC}"
echo "----------------------------------------------------------------"
echo "You will receive a URL below (e.g., https://wild-goose-42.loca.lt)"
echo "Use that URL on your phone/other device to access the dashboard."
echo "----------------------------------------------------------------"
echo ""

# Use npx to run localtunnel without installing it permanently
# We use & to run it in background, but actually for this simple script,
# keeping it in foreground to show URL is better. 
# But we might want both API and Dashboard.

echo "Press Ctrl+C to stop sharing."
echo ""
echo "Starting tunnel for Port 3000 (Dashboard)..."
npx localtunnel --port 3000

# Note: localtunnel will block here until user cancels.
# If connection is unstable, consider ngrok (requires account).
