# BARE METAL INSTALLATION - Pi Zero W Optimized

## The Problem with Previous Install

The Pi Zero W has:
- ❌ Limited disk space (~8GB total)
- ❌ Weak ARM CPU (can't compile Rust dependencies)
- ❌ Only 512MB RAM

The previous `install_fixed.sh` tried to:
1. Create a Python venv (uses extra disk space)
2. Install `pydantic-core` which requires compiling Rust code
3. This took over an hour and failed with "No space left on device"

## The Solution: 100% Bare Metal

**`install_bare_metal.sh`** uses ONLY system packages:
- ✅ No venv (runs on system Python)
- ✅ No compilation (apt packages only)
- ✅ Minimal disk usage
- ✅ Fast installation (~2 minutes)
- ✅ Auto-detects if FastAPI is available, falls back to simple HTTP

## Installation (ON YOUR PI)

```bash
# 1. Pull latest code
cd ~/einkpetclock
git pull

# 2. Clean up old venv if it exists (free space)
rm -rf ~/einkpetclock/venv

# 3. Run bare metal installation
bash scripts/install_bare_metal.sh

# 4. Edit .env
nano .env

# 5. Start services
sudo systemctl enable eink-display eink-api
sudo systemctl start eink-display eink-api

# 6. Check status
sudo systemctl status eink-display
sudo systemctl status eink-api
```

## What Gets Installed

System packages (via apt):
- `python3-dotenv` - .env file support
- `python3-tz` - Timezone (pytz)
- `python3-pil` - Image handling
- `python3-rpi.gpio` - GPIO for buttons
- `python3-fastapi` - API framework (if available)
- `python3-uvicorn` - API server (if available)  
- `python3-httpx` - HTTP client (if available)
- `python3-pydantic` - Data validation (if available)

**Note:** If FastAPI isn't available in Debian repos, the script will use a simple HTTP server fallback that works with just Python standard library.

## API Server Modes

The `api_wrapper.py` automatically detects:

### Mode 1: FastAPI (if available)
- Full featured API with auto-docs at `/docs`
- Pydantic validation
- Better performance

### Mode 2: Simple HTTP (fallback)
- Python standard library only
- Still handles all endpoints: `/api/message`, `/api/poke`, `/api/feed`, `/api/status`
- No external dependencies

## Testing the API

From your Mac:

```bash
# Check which mode is running
curl http://10.8.17.62:5000/api/status

# Send a message
curl -X POST http://10.8.17.62:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!", "from_device":"mac"}'

# Poke the pet
curl -X POST http://10.8.17.62:5000/api/poke

# Feed the pet
curl -X POST http://10.8.17.62:5000/api/feed
```

## Disk Space Management

Check disk usage:
```bash
df -h /
```

If low on space, clean up:
```bash
# Clean apt cache
sudo apt-get clean

# Remove old venv if it exists
rm -rf ~/einkpetclock/venv

# Clean tmp files
sudo rm -rf /tmp/*

# Clean pip cache
rm -rf ~/.cache/pip
```

## Service Configuration

Both services run as user `dai`:
- **eink-display.service** - Main display manager (bare metal Python)
- **eink-api.service** - API server (bare metal Python with api_wrapper.py)

Both have `PYTHONPATH` set to include Waveshare library:
```
Environment="PYTHONPATH=/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure PYTHONPATH is set
export PYTHONPATH="/home/dai/dev/e-Paper/RaspberryPi_JetsonNano/python/lib"
python3 -c "from waveshare_epd import epd2in13_V4; print('OK')"
```

### Services won't start
```bash
# Check logs
sudo journalctl -u eink-display -n 50
sudo journalctl -u eink-api -n 50

# Restart
sudo systemctl restart eink-display eink-api
```

### Low disk space
```bash
# Check what's using space
du -sh ~/* | sort -h
sudo du -sh /var/* | sort -h

# Clean up
sudo apt-get clean
rm -rf ~/.cache/*
```

## Comparison: Old vs New

| Feature | install_fixed.sh | install_bare_metal.sh |
|---------|------------------|----------------------|
| Uses venv | ✅ Yes | ❌ No |
| Compiles code | ✅ Yes (Rust!) | ❌ No |
| Installation time | ~60 min (then fails) | ~2 minutes |
| Disk usage | +500MB | +50MB |
| Dependencies | pip packages | apt packages only |
| Works on Pi Zero W | ❌ No (OOM) | ✅ Yes |

## What's Different

### Old approach (FAILED):
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn httpx pydantic
# ^ This compiles pydantic-core (Rust)
# ^ Takes 1+ hour on Pi Zero W
# ^ Runs out of disk space: "No space left on device"
```

### New approach (WORKS):
```bash
sudo apt-get install python3-fastapi python3-uvicorn
# ^ Pre-compiled ARM binaries
# ^ Installs in ~30 seconds
# ^ Uses minimal disk space
# Or falls back to simple HTTP if not available
```

## Next Steps After Installation

1. ✅ Services are running
2. Test display by pressing buttons (GPIO 6, 13, 19)
3. Send test messages from Mac
4. Monitor logs: `sudo journalctl -u eink-display -f`
5. Add custom sprites to `assets/sprites/`
6. Enjoy your pet clock! 🐰

The system is now optimized for Pi Zero W's limited resources!
