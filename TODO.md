# TODO List for E-Ink Pet Clock

## Completed ✅
- [x] Project structure and configuration
- [x] File-based state management
- [x] Button handler with GPIO
- [x] E-ink display wrapper
- [x] Menu system (4 menus)
- [x] Tamagotchi logic
- [x] Main display manager
- [x] REST API for network communication
- [x] Systemd service files
- [x] Deployment scripts

## To Do Before First Run 🚀

### On Your Mac
- [ ] Copy `.env.example` to `.env` and configure:
  - Device name
  - Device IP (10.8.17.62)
  - Remote device IP (10.8.17.114 for testing)
  - Timezone (America/Mexico_City)
  
### On Raspberry Pi
- [ ] Hardware: Connect 3 buttons to GPIO 6, 13, 19
- [ ] Hardware: Connect Waveshare e-ink display
- [ ] Deploy code from Mac
- [ ] Run `bash scripts/install.sh`
- [ ] Configure `.env` on Pi
- [ ] Start services

## Future Enhancements 💡

### Sprites & Graphics
- [ ] Create bunny sprite images (happy, sad, hungry, sick, neutral)
- [ ] Add animation frames for feeding
- [ ] Design custom icons for menus
- [ ] Add seasonal themes (Christmas, Valentine's, etc.)

### Features
- [ ] Multiple predefined messages (not just poke)
- [ ] Message types: Heart, Hug, Kiss, Think of you, etc.
- [ ] Pet evolution over time
- [ ] Achievement system
- [ ] Weather display (optional)
- [ ] Photo sharing (send small images)

### Polish
- [ ] Better error recovery
- [ ] Offline mode handling
- [ ] Battery level indicator (if using battery)
- [ ] Sound effects via buzzer (optional)
- [ ] LED indicator for new messages

### Optimization
- [ ] Reduce memory usage
- [ ] Faster boot time
- [ ] Better partial refresh strategy
- [ ] Cache frequently used images

## Known Issues 🐛
- None yet! (Will add as discovered)

## Testing Checklist ✓
- [ ] Button presses register correctly
- [ ] Display updates properly
- [ ] API receives messages
- [ ] Pet state persists across restarts
- [ ] Services auto-start on boot
- [ ] Network communication works over ZeroTier
- [ ] Time displays correctly in Mexico City timezone
- [ ] Settings can be changed
- [ ] Messages are stored and retrieved
- [ ] Stats are tracked

## Documentation
- [ ] Record video demo
- [ ] Take photos of final build
- [ ] Document wiring in detail
- [ ] Create sprite design guidelines
