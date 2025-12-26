"""
File-based state management for E-Ink Pet Clock
Uses JSON files for persistent storage with atomic writes
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from core.config import Config


class StateManager:
    """Base class for JSON-based state management with atomic writes"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._state: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Load state from file"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {self.file_path}: {e}")
                self._state = self._default_state()
        else:
            self._state = self._default_state()
            self._save()
    
    def _save(self):
        """Atomically save state to file using temp file + rename"""
        tmp_path = self.file_path.with_suffix('.tmp')
        try:
            with open(tmp_path, 'w') as f:
                json.dump(self._state, f, indent=2)
            tmp_path.rename(self.file_path)
        except IOError as e:
            print(f"Error saving {self.file_path}: {e}")
            if tmp_path.exists():
                tmp_path.unlink()
    
    def _default_state(self) -> Dict[str, Any]:
        """Override in subclass to provide default state"""
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state"""
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value and save"""
        self._state[key] = value
        self._save()
    
    def update(self, **kwargs):
        """Update multiple values and save once"""
        self._state.update(kwargs)
        self._save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get state as dictionary"""
        return self._state.copy()


class PetState(StateManager):
    """Manages pet (bunny) state"""
    
    def __init__(self):
        super().__init__(Config.DATA_DIR / "pet_state.json")
    
    def _default_state(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "name": Config.PET_NAME,
            "type": Config.PET_TYPE,
            "hunger": 5,
            "happiness": 8,
            "health": 10,
            "last_fed": now,
            "last_interaction": now,
            "last_update": now,
            "created_at": now,
            "age_hours": 0,
            "total_feeds": 0,
            "total_interactions": 0,
            "messages_sent": 0,
            "messages_received": 0,
        }
    
    @property
    def hunger(self) -> int:
        return self._state["hunger"]
    
    @property
    def happiness(self) -> int:
        return self._state["happiness"]
    
    @property
    def health(self) -> int:
        return self._state["health"]
    
    @property
    def age_hours(self) -> int:
        return self._state["age_hours"]
    
    def feed(self):
        """Feed the pet"""
        now = datetime.now(timezone.utc).isoformat()
        self.update(
            hunger=max(0, self.hunger - 3),
            happiness=min(Config.MAX_HAPPINESS, self.happiness + 1),
            last_fed=now,
            last_interaction=now,
            total_feeds=self._state["total_feeds"] + 1
        )
    
    def interact(self):
        """Interact with pet (poke, pet, etc.)"""
        now = datetime.now(timezone.utc).isoformat()
        self.update(
            happiness=min(Config.MAX_HAPPINESS, self.happiness + 2),
            last_interaction=now,
            total_interactions=self._state["total_interactions"] + 1
        )
    
    def message_sent(self):
        """Record that a message was sent"""
        self.update(
            messages_sent=self._state["messages_sent"] + 1,
            last_interaction=datetime.now(timezone.utc).isoformat()
        )
    
    def message_received(self):
        """Record that a message was received"""
        self.update(
            messages_received=self._state["messages_received"] + 1
        )
    
    def update_state(self):
        """Update pet state based on time decay"""
        now = datetime.now(timezone.utc)
        last_update = datetime.fromisoformat(self._state["last_update"])
        hours_passed = (now - last_update).total_seconds() / 3600
        
        if hours_passed < 0.1:  # Less than 6 minutes, skip
            return
        
        # Calculate decay
        hunger_increase = int(hours_passed * Config.HUNGER_DECAY_RATE)
        happiness_decrease = int(hours_passed * Config.HAPPINESS_DECAY_RATE)
        
        # Update values
        new_hunger = min(Config.MAX_HUNGER, self.hunger + hunger_increase)
        new_happiness = max(0, self.happiness - happiness_decrease)
        
        # Health depends on hunger and happiness
        if new_hunger >= 8:
            new_health = max(0, self.health - 1)
        elif new_hunger <= 2 and new_happiness >= 7:
            new_health = min(Config.MAX_HEALTH, self.health + 1)
        else:
            new_health = self.health
        
        # Update age
        new_age_hours = self.age_hours + int(hours_passed)
        
        self.update(
            hunger=new_hunger,
            happiness=new_happiness,
            health=new_health,
            age_hours=new_age_hours,
            last_update=now.isoformat()
        )
    
    def get_mood(self) -> str:
        """Get pet mood based on stats"""
        if self.health <= 3:
            return "sick"
        elif self.hunger >= 7:
            return "hungry"
        elif self.happiness >= 8:
            return "happy"
        elif self.happiness <= 3:
            return "sad"
        else:
            return "neutral"


class MessageLog:
    """Manages message log using JSONL (JSON Lines) format"""
    
    def __init__(self):
        self.file_path = Config.DATA_DIR / "messages.jsonl"
        self.max_messages = 50
    
    def add_message(self, from_device: str, message: str, msg_type: str = "text"):
        """Add a new message to the log"""
        entry = {
            "id": int(datetime.now(timezone.utc).timestamp() * 1000),  # Unique ID based on timestamp
            "from": from_device,
            "message": message,
            "type": msg_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        
        # Append to file
        with open(self.file_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Trim if too many messages
        self._trim_if_needed()
    
    def get_messages(self, limit: int = 20, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get recent messages"""
        if not self.file_path.exists():
            return []
        
        messages = []
        with open(self.file_path, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    if not unread_only or not msg.get("read", False):
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
        
        # Return most recent first
        messages.reverse()
        return messages[:limit]
    
    def mark_all_read(self):
        """Mark all messages as read"""
        if not self.file_path.exists():
            return
        
        messages = []
        with open(self.file_path, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    msg["read"] = True
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue
        
        # Rewrite file
        with open(self.file_path, 'w') as f:
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
    
    def get_unread_count(self) -> int:
        """Get count of unread messages"""
        return len(self.get_messages(unread_only=True))
    
    def delete_message(self, msg_id: int):
        """Delete a message by ID"""
        if not self.file_path.exists():
            return
        
        messages = []
        with open(self.file_path, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    # Keep messages that don't match the ID
                    if msg.get("id") != msg_id:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
        
        # Rewrite file without the deleted message
        with open(self.file_path, 'w') as f:
            for msg in messages:
                f.write(json.dumps(msg) + '\n')
    
    def delete_most_recent(self):
        """Delete the most recent message"""
        if not self.file_path.exists():
            return
        
        messages = []
        with open(self.file_path, 'r') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue
        
        if messages:
            # Remove the last message (most recent)
            messages.pop()
            
            # Rewrite file
            with open(self.file_path, 'w') as f:
                for msg in messages:
                    f.write(json.dumps(msg) + '\n')
    
    def _trim_if_needed(self):
        """Keep only the most recent N messages"""
        messages = self.get_messages(limit=self.max_messages)
        if len(messages) >= self.max_messages:
            messages = messages[:self.max_messages]
            with open(self.file_path, 'w') as f:
                for msg in reversed(messages):  # Reverse back to chronological
                    f.write(json.dumps(msg) + '\n')


class UserSettings(StateManager):
    """Manages user settings"""
    
    def __init__(self):
        super().__init__(Config.DATA_DIR / "settings.json")
    
    def _default_state(self) -> Dict[str, Any]:
        return {
            "time_format": Config.TIME_FORMAT,
            "brightness": 3,
            "sleep_enabled": False,
            "sleep_time": "23:00",
            "wake_time": "07:00",
            "refresh_mode": "balanced",  # fast, balanced, slow
            "notifications_enabled": True,
            "last_modified": datetime.now(timezone.utc).isoformat()
        }


class Stats(StateManager):
    """Manages statistics and history"""
    
    def __init__(self):
        super().__init__(Config.DATA_DIR / "stats.json")
    
    def _default_state(self) -> Dict[str, Any]:
        return {
            "first_boot": datetime.now(timezone.utc).isoformat(),
            "total_uptime_hours": 0,
            "total_button_presses": 0,
            "total_display_updates": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "network_errors": 0,
            "last_error": None,
            "last_reset": None
        }
    
    def increment(self, key: str, amount: int = 1):
        """Increment a counter"""
        current = self._state.get(key, 0)
        self.set(key, current + amount)
    
    def record_error(self, error_message: str):
        """Record an error"""
        self.update(
            network_errors=self._state.get("network_errors", 0) + 1,
            last_error={
                "message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


# Singleton instances
_pet_state: Optional[PetState] = None
_message_log: Optional[MessageLog] = None
_settings: Optional[UserSettings] = None
_stats: Optional[Stats] = None


def get_pet_state() -> PetState:
    """Get pet state singleton"""
    global _pet_state
    if _pet_state is None:
        _pet_state = PetState()
    return _pet_state


def get_message_log() -> MessageLog:
    """Get message log singleton"""
    global _message_log
    if _message_log is None:
        _message_log = MessageLog()
    return _message_log


def get_settings() -> UserSettings:
    """Get settings singleton"""
    global _settings
    if _settings is None:
        _settings = UserSettings()
    return _settings


def get_stats() -> Stats:
    """Get stats singleton"""
    global _stats
    if _stats is None:
        _stats = Stats()
    return _stats


if __name__ == "__main__":
    # Test state management
    print("Testing State Management")
    print("=" * 50)
    
    # Test pet state
    pet = get_pet_state()
    print(f"\nPet: {pet.to_dict()}")
    print(f"Mood: {pet.get_mood()}")
    
    # Test feeding
    pet.feed()
    print(f"\nAfter feeding:")
    print(f"  Hunger: {pet.hunger}")
    print(f"  Happiness: {pet.happiness}")
    
    # Test messages
    msg_log = get_message_log()
    msg_log.add_message("test_device", "Hello!", "text")
    print(f"\nMessages: {msg_log.get_messages()}")
    print(f"Unread: {msg_log.get_unread_count()}")
    
    # Test settings
    settings = get_settings()
    print(f"\nSettings: {settings.to_dict()}")
    
    # Test stats
    stats = get_stats()
    stats.increment("total_button_presses", 5)
    print(f"\nStats: {stats.to_dict()}")
