# Mac Development Setup

If you want to test the code on your Mac without the Pi hardware:

## 1. Install Dependencies

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r web/requirements.txt
```

## 2. Configure for Mac

Create `.env` with `MOCK_HARDWARE=true`:

```env
DEVICE_NAME=bunny_clock_test
DEVICE_IP=127.0.0.1
REMOTE_DEVICE_IP=127.0.0.1
API_PORT=5000
MOCK_HARDWARE=true
DEBUG_MODE=true
```

## 3. Test Components

### Test State Management
```bash
python3 core/state.py
```

### Test Display (Mock)
```bash
python3 core/display.py
```

### Test Button Handler (Mock)
```bash
python3 core/button_handler.py
```

### Test Menu System (Mock)
```bash
python3 core/menu_system.py
```

### Run Mock API Server
```bash
python3 scripts/mock_api.py
# Then in another terminal:
curl http://localhost:5000/api/status
```

### Test Network Client
```bash
# First start mock API server, then:
python3 web/network_client.py
```

## 4. Full System Test (Mock)

```bash
# Terminal 1: Run API
python3 scripts/mock_api.py

# Terminal 2: Run Display Manager
python3 core/display_manager.py

# Terminal 3: Send test messages
curl -X POST http://localhost:5000/api/message \
  -H "Content-Type: application/json" \
  -d '{"from_device":"test","message":"Hello!","type":"text"}'
```

## Notes

- Mock mode prints to console instead of updating hardware
- All state is still saved to `data/` directory
- Button presses are simulated (no actual GPIO)
- Display updates are logged but not shown
- Network communication works normally

This is useful for:
- Developing new features
- Testing logic changes
- Debugging without Pi hardware
- Verifying network protocols
