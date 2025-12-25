# Next Steps: Deploy Bunny Sprites

## What We Just Built

✅ **Sprite Conversion**: Converted 8 different bunny animations from colored sprite sheets to black & white 32x32 PNG files
✅ **Menu Update**: Modified `menu_system.py` to load and display sprites based on pet mood
✅ **Deployment Script**: Created automated deployment script for easy updates

## Files Ready to Deploy

### Sprites (47 files total)
- 8 main mood sprites: `neutral.png`, `sleeping.png`, `sick.png`, `happy.png`, `sad.png`, `dead.png`, `excited.png`, `angry.png`
- 39 individual animation frames (for future animation features)

### Code Changes
- `core/menu_system.py` - Updated to use sprites instead of ASCII art

## Deploy to Pi

### Quick Deploy
```bash
cd /Users/rossi/dev/einkpetclock
./scripts/deploy_sprites.sh
```

This will:
1. Sync all sprite files to Pi
2. Update menu_system.py with sprite rendering code
3. Restart the display service
4. Show status confirmation

### Manual Steps (if needed)

1. **Copy sprites to Pi:**
   ```bash
   rsync -avz assets/sprites/ rossi@10.8.17.62:/home/rossi/einkpetclock/assets/sprites/
   ```

2. **Copy updated menu_system.py:**
   ```bash
   rsync -avz core/menu_system.py rossi@10.8.17.62:/home/rossi/einkpetclock/core/
   ```

3. **Restart service:**
   ```bash
   ssh rossi@10.8.17.62 'sudo systemctl restart eink-display.service'
   ```

## Verify Deployment

### Check Service Status
```bash
ssh rossi@10.8.17.62 'sudo systemctl status eink-display.service'
```

Should show: `Active: active (running)`

### Watch Live Logs
```bash
ssh rossi@10.8.17.62 'sudo journalctl -u eink-display.service -f'
```

Look for any errors about missing sprites or PIL import issues.

### Check Sprites on Pi
```bash
ssh rossi@10.8.17.62 'ls -la /home/rossi/einkpetclock/assets/sprites/ | head -15'
```

Should see 47 PNG files.

## Expected Result

The e-ink display should now show:
- **Date** in top left corner (medium - 16pt)
- **Time** in GIANT letters on the left side (64pt - same height as bunny!)
- **64x64 bunny sprite** on the right side, aligned with time (DOUBLE SIZE)
- **Status bar** at bottom with pet stats (health, hunger, mood, messages)
- **Button hints** at very bottom
- Time and bunny are now the SAME HEIGHT (64 pixels) for perfect visual balance!
- Sprite changes based on pet mood:
  - Happy bunny when well-fed
  - Sleeping bunny at night
  - Sad bunny when neglected
  - Sick bunny when health is low
  - Excited/running bunny when hungry
  - Dead bunny if health reaches zero

### Layout Visual
```
┌────────────────────────────────────┐
│ Tue, Dec 24                      ! │
│                                    │
│  ██ ███ ██ ███       [BUNNY 64x64]│ ← Both 64px tall!
│  ███ ███ ██  ██                   │
├────────────────────────────────────┤
│ <3 <3 <3  ***  :)  MSG:2          │
│ [Feed]    [Msg]              [>]  │
└────────────────────────────────────┘
```

## Mood → Sprite Mapping

| Pet Mood | Sprite File | Animation Source |
|----------|------------|------------------|
| happy | happy.png | BunnySitting |
| neutral | neutral.png | BunnyIdle |
| sad | sad.png | BunnyLieDown |
| hungry | excited.png | BunnyRun |
| sick | sick.png | BunnyHurt |
| sleeping | sleeping.png | BunnySleep |
| dead | dead.png | BunnyDead |

## Troubleshooting

### Problem: Sprites not showing, ASCII art still displayed
**Solution:** 
- Check if sprites directory exists on Pi
- Verify PIL is installed: `ssh rossi@10.8.17.62 'python3 -c "from PIL import Image"'`
- Check logs for error messages

### Problem: Import errors
**Solution:**
- PIL should already be installed via `python3-pil` from install_bare_metal.sh
- If not: `ssh rossi@10.8.17.62 'sudo apt install -y python3-pil'`

### Problem: Service fails to start
**Solution:**
- Check logs: `ssh rossi@10.8.17.62 'sudo journalctl -u eink-display.service -n 50'`
- Verify paths in menu_system.py match actual file structure
- Ensure file permissions are correct

## Future: Add Animations

If you want sprites to animate (cycle through frames):

1. Modify `TamagotchiMenu.render()` to track frame index
2. Load frame sequence instead of single sprite
3. Increment frame on each refresh
4. Use files like `BunnyIdle_frame00.png` through `BunnyIdle_frame07.png`

Example:
```python
# In TamagotchiMenu class
self.animation_frame = getattr(self, 'animation_frame', 0) % num_frames
sprite_filename = f"BunnyIdle_frame{self.animation_frame:02d}.png"
self.animation_frame += 1
```

## Documentation

See `docs/SPRITES.md` for complete technical details.

---

**Ready to deploy?** Run: `./scripts/deploy_sprites.sh`
