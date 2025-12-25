#!/usr/bin/env python3
"""
Convert colored bunny sprite sheets to black & white individual sprites
for e-ink display usage
"""
from PIL import Image
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "assets" / "bunny_source"
OUTPUT_DIR = PROJECT_ROOT / "assets" / "sprites"

# Sprite sheet configurations (based on actual file dimensions)
# All sprites are 32x32 pixels. Width / 32 = frame count
SPRITE_CONFIGS = {
    "BunnyIdle-Sheet.png": {
        "frames": 8,  # 256px / 32 = 8 frames
        "output_name": "bunny_idle",
        "mood": "neutral"
    },
    "BunnySleep-Sheet.png": {
        "frames": 2,  # 64px / 32 = 2 frames
        "output_name": "bunny_sleeping",
        "mood": "sleeping"
    },
    "BunnyHurt-Sheet.png": {
        "frames": 3,  # 96px / 32 = 3 frames
        "output_name": "bunny_hurt",
        "mood": "sick"
    },
    "BunnySitting-Sheet.png": {
        "frames": 3,  # 96px / 32 = 3 frames
        "output_name": "bunny_sitting",
        "mood": "happy"
    },
    "BunnyDead-Sheet.png": {
        "frames": 9,  # 288px / 32 = 9 frames
        "output_name": "bunny_dead",
        "mood": "dead"
    },
    "BunnyLieDown-Sheet.png": {
        "frames": 2,  # 64px / 32 = 2 frames
        "output_name": "bunny_liedown",
        "mood": "sad"
    },
    "BunnyRun-Sheet.png": {
        "frames": 5,  # 160px / 32 = 5 frames
        "output_name": "bunny_run",
        "mood": "excited"
    },
    "BunnyAttack-Sheet.png": {
        "frames": 7,  # 224px / 32 = 7 frames
        "output_name": "bunny_attack",
        "mood": "angry"
    },
}


def convert_to_bw_threshold(img, threshold=128):
    """Convert image to pure black and white using threshold"""
    # Convert to grayscale
    gray = img.convert('L')
    
    # Apply threshold: pixels above threshold become white, below become black
    bw = gray.point(lambda x: 255 if x > threshold else 0, mode='1')
    
    return bw


def extract_sprite_frames(sprite_sheet_path, num_frames, sprite_width=32, sprite_height=32):
    """
    Extract individual frames from a sprite sheet
    Assumes sprites are arranged horizontally in a single row
    """
    img = Image.open(sprite_sheet_path)
    
    frames = []
    for i in range(num_frames):
        # Calculate the box for this frame
        left = i * sprite_width
        top = 0
        right = left + sprite_width
        bottom = sprite_height
        
        # Extract the frame
        frame = img.crop((left, top, right, bottom))
        frames.append(frame)
    
    return frames


def process_sprite_sheet(sheet_name, config):
    """Process a single sprite sheet"""
    source_path = SOURCE_DIR / sheet_name
    
    if not source_path.exists():
        print(f"⚠ Skipping {sheet_name} - file not found")
        return
    
    print(f"\n📄 Processing {sheet_name}")
    print(f"   Frames: {config['frames']}")
    
    # Extract frames
    frames = extract_sprite_frames(source_path, config['frames'])
    
    # Convert each frame to B&W and save
    for i, frame in enumerate(frames):
        # Convert to black and white
        bw_frame = convert_to_bw_threshold(frame, threshold=200)
        
        # Generate output filename
        if config['frames'] == 1:
            output_name = f"{config['output_name']}.png"
        else:
            output_name = f"{config['output_name']}_frame{i:02d}.png"
        
        output_path = OUTPUT_DIR / output_name
        
        # Save
        bw_frame.save(output_path)
        print(f"   ✓ Saved {output_name}")
    
    # Also save the first frame as the main sprite for this mood
    if config['frames'] > 0:
        main_output = OUTPUT_DIR / f"{config['mood']}.png"
        bw_frame = convert_to_bw_threshold(frames[0], threshold=200)
        bw_frame.save(main_output)
        print(f"   ✓ Saved {config['mood']}.png (main sprite)")


def main():
    """Convert all sprite sheets"""
    print("=" * 60)
    print("Bunny Sprite Converter for E-Ink Display")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    print(f"\n📁 Source: {SOURCE_DIR}")
    print(f"📁 Output: {OUTPUT_DIR}")
    
    # Process each sprite sheet
    for sheet_name, config in SPRITE_CONFIGS.items():
        process_sprite_sheet(sheet_name, config)
    
    print("\n" + "=" * 60)
    print("✓ Conversion complete!")
    print("=" * 60)
    print(f"\nConverted sprites saved to: {OUTPUT_DIR}")
    print("\nMain mood sprites created:")
    print("  - neutral.png (from BunnyIdle)")
    print("  - sleeping.png (from BunnySleep)")
    print("  - sick.png (from BunnyHurt)")
    print("  - happy.png (from BunnySitting)")
    print("  - sad.png (from BunnyLieDown)")
    print("  - dead.png (from BunnyDead)")
    print("  - excited.png (from BunnyRun)")
    print("  - angry.png (from BunnyAttack)")
    print("\nYou can now use these in the menu system!")


if __name__ == "__main__":
    main()
