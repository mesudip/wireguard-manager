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

# Check and install dependencies
echo -e "${YELLOW}Checking system dependencies...${NC}"
DEPS=("python3" "pip3" "python3-venv" "wg" "ip")
MISSING_DEPS=()

for dep in "${DEPS[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        case "$dep" in
            "python3") MISSING_DEPS+=("python3") ;;
            "pip3") MISSING_DEPS+=("python3-pip") ;;
            "python3-venv") 
                # On debian/ubuntu, it's often a separate package if not included
                if ! python3 -m venv --help &> /dev/null; then
                    MISSING_DEPS+=("python3-venv")
                fi
                ;;
            "wg") MISSING_DEPS+=("wireguard-tools") ;;
        esac
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing dependencies: ${MISSING_DEPS[*]}${NC}"
    apt-get update
    apt-get install -y "${MISSING_DEPS[@]}"
else
    echo -e "${GREEN}All system dependencies are already installed.${NC}"
fi

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating service user: $SERVICE_USER${NC}"
    useradd -r -s /bin/false -d /nonexistent $SERVICE_USER
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory: $INSTALL_DIR${NC}"
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"
cd "$INSTALL_DIR"

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
# Remove existing venv if it's incomplete (missing activate script)
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${YELLOW}Removing incomplete virtual environment...${NC}"
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${RED}Error: Failed to create virtual environment at $VENV_DIR${NC}"
        exit 1
    fi
    
    # Check if activate script was created
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}Error: Virtual environment created but activate script is missing${NC}"
        echo -e "${RED}This usually means python3-venv package is incomplete or broken${NC}"
        echo -e "${YELLOW}Attempting to reinstall python3-venv...${NC}"
        apt-get install --reinstall -y python3-venv
        
        # Try creating venv again
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        
        if [ ! -f "$VENV_DIR/bin/activate" ]; then
            echo -e "${RED}Still failed to create activate script. Python installation may be broken.${NC}"
            exit 1
        fi
    fi
fi

# Install dependencies using pip directly (works with or without activate)
echo -e "${YELLOW}Installing Python dependencies...${NC}"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Create WireGuard directory with proper permissions
echo -e "${YELLOW}Setting up WireGuard directory...${NC}"
mkdir -p /etc/wireguard
chown "$SERVICE_USER:$SERVICE_USER" /etc/wireguard
chmod 700 /etc/wireguard

echo -e "${YELLOW}Creating backend configuration file...${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    cp installer/etc/wireguard/backend.conf "$CONFIG_FILE"
    chown "$SERVICE_USER:$SERVICE_USER" "$CONFIG_FILE"
    chmod 640 "$CONFIG_FILE"
    echo -e "${GREEN}Created default configuration at $CONFIG_FILE${NC}"
else
    echo -e "${YELLOW}Configuration file already exists at $CONFIG_FILE${NC}"
fi

echo -e "${YELLOW}Setting up logging directory...${NC}"
mkdir -p /var/log/wireguard-manager
chown "$SERVICE_USER:$SERVICE_USER" /var/log/wireguard-manager
chmod 755 /var/log/wireguard-manager

# Add service user to necessary groups
usermod -a -G sudo "$SERVICE_USER"

# Create sudoers rule for wireguard commands
echo -e "${YELLOW}Configuring sudo permissions for WireGuard commands...${NC}"
sed "s/{{SERVICE_USER}}/$SERVICE_USER/g" installer/etc/sudoers.d/wireguard-manager.template > /etc/sudoers.d/wireguard-manager
chmod 440 /etc/sudoers.d/wireguard-manager

# Create systemd service file
echo -e "${YELLOW}Creating systemd service...${NC}"
sed -e "s|{{SERVICE_USER}}|$SERVICE_USER|g" \
    -e "s|{{INSTALL_DIR}}|$INSTALL_DIR|g" \
    -e "s|{{VENV_DIR}}|$VENV_DIR|g" \
    installer/etc/systemd/system/wireguard-manager.service.template > "/etc/systemd/system/$SERVICE_NAME.service"

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
