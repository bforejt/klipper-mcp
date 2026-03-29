#!/bin/bash
# Klipper MCP Server Installation Script for CB1
# Run this script on your CB1 to install the MCP server
# Compatible with Python 3.9+

set -e

echo "=========================================="
echo "Klipper MCP Server Installer"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python version: $PYTHON_VERSION"

# Configuration
INSTALL_DIR="${KLIPPER_MCP_INSTALL_DIR:-$HOME/klipper-mcp}"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="klipper-mcp"

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/backups"
mkdir -p "$INSTALL_DIR/scenes"
mkdir -p "$INSTALL_DIR/tools"

# Copy files (assumes files are in current directory)
echo "Copying files..."
cp -r ./*.py "$INSTALL_DIR/" 2>/dev/null || true
cp -r ./tools/*.py "$INSTALL_DIR/tools/" 2>/dev/null || true
cp -r ./data/* "$INSTALL_DIR/data/" 2>/dev/null || true
cp -r ./scenes/* "$INSTALL_DIR/scenes/" 2>/dev/null || true
cp requirements.txt "$INSTALL_DIR/" 2>/dev/null || true
cp klipper-mcp.service "$INSTALL_DIR/" 2>/dev/null || true

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate venv and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"

# Create config from template if needed
if [ ! -f "$INSTALL_DIR/config.py" ]; then
    echo "Creating default config.py..."
    # The config.py should already be copied, but create if missing
    cat > "$INSTALL_DIR/config.py" << 'EOF'
# Edit this file with your printer's settings
MOONRAKER_URL = "http://localhost:7125"
PRINTER_NAME = "Voron"
MCP_HOST = "0.0.0.0"
MCP_PORT = 8000
MCP_TRANSPORT = "http"
API_KEY = "your-secret-key-here"
ARMED = False
ADMIN_PIN = "0000"
EOF
fi

# Install systemd service (substitute placeholders with current user/paths)
echo "Installing systemd service..."
sed -e "s|%%USER%%|$USER|g" \
    -e "s|%%INSTALL_DIR%%|$INSTALL_DIR|g" \
    "$INSTALL_DIR/klipper-mcp.service" > /tmp/klipper-mcp.service
sudo cp /tmp/klipper-mcp.service /etc/systemd/system/klipper-mcp.service
rm /tmp/klipper-mcp.service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

# Create log file
sudo touch /var/log/klipper-mcp.log
sudo chown "$USER:$USER" /var/log/klipper-mcp.log

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit the configuration file:"
echo "   nano $INSTALL_DIR/config.py"
echo ""
echo "2. Set ARMED=True when ready to enable dangerous commands"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "5. View logs:"
echo "   tail -f /var/log/klipper-mcp.log"
echo ""
echo "MCP server will be available at:"
echo "   http://$(hostname -I | awk '{print $1}'):8000/mcp"
echo ""
