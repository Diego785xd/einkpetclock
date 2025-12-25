# Testing Messages on E-Ink Pet Clock

## Quick Test (Easiest Method)

Add a test message directly to the Pi:
```bash
./scripts/test_add_message_direct.sh
```

This will:
- Add a test message to the messages file
- Display should update on next refresh cycle
- You'll see "Msgs: 1 new" in the stats

## View Messages on Pi Display

Press the **[Menu]** button (middle button, GPIO 13) to cycle through menus:
1. Main (clock + bunny)
2. Messages (read messages)
3. Stats (statistics)
4. Settings

## Add Custom Message

```bash
ssh dai@relojdai.local 'echo "{\"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\", \"from\": \"Test\", \"message\": \"Your message here\", \"read\": false}" >> /home/dai/einkpetclock/data/messages.jsonl'
```

## View All Messages

```bash
ssh dai@relojdai.local 'cat /home/dai/einkpetclock/data/messages.jsonl'
```

## Clear All Messages

```bash
ssh dai@relojdai.local 'echo "" > /home/dai/einkpetclock/data/messages.jsonl'
```

## Message Format

Messages are stored in `/home/dai/einkpetclock/data/messages.jsonl` as JSON lines:

```json
{"timestamp": "2025-12-25T04:14:44Z", "from": "Your Mac", "message": "Test message!", "read": false}
```

Fields:
- `timestamp`: ISO 8601 format (UTC)
- `from`: Sender name/identifier
- `message`: Message text
- `read`: Boolean (false = unread, true = read)

## Display Behavior

- **Unread count**: Shows "Msgs: X new" in stats (only if X > 0)
- **Read messages**: Press [Menu] to cycle to Messages menu
- **Message limit**: Display shows recent messages (scrollable)
- **Auto-refresh**: Display updates every ~5 seconds or on button press

## Troubleshooting

### Messages don't appear on display
- Wait 5-10 seconds for next refresh cycle
- Press any button to force immediate refresh
- Check messages file exists: `ssh dai@relojdai.local 'ls -la /home/dai/einkpetclock/data/messages.jsonl'`

### "Msgs: X new" doesn't show
- Only shows if there are unread messages
- Check `"read": false` in messages file
- Verify display service is running: `ssh dai@relojdai.local 'sudo systemctl status eink-display.service'`

### Clear message count
- Mark all as read: `ssh dai@relojdai.local 'sed -i "s/false/true/g" /home/dai/einkpetclock/data/messages.jsonl'`
- Or delete all: `ssh dai@relojdai.local 'echo "" > /home/dai/einkpetclock/data/messages.jsonl'`

## Note About API

The API service (http://relojdai.local:5001) is currently having issues and not responding. The direct file method above works perfectly and is actually simpler for testing!
