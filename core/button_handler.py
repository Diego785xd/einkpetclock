"""
GPIO Button Handler for E-Ink Pet Clock using gpiozero
Handles button presses with debouncing and event queue
"""
from typing import Optional
import time
import queue
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
    """Handles button inputs using gpiozero library with event queue"""
    
    def __init__(self):
        # Event queue with maxsize=1: only keeps the most recent event
        # This acts as a natural debouncer - new presses overwrite pending ones
        self.event_queue = queue.Queue(maxsize=1)
        
        # Last button press time for additional debouncing
        self._last_button_time = {}
        self._debounce_seconds = 0.2  # 200ms software debounce
        
        self._setup_buttons()
    
    def _queue_event(self, button_name: str):
        """Queue a button event (non-blocking, instant return)"""
        # Software debounce check
        now = time.time()
        last_time = self._last_button_time.get(button_name, 0)
        
        if now - last_time < self._debounce_seconds:
            # Too soon after last press of this button, ignore
            return
        
        self._last_button_time[button_name] = now
        
        # Try to put event in queue
        # If queue is full (already has an event), this will fail silently
        # which is what we want - the pending event is still valid
        try:
            self.event_queue.put_nowait(button_name)
        except queue.Full:
            # Queue already has an event, that's fine
            # The user will process that one first
            if Config.DEBUG_MODE:
                print(f"⚠ Event queue full, {button_name} press will be processed next")
    
    def get_event(self, timeout: float = 0) -> Optional[str]:
        """
        Get the next button event from queue (non-blocking by default)
        
        Args:
            timeout: Seconds to wait for event (0 = non-blocking)
            
        Returns:
            Button name string or None if no event
        """
        try:
            return self.event_queue.get(block=(timeout > 0), timeout=timeout if timeout > 0 else None)
        except queue.Empty:
            return None
    
    def has_event(self) -> bool:
        """Check if there's a pending button event"""
        return not self.event_queue.empty()
    
    def _setup_buttons(self):
        """Initialize GPIO buttons with gpiozero"""
        if HAS_GPIOZERO:
            debounce_sec = Config.BUTTON_DEBOUNCE_MS / 1000.0
            hold_time_sec = Config.BUTTON_LONG_PRESS_MS / 1000.0
            
            self.button_return = GPIOZeroButton(Config.BUTTON_RETURN, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            self.button_action = GPIOZeroButton(Config.BUTTON_ACTION, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            self.button_go = GPIOZeroButton(Config.BUTTON_GO, pull_up=True, bounce_time=debounce_sec, hold_time=hold_time_sec)
            
            # Set up callbacks to queue events (instant, non-blocking)
            self.button_return.when_pressed = lambda: self._queue_event("return_press")
            self.button_action.when_pressed = lambda: self._queue_event("action_press")
            self.button_action.when_held = lambda: self._queue_event("action_hold")
            self.button_go.when_pressed = lambda: self._queue_event("go_press")
            
            print("✓ GPIO buttons initialized with gpiozero (event queue mode)")
            print(f"  RETURN: GPIO {Config.BUTTON_RETURN}")
            print(f"  ACTION: GPIO {Config.BUTTON_ACTION}")
            print(f"  GO:     GPIO {Config.BUTTON_GO}")
        else:
            print("⚠ Using mock buttons")
            self.button_return = MockButton(Config.BUTTON_RETURN)
            self.button_action = MockButton(Config.BUTTON_ACTION)
            self.button_go = MockButton(Config.BUTTON_GO)
    
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
