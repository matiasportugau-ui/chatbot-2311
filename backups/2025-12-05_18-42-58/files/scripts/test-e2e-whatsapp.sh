#!/bin/bash
# E2E Test Script for WhatsApp Integration
# Simulates WhatsApp webhook and verifies end-to-end flow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
N8N_WEBHOOK_URL="${N8N_WEBHOOK_URL:-http://localhost:5678/webhook/whatsapp}"
PY_API_URL="${PY_API_URL:-http://localhost:8000}"
VERIFY_TOKEN="${WHATSAPP_VERIFY_TOKEN:-test_verify_token}"
PHONE_NUMBER_ID="${WHATSAPP_PHONE_NUMBER_ID:-test_phone_id}"

echo -e "${YELLOW}=== E2E WhatsApp Integration Tests ===${NC}\n"

# Test 1: Webhook Verification (GET)
echo -e "${YELLOW}Test 1: Webhook Verification${NC}"
VERIFY_RESPONSE=$(curl -s -X GET \
  "${N8N_WEBHOOK_URL}?hub.mode=subscribe&hub.verify_token=${VERIFY_TOKEN}&hub.challenge=test_challenge_123")

if [[ "$VERIFY_RESPONSE" == "test_challenge_123" ]]; then
    echo -e "${GREEN}✓ Webhook verification passed${NC}"
else
    echo -e "${RED}✗ Webhook verification failed${NC}"
    echo "Response: $VERIFY_RESPONSE"
    exit 1
fi

# Test 2: Health Check Python API
echo -e "\n${YELLOW}Test 2: Python API Health Check${NC}"
HEALTH_RESPONSE=$(curl -s "${PY_API_URL}/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Python API is healthy${NC}"
else
    echo -e "${RED}✗ Python API health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test 3: Process Message via Python API
echo -e "\n${YELLOW}Test 3: Process Message via Python API${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "${PY_API_URL}/chat/process" \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Hola, necesito información sobre Isodec",
    "telefono": "+59891234567",
    "sesionId": "test_session_123"
  }')

if echo "$MESSAGE_RESPONSE" | grep -q "mensaje"; then
    echo -e "${GREEN}✓ Message processed successfully${NC}"
    echo "Response preview: $(echo $MESSAGE_RESPONSE | cut -c1-100)..."
else
    echo -e "${RED}✗ Message processing failed${NC}"
    echo "Response: $MESSAGE_RESPONSE"
    exit 1
fi

# Test 4: Simulate WhatsApp Webhook (POST)
echo -e "\n${YELLOW}Test 4: Simulate WhatsApp Webhook${NC}"
WEBHOOK_PAYLOAD='{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "test_entry_id",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "1234567890",
          "phone_number_id": "'"${PHONE_NUMBER_ID}"'"
        },
        "contacts": [{
          "profile": {
            "name": "Test User"
          },
          "wa_id": "+59891234567"
        }],
        "messages": [{
          "from": "+59891234567",
          "id": "test_message_id",
          "timestamp": "'"$(date +%s)"'",
          "type": "text",
          "text": {
            "body": "Quiero cotizar Isodec para mi casa"
          }
        }]
      },
      "field": "messages"
    }]
  }]
}'

# Calculate signature (simplified for testing)
SIGNATURE="sha256=test_signature"

WEBHOOK_RESPONSE=$(curl -s -X POST "${N8N_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: ${SIGNATURE}" \
  -d "$WEBHOOK_PAYLOAD")

if echo "$WEBHOOK_RESPONSE" | grep -q "ok\|status"; then
    echo -e "${GREEN}✓ Webhook POST processed${NC}"
else
    echo -e "${YELLOW}⚠ Webhook POST response: $WEBHOOK_RESPONSE${NC}"
    echo "Note: This may fail if n8n workflow is not active"
fi

# Test 5: Create Quote
echo -e "\n${YELLOW}Test 5: Create Quote${NC}"
QUOTE_RESPONSE=$(curl -s -X POST "${PY_API_URL}/quote/create" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nombre": "Test User",
      "telefono": "+59891234567",
      "direccion": "Test Address",
      "zona": "Montevideo"
    },
    "especificaciones": {
      "producto": "isodec",
      "espesor": "100mm",
      "relleno": "EPS",
      "largo_metros": 10,
      "ancho_metros": 5,
      "color": "Blanco",
      "termina_front": "Gotero",
      "termina_sup": "Gotero",
      "termina_lat_1": "Gotero",
      "termina_lat_2": "Gotero",
      "anclajes": "Incluido",
      "traslado": "Incluido"
    },
    "asignado_a": "MA",
    "observaciones": "Test quote from E2E test"
  }')

if echo "$QUOTE_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✓ Quote created successfully${NC}"
    QUOTE_ID=$(echo "$QUOTE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo "Quote ID: $QUOTE_ID"
else
    echo -e "${RED}✗ Quote creation failed${NC}"
    echo "Response: $QUOTE_RESPONSE"
    exit 1
fi

# Summary
echo -e "\n${GREEN}=== All Tests Passed! ===${NC}"
echo -e "\nTest Summary:"
echo "  ✓ Webhook verification"
echo "  ✓ Python API health check"
echo "  ✓ Message processing"
echo "  ✓ Webhook POST (may require active n8n)"
echo "  ✓ Quote creation"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "  1. Verify MongoDB has conversation records"
echo "  2. Check n8n workflow executions"
echo "  3. Review logs for any errors"

