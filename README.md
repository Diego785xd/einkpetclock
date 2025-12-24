# 🐰 E-Ink Pet Clock

A networked Tamagotchi-style pet clock for Raspberry Pi Zero W with e-ink display. Perfect for couples in long-distance relationships or friends who want to stay connected!

## 🎁 Features

- **Virtual Pet (Bunny)**: Feed, interact with, and care for your digital pet
- **Real-time Clock**: Always-on display with Mexico City timezone
- **Network Messaging**: Send pokes and messages to other clocks via ZeroTier
- **4 Interactive Menus**:
  - 🏠 Main: Tamagotchi with clock
  - 💌 Messages: Inbox for received messages
  - 📊 Stats: Pet statistics and history
  - ⚙️ Settings: Configurable options
- **3-Button Control**: Simple navigation with physical buttons
- **Low Power**: Optimized for Raspberry Pi Zero W
- **Auto-restart**: Systemd services ensure reliability

## 📦 Hardware Requirements

- Raspberry Pi Zero W
- Waveshare 2.13" e-ink display (V4)
- 3x tactile push buttons
- Jumper wires
- Power supply (USB)

## 🔌 Wiring Diagram

```
Raspberry Pi Zero W GPIO Connections:

Buttons:
  GPIO 6  (Pin 31) → [Button 1] → GND   (RETURN button)
  GPIO 13 (Pin 33) → [Button 2] → GND   (ACTION button)
  GPIO 19 (Pin 35) → [Button 3] → GND   (GO button)

E-Ink Display:
  (Standard Waveshare 2.13" V4 connections)
  SPI0, RST=17, DC=25, CS=8, BUSY=24
```

## 🚀 Quick Start

### 1. Setup on Your Mac (Development Machine)

```bash
# Clone/navigate to project
cd /Users/rossi/dev/einkpetclock

# Create your .env file
cp .env.example .env
nano .env

# Edit .env with your settings:
#   DEVICE_NAME=bunny_clock_1
#   DEVICE_IP=10.8.17.62
#   REMOTE_DEVICE_IP=10.8.17.114  # Your Mac for testing
#   etc.

# Make scripts executable
chmod +x scripts/*.sh
```

### 2. Deploy to Raspberry Pi

```bash
# Deploy code to Pi (first time)
./scripts/deploy.sh 10.8.17.62

# SSH into Pi
ssh pi@10.8.17.62

# Run installation
cd ~/einkpetclock
chmod +x scripts/install.sh
./scripts/install.sh

# Follow the prompts to:
#  - Install dependencies
#  - Configure .env on Pi
#  - Start services
```

### 3. Test from Your Mac

```bash
# Test the API
./scripts/test_api.sh 10.8.17.62

# Or manually:
curl http://10.8.17.62:5000/api/status
```

## 📁 Project Structure

```
einkpetclock/
├── core/                      # Main display service (systemd)
│   ├── config.py             # Configuration loader
│   ├── state.py              # File-based state management
│   ├── button_handler.py     # GPIO button interrupts
│   ├── display.py            # E-ink display wrapper
│   ├── menu_system.py        # Menu rendering & navigation
│   └── display_manager.py    # Main service loop
│
├── web/                       # REST API (venv)
│   ├── api.py                # FastAPI server
│   └── network_client.py     # Outgoing requests
│
├── hardware/                  # Hardware examples
│   └── example.py            # Waveshare test
│
├── assets/                    # Resources
│   ├── sprites/              # Bunny sprites (add yours here!)
│   └── fonts/                # Font files
│
├── data/                      # Runtime data (auto-created)
│   ├── pet_state.json        # Current pet stats
│   ├── messages.jsonl        # Message log
│   ├── settings.json         # User settings
│   └── stats.json            # Statistics
│
├── systemd/                   # Service files
│   ├── eink-display.service  # Display service
│   └── eink-api.service      # API service
│
├── scripts/                   # Utilities
│   ├── install.sh            # Pi installation
│   ├── deploy.sh             # Deploy from Mac
│   └── test_api.sh           # API testing
│
├── .env.example              # Configuration template
├── requirements.txt          # Core dependencies
└── README.md                 # This file
```

## 🎮 Button Controls

### Menu 1: Tamagotchi Clock (Main)
- **RETURN**: Feed bunny 🍔
- **GO**: Send poke to other clock 👋
- **ACTION**: Next menu

### Menu 2: Messages
- **RETURN**: Back to main
- **GO**: Navigate messages / mark as read
- **ACTION**: Next menu

### Menu 3: Stats
- **RETURN**: Back to main
- **GO**: Cycle stats pages
- **ACTION**: Next menu

### Menu 4: Settings
- **RETURN**: Back to main
- **GO**: Change selected setting
- **ACTION**: Next menu

## 🌐 API Endpoints

The API runs on port 5000 by default:

```bash
# Get device status
GET /api/status

# Health check
GET /api/health

# Send message
POST /api/message
{
  "from_device": "your_clock",
  "message": "Hello!",
  "type": "text"
}

# Send poke
POST /api/poke
{
  "from_device": "your_clock"
}

# Feed their pet
POST /api/feed
{
  "from_device": "your_clock"
}
```

## 🛠️ Development Workflow

### On Your Mac

```bash
# Edit code locally
code .

# Test changes
python3 core/state.py          # Test state management
python3 web/network_client.py  # Test network client

# Deploy to Pi
./scripts/deploy.sh

# View logs
ssh pi@10.8.17.62
sudo journalctl -u eink-display.service -f
```

### On the Pi

```bash
# Manual service control
sudo systemctl restart eink-display.service
sudo systemctl restart eink-api.service
sudo systemctl status eink-display.service

# View logs
sudo journalctl -u eink-display.service -f
sudo journalctl -u eink-api.service -f

# Test display directly
cd ~/einkpetclock
python3 core/display_manager.py
```

## 🐞 Troubleshooting

### Display not working
```bash
# Check service status
sudo systemctl status eink-display.service

# Check logs
sudo journalctl -u eink-display.service -n 50

# Test display hardware
cd ~/einkpetclock/hardware
python3 example.py
```

### Network issues
```bash
# Check API service
sudo systemctl status eink-api.service

# Test connectivity
ping 10.8.17.114  # Your other device

# Test API
curl http://10.8.17.62:5000/api/health
```

### Buttons not responding
```bash
# Check GPIO permissions
groups pi | grep gpio

# Test buttons directly
python3 core/button_handler.py
```

## 📝 Configuration

Edit `.env` on each device:

```bash
# Device Identity
DEVICE_NAME=bunny_clock_1        # Unique name
DEVICE_TIMEZONE=America/Mexico_City

# Network (ZeroTier IPs)
DEVICE_IP=10.8.17.62             # This device
REMOTE_DEVICE_IP=10.8.17.114     # Other device
API_PORT=5000

# Display
TIME_FORMAT=24                    # 12 or 24

# Pet
PET_TYPE=bunny
PET_NAME=Fluffy

# Development
DEBUG_MODE=false
MOCK_HARDWARE=false              # Set true for Mac testing
```

## 🎨 Customization

### Add Custom Bunny Sprites

1. Create 1-bit (black & white) PNG images
2. Place in `assets/sprites/`
3. Name them: `bunny_happy.png`, `bunny_sad.png`, etc.
4. Update `core/menu_system.py` to load them

### Change Pet Mechanics

Edit `core/config.py`:
```python
HUNGER_DECAY_RATE = 1.0      # Points per hour
HAPPINESS_DECAY_RATE = 0.5   # Points per hour
MAX_HUNGER = 10
MAX_HAPPINESS = 10
```

## 📊 Data Files

All state is stored in JSON files in `data/`:

- `pet_state.json`: Current pet stats
- `messages.jsonl`: Message history (append-only)
- `settings.json`: User preferences
- `stats.json`: Historical statistics

To reset:
```bash
rm data/*.json data/*.jsonl
sudo systemctl restart eink-display.service
```

## 🔒 Security Notes

- ZeroTier provides network encryption
- No authentication on API (trusted network only)
- Don't expose port 5000 to public internet
- Keep .env file secure (contains IPs)

## 🎁 Gift Notes

This is a love project! Some ideas:
- Create custom bunny sprites together
- Exchange different message types
- Track statistics over time
- Add seasonal themes

## 📜 License

Personal project - feel free to adapt for your own use!

## 💝 Credits

Made with love for your girlfriend! 🐰💕

---

**Happy coding and enjoy your synchronized pet clocks!** 🎄✨
