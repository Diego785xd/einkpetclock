#!/usr/bin/env python3
"""
Main Display Manager Service for E-Ink Pet Clock
Runs as systemd service, coordinates display, buttons, and pet state
"""
import signal
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

from core.config import Config
from core.display import get_display
from core.button_handler import get_button_handler
from core.menu_system import MenuStateMachine
from core.state import get_pet_state, get_stats


class DisplayManager:
    """Main display manager orchestrating the clock"""
    
    def __init__(self):
        self.running = False
        self.display = get_display()
        self.buttons = get_button_handler()
        self.menu_system = MenuStateMachine(self.display)
        self.pet = get_pet_state()
        self.stats = get_stats()
        
        # Timing
        self.last_clock_update = datetime.now()
        self.last_pet_update = datetime.now()
        self.last_flag_check = datetime.now()
        self.last_animation_update = datetime.now()
        self.last_full_refresh = datetime.now()  # Track last full refresh for 5-minute cycle
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print(f"Display Manager initialized for {Config.DEVICE_NAME}")
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\nShutdown signal received, cleaning up...")
        self.shutdown()
        sys.exit(0)
    
    def process_button_events(self):
        """Process any pending button events from queue (runs in main thread)"""
        event = self.buttons.get_event(timeout=0)  # Non-blocking
        
        if event is None:
            return  # No event pending
        
        # Process the event in main thread (no threading issues!)
        try:
            self.stats.increment("total_button_presses")
            
            if event == "return_press":
                if Config.DEBUG_MODE:
                    print("Processing RETURN button event")
                self.menu_system.handle_return()
                self.menu_system.request_render()
                
            elif event == "action_press":
                if Config.DEBUG_MODE:
                    print("Processing ACTION button event")
                self.menu_system.handle_action()
                
            elif event == "action_hold":
                if Config.DEBUG_MODE:
                    print("Processing ACTION hold event")
                # Long press - could do special action
                self.menu_system.handle_action()
                
            elif event == "go_press":
                if Config.DEBUG_MODE:
                    print("Processing GO button event")
                self.menu_system.handle_go()
                
        except Exception as e:
            print(f"Error processing button event '{event}': {e}")
            self.stats.record_error(f"Button {event}: {e}")
    
    def setup(self):
        """Initialize hardware (no callbacks - using event queue)"""
        # Initialize display
        self.display.init()
        
        # No callback registration needed - we poll the event queue instead
        
        # Initial render
        self.menu_system.render_current()
        
        print("Display Manager setup complete")
        print("Button mappings:")
        print("  RETURN (GPIO 6):  Feed pet / Back")
        print("  ACTION (GPIO 13): Switch menu")
        print("Using event queue for button handling (non-blocking)")
    
    def check_flags(self):
        """Check for flags from API service"""
        flag_dir = Path("/tmp/eink_flags")
        if not flag_dir.exists():
            return
        
        # Check for new message flag
        new_msg_flag = flag_dir / "new_message.flag"
        if new_msg_flag.exists():
            self.menu_system.request_render()
            new_msg_flag.unlink()
        
        # Check for feed flag
        feed_flag = flag_dir / "feed_pet.flag"
        if feed_flag.exists():
            self.menu_system.request_render()
            feed_flag.unlink()
        
        # Check for poke flag
        poke_flag = flag_dir / "poke.flag"
        if poke_flag.exists():
            self.menu_system.request_render()
            poke_flag.unlink()
    
    def update_clock(self):
        """Update clock display (called periodically)"""
        now = datetime.now()
        
        # Skip if in menu transition
        if self.menu_system.is_in_transition():
            return
        
        # Only update every minute
        if (now - self.last_clock_update).seconds >= Config.CLOCK_UPDATE_INTERVAL:
            self.last_clock_update = now
            
            # If on main menu, update only the time area
            if self.menu_system.current_menu_index == 0:
                main_menu = self.menu_system.menus[0]
                if hasattr(main_menu, 'update_time_only'):
                    try:
                        main_menu.update_time_only()
                    except Exception as e:
                        print(f"Error updating time: {e}")
                        # Reset base image on error
                        if hasattr(main_menu, 'base_image_set'):
                            main_menu.base_image_set = False
                else:
                    self.menu_system.request_render()
                self.stats.increment("total_display_updates")
    
    def update_pet_state(self):
        """Update pet state (hunger, happiness decay)"""
        now = datetime.now()
        
        # Update every hour
        if (now - self.last_pet_update).seconds >= Config.PET_UPDATE_INTERVAL:
            self.last_pet_update = now
            
            # Update pet decay
            self.pet.update_state()
            
            # If on main menu, re-render to show new state
            if self.menu_system.current_menu_index == 0:
                self.menu_system.request_render()
            
            if Config.DEBUG_MODE:
                print(f"Pet updated: H:{self.pet.health} F:{10-self.pet.hunger} M:{self.pet.happiness} Mood:{self.pet.get_mood()}")
    
    def update_animation(self):
        """Update animation frame"""
        now = datetime.now()
        
        # Skip if in menu transition
        if self.menu_system.is_in_transition():
            return
        
        # Update every 0.5 seconds
        time_diff = (now - self.last_animation_update).total_seconds()
        if time_diff >= 0.5:
            self.last_animation_update = now
            
            # Only animate on main menu
            if self.menu_system.current_menu_index == 0:
                # Get the main menu and advance frame, then update only sprite area
                main_menu = self.menu_system.menus[0]
                if hasattr(main_menu, 'advance_frame') and hasattr(main_menu, 'update_sprite_only'):
                    try:
                        main_menu.advance_frame()
                        main_menu.update_sprite_only()
                    except Exception as e:
                        print(f"Error updating sprite animation: {e}")
                        # Reset base image on error
                        if hasattr(main_menu, 'base_image_set'):
                            main_menu.base_image_set = False
    
    def check_full_refresh_needed(self):
        """Check if 5 minutes have passed and do a full refresh"""
        now = datetime.now()
        time_diff = (now - self.last_full_refresh).total_seconds()
        
        # Skip if in menu transition
        if self.menu_system.is_in_transition():
            return
        
        # Full refresh every 5 minutes (300 seconds)
        if time_diff >= 300:
            self.last_full_refresh = now
            
            # If on main menu, do full refresh
            if self.menu_system.current_menu_index == 0:
                main_menu = self.menu_system.menus[0]
                if hasattr(main_menu, 'render_full'):
                    print("Performing scheduled full refresh (5 min interval)")
                    try:
                        main_menu.render_full()
                    except Exception as e:
                        print(f"Error during scheduled full refresh: {e}")
                        # Try to recover
                        if hasattr(main_menu, 'base_image_set'):
                            main_menu.base_image_set = False
                else:
                    self.menu_system.request_render()
    
    def run(self):
        """Main event loop"""
        self.running = True
        
        print("Display Manager running...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                # Process button events (from event queue)
                self.process_button_events()
                
                # Check flags from API
                now = datetime.now()
                if (now - self.last_flag_check).seconds >= 5:  # Check every 5 seconds
                    self.check_flags()
                    self.last_flag_check = now
                
                # Update clock periodically
                self.update_clock()
                
                # Update pet state periodically
                self.update_pet_state()
                
                # Update animation frame
                self.update_animation()
                
                # Check if full refresh needed (every 5 minutes)
                self.check_full_refresh_needed()
                
                # Render if needed (for menu changes, etc.)
                self.menu_system.render_current()
                
                # Sleep to reduce CPU usage (but keep responsive to buttons)
                time.sleep(0.05)  # 50ms = 20 polls per second
        
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Error in main loop: {e}")
            self.stats.record_error(str(e))
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        if not self.running:
            return
        
        self.running = False
        
        print("Shutting down...")
        
        # Show shutdown message
        try:
            img, draw = self.display.create_canvas()
            self.display.draw_text_centered(50, "Shutting down...", 'medium')
            self.display.display(use_partial=False)
            time.sleep(1)
        except:
            pass
        
        # Cleanup hardware
        self.display.sleep()
        self.buttons.cleanup()
        
        print("Display Manager stopped")


def main():
    """Main entry point"""
    print("=" * 50)
    print("E-Ink Pet Clock - Display Manager")
    print("=" * 50)
    print(f"Device: {Config.DEVICE_NAME}")
    print(f"Pet: {Config.PET_NAME}")
    print(f"Debug mode: {Config.DEBUG_MODE}")
    print(f"Mock hardware: {Config.MOCK_HARDWARE}")
    print("=" * 50)
    
    manager = DisplayManager()
    manager.setup()
    manager.run()


if __name__ == "__main__":
    main()
