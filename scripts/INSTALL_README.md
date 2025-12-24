# Installation Scripts

## Choose Your Installation Method

### Option 1: install_simple.sh (RECOMMENDED) ⭐⭐⭐

**Use this if your display hardware already works** (you can run `hardware/example.py`)

```bash
bash scripts/install_simple.sh
```

**Advantages:**
- ✅ Doesn't touch working hardware setup
- ✅ Only installs what's needed (dotenv, pytz)
- ✅ Fast and safe
- ✅ No package conflicts

**This is the best option if:**
- You already tested `hardware/example.py` successfully
- Waveshare library is already working
- You just want to set up the pet clock services

---

### Option 2: install_minimal.sh (Full install for newer Pi OS)

Use this if you need to install everything from scratch on newer systems

```bash
bash scripts/install_minimal.sh
```

**Advantages:**
- Uses system packages (respects PEP 668)
- Installs Waveshare library
- Complete setup

**Requirements:**
- Python 3.11+
- Fresh system or willing to install all dependencies

---

### Option 3: install.sh (Legacy/Older systems)

Use this if you have **older Raspberry Pi OS** with Python < 3.11

```bash
bash scripts/install.sh
```

**Note:** May show PEP 668 warnings on newer systems

---

## Which One Should You Use?

### ✅ If hardware/example.py already works:
```bash
bash scripts/install_simple.sh
```
**This is you!** Use this one. ⭐

### 🔧 If you're setting up from scratch:
```bash
python3 --version
```
- **Python 3.11+** → Use `install_minimal.sh`
- **Python 3.9 or older** → Use `install.sh`

---

## What Each Script Does

### install_simple.sh
1. ✅ Checks if Waveshare library works (doesn't reinstall)
2. ✅ Installs only: python3-dotenv, python3-tz
3. ✅ Creates venv for API
4. ✅ Sets up systemd services
5. ✅ Creates .env from template

### install_minimal.sh
1. Installs all system packages
2. Installs Waveshare library (pip with --break-system-packages)
3. Creates venv for API
4. Sets up systemd services
5. Creates .env from template

### install.sh
1. Installs all system packages (legacy method)
2. Installs Waveshare library (pip)
3. Installs Python packages (user space)
4. Creates venv for API
5. Sets up systemd services
6. Creates .env from template
