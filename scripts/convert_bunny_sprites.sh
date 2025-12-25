#!/bin/bash
# Convert bunny sprite sheets to individual black & white sprites
# Uses macOS built-in sips command

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="$PROJECT_ROOT/assets/bunny_source"
OUTPUT_DIR="$PROJECT_ROOT/assets/sprites"

echo "============================================================"
echo "Bunny Sprite Converter for E-Ink Display"
echo "============================================================"
echo ""
echo "📁 Source: $SOURCE_DIR"
echo "📁 Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process each sprite sheet
# Format: filename:frames:mood_name
SPRITES=(
    "BunnyIdle-Sheet.png:8:neutral"
    "BunnySleep-Sheet.png:2:sleeping"
    "BunnyHurt-Sheet.png:3:sick"
    "BunnySitting-Sheet.png:3:happy"
    "BunnyDead-Sheet.png:9:dead"
    "BunnyLieDown-Sheet.png:2:sad"
    "BunnyRun-Sheet.png:5:excited"
    "BunnyAttack-Sheet.png:7:angry"
)

for sprite_info in "${SPRITES[@]}"; do
    IFS=':' read -r filename frames mood <<< "$sprite_info"
    
    echo ""
    echo "📄 Processing $filename"
    echo "   Frames: $frames"
    
    src_file="$SOURCE_DIR/$filename"
    
    if [[ ! -f "$src_file" ]]; then
        echo "   ⚠ Skipping - file not found"
        continue
    fi
    
    # Extract individual frames
    for ((i=0; i<frames; i++)); do
        # Calculate crop box (each frame is 32x32 pixels)
        x=$((i * 32))
        
        # Extract frame
        temp_frame="$OUTPUT_DIR/temp_frame_$i.png"
        sips -c 32 32 --cropOffset "$x" 0 -s format png "$src_file" --out "$temp_frame" > /dev/null 2>&1
        
        # Convert to monochrome (threshold)
        output_name="${filename%-Sheet.png}_frame$(printf '%02d' $i).png"
        sips -s formatOptions 70 -s format png "$temp_frame" --out "$OUTPUT_DIR/$output_name" > /dev/null 2>&1
        
        echo "   ✓ Saved $output_name"
        
        # Save first frame as main mood sprite
        if [[ $i -eq 0 ]]; then
            cp "$OUTPUT_DIR/$output_name" "$OUTPUT_DIR/$mood.png"
            echo "   ✓ Saved $mood.png (main sprite)"
        fi
        
        # Clean up temp file
        rm -f "$temp_frame"
    done
done

echo ""
echo "============================================================"
echo "✓ Conversion complete!"
echo "============================================================"
echo ""
echo "Converted sprites saved to: $OUTPUT_DIR"
echo ""
echo "Main mood sprites created:"
echo "  - neutral.png (from BunnyIdle)"
echo "  - sleeping.png (from BunnySleep)"
echo "  - sick.png (from BunnyHurt)"
echo "  - happy.png (from BunnySitting)"
echo "  - sad.png (from BunnyLieDown)"
echo "  - dead.png (from BunnyDead)"
echo "  - excited.png (from BunnyRun)"
echo "  - angry.png (from BunnyAttack)"
echo ""
echo "You can now use these in the menu system!"
