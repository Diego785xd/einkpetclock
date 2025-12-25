"""
GPIO Button Handler for E-Ink Pet Clock using gpiozero
Handles button presses with debouncing and callbacks
"""
from typing import Callable, Optional
import time
import threading
from core.config import Config

# Try to import gpiozero
try:
    from gpiozero import Button as GPIOZeroButton
    HAS_GPIOZERO = True
except ImportError:
    HAS_GPIOZERO = False


class MockButton:
    """Mock button for development/testing"""
    def __init__(self, pin):
        self.pin = pin
        self._when_pressed = None
        self._when_held = None
        self.hold_time = 2.0
    
    @property
    def when_pressed(self):
        return self._when_pressed
    
    @when_pressed.setter
    def when_pressed(self, func):
        self._when_pressed = func
    
    @property
    def when_held(self):
        return self._when_held
    
    @when_held.setter
    def when_held(self, func):
        self._when_held = func
    
    def close(self):
        pass


class ButtonHandler:
    """Handles button inputs using gpiozero library with callback protection"""
    
    def __init__(self):
        self.callbacks = {
            "return_press": None,
            "action_press": None,
            "action_hold": None,
            "go_press": None,
        }
        
        # Callback protection
        self._callback_lock = threading.Lock()
        self._callback_running = False
        
        self._setup_buttons()
    
    def _safe_callback(self, callback_name: str):
        """Execute callback safely with lock protection"""
        # Try to acquire lock - if already processing, skip this press
        acquired = self._callback_lock.acquire(blocking=False)
        if not acquired:
            print(f"⚠ Callback {callback_name} skipped - previous callback still running")
            return
        
        try:
            self._callback_running = True
            callback = self.callbacks.get(callback_name)
            if callback:
                try:
                    callback()
                except Exception as e:
                    print(f"Error in button callback {callback_name}: {e}")
        finally:
            self._callback_running = False
            self._callback_lock.release()
    
    def _setup_buttons(self):
        """Initialize GPIO buttons with gpiozero"""
        if HAS_GPIOZERO:
            debounce_sec = Config.BUTTON_DEBOUNCE_MS / 1000.0
            hold_time_sec = Config.BUTTON_LONG_PRESS_MS / 1000.0
            
            self.button_return = GPIOZeroButton(Config.BUTTON_RETURN, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            self.button_action = GPIOZeroButton(Config.BUTTON_ACTION, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            self.button_go = GPIOZeroButton(Config.BUTTON_GO, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            
            self.button_return.when_pressed = self._return_pressed
            self.button_action.when_pressed = self._action_pressed
            self.button_action.when_held = self._action_held
            self.button_go.when_pressed = self._go_pressed
            
            print("✓ GPIO buttons initialized with gpiozero")
            print(f"  RETURN: GPIO {Config.BUTTON_RETURN}")
            print(f"  ACTION: GPIO {Config.BUTTON_ACTION}")
            print(f"  GO:     GPIO {Config.BUTTON_GO}")
        else:
            print("⚠ Using mock buttons")
            self.button_return = MockButton(Config.BUTTON_RETURN)
            self.button_action = MockButton(Config.BUTTON_ACTION)
            self.button_go = MockButton(Config.BUTTON_GO)
    
    def _return_pressed(self):
        self._safe_callback("return_press")
    
    def _action_pressed(self):
        self._safe_callback("action_press")
    
    def _action_held(self):
        self._safe_callback("action_hold")
    
    def _go_pressed(self):
        self._safe_callback("go_press")
    
    def on_return_press(self, callback: Callable):
        self.callbacks["return_press"] = callback
    
    def on_action_press(self, callback: Callable):
        self.callbacks["action_press"] = callback
    
    def on_action_hold(self, callback: Callable):
        self.callbacks["action_hold"] = callback
    
    def on_go_press(self, callback: Callable):
        self.callbacks["go_press"] = callback
    
    def cleanup(self):
        if HAS_GPIOZERO:
            try:
                self.button_return.close()
                self.button_action.close()
                self.button_go.close()
                print("GPIO buttons cleaned up")
            except Exception as e:
                print(f"Warning: Error cleaning up buttons: {e}")


_button_handler: Optional[ButtonHandler] = None


def get_button_handler() -> ButtonHandler:
    global _button_handler
    if _button_handler is None:
        _button_handler = ButtonHandler()
    return _button_handler
