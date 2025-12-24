#!/bin/bash
# Simple installation - assumes hardware dependencies already work
# Use this if you can already run hardware/example.py

set -e

echo "========================================="
echo "E-Ink Pet Clock - Simple Install"
echo "========================================="
echo "This assumes your display hardware already works!"
echo ""

# Detect current directory or use home directory
if [ -f "$(pwd)/core/config.py" ]; then
    PROJECT_DIR="$(pwd)"
else
    PROJECT_DIR="$HOME/einkpetclock"
fi

VENV_DIR="$PROJECT_DIR/venv"

echo "Project directory: $PROJECT_DIR"

# Verify we're in the right place
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory not found at $PROJECT_DIR"
    echo "Please cd to the project directory and run this script again"
    exit 1
fi

cd "$PROJECT_DIR"nstallation - assumes hardware dependencies already work
# Use this if you can already run hardware/example.py

set -e

echo "========================================="
echo "E-Ink Pet Clock - Simple Install"
echo "========================================="
echo "This assumes your display hardware already works!"
echo ""

PROJECT_DIR="/home/pi/einkpetclock"
VENV_DIR="$PROJECT_DIR/venv"

# Verify we're in the right place
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory not found at $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Test if example works
echo "Testing if display example works..."
if python3 -c "from waveshare_epd import epd2in13_V4" 2>/dev/null; then
    echo "✓ Waveshare library is importable"
else
    echo "⚠️  Warning: Cannot import waveshare_epd"
    echo "   Make sure hardware/example.py works before continuing"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install only what's needed for our code
echo ""
echo "Installing minimal dependencies..."

# Check and install python3-dotenv if needed
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "Installing python3-dotenv..."
    sudo apt-get update
    sudo apt-get install -y python3-dotenv
fi

# Check and install pytz if needed
if ! python3 -c "import pytz" 2>/dev/null; then
    echo "Installing python3-tz (pytz)..."
    sudo apt-get install -y python3-tz
fi

# PIL should already be there, but check
if ! python3 -c "import PIL" 2>/dev/null; then
    echo "Installing python3-pil..."
    sudo apt-get install -y python3-pil
fi

# RPi.GPIO should already be there
if ! python3 -c "import RPi.GPIO" 2>/dev/null; then
    echo "Installing python3-rpi.gpio..."
    sudo apt-get install -y python3-rpi.gpio
fi

echo "✓ Core dependencies ready"

# Create virtual environment for API only
echo ""
echo "Creating virtual environment for API..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/web/requirements.txt"
    deactivate
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Create .env if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "Creating .env file..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration:"
    echo "    nano $PROJECT_DIR/.env"
    echo ""
    echo "Required settings:"
    echo "  - DEVICE_NAME (e.g., bunny_clock_dai)"
    echo "  - DEVICE_IP (e.g., 10.8.17.62)"
    echo "  - REMOTE_DEVICE_IP (e.g., 10.8.17.114)"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/assets/sprites"
mkdir -p "$PROJECT_DIR/assets/fonts"
mkdir -p /tmp/eink_flags
echo "✓ Directories created"

# Make scripts executable
chmod +x "$PROJECT_DIR/scripts/"*.sh 2>/dev/null || true

# Set permissions
chmod -R 755 "$PROJECT_DIR"
chmod 644 "$PROJECT_DIR/.env" 2>/dev/null || true

# Install systemd services
echo ""
echo "Installing systemd services..."

# Replace %u and %h with actual user and home directory
sed "s|%u|$USER|g; s|%h|$HOME|g" "$PROJECT_DIR/systemd/eink-display.service" | \
    sudo tee /etc/systemd/system/eink-display.service > /dev/null

sed "s|%u|$USER|g; s|%h|$HOME|g" "$PROJECT_DIR/systemd/eink-api.service" | \
    sudo tee /etc/systemd/system/eink-api.service > /dev/null

sudo systemctl daemon-reload
echo "✓ Services installed"

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
    echo "Starting services..."
    sudo systemctl start eink-display.service
    sleep 2
    sudo systemctl start eink-api.service
    sleep 2
    
    echo ""
    echo "Service status:"
    echo "--- Display Service ---"
    sudo systemctl status eink-display.service --no-pager -l | head -n 12
    echo ""
    echo "--- API Service ---"
    sudo systemctl status eink-api.service --no-pager -l | head -n 12
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "✓ Existing hardware setup preserved"
echo "✓ Minimal dependencies installed"
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
echo "Test your setup:"
echo "  Display test:       python3 $PROJECT_DIR/hardware/example.py"
echo "  API test:           curl http://localhost:5000/api/status"
echo ""
