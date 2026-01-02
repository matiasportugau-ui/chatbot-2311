#!/bin/bash

# BMC WhatsApp Workflow Migration Script
# This script helps migrate from the old workflow to the improved version

set -e

echo "🚀 BMC WhatsApp Workflow Migration Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if n8n is available
if ! command -v n8n &> /dev/null; then
    echo -e "${RED}❌ n8n command not found. Please install n8n first.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "workflow-whatsapp-improved.json" ]; then
    echo -e "${RED}❌ workflow-whatsapp-improved.json not found in current directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-migration checklist:${NC}"
echo "1. Backup current workflow"
echo "2. Stop n8n if running"
echo "3. Import improved workflow"
echo "4. Configure credentials"
echo "5. Test workflow"
echo ""

# Create backup
echo -e "${YELLOW}📦 Creating backup of current workflow...${NC}"
if [ -f "workflow-whatsapp.json" ]; then
    cp workflow-whatsapp.json workflow-whatsapp-backup-$(date +%Y%m%d-%H%M%S).json
    echo -e "${GREEN}✅ Backup created${NC}"
else
    echo -e "${YELLOW}⚠️  Original workflow file not found, skipping backup${NC}"
fi

# Validate JSON
echo -e "${YELLOW}🔍 Validating improved workflow JSON...${NC}"
if python3 -m json.tool workflow-whatsapp-improved.json > /dev/null 2>&1; then
    echo -e "${GREEN}✅ JSON is valid${NC}"
else
    echo -e "${RED}❌ Invalid JSON in improved workflow file${NC}"
    exit 1
fi

# Check n8n status
echo -e "${YELLOW}🔍 Checking n8n status...${NC}"
if pgrep -f "n8n" > /dev/null; then
    echo -e "${YELLOW}⚠️  n8n is running. Please stop it before proceeding.${NC}"
    echo "You can stop n8n with: pkill -f n8n"
    read -p "Press Enter when n8n is stopped..."
fi

echo -e "${GREEN}✅ Ready to proceed with migration${NC}"
echo ""

# Migration steps
echo -e "${YELLOW}🔄 Migration Steps:${NC}"
echo "1. Import the improved workflow into n8n"
echo "2. Configure the following credentials:"
echo "   - WhatsApp Business API (OAuth2)"
echo "   - Google Sheets (Service Account)"
echo "3. Set up environment variables:"
echo "   - API_BASE_URL (for production)"
echo "   - LOG_LEVEL (optional)"
echo "4. Test the workflow with sample data"
echo ""

# Provide import command
echo -e "${YELLOW}📥 Import command:${NC}"
echo "n8n import:workflow --input=workflow-whatsapp-improved.json"
echo ""

# Test data
echo -e "${YELLOW}🧪 Test webhook payload:${NC}"
cat << 'EOF'
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "1234567890",
          "id": "test_message_id",
          "timestamp": "1234567890",
          "text": {
            "body": "Cotizar construcción para 100m2"
          }
        }],
        "contacts": [{
          "profile": {
            "name": "Test User"
          }
        }]
      }
    }]
  }]
}
EOF

echo ""
echo -e "${GREEN}🎉 Migration script completed!${NC}"
echo ""
echo -e "${YELLOW}📚 Next steps:${NC}"
echo "1. Import the workflow using the command above"
echo "2. Configure credentials in n8n"
echo "3. Test with the sample payload"
echo "4. Monitor logs for any issues"
echo "5. Review the IMPROVEMENTS_GUIDE.md for detailed information"
echo ""
echo -e "${GREEN}✅ Happy migrating!${NC}"
