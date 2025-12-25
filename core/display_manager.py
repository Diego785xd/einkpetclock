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
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print(f"Display Manager initialized for {Config.DEVICE_NAME}")
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\nShutdown signal received, cleaning up...")
        self.shutdown()
        sys.exit(0)
    
    def setup(self):
        """Initialize hardware and register button callbacks"""
        # Initialize display
        self.display.init()
        
        # Register button callbacks (using gpiozero API)
        self.buttons.on_return_press(self._on_return_button)
        self.buttons.on_action_press(self._on_action_button)
        self.buttons.on_go_press(self._on_go_button)
        
        # Initial render
        self.menu_system.render_current()
        
        print("Display Manager setup complete")
        print("Button mappings:")
        print("  RETURN (GPIO 6):  Feed pet / Back")
        print("  ACTION (GPIO 13): Switch menu")
        print("  GO (GPIO 19):     Send message / Action")
    
    def _on_return_button(self):
        """Handle RETURN button press"""
        self.stats.increment("total_button_presses")
        self.menu_system.handle_return()
        self.menu_system.request_render()
    
    def _on_action_button(self):
        """Handle ACTION button press"""
        self.stats.increment("total_button_presses")
        self.menu_system.handle_action()
    
    def _on_go_button(self):
        """Handle GO button press"""
        self.stats.increment("total_button_presses")
        self.menu_system.handle_go()
    
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
        
        # Only update every minute
        if (now - self.last_clock_update).seconds >= Config.CLOCK_UPDATE_INTERVAL:
            self.last_clock_update = now
            
            # If on main menu, re-render to update time
            if self.menu_system.current_menu_index == 0:
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
    
    def run(self):
        """Main event loop"""
        self.running = True
        
        print("Display Manager running...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                # Check for long press on ACTION button (could trigger special action)
                if self.buttons.check_long_press("action", Config.BUTTON_ACTION):
                    # Long press ACTION: could show settings or special menu
                    if Config.DEBUG_MODE:
                        print("ACTION long press detected")
                
                # Check flags from API
                now = datetime.now()
                if (now - self.last_flag_check).seconds >= 5:  # Check every 5 seconds
                    self.check_flags()
                    self.last_flag_check = now
                
                # Update clock periodically
                self.update_clock()
                
                # Update pet state periodically
                self.update_pet_state()
                
                # Render if needed
                self.menu_system.render_current()
                
                # Sleep to reduce CPU usage
                time.sleep(0.1)
        
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
