#!/usr/bin/env python3
"""
Visual mockup of new clock-focused layout
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║              E-Ink Pet Clock - New Layout                    ║
╚══════════════════════════════════════════════════════════════╝

Display: 250 x 122 pixels (Waveshare 2.13" V4)

┌────────────────────────────────────────────────────────────┐
│ Tue, Dec 24                                              ! │ ← Date (top left) + error indicator
│                                                            │
│                                                            │
│  ██  ███  ██ ██ ███      ███  ███          ░░░░░░░░░░    │ ← HUGE Time (left)
│  ███ ███  ███   ███      ███ ██ █         ░░░░░░░░░░░░   │   + 64x64 Bunny (right)
│  ███ ███ ████   ███ ████ ███ ███         ░░▓▓░░░░▓▓░░░   │   Aligned horizontally
│                                            ░░░░░░░░░░░░░   │
│                                            ░░░░██░░░░░░   │
│                                            ░░░░░░░░░░░░   │
│                                             ░░░░░░░░░░    │
│                                             ░░░░░░░░░░    │
│                                                            │
├────────────────────────────────────────────────────────────┤ ← Separator line
│ <3 <3 <3    ***    :)    MSG:2                            │ ← Status bar: Health, Hunger, Mood, Messages
├────────────────────────────────────────────────────────────┤
│ [Feed]           [Msg]                               [>]  │ ← Button hints
└────────────────────────────────────────────────────────────┘

KEY FEATURES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Date: Top left (medium) - Shows current date
✓ Time: HUGE on left side - Main focus (this is a CLOCK!)
✓ Bunny: 64x64 on right - DOUBLE SIZE, more visible
✓ Stats: Bottom bar - Health, Hunger, Mood, Messages
✓ Buttons: Very bottom - Clear action labels

SPRITE MOODS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Happy     Neutral    Sleeping     Sad
  (^_^)      (•_•)      (- -)      (;_;)
    
  Hungry     Sick       Dead       Excited
  (>_<)      (X_X)      (×_×)      (o_o)!

LAYOUT CHANGES FROM ORIGINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before                    After
─────────────────────    ──────────────────────
Time: Centered top       Date: Top left
Date: Below time         Time: HUGE left side
Sprite: 32x32 center     Sprite: 64x64 right
Stats: Below sprite      Stats: Bottom bar
Divider: Middle          Divider: Above bar only

ADVANTAGES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Clock-first design - Time is most prominent
2. Bigger bunny - More personality and easier to see mood
3. Balanced layout - Time left, bunny right
4. Clean organization - All stats in dedicated bar
5. Better use of horizontal space

""")
