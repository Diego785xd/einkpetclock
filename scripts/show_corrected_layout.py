#!/usr/bin/env python3
"""
CORRECTED layout with proper spacing
"""

print("""
╔════════════════════════════════════════════════════════════╗
║         CORRECTED Vertical Layout (Proper Spacing)        ║
╚════════════════════════════════════════════════════════════╝

Display: 250 x 122 pixels

┌────────────────────────────────────────────────────────────┐
│ Tue, Dec 24                                              ! │ y=2
│                                                            │
│  ██  ███  ██ ██ ███            ░░░░░░░░░░                │ y=18 Time
│  ███ ███  ███   ███           ░░░░░░░░░░░░               │      + Bunny
│  ███ ███ ████   ███ ████      ░░▓▓░░░░▓▓░░               │
│                                ░░░░░░░░░░░░               │
│                                ░░░░██░░░░░                │
│                                ░░░░░░░░░░░                │
│                                 ░░░░░░░░░                 │
│ Health: <3 <3 <3                                          │ y=68  (closer!)
│ Food:   **                                                │ y=79
│ Mood:   :)                                                │ y=90
│ Msgs: 2 new                                               │ y=101
├────────────────────────────────────────────────────────────┤ y=103 (divider)
│                                                            │
│ [Feed]           [Menu]                              [>]  │ y=109
└────────────────────────────────────────────────────────────┘

SPACING FIXED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Element          Y Position   Notes
──────────────────────────────────────────────────────────────
Date             2            Top left
Time + Bunny     18-82        48pt time + 64x64 sprite
Health           68           Stats START HERE (was 70)
Food             79           11px spacing (was 13px)
Mood             90           11px spacing
Messages         101          11px spacing (if shown)
Divider          103          Moved down (was 95)
Buttons          109          Below divider

CHANGES MADE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Stats start at y=68 (was 70) - LESS GAP after time
✅ Line height = 11px (was 13px) - TIGHTER spacing
✅ Divider at y=103 (was 95) - BELOW all stats
✅ Buttons at y=109 (was 107) - Below divider
✅ "Msgs:" shortened (was "Messages:") - Fits better

RESULT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Less blank space between time and stats
✓ All stats ABOVE the divider line
✓ Divider properly separates content from buttons
✓ Everything fits perfectly on screen

""")
