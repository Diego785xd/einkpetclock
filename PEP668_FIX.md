# Quick Fix for PEP 668 Error

You encountered this error because your Pi has Python 3.13.5, which enforces PEP 668 (externally managed environment).

## ✅ Solution: Use the New Install Script

I've created `install_minimal.sh` which properly handles this:

```bash
cd ~/einkpetclock
bash scripts/install_minimal.sh
```

This script:
- Uses system packages (python3-dotenv, python3-tz) instead of pip
- Only installs Waveshare library system-wide (safe with `--break-system-packages`)
- Creates a venv for the API service (isolated)
- No more PEP 668 warnings!

## What Changed?

### Old install.sh (caused error):
```bash
sudo pip3 install waveshare-epd          # ❌ Blocked by PEP 668
pip3 install --user python-dotenv pytz  # ❌ Also problematic
```

### New install_minimal.sh (works):
```bash
sudo apt-get install python3-dotenv python3-tz  # ✅ System packages
sudo pip3 install --break-system-packages waveshare-epd  # ✅ Safe exception
python3 -m venv venv                    # ✅ API uses venv
```

## Why This Is Better

1. **Respects PEP 668** - Uses system packages when available
2. **Cleaner** - No mixing pip with system packages
3. **Safer** - Won't break OS Python
4. **Faster** - System packages are precompiled

## Already Installed Packages?

Good news! You already have:
- ✅ python3-rpi.gpio (the script installed this)
- ✅ python3-pil (already installed)
- ✅ All base system packages

You just need to finish the installation with `install_minimal.sh`.

## Continue Your Installation

```bash
# You're at this state:
# - System packages: installed ✅
# - Waveshare library: NOT installed ❌
# - Venv for API: NOT created ❌
# - Services: NOT configured ❌

# Run the minimal installer:
bash scripts/install_minimal.sh

# It will:
# 1. Skip already-installed packages (fast!)
# 2. Install Waveshare library properly
# 3. Create venv for API
# 4. Set up systemd services
# 5. Prompt for .env configuration
```

## Alternative: Manual Steps

If you prefer to do it manually:

```bash
# 1. Install Waveshare library
sudo pip3 install --break-system-packages waveshare-epd

# 2. Install system Python packages
sudo apt-get install python3-dotenv python3-tz

# 3. Create venv for API
cd ~/einkpetclock
python3 -m venv venv
source venv/bin/activate
pip install -r web/requirements.txt
deactivate

# 4. Create .env
cp .env.example .env
nano .env  # Edit with your settings

# 5. Install services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable eink-display.service eink-api.service
sudo systemctl start eink-display.service eink-api.service
```

## Verify Installation

```bash
# Check system
bash scripts/check_system.sh

# Check services
sudo systemctl status eink-display.service
sudo systemctl status eink-api.service

# View logs
sudo journalctl -u eink-display.service -f
```

---

**TL;DR:** Run `bash scripts/install_minimal.sh` and you're good! 🎉
