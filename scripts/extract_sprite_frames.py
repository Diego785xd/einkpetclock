#!/usr/bin/env python3
"""
Extract individual frames from sprite sheets
Properly splits sprite sheets every 32 pixels horizontally
"""
from PIL import Image
from pathlib import Path

# Paths
SOURCE_DIR = Path(__file__).parent.parent / "assets" / "bunny_source"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "sprites"

# Sprite sheets to process (sheet_name: number_of_frames)
SPRITE_SHEETS = {
    "BunnyAttack-Sheet.png": 7,
    "BunnyDead-Sheet.png": 9,
    "BunnyHurt-Sheet.png": 3,
    "BunnyIdle-Sheet.png": 8,
    "BunnyLieDown-Sheet.png": 2,
    "BunnyRun-Sheet.png": 5,
    "BunnySleep-Sheet.png": 2,
}

FRAME_SIZE = 32  # Each frame is 32x32 pixels


def extract_frames(sheet_path: Path, num_frames: int, output_name: str):
    """Extract frames from a sprite sheet"""
    print(f"Processing {sheet_path.name}...")
    
    try:
        # Load the sprite sheet
        sheet = Image.open(sheet_path)
        width, height = sheet.size
        
        print(f"  Sheet size: {width}x{height}")
        print(f"  Expected frames: {num_frames}")
        print(f"  Calculated frames: {width // FRAME_SIZE}")
        
        # Verify dimensions
        if width != num_frames * FRAME_SIZE:
            print(f"  WARNING: Width mismatch! {width} != {num_frames * FRAME_SIZE}")
        
        if height != FRAME_SIZE:
            print(f"  WARNING: Height is {height}, expected {FRAME_SIZE}")
        
        # Extract each frame
        extracted = 0
        for i in range(num_frames):
            # Calculate crop box (left, top, right, bottom)
            left = i * FRAME_SIZE
            top = 0
            right = left + FRAME_SIZE
            bottom = FRAME_SIZE
            
            # Crop the frame
            frame = sheet.crop((left, top, right, bottom))
            
            # Verify frame is not completely transparent/empty
            # Convert to RGBA if needed
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            
            # Check if frame has any opaque pixels
            pixels = frame.getdata()
            has_content = any(pixel[3] > 0 for pixel in pixels)
            
            if has_content:
                # Save the frame
                output_path = OUTPUT_DIR / f"{output_name}_frame{i:02d}.png"
                frame.save(output_path)
                extracted += 1
                print(f"  ✓ Extracted frame {i:02d}")
            else:
                print(f"  ⚠ Skipped frame {i:02d} (empty/transparent)")
        
        print(f"  Total extracted: {extracted}/{num_frames}")
        return extracted
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0


def main():
    print("=" * 50)
    print("Sprite Sheet Frame Extractor")
    print("=" * 50)
    print()
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    total_extracted = 0
    total_expected = 0
    
    # Process each sprite sheet
    for sheet_filename, num_frames in SPRITE_SHEETS.items():
        sheet_path = SOURCE_DIR / sheet_filename
        
        if not sheet_path.exists():
            print(f"WARNING: {sheet_filename} not found, skipping")
            continue
        
        # Output name is the sheet name without "-Sheet.png"
        output_name = sheet_filename.replace("-Sheet.png", "")
        
        extracted = extract_frames(sheet_path, num_frames, output_name)
        total_extracted += extracted
        total_expected += num_frames
        print()
    
    print("=" * 50)
    print(f"Extraction complete!")
    print(f"Total frames extracted: {total_extracted}/{total_expected}")
    print("=" * 50)
    
    # List output files
    print("\nGenerated files:")
    sprite_files = sorted(OUTPUT_DIR.glob("Bunny*.png"))
    for f in sprite_files:
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
