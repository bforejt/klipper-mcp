"""
Klipper MCP Server Configuration
Configure your Voron printer settings here.
"""
import os

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
ARMED = os.getenv("ARMED", "false").lower() == "true"

# Admin PIN for destructive operations (delete, restore, emergency stop)
ADMIN_PIN = os.getenv("ADMIN_PIN", "123456")

# =============================================================================
# FILE PATHS (CB1/Raspberry Pi paths)
# =============================================================================
PRINTER_DATA_PATH = os.getenv("PRINTER_DATA_PATH", "/home/biqu/printer_data")
CONFIG_PATH = f"{PRINTER_DATA_PATH}/config"
GCODES_PATH = f"{PRINTER_DATA_PATH}/gcodes"
LOGS_PATH = f"{PRINTER_DATA_PATH}/logs"
BACKUP_PATH = f"{PRINTER_DATA_PATH}/backups"

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
SPOOLMAN_ENABLED = os.getenv("SPOOLMAN_ENABLED", "false").lower() == "true"
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

# TTS (Text-to-Speech) - plays on CB1 speaker
TTS_ENABLED = os.getenv("TTS_ENABLED", "false").lower() == "true"

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
MAINTENANCE_DATA_FILE = os.getenv("MAINTENANCE_DATA_FILE", "/home/biqu/klipper-mcp/data/maintenance.json")
AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "/home/biqu/klipper-mcp/data/audit.log")

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
LED_SCENES_FILE = os.getenv("LED_SCENES_FILE", "/home/biqu/klipper-mcp/scenes/led_scenes.json")
