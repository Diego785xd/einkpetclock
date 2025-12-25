#!/bin/bash
# Fix GPIO permissions for the eink-display service
# Run this script to allow user 'dai' to access GPIO

echo "=== Fixing GPIO Permissions ==="

# Check if gpio group exists
if getent group gpio > /dev/null 2>&1; then
    echo "✓ gpio group exists"
else
    echo "Creating gpio group..."
    sudo groupadd -f gpio
fi

# Add user to gpio group
USER=$(whoami)
echo "Adding $USER to gpio group..."
sudo usermod -a -G gpio $USER

# Set GPIO permissions via udev rules
echo "Creating udev rules for GPIO access..."
sudo tee /etc/udev/rules.d/99-gpio.rules > /dev/null << 'EOF'
# Allow members of gpio group to access GPIO
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio; chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 770 /sys/devices/virtual/gpio; chown -R root:gpio /sys$devpath && chmod -R 770 /sys$devpath'"
EOF

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Alternative: Run service as root (simpler but less secure)
echo ""
echo "=== GPIO Permission Options ==="
echo ""
echo "Option 1: User in gpio group (RECOMMENDED - more secure)"
echo "  - User '$USER' has been added to gpio group"
echo "  - You need to LOG OUT and LOG BACK IN for this to take effect"
echo "  - After re-login, check with: groups | grep gpio"
echo ""
echo "Option 2: Run service as root (QUICK FIX - less secure)"
echo "  - Edit /etc/systemd/system/eink-display.service"
echo "  - Change 'User=$USER' to 'User=root'"
echo "  - Run: sudo systemctl daemon-reload"
echo "  - Run: sudo systemctl restart eink-display"
echo ""
echo "Which option do you prefer?"
echo "  [1] Use gpio group (need to logout/login)"
echo "  [2] Run as root (works immediately)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "2" ]; then
    echo ""
    echo "Configuring service to run as root..."
    sudo sed -i "s/^User=.*/User=root/" /etc/systemd/system/eink-display.service
    sudo systemctl daemon-reload
    sudo systemctl restart eink-display
    echo "✓ Service reconfigured to run as root"
    echo ""
    echo "Check status:"
    echo "  sudo systemctl status eink-display"
else
    echo ""
    echo "✓ GPIO group configured"
    echo ""
    echo "IMPORTANT: You must LOG OUT and LOG BACK IN for gpio group membership to take effect!"
    echo ""
    echo "After re-login, verify with:"
    echo "  groups | grep gpio"
    echo ""
    echo "Then restart the service:"
    echo "  sudo systemctl restart eink-display"
fi
