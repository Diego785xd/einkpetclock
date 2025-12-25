#!/usr/bin/env python3
"""
Test sprite rendering locally
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites"
OUTPUT_PATH = PROJECT_ROOT / "test_sprite_render.png"

# Create a test canvas (same size as e-ink display)
WIDTH = 250
HEIGHT = 122
img = Image.new('1', (WIDTH, HEIGHT), 1)  # 1-bit B&W, white background
draw = ImageDraw.Draw(img)

# Draw title
draw.text((10, 5), "Bunny Sprite Test", fill=0)

# Test each mood sprite
moods = ["neutral", "happy", "sad", "sick", "sleeping", "dead", "excited", "angry"]
x_positions = [10, 70, 130, 190, 10, 70, 130, 190]
y_positions = [25, 25, 25, 25, 70, 70, 70, 70]

for mood, x, y in zip(moods, x_positions, y_positions):
    sprite_path = SPRITES_DIR / f"{mood}.png"
    
    if sprite_path.exists():
        sprite = Image.open(sprite_path)
        # Resize to 28x28 for the grid view
        sprite_small = sprite.resize((28, 28))
        img.paste(sprite_small, (x, y))
        
        # Label
        label = mood[:3].upper()
        draw.text((x + 2, y + 30), label, fill=0)
    else:
        draw.text((x, y), f"X {mood}", fill=0)

# Save test image
img.save(OUTPUT_PATH)
print(f"✓ Test render saved to: {OUTPUT_PATH}")
print(f"  Open with: open {OUTPUT_PATH}")
