"""
Klipper MCP Server Configuration
Configure your Voron printer settings here.
"""
import os
from pathlib import Path

# =============================================================================
# MOONRAKER CONNECTION
# =============================================================================
MOONRAKER_URL = os.getenv("MOONRAKER_URL", "http://localhost:7125")
PRINTER_NAME = "Voron"

# =============================================================================
# MCP SERVER SETTINGS
# =============================================================================
MCP_HOST = "0.0.0.0"  # Listen on all interfaces for remote access
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# =============================================================================
# SECURITY
# =============================================================================
# API key for authenticating MCP clients (generate a strong random key)
API_KEY = os.getenv("API_KEY", "change-me-to-a-secure-key")

# Armed mode - when False, dangerous commands are blocked
ARMED = os.getenv("ARMED", "true").lower() == "true"

# Admin PIN for destructive operations (delete, restore, emergency stop)
ADMIN_PIN = os.getenv("ADMIN_PIN", "123456")

# =============================================================================
# FILE PATHS
# KLIPPER_DATA_DIR overrides the base path for non-standard installs.
# Default: ~/printer_data (works for standard Klipper on any user account)
# =============================================================================
_KLIPPER_BASE = Path(os.environ.get("KLIPPER_DATA_DIR", str(Path.home() / "printer_data")))
PRINTER_DATA_PATH = str(_KLIPPER_BASE)
CONFIG_PATH = str(_KLIPPER_BASE / "config")
GCODES_PATH = str(_KLIPPER_BASE / "gcodes")
LOGS_PATH = str(_KLIPPER_BASE / "logs")
BACKUP_PATH = str(_KLIPPER_BASE / "backups")

# Allowed paths for file operations (security)
ALLOWED_PATHS = [
    CONFIG_PATH,
    GCODES_PATH,
    LOGS_PATH,
    BACKUP_PATH,
]

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
CAMERA_SNAPSHOT_URL = os.getenv("CAMERA_SNAPSHOT_URL", "http://localhost/webcam/?action=snapshot")
CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL", "http://localhost/webcam/?action=stream")

# =============================================================================
# SPOOLMAN SETTINGS (optional)
# =============================================================================
SPOOLMAN_ENABLED = os.getenv("SPOOLMAN_ENABLED", "true").lower() == "true"
SPOOLMAN_URL = os.getenv("SPOOLMAN_URL", "http://localhost:7912")

# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================
# ntfy.sh (free, self-hostable)
NTFY_ENABLED = os.getenv("NTFY_ENABLED", "false").lower() == "true"
NTFY_URL = os.getenv("NTFY_URL", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "voron-printer")

# Discord webhook
DISCORD_ENABLED = os.getenv("DISCORD_ENABLED", "false").lower() == "true"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Slack webhook
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Pushover
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN", "")

# TTS (Text-to-Speech) - plays on CB1 speaker
TTS_ENABLED = os.getenv("TTS_ENABLED", "false").lower() == "true"
TTS_RATE = int(os.getenv("TTS_RATE", "150"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "0.8"))

# =============================================================================
# STEALTHCHANGER SETTINGS
# =============================================================================
# Number of tools configured
TOOL_COUNT = int(os.getenv("TOOL_COUNT", "3"))

# Tool names (optional, for display)
TOOL_NAMES = {
    0: "T0",
    1: "T1", 
    2: "T2",
    3: "T3",
}

# =============================================================================
# MAINTENANCE TRACKING
# =============================================================================
_MCP_DATA_DIR = Path(__file__).parent / "data"
MAINTENANCE_DATA_FILE = os.getenv("MAINTENANCE_DATA_FILE", str(_MCP_DATA_DIR / "maintenance.json"))
AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", str(_MCP_DATA_DIR / "audit.log"))

# Maintenance intervals (in hours)
MAINTENANCE_INTERVALS = {
    "nozzle_change": 500,
    "belt_tension": 200,
    "lubrication": 100,
    "pom_nut_check": 300,
    "filter_change": 200,
    "hotend_clean": 50,
}

# =============================================================================
# LED SCENES
# =============================================================================
_MCP_SCENES_DIR = Path(__file__).parent / "scenes"
LED_SCENES_FILE = os.getenv("LED_SCENES_FILE", str(_MCP_SCENES_DIR / "led_scenes.json"))

# Aliases for backward compatibility
MAINTENANCE_LOG_PATH = MAINTENANCE_DATA_FILE
AUDIT_LOG_PATH = AUDIT_LOG_FILE

