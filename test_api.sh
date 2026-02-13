#!/bin/bash

# API Testing Script for Jupiter Edge+ Credit Card Agent
# Tests all major endpoints and scenarios

# Configuration
API_BASE_URL="http://localhost:8000"
API_KEY="jupiter_api_key_2026"
TEST_USER_ID="919876543210"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

echo "=================================="
echo "🧪 Jupiter Edge+ API Test Suite"
echo "=================================="
echo ""

# Helper function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Health check returned 200"
    echo "   Response: $BODY"
else
    print_result 1 "Health check failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 2: Root Endpoint
echo -e "${BLUE}Test 2: Root Endpoint${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Root endpoint accessible"
else
    print_result 1 "Root endpoint failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 3: API Docs
echo -e "${BLUE}Test 3: API Documentation${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/docs")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "API docs accessible"
else
    print_result 1 "API docs failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 4: Chat API - Without API Key (Should Fail)
echo -e "${BLUE}Test 4: Chat API - No API Key (Should Fail)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/chat" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"$TEST_USER_ID\", \"message\": \"Hi\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "401" ]; then
    print_result 0 "Correctly rejected request without API key"
else
    print_result 1 "Should have returned 401 (got HTTP $HTTP_CODE)"
fi
echo ""

# Test 5: Chat API - English Greeting
echo -e "${BLUE}Test 5: Chat API - English Greeting${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"user_id\": \"$TEST_USER_ID\", \"message\": \"Hi, I want to apply for credit card\", \"user_name\": \"Rahul\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Chat API accepted English greeting"
    echo "   Response: $(echo $BODY | jq -r '.message' 2>/dev/null | head -c 100)..."
else
    print_result 1 "Chat API failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 6: Chat API - Hinglish Message
echo -e "${BLUE}Test 6: Chat API - Hinglish Message${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"user_id\": \"$TEST_USER_ID\", \"message\": \"Namaste, mujhe credit card chahiye\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    LANGUAGE=$(echo $BODY | jq -r '.language' 2>/dev/null)
    if [[ "$LANGUAGE" == "HINGLISH" || "$LANGUAGE" == "HINDI" ]]; then
        print_result 0 "Correctly detected Hinglish/Hindi"
    else
        print_result 1 "Failed to detect Hinglish (detected: $LANGUAGE)"
    fi
else
    print_result 1 "Chat API failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 7: Chat API - Product Query
echo -e "${BLUE}Test 7: Chat API - Product Query${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"user_id\": \"$TEST_USER_ID\", \"message\": \"What is the cashback on shopping?\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    MESSAGE=$(echo $BODY | jq -r '.message' 2>/dev/null)
    if [[ "$MESSAGE" == *"10%"* ]]; then
        print_result 0 "Correctly answered cashback query"
    else
        print_result 1 "Response doesn't contain expected cashback info"
    fi
    echo "   Response: $(echo $MESSAGE | head -c 100)..."
else
    print_result 1 "Chat API failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 8: Chat API - Off-Topic Question
echo -e "${BLUE}Test 8: Chat API - Off-Topic Question${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/chat" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"user_id\": \"$TEST_USER_ID\", \"message\": \"Who is the Prime Minister?\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    INTENT=$(echo $BODY | jq -r '.intent' 2>/dev/null)
    if [[ "$INTENT" == *"OFF_TOPIC"* ]]; then
        print_result 0 "Correctly identified off-topic question"
    else
        print_result 1 "Failed to identify off-topic (intent: $INTENT)"
    fi
else
    print_result 1 "Chat API failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 9: Session Info
echo -e "${BLUE}Test 9: Get Session Info${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/session/$TEST_USER_ID" \
    -H "X-API-Key: $API_KEY")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Retrieved session info"
    echo "   User: $(echo $BODY | jq -r '.user_info.name' 2>/dev/null)"
    echo "   Messages: $(echo $BODY | jq -r '.conversation_count' 2>/dev/null)"
else
    print_result 1 "Failed to get session info (HTTP $HTTP_CODE)"
fi
echo ""

# Test 10: Reset Session
echo -e "${BLUE}Test 10: Reset Session${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/api/reset" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "{\"user_id\": \"$TEST_USER_ID\"}")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Session reset successful"
else
    print_result 1 "Session reset failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 11: API Stats
echo -e "${BLUE}Test 11: API Statistics${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/api/stats" \
    -H "X-API-Key: $API_KEY")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Retrieved API stats"
    echo "   Active sessions: $(echo $BODY | jq -r '.active_sessions' 2>/dev/null)"
else
    print_result 1 "Failed to get stats (HTTP $HTTP_CODE)"
fi
echo ""

# Test 12: WhatsApp Webhook Verification
echo -e "${BLUE}Test 12: WhatsApp Webhook Verification${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/webhook?mode=subscribe&challenge=test123&verify_token=jupiter_edge_plus_2026")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ] && [ "$BODY" = "test123" ]; then
    print_result 0 "Webhook verification successful"
else
    print_result 1 "Webhook verification failed (HTTP $HTTP_CODE)"
fi
echo ""

# Summary
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    exit 1
fi
