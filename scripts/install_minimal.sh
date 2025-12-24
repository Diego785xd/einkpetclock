#!/bin/bash
# Minimal installation - uses system packages when possible
# Better for newer Raspberry Pi OS with PEP 668

set -e

echo "========================================="
echo "E-Ink Pet Clock - Minimal Install"
echo "========================================="

PROJECT_DIR="/home/pi/einkpetclock"
VENV_DIR="$PROJECT_DIR/venv"

echo "Project directory: $PROJECT_DIR"

# Update system
echo ""
echo "Updating system packages..."
sudo apt-get update

# Install ALL dependencies via apt (preferred method)
echo ""
echo "Installing system packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pil \
    python3-rpi.gpio \
    python3-dotenv \
    python3-tz \
    git \
    build-essential

# Install Waveshare library using --break-system-packages (safe for system-wide libraries)
echo ""
echo "Installing Waveshare e-Paper library..."
sudo pip3 install --break-system-packages waveshare-epd

# Create virtual environment for API only
echo ""
echo "Creating virtual environment for API..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/web/requirements.txt"
deactivate

# Create .env if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "Creating .env file..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration:"
    echo "    nano $PROJECT_DIR/.env"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/assets/sprites"
mkdir -p "$PROJECT_DIR/assets/fonts"
mkdir -p /tmp/eink_flags

# Make scripts executable
chmod +x "$PROJECT_DIR/scripts/"*.sh

# Set permissions
chmod -R 755 "$PROJECT_DIR"
chmod 644 "$PROJECT_DIR/.env"

# Install systemd services
echo ""
echo "Installing systemd services..."
sudo cp "$PROJECT_DIR/systemd/eink-display.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/systemd/eink-api.service" /etc/systemd/system/
sudo systemctl daemon-reload

# Enable services
echo ""
read -p "Enable services to start on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl enable eink-display.service
    sudo systemctl enable eink-api.service
    echo "✓ Services enabled"
fi

# Start services
echo ""
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start eink-display.service
    sudo systemctl start eink-api.service
    echo "✓ Services started"
    
    # Show status
    sleep 2
    echo ""
    echo "Service status:"
    echo "--- Display Service ---"
    sudo systemctl status eink-display.service --no-pager -l | head -n 10
    echo ""
    echo "--- API Service ---"
    sudo systemctl status eink-api.service --no-pager -l | head -n 10
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "✓ System packages installed"
echo "✓ Waveshare library installed"
echo "✓ Virtual environment created for API"
echo "✓ Systemd services configured"
echo ""
echo "Useful commands:"
echo "  View display logs:  sudo journalctl -u eink-display.service -f"
echo "  View API logs:      sudo journalctl -u eink-api.service -f"
echo "  Restart display:    sudo systemctl restart eink-display.service"
echo "  Restart API:        sudo systemctl restart eink-api.service"
echo "  Stop all:           sudo systemctl stop eink-display.service eink-api.service"
echo ""
echo "Configuration:"
echo "  Edit settings:      nano $PROJECT_DIR/.env"
echo ""
