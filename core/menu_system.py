"""
Menu System and Renderer for E-Ink Pet Clock
Handles different menus and their rendering
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
import pytz
from pathlib import Path
from PIL import Image

from core.config import Config
from core.display import DisplayManager
from core.state import get_pet_state, get_message_log, get_settings, get_stats

# Path to sprite assets
SPRITES_DIR = Path(__file__).parent.parent / "assets" / "sprites"


class Menu(ABC):
    """Base class for all menus"""
    
    def __init__(self, display: DisplayManager):
        self.display = display
    
    @abstractmethod
    def render(self):
        """Render the menu"""
        pass
    
    @abstractmethod
    def on_return(self):
        """Handle RETURN button press"""
        pass
    
    @abstractmethod
    def on_go(self):
        """Handle GO button press"""
        pass
    
    def get_current_time_str(self, include_seconds: bool = False) -> str:
        """Get formatted time string"""
        settings = get_settings()
        tz = pytz.timezone(Config.DEVICE_TIMEZONE)
        now = datetime.now(tz)
        
        time_format = settings.get("time_format", Config.TIME_FORMAT)
        
        if time_format == 12:
            if include_seconds:
                return now.strftime("%I:%M:%S %p")
            return now.strftime("%I:%M %p")
        else:
            if include_seconds:
                return now.strftime("%H:%M:%S")
            return now.strftime("%H:%M")
    
    def get_current_date_str(self) -> str:
        """Get formatted date string"""
        tz = pytz.timezone(Config.DEVICE_TIMEZONE)
        now = datetime.now(tz)
        return now.strftime("%a, %b %d")


class TamagotchiMenu(Menu):
    """Main menu with tamagotchi and clock"""
    
    def render(self):
        """Render tamagotchi clock view with clock-focused layout"""
        img, draw = self.display.create_canvas()
        
        pet = get_pet_state()
        msg_log = get_message_log()
        stats = get_stats()
        
        # Get time and date
        time_str = self.get_current_time_str()
        date_str = self.get_current_date_str()
        
        # NEW LAYOUT:
        # Top left: Date (small)
        self.display.draw_text((5, 5), date_str, 'medium')
        
        # Center-left: GIANT Time (64pt - same height as bunny sprite)
        self.display.draw_text((10, 25), time_str, 'giant')
        
        # Right side: Bunny sprite (64x64 - double size)
        mood = pet.get_mood()
        sprite_filename = {
            "happy": "happy.png",
            "neutral": "neutral.png",
            "sad": "sad.png",
            "hungry": "excited.png",  # Use excited/run animation for hungry
            "sick": "sick.png",
            "sleeping": "sleeping.png",
            "dead": "dead.png"
        }.get(mood, "neutral.png")
        
        sprite_path = SPRITES_DIR / sprite_filename
        
        if sprite_path.exists():
            # Load sprite and resize to 64x64 (double size)
            sprite = Image.open(sprite_path)
            sprite_large = sprite.resize((64, 64), Image.NEAREST)  # NEAREST for pixel art
            
            # Position on right side, aligned with time
            sprite_x = 250 - 64 - 10  # Right side with 10px margin
            sprite_y = 25  # Same vertical position as time
            
            # Paste sprite onto the canvas
            img.paste(sprite_large, (sprite_x, sprite_y))
        else:
            # Fallback to ASCII art if sprite not found
            pet_x, pet_y = 180, 30
            bunny_art = [
                "(\\___/)",
                "( o.o )",
                " > ^ <"
            ]
            for i, line in enumerate(bunny_art):
                self.display.draw_text((pet_x, pet_y + i * 12), line, 'small')
        
        # Bottom bar separator line
        self.display.draw_line((0, 95, 250, 95))
        
        # Pet stats (bottom bar - condensed)
        stats_y = 98
        
        # Health indicator
        health_icons = "<3 " * min(pet.health // 3, 3)
        self.display.draw_text((5, stats_y), health_icons or "HP:0", 'small')
        
        # Hunger indicator
        hunger_level = max(0, min(3, pet.hunger // 3))
        hunger_bars = "*" * hunger_level if hunger_level > 0 else "FED"
        self.display.draw_text((50, stats_y), hunger_bars, 'small')
        
        # Mood indicator
        mood_icon = {
            "happy": ":)",
            "neutral": ":|",
            "sad": ":(",
            "hungry": ":P",
            "sick": ":X"
        }.get(mood, ":|")
        self.display.draw_text((90, stats_y), mood_icon, 'small')
        
        # Unread message indicator
        unread = msg_log.get_unread_count()
        if unread > 0:
            self.display.draw_text((120, stats_y), f"MSG:{unread}", 'small')
        
        # Network error indicator (top right corner)
        if stats.get("last_error"):
            self.display.draw_text((230, 5), "!", 'small')
        
        # Button hints (very bottom)
        self.display.draw_text((5, 110), "[Feed]", 'small')
        self.display.draw_text((90, 110), "[Msg]", 'small')
        self.display.draw_text((210, 110), "[>]", 'small')
        
        self.display.display(use_partial=True)
    
    def on_return(self):
        """Feed the pet"""
        pet = get_pet_state()
        pet.feed()
        stats = get_stats()
        stats.increment("total_button_presses")
        self.render()  # Immediate visual feedback
    
    def on_go(self):
        """Send message to other device (handled by network layer)"""
        from web.network_client import send_poke  # Avoid circular import
        pet = get_pet_state()
        stats = get_stats()
        
        try:
            if send_poke():
                pet.message_sent()
                stats.increment("total_messages_sent")
        except Exception as e:
            print(f"Error sending poke: {e}")
            stats.record_error(str(e))
        
        stats.increment("total_button_presses")
        self.render()


class MessagesMenu(Menu):
    """Message inbox view"""
    
    def __init__(self, display: DisplayManager):
        super().__init__(display)
        self.selected_index = 0
    
    def render(self):
        """Render message list"""
        img, draw = self.display.create_canvas()
        
        msg_log = get_message_log()
        messages = msg_log.get_messages(limit=5)
        
        # Header
        unread = msg_log.get_unread_count()
        header = f"Messages ({len(messages)})" + (f" - {unread} new" if unread > 0 else "")
        self.display.draw_text((5, 5), header, 'medium')
        
        # Small time in corner
        time_str = self.get_current_time_str()
        self.display.draw_text((180, 5), time_str, 'small')
        
        self.display.draw_line((5, 22, 245, 22))
        
        # Message list
        if not messages:
            self.display.draw_text_centered(50, "No messages", 'medium')
        else:
            y_offset = 28
            for i, msg in enumerate(messages[:3]):  # Show up to 3 messages
                prefix = ">" if i == self.selected_index else " "
                from_device = msg.get("from", "Unknown")
                text = msg.get("message", "")
                
                # Truncate long messages
                if len(text) > 20:
                    text = text[:17] + "..."
                
                msg_text = f"{prefix} {text} -{from_device}"
                self.display.draw_text((5, y_offset), msg_text, 'small')
                y_offset += 16
        
        # Button hints
        self.display.draw_text((5, 110), "[Back]", 'small')
        self.display.draw_text((80, 110), "[Read]", 'small')
        self.display.draw_text((210, 110), "[>]", 'small')
        
        self.display.display(use_partial=True)
    
    def on_return(self):
        """Go back (will be handled by menu state machine)"""
        pass
    
    def on_go(self):
        """Navigate messages or mark as read"""
        msg_log = get_message_log()
        messages = msg_log.get_messages(limit=5)
        
        if messages:
            self.selected_index = (self.selected_index + 1) % min(len(messages), 3)
            msg_log.mark_all_read()
            self.render()


class StatsMenu(Menu):
    """Statistics and history view"""
    
    def __init__(self, display: DisplayManager):
        super().__init__(display)
        self.page = 0
    
    def render(self):
        """Render statistics"""
        img, draw = self.display.create_canvas()
        
        pet = get_pet_state()
        stats = get_stats()
        
        # Header
        self.display.draw_text((5, 5), "Pet Stats", 'medium')
        time_str = self.get_current_time_str()
        self.display.draw_text((180, 5), time_str, 'small')
        
        self.display.draw_line((5, 22, 245, 22))
        
        # Stats content
        y = 30
        line_height = 14
        
        # Age
        age_days = pet.age_hours // 24
        age_hours = pet.age_hours % 24
        self.display.draw_text((10, y), f"Age: {age_days}d {age_hours}h", 'small')
        y += line_height
        
        # Feeds
        self.display.draw_text((10, y), f"Fed: {pet.get('total_feeds', 0)} times", 'small')
        y += line_height
        
        # Messages
        sent = pet.get('messages_sent', 0)
        received = pet.get('messages_received', 0)
        self.display.draw_text((10, y), f"Msgs: {sent} sent, {received} rcv", 'small')
        y += line_height
        
        # Happiness rating
        happiness_stars = "★" * (pet.happiness // 2) + "☆" * (5 - pet.happiness // 2)
        self.display.draw_text((10, y), f"Mood: {happiness_stars}", 'small')
        y += line_height
        
        # Current stats
        self.display.draw_text((10, y), f"H:{pet.health} F:{10-pet.hunger} M:{pet.happiness}", 'small')
        
        # Button hints
        self.display.draw_text((5, 110), "[Back]", 'small')
        self.display.draw_text((80, 110), "[Next]", 'small')
        self.display.draw_text((210, 110), "[>]", 'small')
        
        self.display.display(use_partial=True)
    
    def on_return(self):
        """Go back"""
        pass
    
    def on_go(self):
        """Cycle through stat pages"""
        self.page = (self.page + 1) % 2
        self.render()


class SettingsMenu(Menu):
    """Settings configuration view"""
    
    def __init__(self, display: DisplayManager):
        super().__init__(display)
        self.selected_item = 0
        self.items = ["time_format", "brightness", "refresh_mode"]
    
    def render(self):
        """Render settings"""
        img, draw = self.display.create_canvas()
        
        settings = get_settings()
        
        # Header
        self.display.draw_text((5, 5), "Settings", 'medium')
        time_str = self.get_current_time_str()
        self.display.draw_text((180, 5), time_str, 'small')
        
        self.display.draw_line((5, 22, 245, 22))
        
        # Settings list
        y = 30
        line_height = 16
        
        # Time format
        time_format = settings.get("time_format", 24)
        prefix = ">" if self.selected_item == 0 else " "
        self.display.draw_text((10, y), f"{prefix} Time: {time_format}h", 'small')
        y += line_height
        
        # Brightness
        brightness = settings.get("brightness", 3)
        prefix = ">" if self.selected_item == 1 else " "
        bars = "■" * brightness + "□" * (5 - brightness)
        self.display.draw_text((10, y), f"{prefix} Bright: {bars}", 'small')
        y += line_height
        
        # Refresh mode
        refresh = settings.get("refresh_mode", "balanced")
        prefix = ">" if self.selected_item == 2 else " "
        self.display.draw_text((10, y), f"{prefix} Refresh: {refresh}", 'small')
        y += line_height
        
        # Device info
        y += 10
        self.display.draw_text((10, y), f"Device: {Config.DEVICE_NAME}", 'small')
        
        # Button hints
        self.display.draw_text((5, 110), "[Back]", 'small')
        self.display.draw_text((80, 110), "[Chg]", 'small')
        self.display.draw_text((210, 110), "[>]", 'small')
        
        self.display.display(use_partial=True)
    
    def on_return(self):
        """Go back"""
        pass
    
    def on_go(self):
        """Change selected setting"""
        settings = get_settings()
        
        if self.selected_item == 0:  # Time format
            current = settings.get("time_format", 24)
            settings.set("time_format", 12 if current == 24 else 24)
        
        elif self.selected_item == 1:  # Brightness
            current = settings.get("brightness", 3)
            settings.set("brightness", (current % 5) + 1)
        
        elif self.selected_item == 2:  # Refresh mode
            modes = ["fast", "balanced", "slow"]
            current = settings.get("refresh_mode", "balanced")
            current_idx = modes.index(current) if current in modes else 1
            settings.set("refresh_mode", modes[(current_idx + 1) % len(modes)])
        
        self.selected_item = (self.selected_item + 1) % len(self.items)
        self.render()


class MenuStateMachine:
    """Manages menu navigation and state"""
    
    def __init__(self, display: DisplayManager):
        self.display = display
        self.menus = [
            TamagotchiMenu(display),
            MessagesMenu(display),
            StatsMenu(display),
            SettingsMenu(display),
        ]
        self.current_menu_index = 0
        self.needs_render = True
    
    @property
    def current_menu(self) -> Menu:
        """Get currently active menu"""
        return self.menus[self.current_menu_index]
    
    def next_menu(self):
        """Switch to next menu"""
        self.current_menu_index = (self.current_menu_index + 1) % len(self.menus)
        self.needs_render = True
        
        # Use full refresh when changing menus
        if self.needs_render:
            self.current_menu.render()
            self.needs_render = False
    
    def handle_return(self):
        """Handle RETURN button"""
        if self.current_menu_index == 0:
            # On main menu, RETURN feeds pet
            self.current_menu.on_return()
        else:
            # On other menus, RETURN goes back to main
            self.current_menu_index = 0
            self.needs_render = True
    
    def handle_action(self):
        """Handle ACTION button (switch menu)"""
        self.next_menu()
    
    def handle_go(self):
        """Handle GO button"""
        self.current_menu.on_go()
    
    def render_current(self):
        """Render current menu if needed"""
        if self.needs_render:
            self.current_menu.render()
            self.needs_render = False
    
    def request_render(self):
        """Mark that a render is needed"""
        self.needs_render = True


if __name__ == "__main__":
    # Test menu rendering
    from core.display import get_display
    
    display = get_display()
    display.init()
    
    menu_system = MenuStateMachine(display)
    
    # Test each menu
    import time
    for i in range(4):
        print(f"Rendering menu {i}")
        menu_system.render_current()
        time.sleep(3)
        menu_system.next_menu()
    
    print("Menu test complete")
    display.sleep()
