#!/usr/bin/env python3
"""
Test sending messages to the Pi's e-ink pet clock
"""
import requests
import sys

PI_HOST = "relojdai.local"
PI_PORT = 5001
API_URL = f"http://{PI_HOST}:{PI_PORT}"

def send_message(message_text="Test message!", sender="Your Mac"):
    """Send a message to the Pi"""
    try:
        response = requests.post(
            f"{API_URL}/poke",
            json={"message": message_text, "from": sender},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✓ Message sent successfully!")
            print(f"  Message: '{message_text}'")
            print(f"  From: {sender}")
            return True
        else:
            print(f"✗ Failed to send message: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Pi at {API_URL}")
        print(f"  Make sure the Pi is on and the API service is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def get_messages():
    """Get all messages from the Pi"""
    try:
        response = requests.get(f"{API_URL}/messages", timeout=5)
        if response.status_code == 200:
            messages = response.json()
            print(f"\n📬 Messages on Pi ({len(messages)} total):")
            for i, msg in enumerate(messages, 1):
                status = "📩 NEW" if not msg.get("read", False) else "✓ Read"
                print(f"  {i}. [{status}] {msg.get('message', 'No message')}")
                print(f"     From: {msg.get('from', 'Unknown')} at {msg.get('timestamp', 'Unknown time')}")
            return messages
        else:
            print(f"✗ Failed to get messages: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error getting messages: {e}")
        return []

def main():
    print("=" * 60)
    print("E-Ink Pet Clock - Message Tester")
    print("=" * 60)
    print(f"\nTarget: {API_URL}\n")
    
    # Check if custom message provided
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "Test message from Mac! 👋"
    
    # Send message
    if send_message(message):
        print("\n💡 Check the Pi display - you should see:")
        print("   'Msgs: 1 new' (or higher count) in the stats")
        print("\n💡 To read messages on the Pi:")
        print("   Press the [Menu] button to view Messages menu")
    
    print("\n" + "=" * 60)
    print("\nOther test commands:")
    print("  View messages:     curl http://relojdai.local:5001/messages")
    print("  Send custom msg:   python3 scripts/test_send_message.py 'Your message here'")
    print("  Pet status:        curl http://relojdai.local:5001/pet")
    print("")

if __name__ == "__main__":
    main()
