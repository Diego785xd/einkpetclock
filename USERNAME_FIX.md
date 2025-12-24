# Username Fix Applied ✅

## What Was Fixed

The scripts were hardcoded to use `/home/pi/` but your username is `dai`.

### Updated Files:

1. **`scripts/install_simple.sh`** - Now auto-detects project directory
2. **`systemd/eink-display.service`** - Uses `%u` and `%h` (systemd variables)
3. **`systemd/eink-api.service`** - Uses `%u` and `%h` (systemd variables)
4. **`scripts/deploy.sh`** - Uses `$HOME` on remote system
5. **`scripts/test_api.sh`** - Better JSON formatting fallback

## How to Use Now

### From Pi (as user `dai`):
```bash
cd ~/einkpetclock
bash scripts/install_simple.sh
```

The script will:
- Auto-detect your username (`dai`)
- Use your home directory (`/home/dai/`)
- Install services for your user

### From Mac:
```bash
# Deploy to dai@10.8.17.62
bash scripts/deploy.sh 10.8.17.62 dai

# Or let it auto-detect (uses your Mac username)
bash scripts/deploy.sh 10.8.17.62
```

### Systemd Variables Used:
- `%u` = Username (will be `dai`)
- `%h` = Home directory (will be `/home/dai`)

## Try Again

Your install should now work:

```bash
cd /home/dai/einkpetclock
bash scripts/install_simple.sh
```

✅ No more hardcoded paths!
