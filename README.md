# Klipper MCP Server

A Model Context Protocol (MCP) server for controlling Klipper 3D printers via Moonraker API. Enables AI assistants like Claude to control your 3D printer through VS Code.

## Features

### Core Printer Control
- Get printer status, temperatures, and position
- Run G-code commands
- Start, pause, resume, and cancel prints
- Home axes and emergency stop
- Klipper firmware restart

### StealthChanger Toolchanger
- Select tools (T0-T5)
- Initialize toolchanger
- Tool alignment workflow
- Crash detection control
- Tool dock/pickup operations

### LED Effects (klipper-led_effect)
- Set LED effects and animations
- Stop effects (single or all)
- LED scene presets (idle, printing, complete, etc.)
- Direct LED color control

### File Operations
- List and read G-code files
- Upload and delete files
- Search within files
- Get G-code metadata

### Camera & Timelapse
- Capture webcam snapshots
- Get stream URLs
- Timelapse settings and control
- Manual frame capture

### Print Statistics
- Print history with filtering
- Cumulative totals (time, filament)
- Filament usage analysis
- Recent prints summary

### Diagnostics
- Parse klippy.log for errors
- Common issue detection
- MCU status
- G-code history
- Problem troubleshooting guide

### Temperature & Bed Mesh
- Temperature history
- Anomaly detection
- Bed mesh profiles
- Mesh calibration

### Spoolman Integration
- List and track filament spools
- Set active spool
- Low filament warnings
- Usage by material

### Notifications
- Discord, Slack, Pushover webhooks
- Text-to-speech announcements
- Print completion alerts
- Temperature alerts

### Backup & Maintenance
- Config file backup/restore
- Maintenance logging
- Due maintenance alerts
- Data export

### G-code Analysis
- File analysis and metadata
- Comment extraction
- Move statistics
- Layer extraction
- Validation checks

## Installation

### On CB1 (BigTreeTech)

1. **Clone or copy files to CB1:**
   ```bash
   cd ~
   git clone <repo-url> klipper-mcp
   # Or copy files via SCP/SFTP
   ```

2. **Run the installer:**
   ```bash
   cd ~/klipper-mcp
   chmod +x install.sh
   ./install.sh
   ```

3. **Configure settings:**
   ```bash
   nano ~/klipper-mcp/config.py
   ```
   
   Update these settings:
   - `MOONRAKER_URL`: Usually `http://localhost:7125`
   - `PRINTER_NAME`: Your printer name
   - `API_KEY`: Generate a secure key
   - `ADMIN_PIN`: Set a PIN for destructive operations
   - `ARMED`: Set to `True` when ready

4. **Start the service:**
   ```bash
   sudo systemctl start klipper-mcp
   sudo systemctl status klipper-mcp
   ```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

## VS Code Configuration

Add to your VS Code `mcp.json`:

```json
{
  "mcpServers": {
    "voron": {
      "type": "http",
      "url": "http://192.168.2.87:8000/mcp",
      "headers": {
        "X-API-Key": "your-api-key"
      }
    }
  }
}
```

Replace `192.168.2.87` with your CB1's IP address.

## Security

### ARMED Flag
Dangerous operations (G-code execution, temperature changes) require `ARMED=True` in config.

### Admin PIN
Destructive operations (file deletion, config restore) require the admin PIN.

### Audit Log
All operations are logged to `data/audit.log` for security review.

## Configuration Reference

```python
# config.py

# Moonraker connection
MOONRAKER_URL = "http://localhost:7125"
PRINTER_NAME = "Voron"

# MCP Server
MCP_HOST = "0.0.0.0"
MCP_PORT = 8000
MCP_TRANSPORT = "http"  # or "stdio"

# Security
API_KEY = "your-secret-key"
ARMED = False  # Set True to enable dangerous ops
ADMIN_PIN = "1234"

# Camera
CAMERA_SNAPSHOT_URL = "http://localhost/webcam/?action=snapshot"
CAMERA_STREAM_URL = "http://localhost/webcam/?action=stream"

# Spoolman (optional)
SPOOLMAN_ENABLED = False
SPOOLMAN_URL = "http://localhost:7912"

# Notifications (optional)
DISCORD_WEBHOOK_URL = ""
SLACK_WEBHOOK_URL = ""
PUSHOVER_USER_KEY = ""
PUSHOVER_API_TOKEN = ""

# Text-to-Speech (optional)
TTS_ENABLED = False
TTS_RATE = 150
TTS_VOLUME = 1.0

# Maintenance intervals (hours)
MAINTENANCE_INTERVALS = {
    "nozzle": 200,
    "belts": 500,
    "linear_rails": 1000,
    "filters": 100
}

# StealthChanger
TOOL_COUNT = 4
```

## Troubleshooting

### Server won't start
- Check Moonraker is running: `systemctl status moonraker`
- Verify config.py settings
- Check logs: `tail -f /var/log/klipper-mcp.log`

### Can't connect from VS Code
- Verify CB1 IP address
- Check firewall allows port 8000
- Verify API key matches

### Operations failing
- Check `ARMED=True` for dangerous operations
- Verify Klipper is running and ready
- Check klippy.log for errors

## License

MIT License
