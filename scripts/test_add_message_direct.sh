#!/bin/bash
# Add a test message directly to the Pi's message log

PI_USER="dai"
PI_HOST="relojdai.local"
MESSAGES_FILE="/home/dai/einkpetclock/data/messages.jsonl"

echo "============================================================"
echo "Add Test Message to Pi (Direct Method)"
echo "============================================================"
echo ""

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create message JSON
MESSAGE_JSON=$(cat <<EOF
{"timestamp": "$TIMESTAMP", "from": "Your Mac", "message": "Test message! 👋", "read": false}
EOF
)

echo "📨 Adding message to Pi..."
echo "Message: $MESSAGE_JSON"
echo ""

# Append to messages file
ssh "$PI_USER@$PI_HOST" "echo '$MESSAGE_JSON' >> $MESSAGES_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Message added successfully!"
    echo ""
    echo "💡 Check the Pi display - you should see:"
    echo "   'Msgs: 1 new' (or higher count) in the stats"
    echo ""
    echo "💡 To read messages on the Pi:"
    echo "   Press the [Menu] button to cycle to Messages menu"
    echo ""
    echo "📋 To view all messages on Pi:"
    echo "   ssh $PI_USER@$PI_HOST 'cat $MESSAGES_FILE'"
else
    echo "✗ Failed to add message"
fi
