# Custom Bunny Sprites Integration

## Overview
Successfully integrated custom 32x32 pixel bunny sprite animations from colored sprite sheets into the e-ink pet clock display.

## Files Created/Modified

### 1. Sprite Conversion Script
**File:** `scripts/convert_bunny_sprites.sh`
- Extracts individual frames from sprite sheets
- Converts colored sprites to format suitable for e-ink display
- Processes 8 different animations (Idle, Sleep, Hurt, Sitting, Dead, LieDown, Run, Attack)
- Creates mood-based sprite files (neutral, sleeping, sick, happy, sad, dead, excited, angry)

### 2. Updated Menu System
**File:** `core/menu_system.py`
- Added PIL Image import and SPRITES_DIR path
- Modified `TamagotchiMenu.render()` to load and display sprites
- Maps pet moods to specific sprite files:
  - `happy` → happy.png (BunnySitting)
  - `neutral` → neutral.png (BunnyIdle)
  - `sad` → sad.png (BunnyLieDown)
  - `hungry` → excited.png (BunnyRun)
  - `sick` → sick.png (BunnyHurt)
  - `sleeping` → sleeping.png (BunnySleep)
  - `dead` → dead.png (BunnyDead)
- Fallback to ASCII art if sprites not found

### 3. Deployment Script
**File:** `scripts/deploy_sprites.sh`
- Syncs sprites directory to Pi via rsync
- Updates menu_system.py
- Restarts display service
- Provides status check commands

### 4. Assets Structure
```
assets/
├── bunny_source/          # Original colored sprite sheets (PNG)
│   ├── BunnyIdle-Sheet.png (256x32 = 8 frames)
│   ├── BunnySleep-Sheet.png (64x32 = 2 frames)
│   ├── BunnyHurt-Sheet.png (96x32 = 3 frames)
│   ├── BunnySitting-Sheet.png (96x32 = 3 frames)
│   ├── BunnyDead-Sheet.png (288x32 = 9 frames)
│   ├── BunnyLieDown-Sheet.png (64x32 = 2 frames)
│   ├── BunnyRun-Sheet.png (160x32 = 5 frames)
│   └── BunnyAttack-Sheet.png (224x32 = 7 frames)
│
└── sprites/               # Converted B&W sprites (32x32 PNG)
    ├── neutral.png        # Main mood sprites
    ├── sleeping.png
    ├── sick.png
    ├── happy.png
    ├── sad.png
    ├── dead.png
    ├── excited.png
    ├── angry.png
    ├── BunnyIdle_frame00.png    # Individual animation frames
    ├── BunnyIdle_frame01.png    # (if you want to add animations later)
    └── ... (39 total frame files)
```

## Sprite Sheet Details
All sprites are 32 pixels tall, arranged horizontally:

| Animation | Dimensions | Frames | Mood Mapping |
|-----------|-----------|--------|--------------|
| BunnyIdle | 256x32 | 8 | neutral |
| BunnySleep | 64x32 | 2 | sleeping |
| BunnyHurt | 96x32 | 3 | sick |
| BunnySitting | 96x32 | 3 | happy |
| BunnyDead | 288x32 | 9 | dead |
| BunnyLieDown | 64x32 | 2 | sad |
| BunnyRun | 160x32 | 5 | excited/hungry |
| BunnyAttack | 224x32 | 7 | angry |

## Display Positioning
- Display size: 250x122 pixels
- Sprite size: 32x32 pixels
- Position: Centered horizontally (x=109), below date line (y=60)

## How to Deploy

### 1. Convert Sprites (already done)
```bash
cd /Users/rossi/dev/einkpetclock
./scripts/convert_bunny_sprites.sh
```

### 2. Deploy to Pi
```bash
./scripts/deploy_sprites.sh
```

### 3. Check Status
```bash
ssh rossi@10.8.17.62 'sudo systemctl status eink-display.service'
```

### 4. View Live Logs
```bash
ssh rossi@10.8.17.62 'sudo journalctl -u eink-display.service -f'
```

## Dependencies on Pi
- python3-pil (already installed via install_bare_metal.sh)
- PIL/Pillow can load PNG images
- E-ink display supports pasting images onto canvas

## Future Enhancements
If you want to add animations later:
1. Load frame sequences instead of single sprites
2. Cycle through frames on each display refresh
3. Create an `Animation` class to manage frame timing
4. Map specific animations to actions (e.g., show BunnyAttack frames when feeding)

## Troubleshooting

### Sprites not showing
- Check sprites exist: `ls -la /home/rossi/einkpetclock/assets/sprites/`
- Check PIL import works: `python3 -c "from PIL import Image; print('OK')"`
- Check file permissions: `chmod 644 assets/sprites/*.png`

### Display shows ASCII art instead
- Sprites directory might not exist on Pi
- Sprite files might not have been copied
- Check logs for error messages

### Black/white conversion issues
- Adjust threshold in conversion script (currently using default)
- Some sprites might need manual editing for better contrast
- sips command parameters can be tuned for better results

## Notes
- Sprites are converted using macOS `sips` command (built-in)
- Original colored sprite sheets preserved in `assets/bunny_source/`
- Individual animation frames available if you want to implement animations
- Current implementation shows static first frame for each mood
