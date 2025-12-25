"""
E-Ink Display Manager for Waveshare 2.13" V4
Provides abstraction layer with partial refresh support
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple
from pathlib import Path
from core.config import Config

# Try to import Waveshare EPD library
try:
    from waveshare_epd import epd2in13_V4
    HAS_EPD = True
except ImportError:
    HAS_EPD = False
    print("Warning: waveshare_epd not available. Using mock display.")


class MockEPD:
    """Mock e-ink display for development"""
    
    def __init__(self):
        self.width = 122
        self.height = 250
    
    def init(self):
        print("Mock EPD: init()")
    
    def init_fast(self):
        print("Mock EPD: init_fast()")
    
    def Clear(self, color):
        print(f"Mock EPD: Clear({color})")
    
    def display(self, buffer):
        print("Mock EPD: display() - Full refresh")
    
    def display_fast(self, buffer):
        print("Mock EPD: display_fast() - Partial refresh")
    
    def sleep(self):
        print("Mock EPD: sleep()")
    
    def getbuffer(self, image):
        return b"mock_buffer"


class DisplayManager:
    """Manages e-ink display with optimized refresh strategies"""
    
    def __init__(self):
        if HAS_EPD:
            self.epd = epd2in13_V4.EPD()
        else:
            self.epd = MockEPD()
        
        # Display dimensions (rotated for landscape)
        self.width = self.epd.height  # 250
        self.height = self.epd.width  # 122
        
        # Current image buffer
        self.image: Optional[Image.Image] = None
        self.draw: Optional[ImageDraw.Draw] = None
        
        # Refresh tracking
        self.update_count = 0
        self.last_full_refresh = 0
        
        # Fonts
        self.fonts = {}
        self._load_fonts()
        
        self.initialized = False
    
    def _load_fonts(self):
        """Load fonts for rendering"""
        # Try to load custom fonts, fall back to default
        font_dir = Config.FONTS_DIR
        
        try:
            # Load different sizes
            self.fonts = {
                'small': ImageFont.truetype(str(font_dir / "Font.ttc"), 12),
                'medium': ImageFont.truetype(str(font_dir / "Font.ttc"), 16),
                'large': ImageFont.truetype(str(font_dir / "Font.ttc"), 24),
                'xlarge': ImageFont.truetype(str(font_dir / "Font.ttc"), 32),
                'giant': ImageFont.truetype(str(font_dir / "Font.ttc"), 64),  # Huge clock digits
            }
        except:
            # Fall back to default font
            print("Warning: Could not load custom fonts, using default")
            default_font = ImageFont.load_default()
            self.fonts = {
                'small': default_font,
                'medium': default_font,
                'large': default_font,
                'xlarge': default_font,
                'giant': default_font,
            }
    
    def init(self):
        """Initialize the display"""
        if not self.initialized:
            self.epd.init()
            self.epd.Clear(0xFF)  # Clear to white
            self.initialized = True
            print("Display initialized")
    
    def init_fast(self):
        """Initialize display in fast mode (partial refresh)"""
        if HAS_EPD:
            self.epd.init_fast()
        self.initialized = True
    
    def create_canvas(self) -> Tuple[Image.Image, ImageDraw.Draw]:
        """Create a new drawing canvas"""
        # Create image (1-bit, white background)
        self.image = Image.new('1', (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)
        return self.image, self.draw
    
    def display(self, use_partial: bool = True):
        """
        Display the current image buffer
        
        Args:
            use_partial: Use partial refresh if True, full refresh if False
        """
        if self.image is None:
            print("Warning: No image to display")
            return
        
        self.update_count += 1
        
        # Decide refresh strategy
        force_full = (self.update_count - self.last_full_refresh) >= Config.FULL_REFRESH_CYCLES
        
        if use_partial and not force_full:
            # Partial refresh (faster, but can cause ghosting)
            if HAS_EPD:
                if not self.initialized:
                    self.init_fast()
                self.epd.display_fast(self.epd.getbuffer(self.image))
            else:
                self.epd.display_fast(self.epd.getbuffer(self.image))
            
            if Config.DEBUG_MODE:
                print(f"Display update #{self.update_count} (partial)")
        else:
            # Full refresh (clears ghosting)
            if not self.initialized:
                self.init()
            self.epd.display(self.epd.getbuffer(self.image))
            self.last_full_refresh = self.update_count
            
            if Config.DEBUG_MODE:
                print(f"Display update #{self.update_count} (full)")
    
    def clear(self):
        """Clear display to white"""
        if self.initialized:
            self.epd.Clear(0xFF)
    
    def sleep(self):
        """Put display to sleep mode"""
        if self.initialized:
            self.epd.sleep()
            self.initialized = False
            print("Display sleep mode")
    
    def get_font(self, size: str = 'medium') -> ImageFont.FreeTypeFont:
        """Get a font by size name"""
        return self.fonts.get(size, self.fonts['medium'])
    
    # Convenience drawing methods
    
    def draw_text(
        self,
        xy: Tuple[int, int],
        text: str,
        font_size: str = 'medium',
        anchor: Optional[str] = None
    ):
        """Draw text at position"""
        if self.draw is None:
            return
        
        font = self.get_font(font_size)
        self.draw.text(xy, text, font=font, fill=0, anchor=anchor)
    
    def draw_text_centered(
        self,
        y: int,
        text: str,
        font_size: str = 'medium'
    ):
        """Draw text centered horizontally"""
        if self.draw is None:
            return
        
        font = self.get_font(font_size)
        # Get text bounding box
        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        self.draw.text((x, y), text, font=font, fill=0)
    
    def draw_icon(self, xy: Tuple[int, int], icon: str, size: int = 16):
        """Draw a simple icon (emoji/character)"""
        if self.draw is None:
            return
        
        font = self.get_font('medium')
        self.draw.text(xy, icon, font=font, fill=0)
    
    def draw_rectangle(
        self,
        xy: Tuple[int, int, int, int],
        outline: bool = True,
        fill: bool = False
    ):
        """Draw a rectangle"""
        if self.draw is None:
            return
        
        outline_color = 0 if outline else None
        fill_color = 0 if fill else None
        self.draw.rectangle(xy, outline=outline_color, fill=fill_color)
    
    def draw_line(self, xy: Tuple[int, int, int, int], width: int = 1):
        """Draw a line"""
        if self.draw is None:
            return
        
        self.draw.line(xy, fill=0, width=width)
    
    def load_sprite(self, sprite_path: Path) -> Optional[Image.Image]:
        """Load a sprite image"""
        try:
            sprite = Image.open(sprite_path)
            # Convert to 1-bit
            return sprite.convert('1')
        except Exception as e:
            print(f"Error loading sprite {sprite_path}: {e}")
            return None
    
    def paste_sprite(self, sprite: Image.Image, xy: Tuple[int, int]):
        """Paste a sprite onto the canvas"""
        if self.image is None:
            return
        
        self.image.paste(sprite, xy)
    
    def save_screenshot(self, filename: str):
        """Save current image as PNG (for debugging)"""
        if self.image:
            path = Config.DATA_DIR / filename
            self.image.save(path)
            print(f"Screenshot saved: {path}")


# Singleton instance
_display_manager: Optional[DisplayManager] = None


def get_display() -> DisplayManager:
    """Get display manager singleton"""
    global _display_manager
    if _display_manager is None:
        _display_manager = DisplayManager()
    return _display_manager


if __name__ == "__main__":
    # Test display manager
    import time
    
    display = get_display()
    display.init()
    
    # Test 1: Simple text
    img, draw = display.create_canvas()
    display.draw_text_centered(10, "E-Ink Pet Clock", 'large')
    display.draw_text_centered(40, "Display Test", 'medium')
    display.draw_text((10, 70), "Bottom left", 'small')
    display.draw_rectangle((5, 5, 245, 117), outline=True)
    display.display(use_partial=False)
    
    time.sleep(3)
    
    # Test 2: Multiple updates
    for i in range(5):
        img, draw = display.create_canvas()
        display.draw_text_centered(50, f"Update #{i+1}", 'xlarge')
        display.display(use_partial=True)
        time.sleep(1)
    
    print("Display test complete")
    display.sleep()
