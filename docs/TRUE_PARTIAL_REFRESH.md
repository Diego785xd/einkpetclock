# True Partial Refresh Implementation

## Problem
The display was performing full screen refreshes every time, even with `display_fast()`. This caused the entire screen to flash/refresh every 0.5 seconds during animation, which was excessive.

## Solution
Implemented true partial refresh using the e-ink display's `displayPartBaseImage()` and `displayPartial()` methods, which only update changed pixel areas.

## How It Works

### 1. Base Image Concept
- When entering the main menu, a **full render** is performed once
- This image is set as the "base image" using `displayPartBaseImage()`
- All static content (date, labels, divider, buttons) is part of this base

### 2. Partial Updates
Only dynamic areas are redrawn:
- **Sprite animation** (every 0.5s): Only the 64x64px sprite area is cleared and redrawn
- **Time display** (every 1 min): Only the time text area is cleared and redrawn
- **Stats changes**: Only affected stat areas are updated

### 3. Full Refresh Strategy
Full screen refresh occurs:
- **Every 5 minutes**: Clears ghosting artifacts from partial updates
- **On menu changes**: When switching between menus
- **On returning to main menu**: Resets the base image

## Key Changes

### TamagotchiMenu Class
- **`render_full()`**: Performs full render and sets base image
- **`render(is_base_render=False)`**: Can render as base or use existing base
- **`update_sprite_only()`**: Only updates the sprite rectangle area
- **`update_time_only()`**: Only updates the time text area

### DisplayManager
- **`update_animation()`**: Calls `update_sprite_only()` instead of full render
- **`update_clock()`**: Calls `update_time_only()` instead of full render
- **`check_full_refresh_needed()`**: Triggers full refresh every 5 minutes
- Tracks `last_full_refresh` for 5-minute cycles

### Display Class
- Added `base_image_set` flag to track if base image is initialized
- `display()` method now supports `partial_mode="true"` for `displayPartial()`
- `set_base_image()` method for explicit base image setting

## Performance Impact

### Before
- Full screen refresh every 0.5s during animation
- ~1-2 second visible refresh per frame
- High power consumption

### After
- Full screen refresh only every 5 minutes or on menu changes
- Sprite area only refreshes every 0.5s (~200ms update, mostly invisible)
- Time area only refreshes every 1 minute
- Significantly reduced power consumption
- Smoother animation appearance

## Benefits
1. **Smooth animation**: Only sprite area flickers briefly
2. **Lower power**: Fewer full screen refreshes
3. **Better UX**: Rest of display remains stable while sprite animates
4. **Reduced ghosting**: Full refresh every 5 min keeps display clean

## Example Flow

```
1. User switches to main menu
   → render_full() called
   → Full screen refresh
   → Base image set

2. Every 0.5 seconds
   → advance_frame() increments frame counter
   → update_sprite_only() called
   → Clear sprite rectangle (64x64px)
   → Draw new sprite frame
   → displayPartial() - only sprite area updates

3. Every 1 minute
   → update_time_only() called
   → Clear time rectangle
   → Draw new time
   → displayPartial() - only time area updates

4. Every 5 minutes
   → check_full_refresh_needed() called
   → render_full() called
   → Full screen refresh to clear ghosting
   → Base image reset

5. User presses button to change menu
   → Menu changes
   → Full render of new menu
   → If returning to main menu, render_full() sets new base
```

## Configuration
- Animation interval: 0.5 seconds (adjustable in update_animation)
- Time update: 60 seconds (Config.CLOCK_UPDATE_INTERVAL)
- Full refresh cycle: 300 seconds / 5 minutes (adjustable in check_full_refresh_needed)
