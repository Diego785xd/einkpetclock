#!/bin/bash
# Quick deploy and install on Pi from Mac
# Usage: ./scripts/quick_install_on_pi.sh

PI_USER="dai"
PI_IP="10.8.17.62"
PI_PASSWORD="314159"

echo "=== Deploying to Pi and Installing ==="
echo ""

# Pull latest changes on Pi
echo "Step 1: Pulling latest code on Pi..."
ssh ${PI_USER}@${PI_IP} << 'ENDSSH'
cd ~/einkpetclock
git pull
echo "✓ Code updated"
ENDSSH

echo ""
echo "Step 2: Running installation script..."
ssh ${PI_USER}@${PI_IP} << 'ENDSSH'
cd ~/einkpetclock
bash scripts/install_fixed.sh
ENDSSH

echo ""
echo "Step 3: Running system tests..."
ssh ${PI_USER}@${PI_IP} << 'ENDSSH'
cd ~/einkpetclock
bash scripts/test_system.sh
ENDSSH

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps (run on Pi):"
echo "1. Edit .env: ssh ${PI_USER}@${PI_IP} 'nano ~/einkpetclock/.env'"
echo "2. Start services: ssh ${PI_USER}@${PI_IP} 'sudo systemctl start eink-display eink-api'"
echo "3. Check status: ssh ${PI_USER}@${PI_IP} 'sudo systemctl status eink-display'"
