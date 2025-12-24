#!/usr/bin/env python3
"""
Mock API Server for Testing on Mac
Simulates the Pi's API for local development
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set mock hardware mode
import os
os.environ['MOCK_HARDWARE'] = 'true'

from web.api import app
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("Mock API Server for Mac Testing")
    print("=" * 50)
    print("This simulates the Pi's API on your Mac")
    print("URL: http://localhost:5000")
    print("=" * 50)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
