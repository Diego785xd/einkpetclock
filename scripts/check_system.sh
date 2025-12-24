#!/bin/bash
# Check Pi environment and dependencies

echo "========================================="
echo "E-Ink Pet Clock - System Check"
echo "========================================="
echo ""

# Python version
echo "Python Version:"
python3 --version
echo ""

# Check if this is a Pi
echo "Device Check:"
if [ -f /proc/device-tree/model ]; then
    cat /proc/device-tree/model
    echo ""
else
    echo "Not a Raspberry Pi (or model file not found)"
fi
echo ""

# Check installed packages
echo "Checking installed packages..."
echo ""

check_package() {
    if dpkg -l | grep -q "^ii  $1 "; then
        echo "✓ $1 installed"
    else
        echo "✗ $1 NOT installed"
    fi
}

check_package "python3"
check_package "python3-pip"
check_package "python3-venv"
check_package "python3-pil"
check_package "python3-rpi.gpio"
check_package "python3-dotenv"
check_package "python3-tz"
echo ""

# Check Python packages
echo "Checking Python packages (pip)..."
echo ""

check_pip_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "✓ $1 importable"
    else
        echo "✗ $1 NOT importable"
    fi
}

check_pip_package "dotenv"
check_pip_package "PIL"
check_pip_package "pytz"
check_pip_package "waveshare_epd"
check_pip_package "RPi.GPIO"
echo ""

# Check if services exist
echo "Checking systemd services..."
echo ""

if [ -f /etc/systemd/system/eink-display.service ]; then
    echo "✓ eink-display.service installed"
    sudo systemctl status eink-display.service --no-pager | head -n 3
else
    echo "✗ eink-display.service NOT installed"
fi
echo ""

if [ -f /etc/systemd/system/eink-api.service ]; then
    echo "✓ eink-api.service installed"
    sudo systemctl status eink-api.service --no-pager | head -n 3
else
    echo "✗ eink-api.service NOT installed"
fi
echo ""

# Check project files
echo "Checking project files..."
echo ""

if [ -f /home/pi/einkpetclock/.env ]; then
    echo "✓ .env file exists"
else
    echo "✗ .env file NOT found (copy from .env.example)"
fi

if [ -d /home/pi/einkpetclock/venv ]; then
    echo "✓ Virtual environment exists"
else
    echo "✗ Virtual environment NOT created"
fi

if [ -d /home/pi/einkpetclock/data ]; then
    echo "✓ Data directory exists"
else
    echo "✗ Data directory NOT created"
fi
echo ""

# Check GPIO
echo "Checking GPIO access..."
if groups | grep -q gpio; then
    echo "✓ User is in gpio group"
else
    echo "✗ User NOT in gpio group (run: sudo usermod -a -G gpio $USER)"
fi
echo ""

# Network check
echo "Network Information:"
echo "Hostname: $(hostname)"
echo "IP addresses:"
ip -4 addr show | grep inet | awk '{print "  " $2}'
echo ""

# ZeroTier check
if command -v zerotier-cli &> /dev/null; then
    echo "ZeroTier status:"
    sudo zerotier-cli listnetworks 2>/dev/null | head -n 5
else
    echo "✗ ZeroTier NOT installed"
fi
echo ""

echo "========================================="
echo "Recommendations:"
echo "========================================="

if python3 --version 2>&1 | grep -q "3.1[1-9]"; then
    echo "✓ Python 3.11+ detected"
    echo "  → Use: bash scripts/install_minimal.sh"
else
    echo "✓ Older Python detected"
    echo "  → Use: bash scripts/install.sh"
fi
echo ""
