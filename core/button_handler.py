"""
GPIO Button Handler for E-Ink Pet Clock
Handles button presses with debouncing and callbacks
"""
import time
from typing import Callable, Optional
from core.config import Config

# Try to import RPi.GPIO, fall back to mock for development
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except (ImportError, RuntimeError):
    HAS_GPIO = False
    print("Warning: RPi.GPIO not available. Using mock GPIO.")


class MockGPIO:
    """Mock GPIO for development/testing"""
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    PUD_DOWN = "PUD_DOWN"
    FALLING = "FALLING"
    RISING = "RISING"
    BOTH = "BOTH"
    
    @staticmethod
    def setmode(mode):
        pass
    
    @staticmethod
    def setup(pin, mode, pull_up_down=None):
        pass
    
    @staticmethod
    def add_event_detect(pin, edge, callback=None, bouncetime=None):
        pass
    
    @staticmethod
    def remove_event_detect(pin):
        pass
    
    @staticmethod
    def cleanup():
        pass
    
    @staticmethod
    def input(pin):
        return 1  # Simulate button not pressed


class ButtonHandler:
    """Manages button inputs with debouncing and callbacks"""
    
    def __init__(self):
        self.gpio = GPIO if HAS_GPIO else MockGPIO()
        self.callbacks = {
            "return": None,
            "action": None,
            "go": None
        }
        self.last_press_time = {
            "return": 0,
            "action": 0,
            "go": 0
        }
        self.long_press_threshold = 2.0  # seconds for long press
        self.press_start_time = {
            "return": 0,
            "action": 0,
            "go": 0
        }
        self.is_long_press_triggered = {
            "return": False,
            "action": False,
            "go": False
        }
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Initialize GPIO pins"""
        if not HAS_GPIO and not Config.MOCK_HARDWARE:
            print("Warning: Running without GPIO hardware")
            return
        
        try:
            self.gpio.setmode(self.gpio.BCM)
            
            # Setup buttons with internal pull-up resistors
            self.gpio.setup(Config.BUTTON_RETURN, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
            self.gpio.setup(Config.BUTTON_ACTION, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
            self.gpio.setup(Config.BUTTON_GO, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
            
            # Add event detection for button presses (FALLING = button pressed)
            self.gpio.add_event_detect(
                Config.BUTTON_RETURN,
                self.gpio.FALLING,
                callback=self._return_button_callback,
            )
            self.gpio.add_event_detect(
                Config.BUTTON_ACTION,
                self.gpio.FALLING,
                callback=self._action_button_callback,
                bouncetime=Config.BUTTON_DEBOUNCE_MS
            )
            self.gpio.add_event_detect(
                Config.BUTTON_GO,
                self.gpio.FALLING,
                callback=self._go_button_callback,
                bouncetime=Config.BUTTON_DEBOUNCE_MS
            )
            
            print("GPIO buttons initialized")
            print(f"  RETURN: GPIO {Config.BUTTON_RETURN}")
            print(f"  ACTION: GPIO {Config.BUTTON_ACTION}")
            print(f"  GO:     GPIO {Config.BUTTON_GO}")
            
        except RuntimeError as e:
            print(f"\n{'='*60}")
            print("ERROR: Failed to initialize GPIO")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print()
            print("This usually means GPIO permission issues.")
            print()
            print("Quick fix (run on Pi):")
            print("  sudo bash scripts/fix_gpio_permissions.sh")
            print()
            print("Or manually fix:")
            print("  1. Run service as root:")
            print("     sudo sed -i 's/^User=.*/User=root/' /etc/systemd/system/eink-display.service")
            print("     sudo systemctl daemon-reload")
            print("     sudo systemctl restart eink-display")
            print()
            print("  2. Or add user to gpio group (requires logout):")
            print("     sudo usermod -a -G gpio $(whoami)")
            print(f"{'='*60}\n")
            raise
    def _debounce_check(self, button_name: str) -> bool:
        """Check if enough time has passed since last press"""
        now = time.time()
        time_since_last = now - self.last_press_time[button_name]
        debounce_time = Config.BUTTON_DEBOUNCE_MS / 1000.0
        
        if time_since_last < debounce_time:
            return False
        
        self.last_press_time[button_name] = now
        return True
    
    def _return_button_callback(self, channel):
        """Callback for RETURN button press"""
        if self._debounce_check("return") and self.callbacks["return"]:
            if Config.DEBUG_MODE:
                print("Button pressed: RETURN")
            self.callbacks["return"]()
    
    def _action_button_callback(self, channel):
        """Callback for ACTION button press"""
        if self._debounce_check("action") and self.callbacks["action"]:
            if Config.DEBUG_MODE:
                print("Button pressed: ACTION")
            self.callbacks["action"]()
    
    def _go_button_callback(self, channel):
        """Callback for GO button press"""
        if self._debounce_check("go") and self.callbacks["go"]:
            if Config.DEBUG_MODE:
                print("Button pressed: GO")
            self.callbacks["go"]()
    
    def on_return(self, callback: Callable[[], None]):
        """Register callback for RETURN button"""
        self.callbacks["return"] = callback
    
    def on_action(self, callback: Callable[[], None]):
        """Register callback for ACTION button"""
        self.callbacks["action"] = callback
    
    def on_go(self, callback: Callable[[], None]):
        """Register callback for GO button"""
        self.callbacks["go"] = callback
    
    def check_long_press(self, button_name: str, pin: int) -> bool:
        """Check if a button is being held for long press (call in main loop)"""
        if not HAS_GPIO:
            return False
        
        is_pressed = self.gpio.input(pin) == 0  # LOW = pressed
        
        if is_pressed:
            if self.press_start_time[button_name] == 0:
                self.press_start_time[button_name] = time.time()
                self.is_long_press_triggered[button_name] = False
            
            press_duration = time.time() - self.press_start_time[button_name]
            
            if press_duration >= self.long_press_threshold and not self.is_long_press_triggered[button_name]:
                self.is_long_press_triggered[button_name] = True
                return True
        else:
            # Button released
            self.press_start_time[button_name] = 0
            self.is_long_press_triggered[button_name] = False
        
        return False
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if HAS_GPIO:
            self.gpio.cleanup()
            print("GPIO cleanup complete")


# Singleton instance
_button_handler: Optional[ButtonHandler] = None


def get_button_handler() -> ButtonHandler:
    """Get button handler singleton"""
    global _button_handler
    if _button_handler is None:
        _button_handler = ButtonHandler()
    return _button_handler


if __name__ == "__main__":
    # Test button handler
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\nCleaning up...")
        buttons.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    buttons = get_button_handler()
    
    # Register test callbacks
    buttons.on_return(lambda: print("RETURN pressed!"))
    buttons.on_action(lambda: print("ACTION pressed!"))
    buttons.on_go(lambda: print("GO pressed!"))
    
    print("Button handler test running...")
    print("Press buttons to test. Ctrl+C to exit.")
    
    try:
        while True:
            # Check for long press on ACTION button
            if buttons.check_long_press("action", Config.BUTTON_ACTION):
                print("ACTION long press detected!")
            time.sleep(0.1)
    except KeyboardInterrupt:
        buttons.cleanup()
