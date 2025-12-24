#!/bin/bash
# Debug script to check all imports and paths

echo "=== Python Version ==="
python3 --version

echo -e "\n=== Checking Required Packages ==="
echo -n "dotenv: "
python3 -c 'import dotenv; print("OK")' 2>&1 || echo "MISSING"

echo -n "pytz: "
python3 -c 'import pytz; print("OK")' 2>&1 || echo "MISSING"

echo -n "PIL: "
python3 -c 'from PIL import Image; print("OK")' 2>&1 || echo "MISSING"

echo -n "RPi.GPIO: "
python3 -c 'import RPi.GPIO; print("OK")' 2>&1 || echo "MISSING"

echo -e "\n=== Checking Waveshare EPD ==="
echo "Without path modification:"
python3 -c 'from waveshare_epd import epd2in13_V4; print("OK")' 2>&1 || echo "MISSING"

echo "With e-Paper lib path:"
python3 -c 'import sys; sys.path.insert(0, "/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"); from waveshare_epd import epd2in13_V4; print("OK")'

echo -e "\n=== e-Paper Directory Check ==="
if [ -d "/home/dai/dev/e-Paper" ]; then
    echo "e-Paper directory exists"
    ls -la /home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/ | head -5
else
    echo "e-Paper directory NOT FOUND"
fi

echo -e "\n=== Trying to import core modules ==="
cd ~/einkpetclock
export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"

echo "Testing core.config import:"
python3 -c 'from core.config import Config; print("OK")' 2>&1 || echo "FAILED"

echo "Testing core.display import:"
python3 -c 'from core.display import DisplayManager; print("OK")' 2>&1 || echo "FAILED"
