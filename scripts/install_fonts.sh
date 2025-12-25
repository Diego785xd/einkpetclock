#!/bin/bash
# Install and configure fonts on Raspberry Pi

set -e

PI_USER="dai"
PI_HOST="relojdai.local"
PROJECT_DIR="/home/dai/einkpetclock"

echo "============================================================"
echo "Installing Fonts on Raspberry Pi"
echo "============================================================"
echo ""

echo "📦 Installing fonts-dejavu package on Pi..."
ssh "$PI_USER@$PI_HOST" 'sudo apt-get update && sudo apt-get install -y fonts-dejavu fonts-dejavu-core'

echo ""
echo "🔗 Creating symlink to DejaVuSans font..."
ssh "$PI_USER@$PI_HOST" "cd $PROJECT_DIR/assets/fonts && ln -sf /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf Font.ttc"

echo ""
echo "✅ Verifying font installation..."
ssh "$PI_USER@$PI_HOST" "ls -lh $PROJECT_DIR/assets/fonts/Font.ttc"

echo ""
echo "🔄 Restarting display service..."
ssh "$PI_USER@$PI_HOST" 'sudo systemctl restart eink-display.service'

echo ""
echo "✓ Font installation complete!"
echo ""
echo "Check if fonts loaded successfully:"
echo "  ssh $PI_USER@$PI_HOST 'sudo journalctl -u eink-display.service -n 20'"
echo ""
echo "You should NO LONGER see 'Warning: Could not load custom fonts'"
