#!/bin/bash
# Complete test of the eink pet clock system
# Run this AFTER install_fixed.sh

echo "=== E-Ink Pet Clock System Test ==="
echo ""

# Set up environment
export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
PROJECT_DIR="$HOME/einkpetclock"
cd "$PROJECT_DIR"

echo "Project: $PROJECT_DIR"
echo "PYTHONPATH: $PYTHONPATH"
echo ""

# Test 1: Import all core modules
echo "=== Test 1: Core Module Imports ==="
python3 << 'PYEOF'
try:
    from core.config import Config
    print("✓ core.config")
    
    from core.state import PetState, MessageLog, UserSettings, Stats
    print("✓ core.state")
    
    from core.button_handler import ButtonHandler
    print("✓ core.button_handler")
    
    from core.display import DisplayManager
    print("✓ core.display")
    
    from core.menu_system import MenuStateMachine
    print("✓ core.menu_system")
    
    from core.display_manager import DisplayManager as DM
    print("✓ core.display_manager")
    
    print("\n✓ All core modules imported successfully!")
except Exception as e:
    print(f"\n✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo "✗ Core module test FAILED"
    exit 1
fi

echo ""

# Test 2: Check .env configuration
echo "=== Test 2: Configuration ==="
python3 << 'PYEOF'
from core.config import Config
import os

config = Config()
print(f"Device Name: {config.DEVICE_NAME}")
print(f"Device IP: {config.DEVICE_IP}")
print(f"Remote IP: {config.REMOTE_DEVICE_IP}")
print(f"Timezone: {config.TIMEZONE}")
print(f"Data Dir: {config.DATA_DIR}")
print(f"Button Pins: {config.BUTTON_LEFT}, {config.BUTTON_CENTER}, {config.BUTTON_RIGHT}")

# Check if .env exists
if os.path.exists('.env'):
    print("\n✓ .env file exists")
else:
    print("\n⚠ .env file not found - using defaults")
PYEOF

echo ""

# Test 3: State management
echo "=== Test 3: State Management ==="
python3 << 'PYEOF'
from core.state import PetState
from core.config import Config

config = Config()
pet = PetState(config.DATA_DIR)

# Create/load state
if pet.data:
    print(f"✓ Pet state loaded: {pet.data['name']}")
    print(f"  Hunger: {pet.data['hunger']}")
    print(f"  Happiness: {pet.data['happiness']}")
    print(f"  Health: {pet.data['health']}")
else:
    print("✓ Pet state initialized (new)")
PYEOF

echo ""

# Test 4: Display (mock mode OK if not root)
echo "=== Test 4: Display Manager ==="
python3 << 'PYEOF'
from core.display import DisplayManager
from core.config import Config

config = Config()
try:
    display = DisplayManager(config)
    print("✓ DisplayManager created")
    
    # Try to initialize (will use mock if not root/no GPIO)
    display.init()
    print("✓ Display initialized (may be mock)")
    
except Exception as e:
    print(f"⚠ Display error (expected if not root): {e}")
PYEOF

echo ""

# Test 5: Web API imports
echo "=== Test 5: Web API ==="
python3 << 'PYEOF'
try:
    from web.api import app
    print("✓ FastAPI app imported")
    
    from web.network_client import send_message
    print("✓ Network client imported")
    
except Exception as e:
    print(f"✗ API import failed: {e}")
    print("Make sure venv is created and packages installed")
    exit(1)
PYEOF

echo ""

# Test 6: Check service files
echo "=== Test 6: Service Files ==="
if [ -f "/etc/systemd/system/eink-display.service" ]; then
    echo "✓ eink-display.service installed"
else
    echo "⚠ eink-display.service not installed"
fi

if [ -f "/etc/systemd/system/eink-api.service" ]; then
    echo "✓ eink-api.service installed"
else
    echo "⚠ eink-api.service not installed"
fi

echo ""

# Test 7: Check if services are running
echo "=== Test 7: Service Status ==="
systemctl is-active eink-display >/dev/null 2>&1 && echo "✓ eink-display is running" || echo "⚠ eink-display is not running"
systemctl is-active eink-api >/dev/null 2>&1 && echo "✓ eink-api is running" || echo "⚠ eink-api is not running"

echo ""
echo "=== Test Complete ==="
echo ""
echo "If all tests passed, you can start the services with:"
echo "  sudo systemctl start eink-display"
echo "  sudo systemctl start eink-api"
echo ""
echo "To make them start on boot:"
echo "  sudo systemctl enable eink-display"
echo "  sudo systemctl enable eink-api"
