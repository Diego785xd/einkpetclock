"""
FastAPI REST API service for E-Ink Pet Clock
Handles incoming messages and interactions from other devices
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config
from core.state import get_pet_state, get_message_log, get_stats


# Pydantic models for request/response
class MessageRequest(BaseModel):
    from_device: str = "unknown"
    message: str
    type: str = "text"


class FeedRequest(BaseModel):
    from_device: str = "unknown"


class PokeRequest(BaseModel):
    from_device: str = "unknown"


class StatusResponse(BaseModel):
    device_name: str
    pet_name: str
    pet_mood: str
    hunger: int
    happiness: int
    health: int
    messages_count: int
    online: bool = True


# Create FastAPI app
app = FastAPI(title="E-Ink Pet Clock API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "E-Ink Pet Clock API",
        "device": Config.DEVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get current device status"""
    pet = get_pet_state()
    msg_log = get_message_log()
    
    return StatusResponse(
        device_name=Config.DEVICE_NAME,
        pet_name=pet.get("name", "Bunny"),
        pet_mood=pet.get_mood(),
        hunger=pet.hunger,
        happiness=pet.happiness,
        health=pet.health,
        messages_count=len(msg_log.get_messages())
    )


@app.post("/api/message")
async def receive_message(request: MessageRequest):
    """Receive a message from remote device"""
    try:
        msg_log = get_message_log()
        pet = get_pet_state()
        stats = get_stats()
        
        # Add message to log
        msg_log.add_message(
            from_device=request.from_device,
            message=request.message,
            msg_type=request.type
        )
        
        # Update stats
        pet.message_received()
        stats.increment("total_messages_received")
        
        # Special handling for pokes
        if request.type == "poke":
            pet.interact()
        
        # Set flag for display to pick up (optional)
        flag_file = Path("/tmp/eink_flags/new_message.flag")
        flag_file.parent.mkdir(exist_ok=True)
        flag_file.touch()
        
        return {
            "status": "success",
            "message": "Message received",
            "unread_count": msg_log.get_unread_count()
        }
    
    except Exception as e:
        stats = get_stats()
        stats.record_error(f"Error receiving message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feed")
async def receive_feed(request: FeedRequest):
    """Receive a feed action from remote device"""
    try:
        pet = get_pet_state()
        msg_log = get_message_log()
        
        # Feed the pet
        pet.feed()
        
        # Add notification message
        msg_log.add_message(
            from_device=request.from_device,
            message="Fed your bunny! 🍔",
            msg_type="feed"
        )
        
        # Set flag
        flag_file = Path("/tmp/eink_flags/feed_pet.flag")
        flag_file.parent.mkdir(exist_ok=True)
        flag_file.touch()
        
        return {
            "status": "success",
            "message": "Pet fed",
            "hunger": pet.hunger,
            "happiness": pet.happiness
        }
    
    except Exception as e:
        stats = get_stats()
        stats.record_error(f"Error handling feed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/poke")
async def receive_poke(request: PokeRequest):
    """Receive a poke/interaction from remote device"""
    try:
        pet = get_pet_state()
        msg_log = get_message_log()
        
        # Interact with pet
        pet.interact()
        
        # Add notification
        msg_log.add_message(
            from_device=request.from_device,
            message="Poked you! 👋",
            msg_type="poke"
        )
        
        # Set flag
        flag_file = Path("/tmp/eink_flags/poke.flag")
        flag_file.parent.mkdir(exist_ok=True)
        flag_file.touch()
        
        return {
            "status": "success",
            "message": "Poke received",
            "happiness": pet.happiness
        }
    
    except Exception as e:
        stats = get_stats()
        stats.record_error(f"Error handling poke: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "device": Config.DEVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting API server for {Config.DEVICE_NAME}")
    print(f"Listening on {Config.DEVICE_IP}:{Config.API_PORT}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces
        port=Config.API_PORT,
        log_level="info"
    )
