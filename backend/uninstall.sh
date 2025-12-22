#!/bin/bash

# WireGuard Manager Uninstallation Script

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting WireGuard Manager uninstallation...${NC}"

# Stop and disable service
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${YELLOW}Stopping service...${NC}"
    systemctl stop $SERVICE_NAME
fi

if systemctl is-enabled --quiet $SERVICE_NAME 2>/dev/null; then
    echo -e "${YELLOW}Disabling service...${NC}"
    systemctl disable $SERVICE_NAME
fi

# Remove systemd service file
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo -e "${YELLOW}Removing systemd service file...${NC}"
    rm /etc/systemd/system/$SERVICE_NAME.service
    systemctl daemon-reload
fi

# Remove sudoers file
if [ -f "/etc/sudoers.d/wireguard-manager" ]; then
    echo -e "${YELLOW}Removing sudoers configuration...${NC}"
    rm /etc/sudoers.d/wireguard-manager
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Removing installation directory...${NC}"
    rm -rf $INSTALL_DIR
fi

# Ask about removing user
read -p "Remove service user '$SERVICE_USER'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if id "$SERVICE_USER" &>/dev/null; then
        echo -e "${YELLOW}Removing service user...${NC}"
        userdel $SERVICE_USER
    fi
fi

# Ask about removing WireGuard configs
read -p "Remove WireGuard configurations in /etc/wireguard? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing WireGuard configurations...${NC}"
    rm -rf /etc/wireguard/*
fi

echo -e "${GREEN}✓ Uninstallation complete!${NC}"
