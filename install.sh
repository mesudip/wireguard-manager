#!/bin/bash

# WireGuard Manager Main Installation Script
# This script builds the frontend and installs both frontend and backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STATIC_INSTALL_DIR="/lib/wireguard/backend"
FRONTEND_DIR="frontend"
FRONTEND_DIST="$FRONTEND_DIR/dist"
BACKEND_DIR="backend"

# Error handler for stylized failure reporting
error_handler() {
    local exit_code=$?
    echo -e "\n${RED}================================================${NC}"
    echo -e "${RED}✗ WireGuard Manager installation failed!${NC}"
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}Error occurred on line $(caller | cut -d' ' -f1)${NC}"
    exit $exit_code
}

trap 'error_handler' ERR

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Starting WireGuard Manager installation...${NC}"

# Check if dist folder exists and is not empty
if [ -d "$FRONTEND_DIST" ] && [ "$(ls -A $FRONTEND_DIST)" ]; then
    echo -e "${GREEN}Found existing build in $FRONTEND_DIST directory${NC}"
else
    echo -e "${YELLOW}No build found. Building frontend...${NC}"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed. Please install Node.js first.${NC}"
        echo "You can install Node.js from: https://nodejs.org/"
        exit 1
    fi

    # Check if yarn is installed
    if ! command -v yarn &> /dev/null; then
        echo -e "${RED}Error: yarn is not installed. Please install yarn first.${NC}"
        echo "You can install it with: npm install --global yarn"
        exit 1
    fi
    
    # Install dependencies
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    (cd "$FRONTEND_DIR" && yarn)
    
    # Build the frontend
    echo -e "${YELLOW}Building frontend...${NC}"
    (cd "$FRONTEND_DIR" && yarn build)
    
    # Verify build was successful
    if [ ! -d "$FRONTEND_DIST" ] || [ ! "$(ls -A "$FRONTEND_DIST")" ]; then
        echo -e "${RED}Error: Build failed. $FRONTEND_DIST directory is empty or does not exist.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Frontend build completed successfully${NC}"
fi

# Create static files directory
echo -e "${YELLOW}Creating static files directory: $STATIC_INSTALL_DIR${NC}"
mkdir -p $STATIC_INSTALL_DIR

# Copy built files to static directory
echo -e "${YELLOW}Installing static files...${NC}"
rm -rf $STATIC_INSTALL_DIR/*
cp -r $FRONTEND_DIST/* $STATIC_INSTALL_DIR/

# Set proper permissions
chown -R root:root $STATIC_INSTALL_DIR
chmod -R 755 $STATIC_INSTALL_DIR

echo -e "${GREEN}Static files installed to $STATIC_INSTALL_DIR${NC}"

# Install backend
echo -e "${YELLOW}Installing backend...${NC}"
if [ -d "$BACKEND_DIR" ]; then
    cd $BACKEND_DIR
    if [ -f "install.sh" ]; then
        chmod +x install.sh
        ./install.sh
    else
        echo -e "${RED}Error: Backend install script not found${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Backend directory not found${NC}"
    exit 1
fi

# Get IP addresses for the success message
echo -e "${YELLOW}Detecting server IP addresses...${NC}"
IPV4_PUBLIC=$(curl -s4 --max-time 2 ifconfig.me 2>/dev/null || echo "")
IPV6_PUBLIC=$(curl -s6 --max-time 2 ifconfig.me 2>/dev/null || echo "")
LOCAL_IPS=$(hostname -I 2>/dev/null || echo "127.0.0.1")

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ WireGuard Manager installation complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "The frontend has been installed to: $STATIC_INSTALL_DIR"
echo "The backend is serving both API and static files on http://localhost:5000"
echo ""
echo "Next steps:"
echo "  1. Configure the backend: nano /etc/wireguard/backend.conf"
echo "  2. Restart the service: systemctl restart wireguard-manager"

echo "  3. Access the web interface:"
if [ -n "$IPV4_PUBLIC" ]; then
    echo "     - Public IPv4: http://$IPV4_PUBLIC:5000"
fi
if [ -n "$IPV6_PUBLIC" ]; then
    echo "     - Public IPv6: http://[$IPV6_PUBLIC]:5000"
fi

# Also show local IPs if no public IPs or just as additional info
if [ -n "$LOCAL_IPS" ]; then
    for ip in $LOCAL_IPS; do
        echo "     - Local IP: http://$ip:5000"
    done
fi
echo ""
echo "Useful commands:"
echo "  - Check status: systemctl status wireguard-manager"
echo "  - View logs: journalctl -u wireguard-manager -f"
echo "  - Restart: systemctl restart wireguard-manager"
