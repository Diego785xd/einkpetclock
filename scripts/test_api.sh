#!/bin/bash
# Test script - send test messages to the clock from your Mac
# Usage: ./test_api.sh [pi_ip] [port]

PI_IP="${1:-10.8.17.62}"
PORT="${2:-5000}"
BASE_URL="http://$PI_IP:$PORT"

echo "Testing E-Ink Pet Clock API"
echo "URL: $BASE_URL"
echo ""

# Test 1: Health check
echo "1. Health check..."
curl -s "$BASE_URL/api/health" | python3 -m json.tool
echo ""

# Test 2: Get status
echo "2. Get status..."
curl -s "$BASE_URL/api/status" | python3 -m json.tool
echo ""

# Test 3: Send message
echo "3. Sending test message..."
curl -s -X POST "$BASE_URL/api/message" \
    -H "Content-Type: application/json" \
    -d '{
        "from_device": "mac_test",
        "message": "Hello from Mac! 👋",
        "type": "text"
    }' | python3 -m json.tool
echo ""

# Test 4: Send poke
echo "4. Sending poke..."
curl -s -X POST "$BASE_URL/api/poke" \
    -H "Content-Type: application/json" \
    -d '{
        "from_device": "mac_test"
    }' | python3 -m json.tool
echo ""

# Test 5: Send feed
echo "5. Sending feed..."
curl -s -X POST "$BASE_URL/api/feed" \
    -H "Content-Type: application/json" \
    -d '{
        "from_device": "mac_test"
    }' | python3 -m json.tool
echo ""

echo "Tests complete!"
echo ""
echo "The clock should show the new message and updated pet state."
