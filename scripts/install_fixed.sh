#!/bin/bash
# Fixed installation script for eink pet clock
# Handles the Waveshare library path correctly

set -e

echo "=== E-Ink Pet Clock Installation (Fixed Version) ==="

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

# Check required system packages
echo ""
echo "=== Checking Required Python Packages ==="

check_package() {
    local pkg=$1
    local import_name=$2
    echo -n "Checking $pkg... "
    if python3 -c "import $import_name" 2>/dev/null; then
        echo "✓ installed"
        return 0
    else
        echo "✗ missing"
        return 1
    fi
}

MISSING_PACKAGES=()

check_package "python-dotenv" "dotenv" || MISSING_PACKAGES+=("python3-dotenv")
check_package "pytz" "pytz" || MISSING_PACKAGES+=("python3-tz")
check_package "PIL" "PIL" || MISSING_PACKAGES+=("python3-pil")
check_package "RPi.GPIO" "RPi.GPIO" || MISSING_PACKAGES+=("python3-rpi.gpio")

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "Installing missing packages: ${MISSING_PACKAGES[@]}"
    sudo apt-get update
    sudo apt-get install -y "${MISSING_PACKAGES[@]}"
else
    echo ""
    echo "✓ All required system packages are installed"
fi

# Test Waveshare import with correct path
echo ""
echo "=== Testing Waveshare EPD Import ==="
if python3 -c "import sys; sys.path.insert(0, '$WAVESHARE_LIB'); from waveshare_epd import epd2in13_V4; print('✓ Waveshare EPD import successful')" 2>/dev/null; then
    echo "✓ Waveshare library can be imported"
else
    echo "✗ ERROR: Cannot import Waveshare library even with correct path"
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

# Create Python path setup script
echo ""
echo "=== Creating Python Path Setup ==="
cat > "$PROJECT_DIR/setup_pythonpath.sh" << 'EOF'
#!/bin/bash
# Sets up PYTHONPATH for eink pet clock
export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
EOF
chmod +x "$PROJECT_DIR/setup_pythonpath.sh"
echo "✓ Created setup_pythonpath.sh"

# Create venv for API service
echo ""
echo "=== Creating Virtual Environment for API ==="
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv "$PROJECT_DIR/venv"
    echo "✓ Created virtual environment"
fi

# Install Python packages in venv
echo ""
echo "=== Installing API Dependencies in venv ==="
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install fastapi uvicorn httpx pydantic
deactivate
echo "✓ API dependencies installed"

# Update systemd service files
echo ""
echo "=== Configuring Systemd Services ==="

# Get actual username and home directory
ACTUAL_USER=$(whoami)
ACTUAL_HOME="$HOME"

echo "User: $ACTUAL_USER"
echo "Home: $ACTUAL_HOME"

# Create display service
cat > "$PROJECT_DIR/systemd/eink-display.service" << EOF
[Unit]
Description=E-Ink Display Manager
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"
ExecStart=/usr/bin/python3 -m core.display_manager
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create API service
cat > "$PROJECT_DIR/systemd/eink-api.service" << EOF
[Unit]
Description=E-Ink Pet Clock API
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn web.api:app --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service files configured with PYTHONPATH"

# Install services
echo ""
echo "=== Installing Systemd Services ==="
sudo cp "$PROJECT_DIR/systemd/eink-display.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/systemd/eink-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
echo "✓ Services installed"

echo ""
echo "=== Testing Core Module Imports ==="
export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"

if python3 -c "from core.config import Config; print('✓ core.config')"; then
    echo "✓ core.config import successful"
fi

if python3 -c "from core.display import DisplayManager; print('✓ core.display')"; then
    echo "✓ core.display import successful"
fi

if python3 -c "from core.state import PetState; print('✓ core.state')"; then
    echo "✓ core.state import successful"
fi

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your device settings:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Start the services:"
echo "   sudo systemctl enable eink-display"
echo "   sudo systemctl enable eink-api"
echo "   sudo systemctl start eink-display"
echo "   sudo systemctl start eink-api"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status eink-display"
echo "   sudo systemctl status eink-api"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u eink-display -f"
echo "   sudo journalctl -u eink-api -f"
echo ""
echo "Note: The PYTHONPATH for Waveshare library is automatically configured in the service files."
