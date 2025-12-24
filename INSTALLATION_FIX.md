# FIXED INSTALLATION GUIDE

## THE PROBLEM

The code wasn't working because:
1. **Waveshare library path issue**: The Waveshare e-Paper library at `/home/dai/dev/e-Paper` was not in Python's sys.path
2. **Missing system packages**: python3-dotenv, python3-tz, etc. were not installed
3. **Old installation script**: Previous scripts didn't handle the library path correctly

## THE SOLUTION

Created `install_fixed.sh` which:
- ✓ Finds the Waveshare library at `/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib`
- ✓ Adds `PYTHONPATH` environment variable to systemd services
- ✓ Installs missing system packages
- ✓ Creates venv for API with FastAPI
- ✓ Tests all imports before completing

## INSTALLATION STEPS

SSH into your Pi and run:

```bash
cd ~/einkpetclock
bash scripts/install_fixed.sh
```

The script will:
1. Check for Waveshare library (must exist at `/home/dai/dev/e-Paper`)
2. Install any missing system packages (dotenv, pytz, PIL, RPi.GPIO)
3. Create virtual environment for API
4. Configure systemd services with correct PYTHONPATH
5. Test all imports

## AFTER INSTALLATION

1. **Edit your .env file** (it was created from .env.example):
   ```bash
   nano ~/einkpetclock/.env
   ```
   
   Set:
   - `DEVICE_NAME=bunny`
   - `DEVICE_IP=10.8.17.62`
   - `REMOTE_DEVICE_IP=10.8.17.114`
   - `TIMEZONE=America/Mexico_City`

2. **Test the system**:
   ```bash
   cd ~/einkpetclock
   bash scripts/test_system.sh
   ```
   
   This will verify all modules can be imported and everything works.

3. **Start the services**:
   ```bash
   sudo systemctl enable eink-display
   sudo systemctl enable eink-api
   sudo systemctl start eink-display
   sudo systemctl start eink-api
   ```

4. **Check status**:
   ```bash
   sudo systemctl status eink-display
   sudo systemctl status eink-api
   ```

5. **View live logs**:
   ```bash
   # Display service logs
   sudo journalctl -u eink-display -f
   
   # API service logs
   sudo journalctl -u eink-api -f
   ```

## TESTING THE API

From your Mac:

```bash
# Test API is responding
curl http://10.8.17.62:5000/api/status

# Send a message
curl -X POST http://10.8.17.62:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello bunny!", "from":"rossi"}'

# Poke the pet
curl -X POST http://10.8.17.62:5000/api/poke

# Feed the pet
curl -X POST http://10.8.17.62:5000/api/feed
```

## TROUBLESHOOTING

### Import Errors

If you get `ModuleNotFoundError: No module named 'waveshare_epd'`:
- Make sure `/home/dai/dev/e-Paper` exists
- Check the PYTHONPATH in service files has the correct path
- Try manually: `export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib" && python3 -c "from waveshare_epd import epd2in13_V4"`

### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u eink-display -n 50 --no-pager

# Check if service file is correct
cat /etc/systemd/system/eink-display.service | grep PYTHONPATH

# Reload daemon if you changed service files
sudo systemctl daemon-reload
```

### Display Not Updating

1. Check GPIO permissions: The service runs as user `dai`
2. Check button connections: GPIO 6, 13, 19
3. Test display manually:
   ```bash
   cd ~/einkpetclock/hardware
   python3 example.py
   ```

### API Not Responding

1. Check if it's running: `sudo systemctl status eink-api`
2. Check port is open: `sudo netstat -tulpn | grep 5000`
3. Check venv has packages: `~/einkpetclock/venv/bin/pip list`

## WHAT WAS FIXED

### Old install_simple.sh had:
- ❌ Tried to install `waveshare-epd` via pip (fails with PEP 668)
- ❌ Didn't set PYTHONPATH for the existing library
- ❌ Had corrupted content with duplicate code
- ❌ Used %u/%h variables that weren't being replaced

### New install_fixed.sh has:
- ✅ Uses existing Waveshare library with PYTHONPATH
- ✅ Installs only system packages (python3-dotenv, python3-tz, etc.)
- ✅ Sets PYTHONPATH in systemd service files
- ✅ Auto-detects user and home directory
- ✅ Tests all imports before completing
- ✅ Clean, working code

## NEXT STEPS AFTER IT WORKS

1. **Add custom bunny sprites**: Place PNG images in `assets/sprites/`
2. **Test network communication**: Send messages from Mac to Pi
3. **Customize menus**: Edit `core/menu_system.py` to change what's displayed
4. **Adjust pet mechanics**: Edit `core/state.py` to tune hunger/happiness decay rates

Let me know when you've run the installation and tests!
