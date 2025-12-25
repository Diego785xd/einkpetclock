# New Clock-Focused Layout

## Layout Design (250x122 display)

```
┌─────────────────────────────────────────────────┐
│ Tue, Dec 24                                   ! │ 5px  (Date + error indicator)
│                                                 │
│                                                 │
│  10:30 AM              ┌────────────┐          │ 25px (HUGE time + 64x64 sprite)
│                        │   /\_/\    │          │
│                        │  ( o.o )   │          │
│                        │   > ^ <    │          │
│                        │            │          │
│                        │   BUNNY    │          │
│                        │  SPRITE    │          │
│                        │   64x64    │          │
│                        └────────────┘          │
│                                                 │
│                                                 │
├─────────────────────────────────────────────────┤ 95px (separator line)
│ <3 <3 <3  ***  :)  MSG:2                       │ 98px (status bar)
├─────────────────────────────────────────────────┤
│ [Feed]        [Msg]                       [>]  │ 110px (button hints)
└─────────────────────────────────────────────────┘
```

## Key Changes

### Before
- Time: Centered at top (xlarge)
- Date: Below time (small)
- Sprite: Center (32x32)
- Stats: Below sprite
- Divider: Middle of screen

### After
- Date: Top left (medium) - same size as old time
- Time: Left side, huge (xlarge) - MAIN FOCUS
- Sprite: Right side (64x64) - DOUBLE SIZE, aligned with time
- Stats: Bottom bar (condensed)
- Divider: Above bottom bar only
- Button hints: Very bottom

## Measurements

- Display: 250 x 122 pixels
- Date position: (5, 5)
- Time position: (10, 25) - xlarge font
- Sprite size: 64 x 64 pixels (was 32x32)
- Sprite position: (176, 25) - right side with 10px margin
- Status bar: y=98
- Button hints: y=110
- Separator line: y=95

## Benefits

1. **Clock is the star** - Time is huge and immediately visible
2. **Date is visible** but doesn't compete with time
3. **Bunny is bigger** - More personality, easier to see mood
4. **Balanced layout** - Time on left, bunny on right
5. **Clean bottom bar** - All stats and buttons organized

## Sprite Scaling

- Original sprites: 32x32 pixels
- New size: 64x64 pixels (2x scale)
- Scaling method: `Image.NEAREST` to preserve pixel art sharpness
- No blur or anti-aliasing - keeps crisp pixel aesthetic
