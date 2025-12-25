#!/bin/bash
# Deploy sprite updates to Raspberry Pi

set -e

PI_USER="rossi"
PI_IP="10.8.17.62"
PROJECT_DIR="/home/rossi/einkpetclock"

echo "============================================================"
echo "Deploying Sprites to Raspberry Pi"
echo "============================================================"
echo ""
echo "Target: $PI_USER@$PI_IP:$PROJECT_DIR"
echo ""

# Copy sprites directory
echo "📦 Syncing sprites..."
rsync -avz --progress \
    assets/sprites/ \
    "$PI_USER@$PI_IP:$PROJECT_DIR/assets/sprites/"

echo ""
echo "📦 Syncing updated menu_system.py..."
rsync -avz --progress \
    core/menu_system.py \
    "$PI_USER@$PI_IP:$PROJECT_DIR/core/"

echo ""
echo "🔄 Restarting display service..."
ssh "$PI_USER@$PI_IP" "sudo systemctl restart eink-display.service"

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Check status with:"
echo "  ssh $PI_USER@$PI_IP 'sudo systemctl status eink-display.service'"
echo ""
echo "View logs with:"
echo "  ssh $PI_USER@$PI_IP 'sudo journalctl -u eink-display.service -f'"
