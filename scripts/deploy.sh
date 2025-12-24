#!/bin/bash
# Deployment script - run from your Mac to deploy to Pi
# Usage: ./deploy.sh [pi_ip_address] [pi_username]

set -e

# Configuration
PI_IP="${1:-10.8.17.62}"  # Default to the IP from .env.example
PI_USER="${2:-$USER}"     # Default to current username, or specify (e.g., pi, dai)
PI_DIR="\$HOME/einkpetclock"  # Use remote user's home directory
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "========================================="
echo "E-Ink Pet Clock Deployment"
echo "========================================="
echo "Local:  $LOCAL_DIR"
echo "Remote: $PI_USER@$PI_IP:\$HOME/einkpetclock"
echo ""

# Check if Pi is reachable
echo "Checking if Pi is reachable..."
if ! ping -c 1 -W 2 "$PI_IP" > /dev/null 2>&1; then
    echo "Error: Cannot reach Pi at $PI_IP"
    echo "Make sure:"
    echo "  1. Pi is powered on"
    echo "  2. Both devices are on ZeroTier network"
    echo "  3. IP address is correct"
    exit 1
fi
echo "✓ Pi is reachable"

# Test SSH connection
echo ""
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$PI_USER@$PI_IP" "echo '✓ SSH connection works'" 2>/dev/null; then
    echo "Error: Cannot SSH to Pi"
    echo "Run: ssh-copy-id $PI_USER@$PI_IP"
    exit 1
fi

# Create directory on Pi if it doesn't exist
echo ""
echo "Ensuring project directory exists on Pi..."
ssh "$PI_USER@$PI_IP" "mkdir -p \$HOME/einkpetclock"

# Rsync files (excludes .git, __pycache__, data, venv, etc.)
echo ""
echo "Syncing files..."
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='data/*.json' \
    --exclude='data/*.jsonl' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='*.tmp' \
    "$LOCAL_DIR/" "$PI_USER@$PI_IP:\$HOME/einkpetclock/"

echo ""
echo "✓ Files synced successfully"

# Restart services if they're running
echo ""
read -p "Restart services on Pi? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Restarting services..."
    ssh "$PI_USER@$PI_IP" << 'EOF'
        if systemctl is-active --quiet eink-display.service; then
            sudo systemctl restart eink-display.service
            echo "✓ Display service restarted"
        fi
        if systemctl is-active --quiet eink-api.service; then
            sudo systemctl restart eink-api.service
            echo "✓ API service restarted"
        fi
EOF
fi

# Show status
echo ""
read -p "Show service status? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Service status:"
    ssh "$PI_USER@$PI_IP" << 'EOF'
        echo "--- Display Service ---"
        sudo systemctl status eink-display.service --no-pager -l | head -n 15
        echo ""
        echo "--- API Service ---"
        sudo systemctl status eink-api.service --no-pager -l | head -n 15
EOF
fi

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo ""
echo "To view logs:"
echo "  ssh $PI_USER@$PI_IP"
echo "  sudo journalctl -u eink-display.service -f"
echo ""
echo "To test API:"
echo "  curl http://$PI_IP:5000/api/status"
echo ""
