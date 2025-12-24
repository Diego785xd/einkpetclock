"""
Network client for sending messages to remote device
"""
import httpx
from typing import Optional, Dict, Any
from core.config import Config


def send_message(message: str, msg_type: str = "text") -> bool:
    """
    Send a text message to the remote device
    
    Args:
        message: The message text
        msg_type: Type of message (text, poke, feed, etc.)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        url = Config.get_remote_url("/api/message")
        data = {
            "from": Config.DEVICE_NAME,
            "message": message,
            "type": msg_type
        }
        
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, json=data)
            return response.status_code == 200
    
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def send_poke() -> bool:
    """
    Send a poke/interaction to the remote device
    
    Returns:
        True if successful, False otherwise
    """
    return send_message("Poke!", "poke")


def send_feed() -> bool:
    """
    Send a feed action to the remote device (feed their pet)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        url = Config.get_remote_url("/api/feed")
        data = {
            "from": Config.DEVICE_NAME
        }
        
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, json=data)
            return response.status_code == 200
    
    except Exception as e:
        print(f"Error sending feed: {e}")
        return False


def get_remote_status() -> Optional[Dict[str, Any]]:
    """
    Get status of the remote device
    
    Returns:
        Status dictionary if successful, None otherwise
    """
    try:
        url = Config.get_remote_url("/api/status")
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            if response.status_code == 200:
                return response.json()
            return None
    
    except Exception as e:
        print(f"Error getting remote status: {e}")
        return None


if __name__ == "__main__":
    # Test network client
    print("Testing network client...")
    print(f"Remote device: {Config.REMOTE_DEVICE_IP}:{Config.API_PORT}")
    
    # Test message
    print("\nSending test message...")
    if send_message("Hello from test!", "text"):
        print("✓ Message sent successfully")
    else:
        print("✗ Failed to send message")
    
    # Test poke
    print("\nSending poke...")
    if send_poke():
        print("✓ Poke sent successfully")
    else:
        print("✗ Failed to send poke")
    
    # Test status
    print("\nGetting remote status...")
    status = get_remote_status()
    if status:
        print(f"✓ Status received: {status}")
    else:
        print("✗ Failed to get status")
