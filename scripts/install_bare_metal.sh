#!/bin/bash
# Lightweight installation for Pi Zero W - ALL BARE METAL, NO VENV
# No compilation, uses only system packages

set -e

echo "=== E-Ink Pet Clock Installation (Bare Metal - Lightweight) ==="

# Auto-detect project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo "Project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Check for Waveshare e-Paper library
WAVESHARE_LIB="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"
if [ ! -d "$WAVESHARE_LIB" ]; then
    echo "ERROR: Waveshare e-Paper library not found at $WAVESHARE_LIB"
    echo "Please clone the Waveshare e-Paper repository first:"
    echo "  cd ~/dev"
    echo "  git clone https://github.com/waveshare/e-Paper.git"
    exit 1
fi

echo "✓ Found Waveshare library at $WAVESHARE_LIB"

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "✓ Python version: $PYTHON_VERSION"

# Check disk space
echo ""
echo "=== Checking Disk Space ==="
df -h / | tail -1
FREE_KB=$(df / | tail -1 | awk '{print $4}')
if [ "$FREE_KB" -lt 500000 ]; then
    echo "⚠  WARNING: Low disk space! You have less than 500MB free."
    echo "   Consider cleaning up /tmp or other directories"
fi

echo ""
echo "=== Installing System Packages (No Compilation) ==="

# List of required system packages
PACKAGES=(
    "python3-dotenv"      # For .env file support
    "python3-tz"          # For timezone support (pytz)
    "python3-pil"         # For image handling
    "python3-rpi.gpio"    # For GPIO button handling
    "python3-fastapi"     # For API (if available)
    "python3-uvicorn"     # For API server (if available)
    "python3-httpx"       # For HTTP client (if available)
    "python3-pydantic"    # For data validation (if available)
)

echo "Updating package list..."
sudo apt-get update

MISSING_PACKAGES=()
UNAVAILABLE_PACKAGES=()

for pkg in "${PACKAGES[@]}"; do
    echo -n "Checking $pkg... "
    if dpkg -l | grep -q "^ii  $pkg "; then
        echo "✓ already installed"
    elif apt-cache show "$pkg" >/dev/null 2>&1; then
        echo "will install"
        MISSING_PACKAGES+=("$pkg")
    else
        echo "⚠ not available in repos"
        UNAVAILABLE_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "Installing: ${MISSING_PACKAGES[@]}"
    sudo apt-get install -y "${MISSING_PACKAGES[@]}"
else
    echo ""
    echo "✓ All available packages are already installed"
fi

# Handle unavailable packages
if [ ${#UNAVAILABLE_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "⚠  The following packages are not available as system packages:"
    for pkg in "${UNAVAILABLE_PACKAGES[@]}"; do
        echo "   - $pkg"
    done
    echo ""
    echo "We'll use a minimal fallback API or skip the web API."
fi

# Test imports
echo ""
echo "=== Testing Required Imports ==="

export PYTHONPATH="$WAVESHARE_LIB:$PYTHONPATH"

# Test core dependencies (must have)
python3 << 'PYEOF'
import sys
errors = []

try:
    import dotenv
    print("✓ dotenv")
except ImportError:
    print("✗ dotenv (REQUIRED)")
    errors.append("dotenv")

try:
    import pytz
    print("✓ pytz")
except ImportError:
    print("✗ pytz (REQUIRED)")
    errors.append("pytz")

try:
    from PIL import Image
    print("✓ PIL")
except ImportError:
    print("✗ PIL (REQUIRED)")
    errors.append("PIL")

try:
    import RPi.GPIO
    print("✓ RPi.GPIO")
except ImportError:
    print("✗ RPi.GPIO (REQUIRED)")
    errors.append("RPi.GPIO")

try:
    from waveshare_epd import epd2in13_V4
    print("✓ waveshare_epd")
except ImportError:
    print("✗ waveshare_epd (REQUIRED)")
    errors.append("waveshare_epd")

# Test optional API dependencies
try:
    import fastapi
    print("✓ fastapi (optional)")
except ImportError:
    print("⚠ fastapi (optional - API will not work)")

try:
    import uvicorn
    print("✓ uvicorn (optional)")
except ImportError:
    print("⚠ uvicorn (optional - API will not work)")

try:
    import httpx
    print("✓ httpx (optional)")
except ImportError:
    print("⚠ httpx (optional - network client will not work)")

if errors:
    print(f"\n✗ FATAL: Missing required dependencies: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All required dependencies available")
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Dependency check failed. Please install missing packages."
    exit 1
fi

# Create data directories
echo ""
echo "=== Creating Data Directories ==="
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "/tmp/eink_flags"
echo "✓ Directories created"

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "=== Creating .env File ==="
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "✓ Created .env from .env.example"
    echo "⚠  Please edit .env with your settings!"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Get actual username and home directory
ACTUAL_USER=$(whoami)
ACTUAL_HOME="$HOME"

echo ""
echo "=== Configuring Systemd Services (Bare Metal) ==="
echo "User: $ACTUAL_USER"
echo "Home: $ACTUAL_HOME"

# Create display service (BARE METAL - no venv)
cat > "$PROJECT_DIR/systemd/eink-display.service" << EOF
[Unit]
Description=E-Ink Display Manager (Bare Metal)
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$WAVESHARE_LIB"
ExecStart=/usr/bin/python3 -m core.display_manager
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create API service using wrapper (auto-detects FastAPI vs simple HTTP)
echo "Creating API service with auto-detection wrapper"

cat > "$PROJECT_DIR/systemd/eink-api.service" << EOF
[Unit]
Description=E-Ink Pet Clock API (Bare Metal - Auto-detect)
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$WAVESHARE_LIB"
ExecStart=/usr/bin/python3 $PROJECT_DIR/web/api_wrapper.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ API service configured (will use FastAPI if available, otherwise simple HTTP)"

echo "✓ Service files configured"

# Install services
echo ""
echo "=== Installing Systemd Services ==="
sudo cp "$PROJECT_DIR/systemd/eink-display.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/systemd/eink-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
echo "✓ Services installed"

# Test core module imports
echo ""
echo "=== Testing Core Module Imports ==="
export PYTHONPATH="$WAVESHARE_LIB:$PYTHONPATH"

python3 << 'PYEOF'
import sys
try:
    from core.config import Config
    print("✓ core.config")
    
    from core.state import PetState
    print("✓ core.state")
    
    from core.display import DisplayManager
    print("✓ core.display")
    
    from core.button_handler import ButtonHandler
    print("✓ core.button_handler")
    
    from core.menu_system import MenuStateMachine
    print("✓ core.menu_system")
    
    from core.display_manager import DisplayManager as DM
    print("✓ core.display_manager")
    
    print("\n✓ All core modules imported successfully!")
except Exception as e:
    print(f"\n✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "✗ Module import test failed"
    exit 1
fi

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Configuration:"
echo "  - All services run BARE METAL (no venv, no compilation)"
echo "  - Display service: systemd managed Python process"
echo "  - API service: Auto-detect (FastAPI or simple HTTP)"
echo "  - Waveshare library: $WAVESHARE_LIB"
echo "  - All packages: System-installed (apt)
echo ""
echo "Disk usage after installation:"
df -h / | tail -1
echo ""
echo "Next steps:"
echo "1. Edit .env file:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Start services:"
echo "   sudo systemctl enable eink-display eink-api"
echo "   sudo systemctl start eink-display eink-api"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status eink-display"
echo "   sudo systemctl status eink-api"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u eink-display -f"
echo "   sudo journalctl -u eink-api -f"
