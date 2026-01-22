#!/bin/bash
# Quick setup script to install and start the weather dashboard service

echo "================================================"
echo "Weather Dashboard - Service Setup"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "WARNING: This script is designed for Raspberry Pi"
    echo "Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your API key:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Working directory: $SCRIPT_DIR"
echo ""

# Update service file with correct paths and user
CURRENT_USER=$(whoami)
echo "Creating service file for user: $CURRENT_USER"

cat > /tmp/weather-dashboard.service <<EOF
[Unit]
Description=Weather Dashboard for Inky Impression Display
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/weather_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Copy service file
echo "Installing systemd service..."
sudo cp /tmp/weather-dashboard.service /etc/systemd/system/weather-dashboard.service

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service to start on boot..."
sudo systemctl enable weather-dashboard.service

# Start service
echo "Starting weather dashboard service..."
sudo systemctl start weather-dashboard.service

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Service Status:"
sudo systemctl status weather-dashboard.service --no-pager
echo ""
echo "Useful Commands:"
echo "  View logs:    sudo journalctl -u weather-dashboard.service -f"
echo "  Restart:      sudo systemctl restart weather-dashboard.service"
echo "  Stop:         sudo systemctl stop weather-dashboard.service"
echo "  Status:       sudo systemctl status weather-dashboard.service"
echo ""
