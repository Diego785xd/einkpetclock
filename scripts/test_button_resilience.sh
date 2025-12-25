#!/bin/bash
# Test script to verify button interaction fixes
# This helps verify that rapid button presses don't freeze the display

echo "========================================"
echo "E-Ink Pet Clock - Button Test"
echo "========================================"
echo ""
echo "This script monitors the display service for issues"
echo "Try rapidly pressing buttons on the device while running this"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to check service status
check_service() {
    if ssh dai@relojdai.local 'systemctl is-active --quiet eink-display.service'; then
        return 0
    else
        return 1
    fi
}

# Monitor the service
echo "Monitoring eink-display.service..."
echo "Time: $(date)"
echo ""

# Initial check
if check_service; then
    echo "✓ Service is running"
else
    echo "✗ Service is NOT running!"
    exit 1
fi

echo ""
echo "Following logs (press Ctrl+C to stop)..."
echo "=========================================="

# Follow logs in real-time
ssh dai@relojdai.local 'journalctl -u eink-display.service -f --no-pager'
