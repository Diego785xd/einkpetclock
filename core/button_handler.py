"""
GPIO Button Handler for E-Ink Pet Clock using gpiozero
Handles button presses with debouncing and callbacks
"""
import time
from typing import Callable, Optional
from core.config import Config

# Try to import gpiozero (preferred) or RPi.GPIO (fallback)
try:
    from gpiozero import Button as GPIOZeroButton
    HAS_GPIOZERO = True
    print("Using gpiozero for button handling")
except ImportError:
    HAS_GPIOZERO = False
    try:
        import RPi.GPIO as GPIO
        HAS_GPIO = True
        print("Warning: gpiozero not available, falling back to RPi.GPIO")
    except (ImportError, RuntimeError):
        HAS_GPIO = False
        print("Warning: No GPIO library available. Using mock buttons.")


class MockButton:
    """Mock button for development/testing"""
    def __init__(self, pin):
        self.pin = pin
        self._when_pressed = None
        self._when_released = None
        self._when_held = None
        self.hold_time = 2.0
    
    @property
    def when_pressed(self):
        return self._when_pressed
    
    @when_pressed.setter
    def when_pressed(self, func):
        self._when_pressed = func
    
    @property
    def when_released(self):
        return self._when_released
    
    @when_released.setter
    def when_released(self, func):
        self._when_released = func
    
    @property
    def when_held(self):
        return self._when_held
    
    @when_held.setter
    def when_held(self, func):
        self._when_held = func
    
    def close(self):
        pass


class ButtonHandler:
    """
    Handles button inputs using gpiozero library
    Supports press, release, and long press (hold) events
    """
    
    def __init__(self):
        """Initialize button handler"""
        self.callbacks = {
            "return_press": None,
            "return_release": None,
            "return_hold": None,
            "action_press": None,
            "action_release": None,
            "action_hold": None,
            "go_press": None,
            "go_release": None,
            "go_hold": None,
        }
        
        # Track last press times for additional debouncing if needed
        self.last_press_time = {
            "return": 0,
            "action": 0,
            "go": 0
        }
        
        # Initialize buttons
        self._setup_buttons()
    
    def _setup_buttons(self):
        """Initialize GPIO buttons with gpiozero"""
        if HAS_GPIOZERO:
            # Use gpiozero (preferred)
            # pull_up=True means buttons connect to GND (active low)
            # bounce_time is debounce time in seconds
            debounce_sec = Config.BUTTON_DEBOUNCE_MS / 1000.0
            hold_time_sec = Config.BUTTON_LONG_PRESS_MS / 1000.0
            
            self.button_return = GPIOZeroButton(
                Config.BUTTON_RETURN,
                pull_up=True,
                bounce_time=debounce_sec,
                hold_time=hold_time_sec
            )
            self.button_action = GPIOZeroButton(
                Config.BUTTON_ACTION,
                pull_up=True,
                bounce_time=debounce_sec,
                hold_time=hold_time_sec
            )
            self.button_go = GPIOZeroButton(
                Config.BUTTON_GO,
                pull_up=True,
                bounce_time=debounce_sec,
                hold_time=hold_time_sec
            )
            
            # Assign callbacks
            self.button_return.when_pressed = self._return_pressed
            self.button_return.when_released = self._return_released
            self.button_return.when_held = self._return_held
            
            self.button_action.when_pressed = self._action_pressed
            self.button_action.when_released = self._action_released
            self.button_action.when_held = self._action_held
            
            self.button_go.when_pressed = self._go_pressed
            self.button_go.when_released = self._go_released
            self.button_go.when_held = self._go_held
            
            print("✓ GPIO buttons initialized with gpiozero")
            print(f"  RETURN: GPIO {Config.BUTTON_RETURN}")
            print(f"  ACTION: GPIO {Config.BUTTON_ACTION}")
            print(f"  GO:     GPIO {Config.BUTTON_GO}")
            
        else:
            # Use mock buttons for development
            print("⚠ Using mock buttons (no GPIO hardware)")
            self.button_return = MockButton(Config.BUTTON_RETURN)
            self.button_action = MockButton(Config.BUTTON_ACTION)
            self.button_go = MockButton(Config.BUTTON_GO)
    
    # Callback wrappers for RETURN button
    def _return_pressed(self):
        """Called when RETURN button is pressed"""
        if self.callbacks["return_press"]:
            self.callbacks["return_press"]()
    
    def _return_released(self):
        """Called when RETURN button is released"""
        if self.callbacks["return_release"]:
            self.callbacks["return_release"]()
    
    def _return_held(self):
        """Called when RETURN button is held"""
        if self.callbacks["return_hold"]:
            self.callbacks["return_hold"]()
    
    # Callback wrappers for ACTION button
    def _action_pressed(self):
        """Called when ACTION button is pressed"""
        if self.callbacks["action_press"]:
            self.callbacks["action_press"]()
    
    def _action_released(self):
        """Called when ACTION button is released"""
        if self.callbacks["action_release"]:
            self.callbacks["action_release"]()
    
    def _action_held(self):
        """Called when ACTION button is held"""
        if self.callbacks["action_hold"]:
            self.callbacks["action_hold"]()
    
    # Callback wrappers for GO button
    def _go_pressed(self):
        """Called when GO button is pressed"""
        if self.callbacks["go_press"]:
            self.callbacks["go_press"]()
    
    def _go_released(self):
        """Called when GO button is released"""
        if self.callbacks["go_release"]:
            self.callbacks["go_release"]()
    
    def _go_held(self):
        """Called when GO button is held"""
        if self.callbacks["go_hold"]:
            self.callbacks["go_hold"]()
    
    # Public API for registering callbacks
    def on_return_press(self, callback: Callable):
        """Register callback for RETURN button press"""
        self.callbacks["return_press"] = callback
    
    def on_return_release(self, callback: Callable):
        """Register callback for RETURN button release"""
        self.callbacks["return_release"] = callback
    
    def on_return_hold(self, callback: Callable):
        """Register callback for RETURN button long press"""
        self.callbacks["return_hold"] = callback
    
    def on_action_press(self, callback: Callable):
        """Register callback for ACTION button press"""
        self.callbacks["action_press"] = callback
    
    def on_action_release(self, callback: Callable):
        """Register callback for ACTION button release"""
        self.callbacks["action_release"] = callback
    
    def on_action_hold(self, callback: Callable):
        """Register callback for ACTION button long press"""
        self.callbacks["action_hold"] = callback
    
    def on_go_press(self, callback: Callable):
        """Register callback for GO button press"""
        self.callbacks["go_press"] = callback
    
    def on_go_release(self, callback: Callable):
        """Register callback for GO button release"""
        self.callbacks["go_release"] = callback
    
    def on_go_hold(self, callback: Callable):
        """Register callback for GO button long press"""
        self.callbacks["go_hold"] = callback
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if HAS_GPIOZERO:
            try:
                self.button_return.close()
                self.button_action.close()
                self.button_go.close()
                print("GPIO buttons cleaned up")
            except Exception as e:
                print(f"Warning: Error cleaning up buttons: {e}")


# Singleton instance
_button_handler: Optional[ButtonHandler] = None


def get_button_handler() -> ButtonHandler:
    """Get or create the singleton button handler"""
    global _button_handler
    if _button_handler is None:
        _button_handler = ButtonHandler()
    return _button_handler
