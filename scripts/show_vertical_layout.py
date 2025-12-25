#!/usr/bin/env python3
"""
Final layout with VERTICAL stats (multi-line) and regular font
"""

print("""
╔════════════════════════════════════════════════════════════╗
║    Final E-Ink Pet Clock Layout (VERTICAL STATS)          ║
╚════════════════════════════════════════════════════════════╝

Display: 250 x 122 pixels
Font: DejaVuSans (regular, not bold)

┌────────────────────────────────────────────────────────────┐
│ Tue, Dec 24                                              ! │ y=2  (Date + error)
│                                                            │
│  ██  ███  ██ ██ ███            ░░░░░░░░░░                │ y=18 (Time 48pt)
│  ███ ███  ███   ███           ░░░░░░░░░░░░               │      + Bunny 64x64
│  ███ ███ ████   ███ ████      ░░▓▓░░░░▓▓░░               │
│                                ░░░░░░░░░░░░               │
│                                ░░░░██░░░░░                │
│                                ░░░░░░░░░░░                │
│                                 ░░░░░░░░░                 │
│                                                            │
│ Health: <3 <3 <3                                          │ y=70 (Health - line 1)
│ Food:   **                                                │ y=83 (Food - line 2)
│ Mood:   :)                                                │ y=96 (Mood - line 3)
│ Messages: 2 new                                           │ y=109 (Messages - line 4, if any)
├────────────────────────────────────────────────────────────┤ y=95 (Divider)
│ [Feed]           [Menu]                              [>]  │ y=107 (Buttons)
└────────────────────────────────────────────────────────────┘

LAYOUT BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Section          Y Position   Height    Content
────────────────────────────────────────────────────────────────
Header           2            12px      Date + error indicator
Main Display     18-69        51px      Time (48pt) + Bunny (64x64)
Pet Stats        70-109       39px      4 lines stacked vertically:
  - Health       70           13px        Health: <3 <3 <3
  - Food         83           13px        Food:   **
  - Mood         96           13px        Mood:   :)
  - Messages     109          13px        Messages: X new (optional)
Divider          95           1px       Horizontal line
Button Bar       107          15px      Feed, Menu, Next buttons

KEY IMPROVEMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ VERTICAL LAYOUT - Stats stacked on separate lines
✅ REGULAR FONT - Not bold, easier to read
✅ CLEAR LABELS - Each stat has descriptive name
✅ ALIGNED TEXT - Colons aligned for clean look
✅ OPTIONAL MESSAGES - Only shows if you have new messages
✅ NO OVERLAP - Everything fits perfectly

STAT EXPLANATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health: <3 <3 <3    Health Points
                    • 3 hearts = Full health (HP: 9-10)
                    • 2 hearts = Good health (HP: 6-8)
                    • 1 heart  = Low health (HP: 3-5)
                    • No hearts = Critical! (HP: 0-2)

Food:   **          Hunger Level
                    • No stars = Full/Fed (hunger: 0-2)
                    • *        = Slightly hungry (hunger: 3-5)
                    • **       = Hungry (hunger: 6-8)
                    • ***      = Very hungry! (hunger: 9-10)

Mood:   :)          Emotional State
                    • :)  = Happy (well cared for)
                    • :|  = Neutral (doing okay)
                    • :(  = Sad (neglected)
                    • :P  = Hungry (wants food!)
                    • :X  = Sick (needs attention)
                    • ZZ  = Sleeping (nighttime)
                    • XX  = Dead (health = 0)

Messages: 2 new     Unread Messages
                    • Only appears if you have messages
                    • Shows count of unread messages

VISUAL COMPARISON:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE (single line):
HP: <3 <3 <3   Food: **   Mood: :)

AFTER (multi-line):
Health: <3 <3 <3
Food:   **
Mood:   :)

Much cleaner and easier to read!

""")
