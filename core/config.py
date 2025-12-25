"""
Configuration loader for E-Ink Pet Clock
Loads settings from .env file and provides defaults
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print(f"Warning: .env file not found at {ENV_PATH}")
    print("Using default configuration. Copy .env.example to .env to configure.")


class Config:
    """Application configuration"""
    
    # Paths
    PROJECT_ROOT = PROJECT_ROOT
    DATA_DIR = PROJECT_ROOT / "data"
    ASSETS_DIR = PROJECT_ROOT / "assets"
    SPRITES_DIR = ASSETS_DIR / "sprites"
    FONTS_DIR = ASSETS_DIR / "fonts"
    
    # Device Identity
    DEVICE_NAME: str = os.getenv("DEVICE_NAME", "bunny_clock")
    DEVICE_TIMEZONE: str = os.getenv("DEVICE_TIMEZONE", "America/Mexico_City")
    
    # Network Configuration
    DEVICE_IP: str = os.getenv("DEVICE_IP", "10.8.17.62")
    REMOTE_DEVICE_IP: str = os.getenv("REMOTE_DEVICE_IP", "10.8.17.114")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    
    # Display Settings
    TIME_FORMAT: int = int(os.getenv("TIME_FORMAT", "24"))
    DISPLAY_WIDTH: int = 250  # Waveshare 2.13" V4
    DISPLAY_HEIGHT: int = 122
    
    # Pet Settings
    PET_TYPE: str = os.getenv("PET_TYPE", "bunny")
    PET_NAME: str = os.getenv("PET_NAME", "Fluffy")
    
    # GPIO Pin Configuration
    BUTTON_RETURN: int = 6   # Pin 31
    BUTTON_ACTION: int = 13  # Pin 33
    BUTTON_GO: int = 19      # Pin 35
    BUTTON_DEBOUNCE_MS: int = 200
    BUTTON_LONG_PRESS_MS: int = 2000  # 2 seconds for long press
    
    # Update Intervals (seconds)
    CLOCK_UPDATE_INTERVAL: int = 60  # Update time every minute
    PET_UPDATE_INTERVAL: int = 3600  # Update pet state every hour
    FULL_REFRESH_CYCLES: int = 10    # Full refresh every N updates
    
    # Pet Mechanics
    HUNGER_DECAY_RATE: float = 1.0  # Points per hour
    HAPPINESS_DECAY_RATE: float = 0.5  # Points per hour
    MAX_HUNGER: int = 10
    MAX_HAPPINESS: int = 10
    MAX_HEALTH: int = 10
    
    # Development/Testing
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    MOCK_HARDWARE: bool = os.getenv("MOCK_HARDWARE", "false").lower() == "true"
    
    @classmethod
    def get_remote_url(cls, endpoint: str = "") -> str:
        """Get full URL for remote device API endpoint"""
        return f"http://{cls.REMOTE_DEVICE_IP}:{cls.API_PORT}{endpoint}"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.ASSETS_DIR.mkdir(exist_ok=True)
        cls.SPRITES_DIR.mkdir(exist_ok=True)
        cls.FONTS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary"""
        return {
            "device_name": cls.DEVICE_NAME,
            "device_timezone": cls.DEVICE_TIMEZONE,
            "device_ip": cls.DEVICE_IP,
            "remote_device_ip": cls.REMOTE_DEVICE_IP,
            "api_port": cls.API_PORT,
            "time_format": cls.TIME_FORMAT,
            "pet_type": cls.PET_TYPE,
            "pet_name": cls.PET_NAME,
            "debug_mode": cls.DEBUG_MODE,
            "mock_hardware": cls.MOCK_HARDWARE,
        }


# Initialize directories on import
Config.ensure_directories()


if __name__ == "__main__":
    # Test configuration
    print("E-Ink Pet Clock Configuration")
    print("=" * 50)
    for key, value in Config.to_dict().items():
        print(f"{key:20s}: {value}")
    print("\nDirectories:")
    print(f"  Project Root: {Config.PROJECT_ROOT}")
    print(f"  Data Dir:     {Config.DATA_DIR}")
    print(f"  Assets Dir:   {Config.ASSETS_DIR}")
