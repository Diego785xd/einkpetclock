# Quick Start Guide

## For Your Mac (Development/Testing)

1. **Setup configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Test the API endpoint (when Pi is running)**
   ```bash
   # Test from Mac to Pi
   curl http://10.8.17.62:5000/api/status
   
   # Or use the test script
   bash scripts/test_api.sh 10.8.17.62
   ```

3. **Deploy to Pi**
   ```bash
   bash scripts/deploy.sh 10.8.17.62
   ```

## For Raspberry Pi (Production)

1. **First deployment from Mac**
   ```bash
   # On Mac
   bash scripts/deploy.sh 10.8.17.62
   
   # SSH to Pi
   ssh pi@10.8.17.62
   ```

2. **Run installation on Pi**
   ```bash
   cd ~/einkpetclock
   bash scripts/install.sh
   ```

3. **Configure your device**
   ```bash
   nano .env
   # Set DEVICE_NAME, DEVICE_IP, REMOTE_DEVICE_IP, etc.
   ```

4. **Start services**
   ```bash
   sudo systemctl start eink-display.service
   sudo systemctl start eink-api.service
   ```

5. **View logs**
   ```bash
   sudo journalctl -u eink-display.service -f
   ```

## Common Commands

### On Mac
- Deploy code: `bash scripts/deploy.sh 10.8.17.62`
- Test API: `bash scripts/test_api.sh 10.8.17.62`
- Send message: `curl -X POST http://10.8.17.62:5000/api/message -H "Content-Type: application/json" -d '{"from_device":"mac","message":"Hi!","type":"text"}'`

### On Pi
- Restart display: `sudo systemctl restart eink-display.service`
- Restart API: `sudo systemctl restart eink-api.service`
- View logs: `sudo journalctl -u eink-display.service -f`
- Check status: `sudo systemctl status eink-display.service`
- Stop services: `sudo systemctl stop eink-display.service eink-api.service`

## Troubleshooting

### Can't reach Pi
- Check ZeroTier: `zerotier-cli listnetworks`
- Ping Pi: `ping 10.8.17.62`

### Services not starting
- Check logs: `sudo journalctl -u eink-display.service -n 50`
- Check permissions: `ls -la /home/pi/einkpetclock/`
- Verify .env exists: `cat /home/pi/einkpetclock/.env`

### Display not updating
- Check if service is running: `sudo systemctl status eink-display.service`
- Test display directly: `python3 /home/pi/einkpetclock/hardware/example.py`

## Notes

- Scripts in `scripts/` need execute permissions on Pi (install.sh does this automatically)
- The .env file is NOT synced by deploy.sh (it's excluded for security)
- Data files are preserved during deployments
- Use `MOCK_HARDWARE=true` in .env to test without physical hardware
