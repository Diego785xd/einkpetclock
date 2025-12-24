# Installation Scripts

## Choose Your Installation Method

### Option 1: install_minimal.sh (Recommended for newer Pi OS) ⭐

Use this if you have **Raspberry Pi OS Bookworm (2023+)** or newer with Python 3.11+

```bash
bash scripts/install_minimal.sh
```

**Advantages:**
- Uses system packages (respects PEP 668)
- Cleaner installation
- No `--break-system-packages` warnings
- Faster installation

**Requirements:**
- Debian packages: python3-dotenv, python3-tz already available
- Only installs Waveshare library with sudo pip

---

### Option 2: install.sh (Legacy/Older systems)

Use this if you have **older Raspberry Pi OS** with Python < 3.11

```bash
bash scripts/install.sh
```

**Advantages:**
- Works on older systems
- More compatible with legacy setups

**Note:** May show PEP 668 warnings on newer systems (safe to ignore)

---

## Which One Should You Use?

Run this command on your Pi to check:

```bash
python3 --version
```

- **Python 3.11 or newer** → Use `install_minimal.sh` ✅
- **Python 3.9 or older** → Use `install.sh`

Based on your error message showing Python 3.13.5, you should use:

```bash
bash scripts/install_minimal.sh
```

---

## After Installation

Both scripts do the same thing:
1. Install system dependencies
2. Create virtual environment for API
3. Configure systemd services
4. Set up directories
5. Prompt for .env configuration

The only difference is HOW they install Python packages.
