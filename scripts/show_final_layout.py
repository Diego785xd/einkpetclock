#!/usr/bin/env python3
"""
Final optimized layout with labels
"""

print("""
╔════════════════════════════════════════════════════════════╗
║         Final E-Ink Pet Clock Layout (with labels)        ║
╚════════════════════════════════════════════════════════════╝

Display: 250 x 122 pixels

┌────────────────────────────────────────────────────────────┐
│ Tue, Dec 24                                              ! │ y=2  (Date + error)
│                                                            │
│  ██  ███  ██ ██ ███            ░░░░░░░░░░                │ y=18 (HUGE Time 48pt)
│  ███ ███  ███   ███           ░░░░░░░░░░░░               │      + 64x64 Bunny
│  ███ ███ ████   ███ ████      ░░▓▓░░░░▓▓░░               │
│                                ░░░░░░░░░░░░               │
│                                ░░░░██░░░░░                │
│                                ░░░░░░░░░░░                │
│                                 ░░░░░░░░░                 │
│                                                            │
│                                                            │
│ HP: <3 <3 <3   Food: **   Mood: :)                       │ y=72 (Stats WITH LABELS)
│ Messages: 2 new                                           │ y=86 (if messages exist)
│                                                            │
├────────────────────────────────────────────────────────────┤ y=95 (Divider)
│ [Feed]           [Menu]                              [>]  │ y=107 (Buttons only)
└────────────────────────────────────────────────────────────┘

LAYOUT BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Section          Y Position   Content
──────────────────────────────────────────────────────────────
Header           2            Date + Network error indicator
Main Display     18-82        Time (48pt) + Bunny sprite (64x64)
Pet Stats        72-86        HP, Food, Mood WITH LABELS
                              Messages line (if applicable)
Divider          95           Horizontal line
Button Bar       107          Feed, Menu, Next buttons

STAT LABELS EXPLAINED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HP: <3 <3 <3      = Health points (3 hearts = full health)
                    More hearts = healthier
                    No hearts = critical!

Food: **          = Hunger level (inverted scale)
                    No stars = Full/Fed
                    * = Slightly hungry
                    ** = Hungry
                    *** = Very hungry!

Mood: :)          = Current emotional state
                    :) = Happy
                    :| = Neutral
                    :( = Sad
                    :P = Hungry (wants food)
                    :X = Sick (needs care)
                    ZZ = Sleeping
                    XX = Dead

Messages: 2 new   = Unread messages from other device
                    (only shown if you have messages)

BUTTON ACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Feed]   = Feed your pet (increases food, health)
[Menu]   = Switch between menus (Stats, Messages, Settings)
[>]      = Action button (send message, etc.)

IMPROVEMENTS FROM PREVIOUS VERSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Stats moved below time - uses blank space
✓ Added LABELS to stats - now understandable!
✓ "HP:" prefix - clarifies hearts are health
✓ "Food:" prefix - clarifies hunger system
✓ "Mood:" prefix - clarifies emotion icons
✓ "Messages: X new" - clear message count
✓ Divider only above buttons - cleaner separation
✓ Changed [Msg] to [Menu] - more accurate
✓ All content above divider - organized layout

""")
