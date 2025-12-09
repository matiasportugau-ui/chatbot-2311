#!/bin/bash
# Railway Deployment Test Script
# Tests the deployed chatbot API endpoints

API_URL="https://web-production-b896.up.railway.app"

echo "🔍 Testing Railway Deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Health check
echo "1️⃣  Health Check:"
echo "   GET $API_URL/health"
echo ""
HEALTH_RESPONSE=$(curl -s $API_URL/health)
echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 2: Simple greeting
echo "2️⃣  Chat Test - Simple Greeting:"
echo "   POST $API_URL/api/chat"
echo "   Message: 'Hola'"
echo ""
CHAT_RESPONSE=$(curl -s -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola",
    "session_id": "test-session-001"
  }')
echo "$CHAT_RESPONSE" | jq '.' 2>/dev/null || echo "$CHAT_RESPONSE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 3: Product inquiry
echo "3️⃣  Chat Test - Product Inquiry:"
echo "   Message: '¿Qué productos tienen?'"
echo ""
PRODUCT_RESPONSE=$(curl -s -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué productos tienen?",
    "session_id": "test-session-001"
  }')
echo "$PRODUCT_RESPONSE" | jq '.' 2>/dev/null || echo "$PRODUCT_RESPONSE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if AI is working
if echo "$CHAT_RESPONSE" | grep -q "IA no disponible"; then
    echo "❌ AI NOT CONFIGURED"
    echo "   Add OPENAI_API_KEY to Railway environment variables"
elif echo "$CHAT_RESPONSE" | grep -q "mensaje"; then
    echo "✅ AI IS WORKING"
    echo "   Deployment successful!"
else
    echo "⚠️  UNEXPECTED RESPONSE"
    echo "   Check deploy logs for errors"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tests complete!"
echo ""
echo "📊 View detailed logs at:"
echo "   https://railway.app/project/compassionate-vitality"
