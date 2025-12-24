#!/bin/bash
# Fix line endings in scripts (run on Pi if you get "required file not found" error)

echo "Fixing line endings in scripts..."

cd "$(dirname "$0")"

for script in *.sh; do
    if [ -f "$script" ]; then
        # Convert to Unix line endings
        dos2unix "$script" 2>/dev/null || sed -i 's/\r$//' "$script" 2>/dev/null || perl -pi -e 's/\r\n/\n/g' "$script"
        chmod +x "$script"
        echo "✓ Fixed: $script"
    fi
done

echo "Done! Try running your script again."
