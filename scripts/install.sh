#!/bin/bash
# Installation script for E-Ink Pet Clock on Raspberry Pi
# Run this on the Pi after first deployment

set -e

echo "========================================="
echo "E-Ink Pet Clock Installation"
echo "========================================="

# Check if running on Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

PROJECT_DIR="/home/pi/einkpetclock"
VENV_DIR="$PROJECT_DIR/venv"

echo "Project directory: $PROJECT_DIR"

# Update system
echo ""
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-pil \
    python3-rpi.gpio \
    git \
    build-essential

# Install Waveshare e-Paper library
echo ""
echo "Installing Waveshare e-Paper library..."
sudo pip3 install waveshare-epd

# Install base Python dependencies
echo ""
echo "Installing Python dependencies..."
cd "$PROJECT_DIR"
pip3 install --user -r requirements.txt
pip3 install --user pytz  # For timezone support

# Create and setup venv for API
echo ""
echo "Creating virtual environment for API..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r web/requirements.txt
deactivate

# Create .env if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "Creating .env file..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "Please edit .env file with your configuration:"
    echo "  nano $PROJECT_DIR/.env"
    read -p "Press Enter to continue after editing..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/assets/sprites"
mkdir -p "$PROJECT_DIR/assets/fonts"
mkdir -p /tmp/eink_flags

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
    echo "Services enabled"
fi

# Start services
echo ""
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start eink-display.service
    sudo systemctl start eink-api.service
    echo "Services started"
    
    # Show status
    sleep 2
    echo ""
    echo "Service status:"
    sudo systemctl status eink-display.service --no-pager -l
    echo ""
    sudo systemctl status eink-api.service --no-pager -l
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  View display logs:  sudo journalctl -u eink-display.service -f"
echo "  View API logs:      sudo journalctl -u eink-api.service -f"
echo "  Restart display:    sudo systemctl restart eink-display.service"
echo "  Restart API:        sudo systemctl restart eink-api.service"
echo "  Stop all:           sudo systemctl stop eink-display.service eink-api.service"
echo ""
echo "Edit configuration:   nano $PROJECT_DIR/.env"
echo ""
