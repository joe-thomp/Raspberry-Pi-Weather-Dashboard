#!/bin/bash

# Weather Dashboard Installation Script for Raspberry Pi
# This script installs the weather dashboard as a systemd service

set -e

echo "🌤️  Installing Weather Dashboard for Inky Impression"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "Project directory: $PROJECT_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r "$PROJECT_DIR/requirements.txt"

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating .env file from template..."
    cp "$PROJECT_DIR/env_example.txt" "$PROJECT_DIR/.env"
    echo "⚠️  Please edit .env file and add your OpenWeatherMap API key"
    echo "   Get your free API key from: https://openweathermap.org/api"
fi

# Make scripts executable
chmod +x "$PROJECT_DIR/weather_dashboard.py"

# Install systemd service
echo "Installing systemd service..."
cp "$PROJECT_DIR/weather-dashboard.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable weather-dashboard.service

echo ""
echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit $PROJECT_DIR/.env and add your OpenWeatherMap API key"
echo "2. Configure your location in the .env file"
echo "3. Test the installation: sudo systemctl start weather-dashboard"
echo "4. Check status: sudo systemctl status weather-dashboard"
echo "5. View logs: journalctl -u weather-dashboard -f"
echo ""
echo "To start the service automatically on boot:"
echo "   sudo systemctl enable weather-dashboard"
echo ""
echo "To run a test update:"
echo "   cd $PROJECT_DIR && python3 weather_dashboard.py --test"
