#!/bin/bash

# =============================================================================
# Corduroy EC2 Initial Setup Script
# =============================================================================
# Run this ONCE on a fresh EC2 instance to install all dependencies.
# After initial setup, use ec2-services.sh for service management.
#
# Usage (on EC2 instance):
#   sudo bash ec2-setup.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Corduroy EC2 Initial Setup                   ${NC}"
echo -e "${BLUE}================================================${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (sudo bash ec2-setup.sh)${NC}"
    exit 1
fi

APP_DIR="/home/ubuntu/corduroy"
APP_USER="ubuntu"

# Update system packages
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install Python and pip
echo -e "${YELLOW}[2/7] Installing Python 3 and pip...${NC}"
apt-get install -y python3 python3-pip python3-venv

# Install Node.js (LTS version)
echo -e "${YELLOW}[3/7] Installing Node.js...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
echo -e "${GREEN}Node.js version: $(node --version)${NC}"
echo -e "${GREEN}npm version: $(npm --version)${NC}"

# Install Yarn
echo -e "${YELLOW}[4/7] Installing Yarn...${NC}"
npm install -g yarn

# Install Nginx
echo -e "${YELLOW}[5/7] Installing Nginx...${NC}"
apt-get install -y nginx

# Install Python dependencies globally
echo -e "${YELLOW}[6/7] Installing Python dependencies...${NC}"
cd "$APP_DIR"
pip3 install --upgrade pip --break-system-packages
pip3 install -r requirements.lock --break-system-packages --ignore-installed

# Note: Frontend is built locally and synced via ec2-deploy.sh
# Just ensure standalone assets are configured
echo -e "${YELLOW}[7/7] Setting up frontend...${NC}"
cd "$APP_DIR/frontend"
if [ -d ".next/standalone" ]; then
    cp -r public .next/standalone/ 2>/dev/null || true
    cp -r .next/static .next/standalone/.next/ 2>/dev/null || true
    echo -e "${GREEN}✓ Frontend standalone assets configured${NC}"
else
    echo -e "${YELLOW}⚠ Frontend build not found. Run './ec2-deploy.sh --full' from local machine.${NC}"
fi

# Create systemd directory if not exists
mkdir -p "$APP_DIR/systemd"

echo
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Initial Setup Complete!                       ${NC}"
echo -e "${GREEN}================================================${NC}"
echo
echo -e "Next steps:"
echo -e "  1. Create ${CYAN}.env${NC} file with your database credentials"
echo -e "  2. Run ${CYAN}sudo bash ec2-services.sh install${NC} to install services"
echo -e "  3. Run ${CYAN}sudo bash ec2-services.sh start${NC} to start everything"
echo

