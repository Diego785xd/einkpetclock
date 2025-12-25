#!/bin/bash
# Test sending a message to the Pi's pet clock

PI_HOST="relojdai.local"
PI_PORT="5001"

echo "============================================================"
echo "Test Message Sender for E-Ink Pet Clock"
echo "============================================================"
echo ""
echo "Target: http://$PI_HOST:$PI_PORT"
echo ""

# Method 1: Send a poke (simple message)
echo "📨 Sending test message (poke)..."
curl -X POST "http://$PI_HOST:$PI_PORT/poke" \
    -H "Content-Type: application/json" \
    -d '{"message": "Test message from Mac!", "from": "Your Mac"}' \
    2>/dev/null

echo ""
echo ""
echo "✓ Message sent!"
echo ""
echo "Check the Pi display - you should see:"
echo "  'Msgs: 1 new' on the stats section"
echo ""
echo "To send more messages, run this script again or use:"
echo "  curl -X POST http://$PI_HOST:$PI_PORT/poke -H 'Content-Type: application/json' -d '{\"message\":\"Hello!\"}'"
echo ""
echo "To view messages on the Pi:"
echo "  Press the [Menu] button to cycle to Messages menu"
