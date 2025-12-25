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
import threading
import time

from core.config import Config
from core.display import DisplayManager
from core.state import get_pet_state, get_message_log, get_settings, get_stats

# Check if we have EPD hardware
try:
    from waveshare_epd import epd2in13_V4
    HAS_EPD = True
except ImportError:
    HAS_EPD = False

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
    
    def __init__(self, display: DisplayManager):
        super().__init__(display)
        # Animation state
        self.current_frame = 0
        self.last_frame_time = 0
        self.animation_frames = []
        self.current_mood = None
        self.base_image_set = False  # Track if base image is set for partial updates
        
        # Sprite position (for partial updates)
        self.sprite_x = 250 - 64 - 5  # Right side with 5px margin
        self.sprite_y = 18  # Aligned with time
        self.sprite_size = 64
        
        # Time position (for partial updates)
        self.time_x = 5
        self.time_y = 18
        self.time_width = 170  # Approximate width for time text
        self.time_height = 50  # Approximate height for 48pt font
    
    def _get_animation_frames(self, mood: str) -> List[str]:
        """Get list of frame filenames for a given mood"""
        # Map moods to animation sequences (properly extracted frames)
        animation_map = {
            "happy": ["BunnyRun_frame{:02d}.png".format(i) for i in range(5)],      # Running happily
            "neutral": ["BunnyIdle_frame{:02d}.png".format(i) for i in range(8)],   # Idle breathing
            "sad": ["BunnyLieDown_frame{:02d}.png".format(i) for i in range(2)],    # Lying down
            "hungry": ["BunnyAttack_frame{:02d}.png".format(i) for i in range(7)],  # Attacking for food
            "sick": ["BunnyHurt_frame{:02d}.png".format(i) for i in range(3)],      # Hurt/sick
            "sleeping": ["BunnySleep_frame{:02d}.png".format(i) for i in range(2)], # Sleeping
            "dead": ["BunnyDead_frame{:02d}.png".format(i) for i in range(9)]       # Death animation
        }
        return animation_map.get(mood, animation_map["neutral"])
    
    def advance_frame(self):
        """Advance to next animation frame"""
        if self.animation_frames:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
    
    def render_full(self):
        """Full render - sets the base image for partial updates"""
        self.render(is_base_render=True)
    
    def render(self, is_base_render=False):
        """Render tamagotchi clock view with clock-focused layout
        
        Args:
            is_base_render: If True, renders full image and sets as base for partial updates
        """
        img, draw = self.display.create_canvas()
        
        pet = get_pet_state()
        msg_log = get_message_log()
        stats = get_stats()
        
        # Get time and date
        time_str = self.get_current_time_str()
        date_str = self.get_current_date_str()
        
        # OPTIMIZED LAYOUT - Use all available space:
        # Top: Date (top left)
        self.display.draw_text((5, 2), date_str, 'small')
        
        # Messages indicator (top right corner)
        unread = msg_log.get_unread_count()
        if unread > 0:
            self.display.draw_text((200, 2), f"{unread} msgs", 'small')
        
        # Network error indicator (top right corner, after messages)
        if stats.get("last_error"):
            self.display.draw_text((235, 2), "!", 'small')
        
        # Big Time (left side, 48pt font)
        self.display.draw_text((5, 18), time_str, 'huge')  # 48pt font
        
        # Bunny sprite with animation (right side, aligned with time)
        mood = pet.get_mood()
        
        # Update animation frames if mood changed
        if mood != self.current_mood:
            self.current_mood = mood
            self.animation_frames = self._get_animation_frames(mood)
            self.current_frame = 0
        
        # Get current frame filename
        if self.animation_frames:
            sprite_filename = self.animation_frames[self.current_frame]
        else:
            # Fallback to static sprite
            sprite_filename = {
                "happy": "happy.png",
                "neutral": "neutral.png",
                "sad": "sad.png",
                "hungry": "excited.png",
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
            sprite_x = 250 - 64 - 5  # Right side with 5px margin
            sprite_y = 18  # Aligned with time
            
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
        
        # Pet stats (right below time text, stacked vertically with labels)
        # Time is at y=18 with 48pt font, which takes ~48-64px height
        # So time ends around y=66-82. Start stats at y=70 to avoid overlap
        stats_start_y = 70  # Moved down to avoid overlap with 48pt time
        line_height = 11  # Tight line spacing (12pt font height)
        
        # Health with label (line 1)
        health_icons = "<3 " * min(pet.health // 3, 3)
        health_display = health_icons if health_icons else "<3 "
        self.display.draw_text((5, stats_start_y), f"Health: {health_display}", 'small')
        
        # Hunger with label (line 2)
        hunger_level = max(0, min(3, pet.hunger // 3))
        if hunger_level == 0:
            hunger_display = "Full"
        else:
            hunger_display = "*" * hunger_level
        self.display.draw_text((5, stats_start_y + line_height), f"Food:   {hunger_display}", 'small')
        
        # Mood with label and emoji (line 3)
        mood_icon = {
            "happy": ":)",
            "neutral": ":|",
            "sad": ":(",
            "hungry": ":P",
            "sick": ":X",
            "sleeping": "ZZ",
            "dead": "XX"
        }.get(mood, ":|")
        self.display.draw_text((5, stats_start_y + line_height * 2), f"Mood:   {mood_icon}", 'small')
        
        # Bottom divider line - positioned to be below all stats
        self.display.draw_line((0, 106, 250, 106))
        
        # Button hints (very bottom, below divider)
        self.display.draw_text((3, 109), "[Feed]", 'small')
        self.display.draw_text((85, 109), "[Menu]", 'small')
        self.display.draw_text((215, 109), "[>]", 'small')
        
        # Display strategy
        if is_base_render or not self.base_image_set:
            # First render or full refresh - set as base image
            self.display.display(use_partial=False)  # Full refresh to clear ghosting
            # Now set this as the base for partial updates
            if HAS_EPD:
                from core.display import get_display
                display_obj = get_display()
                if hasattr(display_obj, 'epd'):
                    display_obj.epd.displayPartBaseImage(display_obj.epd.getbuffer(img))
                    self.base_image_set = True
                    if Config.DEBUG_MODE:
                        print("Base image set for partial updates")
        else:
            # Partial update - only changed areas
            self.display.display(use_partial=True, partial_mode="true")
    
    def update_sprite_only(self):
        """Update only the sprite area (for animation)"""
        if not self.base_image_set:
            # Need base image first - trigger full render
            if Config.DEBUG_MODE:
                print("Base image not set, triggering full render")
            self.render_full()
            return
        
        # Validate display state
        from core.display import get_display
        display_obj = get_display()
        
        if not display_obj.image or not display_obj.draw:
            print("⚠ Display state invalid, resetting base image")
            self.base_image_set = False
            return
        
        pet = get_pet_state()
        mood = pet.get_mood()
        
        # Update animation frames if mood changed
        if mood != self.current_mood:
            self.current_mood = mood
            self.animation_frames = self._get_animation_frames(mood)
            self.current_frame = 0
        
        # Get current frame filename
        if self.animation_frames:
            sprite_filename = self.animation_frames[self.current_frame]
        else:
            sprite_filename = "neutral.png"
        
        sprite_path = SPRITES_DIR / sprite_filename
        
        if sprite_path.exists():
            try:
                # Clear the sprite area (draw white rectangle)
                display_obj.draw.rectangle(
                    [(self.sprite_x, self.sprite_y), 
                     (self.sprite_x + self.sprite_size, self.sprite_y + self.sprite_size)],
                    fill=255
                )
                
                # Load and paste new sprite
                sprite = Image.open(sprite_path)
                sprite_large = sprite.resize((self.sprite_size, self.sprite_size), Image.NEAREST)
                display_obj.image.paste(sprite_large, (self.sprite_x, self.sprite_y))
                
                # Partial update only the sprite area
                if hasattr(display_obj, 'epd') and HAS_EPD:
                    display_obj.epd.displayPartial(display_obj.epd.getbuffer(display_obj.image))
                    if Config.DEBUG_MODE:
                        print(f"Sprite updated (frame {self.current_frame})")
            except Exception as e:
                print(f"Error updating sprite: {e}")
                self.base_image_set = False  # Reset on error
    
    def update_time_only(self):
        """Update only the time area"""
        if not self.base_image_set:
            # Need base image first
            if Config.DEBUG_MODE:
                print("Base image not set for time update, triggering full render")
            self.render_full()
            return
        
        from core.display import get_display
        display_obj = get_display()
        
        if not display_obj.image or not display_obj.draw:
            print("⚠ Display state invalid for time update, resetting base image")
            self.base_image_set = False
            return
        
        try:
            # Clear the time area (draw white rectangle)
            display_obj.draw.rectangle(
                [(self.time_x, self.time_y), 
                 (self.time_x + self.time_width, self.time_y + self.time_height)],
                fill=255
            )
            
            # Redraw time
            time_str = self.get_current_time_str()
            display_obj.draw_text((self.time_x, self.time_y), time_str, 'huge')
            
            # Partial update only the time area
            if hasattr(display_obj, 'epd') and HAS_EPD:
                display_obj.epd.displayPartial(display_obj.epd.getbuffer(display_obj.image))
                if Config.DEBUG_MODE:
                    print("Time updated")
        except Exception as e:
            print(f"Error updating time: {e}")
            self.base_image_set = False  # Reset on error
    
    def reset_base_image(self):
        """Reset base image flag when menu changes"""
        self.base_image_set = False
    
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
    
    def render(self, use_partial=True):
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
        
        self.display.display(use_partial=use_partial)
    
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
    
    def render(self, use_partial=True):
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
        
        self.display.display(use_partial=use_partial)
    
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
    
    def render(self, use_partial=True):
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
        
        self.display.display(use_partial=use_partial)
    
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
    """Manages menu navigation and state with thread safety and throttling"""
    
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
        
        # Thread safety
        self._lock = threading.Lock()
        self._rendering = False
        self._in_transition = False  # NEW: Prevents updates during menu changes
        
        # Button press throttling
        self._last_button_press = 0
        self._min_button_interval = 0.3  # 300ms minimum between button presses
        
        # Error recovery
        self._render_failures = 0
        self._max_render_failures = 3
    
    @property
    def current_menu(self) -> Menu:
        """Get currently active menu"""
        return self.menus[self.current_menu_index]
    
    def is_in_transition(self) -> bool:
        """Check if menu is currently transitioning (prevents animation updates)"""
        return self._in_transition or self._rendering
    
    def _can_process_button(self) -> bool:
        """Check if enough time has passed since last button press"""
        now = time.time()
        if now - self._last_button_press < self._min_button_interval:
            if Config.DEBUG_MODE:
                print(f"Button press throttled (too fast)")
            return False
        self._last_button_press = now
        return True
    
    def _safe_render(self, menu_func):
        """Safely render a menu with error recovery"""
        try:
            menu_func()
            self._render_failures = 0  # Reset on success
            return True
        except Exception as e:
            self._render_failures += 1
            print(f"Error rendering menu: {e}")
            
            if self._render_failures >= self._max_render_failures:
                print("Too many render failures, resetting to main menu")
                self.current_menu_index = 0
                self._render_failures = 0
                try:
                    self.menus[0].render()
                except Exception as e2:
                    print(f"Fatal: Cannot render main menu: {e2}")
            return False
    
    def next_menu(self):
        """Switch to next menu with thread safety"""
        with self._lock:
            if self._rendering or self._in_transition:
                if Config.DEBUG_MODE:
                    print("Render/transition in progress, skipping menu switch")
                return
            
            if not self._can_process_button():
                return
            
            self._in_transition = True  # Block all updates during transition
            self._rendering = True
        
        # Release lock before rendering (which is slow)
        try:
            old_menu_index = self.current_menu_index
            self.current_menu_index = (self.current_menu_index + 1) % len(self.menus)
            self.needs_render = True
            
            # Reset base image for ALL menus (clear stale state)
            for menu in self.menus:
                if hasattr(menu, 'base_image_set'):
                    menu.base_image_set = False
            
            # Use full render when changing menus to prevent ghosting
            if self.needs_render:
                if self.current_menu_index == 0 and hasattr(self.current_menu, 'render_full'):
                    # Going to main menu - set up for partial updates
                    self._safe_render(self.current_menu.render_full)
                else:
                    # Other menus - use full refresh to clear ghosting
                    if hasattr(self.current_menu, 'render'):
                        self._safe_render(lambda: self.current_menu.render(use_partial=False))
                    else:
                        self._safe_render(self.current_menu.render)
                self.needs_render = False
            
            # Small delay to ensure display settles (outside lock!)
            time.sleep(0.1)
            
        finally:
            with self._lock:
                self._rendering = False
                self._in_transition = False  # Re-enable updates
    
    def handle_return(self):
        """Handle RETURN button with thread safety"""
        with self._lock:
            if self._rendering or self._in_transition:
                if Config.DEBUG_MODE:
                    print("Render/transition in progress, ignoring button press")
                return
            
            if not self._can_process_button():
                return
            
            if self.current_menu_index == 0:
                # On main menu, RETURN feeds pet - no transition needed
                self._rendering = True
        
        # Release lock before potentially slow operations
        try:
            if self.current_menu_index == 0:
                # On main menu, RETURN feeds pet
                self.current_menu.on_return()
            else:
                # On other menus, RETURN goes back to main
                with self._lock:
                    self._in_transition = True  # Block updates during transition
                    self._rendering = True
                
                self.current_menu_index = 0
                self.needs_render = True
                
                # Reset base image for ALL menus
                for menu in self.menus:
                    if hasattr(menu, 'base_image_set'):
                        menu.base_image_set = False
                
                if self.needs_render:
                    # Use full render when going back to main menu
                    if hasattr(self.current_menu, 'render_full'):
                        self._safe_render(self.current_menu.render_full)
                    else:
                        self._safe_render(self.current_menu.render)
                    self.needs_render = False
                
                # Small delay to ensure display settles (outside lock!)
                time.sleep(0.1)
                
        finally:
            with self._lock:
                self._rendering = False
                if self.current_menu_index != 0:
                    self._in_transition = False  # Re-enable updates if we transitioned
    
    def handle_action(self):
        """Handle ACTION button (switch menu) with thread safety"""
        self.next_menu()
    
    def handle_go(self):
        """Handle GO button with thread safety"""
        with self._lock:
            if self._rendering:
                if Config.DEBUG_MODE:
                    print("Render in progress, ignoring button press")
                return
            
            if not self._can_process_button():
                return
            
            self._rendering = True
            try:
                self.current_menu.on_go()
            finally:
                self._rendering = False
    
    def render_current(self):
        """Render current menu if needed with thread safety"""
        # Use try_lock to avoid blocking the main loop
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            if Config.DEBUG_MODE:
                print("Render locked, skipping")
            return
        
        try:
            if self.needs_render and not self._rendering:
                self._rendering = True
                try:
                    self._safe_render(self.current_menu.render)
                    self.needs_render = False
                finally:
                    self._rendering = False
        finally:
            self._lock.release()
    
    def request_render(self):
        """Mark that a render is needed (thread-safe)"""
        with self._lock:
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
