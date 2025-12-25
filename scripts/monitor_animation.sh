#!/bin/bash
# Monitor the animation system in real-time

echo "========================================"
echo "E-Ink Pet Clock - Animation Monitor"
echo "========================================"
echo ""
echo "This script monitors the display service"
echo "You should see frame updates every 0.5 seconds"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Follow logs and filter for animation-related messages
ssh dai@relojdai.local 'journalctl -u eink-display.service -f --no-pager | grep -i --line-buffered -E "(update|frame|render|animation|display)"'
