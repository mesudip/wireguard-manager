#!/bin/bash

# WireGuard Manager Backend Installation Script
# This script installs the WireGuard Manager backend as a system service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/wireguard-manager"
SERVICE_USER="wireguard-manager"
SERVICE_NAME="wireguard-manager"
VENV_DIR="$INSTALL_DIR/venv"
CONFIG_FILE="/etc/wireguard/backend.conf"
STATIC_DIR="/lib/wireguard/backend"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Starting WireGuard Manager backend installation...${NC}"

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv wireguard-tools

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating service user: $SERVICE_USER${NC}"
    useradd -r -s /bin/false -d /nonexistent $SERVICE_USER
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory: $INSTALL_DIR${NC}"
mkdir -p $INSTALL_DIR
cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv $VENV_DIR

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create WireGuard directory with proper permissions
echo -e "${YELLOW}Setting up WireGuard directory...${NC}"
mkdir -p /etc/wireguard
chown $SERVICE_USER:$SERVICE_USER /etc/wireguard
chmod 700 /etc/wireguard

echo -e "${YELLOW}Creating backend configuration file...${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
# WireGuard Manager Backend Configuration
# This file configures the backend API server

[server]
# Server host - use '::' for IPv4+IPv6, '0.0.0.0' for IPv4 only
host = ::
port = 5000
debug = false

[cors]
# Enable CORS support
enabled = true
# CORS origins - use '*' for all, or comma-separated list of domains
# Example: origins = http://localhost:3000,https://example.com
origins = *
methods = GET,POST,PUT,DELETE,OPTIONS
allow_headers = Content-Type,Authorization
expose_headers = 
supports_credentials = false
max_age = 3600

[wireguard]
base_dir = /etc/wireguard

[logging]
# Logging method: 'console' or 'directory'
method = console
level = INFO
dir = /var/log/wireguard-manager
max_bytes = 10485760
backup_count = 5
EOF
    chown $SERVICE_USER:$SERVICE_USER "$CONFIG_FILE"
    chmod 640 "$CONFIG_FILE"
    echo -e "${GREEN}Created default configuration at $CONFIG_FILE${NC}"
else
    echo -e "${YELLOW}Configuration file already exists at $CONFIG_FILE${NC}"
fi

echo -e "${YELLOW}Setting up logging directory...${NC}"
mkdir -p /var/log/wireguard-manager
chown $SERVICE_USER:$SERVICE_USER /var/log/wireguard-manager
chmod 755 /var/log/wireguard-manager

# Add service user to necessary groups for WireGuard management
usermod -a -G sudo $SERVICE_USER

# Create sudoers rule for wireguard commands
echo -e "${YELLOW}Configuring sudo permissions for WireGuard commands...${NC}"
cat > /etc/sudoers.d/wireguard-manager << EOF
# Allow wireguard-manager to run WireGuard commands without password
$SERVICE_USER ALL=(ALL) NOPASSWD: /usr/bin/wg
$SERVICE_USER ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
$SERVICE_USER ALL=(ALL) NOPASSWD: /bin/systemctl start wg-quick@*
$SERVICE_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop wg-quick@*
$SERVICE_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart wg-quick@*
$SERVICE_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable wg-quick@*
$SERVICE_USER ALL=(ALL) NOPASSWD: /bin/systemctl disable wg-quick@*
EOF
chmod 440 /etc/sudoers.d/wireguard-manager

# Create systemd service file
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=WireGuard Manager API Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/etc/wireguard /var/log/wireguard-manager

[Install]
WantedBy=multi-user.target
EOF

# Set proper ownership
echo -e "${YELLOW}Setting file permissions...${NC}"
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR

if [ -d "$STATIC_DIR" ]; then
    echo -e "${YELLOW}Setting permissions for static files directory...${NC}"
    chmod -R 755 $STATIC_DIR
    echo -e "${GREEN}Static files directory is accessible${NC}"
fi

# Reload systemd and enable service
echo -e "${YELLOW}Enabling and starting service...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Check service status
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✓ Backend installation complete!${NC}"
    echo -e "${GREEN}✓ WireGuard Manager is running on http://localhost:5000${NC}"
    echo ""
    echo "Configuration:"
    echo "  - Config file: $CONFIG_FILE"
    echo "  - Logs: /var/log/wireguard-manager/"
    echo "  - Static files: $STATIC_DIR"
    echo ""
    echo "Useful commands:"
    echo "  - Check status: systemctl status $SERVICE_NAME"
    echo "  - View logs: journalctl -u $SERVICE_NAME -f"
    echo "  - Restart: systemctl restart $SERVICE_NAME"
    echo "  - Stop: systemctl stop $SERVICE_NAME"
    echo "  - Edit config: nano $CONFIG_FILE (then restart service)"
else
    echo -e "${RED}✗ Installation completed but service failed to start${NC}"
    echo "Check logs with: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi
