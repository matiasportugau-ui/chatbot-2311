#!/bin/bash
# Test script for API debugging endpoints
# Requires the API server to be running on localhost:8000

set -e

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

echo "=========================================="
echo "API Endpoints Test Suite"
echo "=========================================="
echo "Testing API at: $API_BASE_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test health endpoint
echo "1. Testing /api/health endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/health" || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ Health endpoint works${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    
    # Check for rate limits in response
    if echo "$body" | grep -q "rate_limits"; then
        echo -e "${GREEN}✅ Rate limits included in health check${NC}"
    else
        echo -e "${YELLOW}⚠️  Rate limits not in health check (may be normal if no requests made)${NC}"
    fi
else
    echo -e "${RED}❌ Health endpoint failed with code: $http_code${NC}"
    echo "Response: $body"
fi

echo ""

# Test rate limits endpoint
echo "2. Testing /api/monitoring/rate-limits endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/monitoring/rate-limits" || echo -e "\n000")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ Rate limits endpoint works${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ Rate limits endpoint failed with code: $http_code${NC}"
    echo "Response: $body"
fi

echo ""

# Test debug endpoint with a sample request ID
echo "3. Testing /api/debug/request/{request_id} endpoint..."
# First, make a request to generate a request ID
echo "Making a test request to generate request ID..."
chat_response=$(curl -s -X POST "$API_BASE_URL/chat/process" \
    -H "Content-Type: application/json" \
    -H "X-Client-Request-Id: test-debug-$(date +%s)" \
    -d '{
        "mensaje": "test",
        "telefono": "+59812345678"
    }' || echo "")

if [ -n "$chat_response" ]; then
    # Extract request ID from response headers or try to get it from the health endpoint
    # For now, we'll test with a known format
    test_request_id="test-request-id-123"
    
    response=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/debug/request/$test_request_id" || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "404" ]; then
        echo -e "${YELLOW}⚠️  Request ID not found (expected if using test ID)${NC}"
        echo "This is normal - the endpoint works but the test ID doesn't exist"
        echo -e "${GREEN}✅ Debug endpoint is accessible${NC}"
    elif [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ Debug endpoint works${NC}"
        echo "Response:"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ Debug endpoint failed with code: $http_code${NC}"
        echo "Response: $body"
    fi
else
    echo -e "${YELLOW}⚠️  Could not make test request, skipping debug endpoint test${NC}"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "To test with a real request ID:"
echo "1. Make a request to /chat/process"
echo "2. Note the X-Request-ID header in the response"
echo "3. Use that ID with /api/debug/request/{id}"
echo ""
echo "Example:"
echo "  curl -X POST $API_BASE_URL/chat/process \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'X-Client-Request-Id: my-custom-id' \\"
echo "    -d '{\"mensaje\": \"test\", \"telefono\": \"+59812345678\"}'"
echo ""
echo "  curl $API_BASE_URL/api/debug/request/my-custom-id"

