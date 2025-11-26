#!/bin/bash

# =============================================================================
# Corduroy EC2 Service Management Script
# =============================================================================
# Manages the backend, frontend, and nginx services on EC2.
#
# Usage:
#   sudo bash ec2-services.sh [command]
#
# Commands:
#   install   - Install systemd services and nginx config
#   start     - Start all services
#   stop      - Stop all services
#   restart   - Restart all services
#   status    - Show status of all services
#   deploy    - Full deploy (install deps + restart)
#   logs      - Show recent logs
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

APP_DIR="/home/ubuntu/corduroy"
APP_USER="ubuntu"

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Please run as root (sudo bash ec2-services.sh)${NC}"
        exit 1
    fi
}

# Install systemd services
install_services() {
    echo -e "${YELLOW}Installing systemd services...${NC}"
    
    # Copy service files
    cp "$APP_DIR/systemd/corduroy-backend.service" /etc/systemd/system/
    cp "$APP_DIR/systemd/corduroy-frontend.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services to start on boot
    systemctl enable corduroy-backend
    systemctl enable corduroy-frontend
    
    echo -e "${GREEN}✓ Systemd services installed${NC}"
    
    # Install nginx config
    echo -e "${YELLOW}Installing Nginx configuration...${NC}"
    cp "$APP_DIR/nginx.conf" /etc/nginx/nginx.conf
    
    # Test nginx config
    if nginx -t; then
        echo -e "${GREEN}✓ Nginx configuration valid${NC}"
    else
        echo -e "${RED}✗ Nginx configuration invalid${NC}"
        exit 1
    fi
    
    # Enable nginx
    systemctl enable nginx
    
    echo -e "${GREEN}✓ Services installed successfully${NC}"
}

# Start all services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    
    systemctl start corduroy-backend
    echo -e "${GREEN}✓ Backend started${NC}"
    
    systemctl start corduroy-frontend
    echo -e "${GREEN}✓ Frontend started${NC}"
    
    systemctl start nginx
    echo -e "${GREEN}✓ Nginx started${NC}"
    
    # Wait a moment for services to initialize
    sleep 3
    
    # Health check
    echo
    echo -e "${YELLOW}Running health checks...${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Backend health check passed${NC}"
    else
        echo -e "${RED}✗ Backend health check failed${NC}"
    fi
    
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✓ Frontend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
    fi
}

# Stop all services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    
    systemctl stop nginx 2>/dev/null || true
    echo -e "${GREEN}✓ Nginx stopped${NC}"
    
    systemctl stop corduroy-frontend 2>/dev/null || true
    echo -e "${GREEN}✓ Frontend stopped${NC}"
    
    systemctl stop corduroy-backend 2>/dev/null || true
    echo -e "${GREEN}✓ Backend stopped${NC}"
}

# Restart all services
restart_services() {
    echo -e "${YELLOW}Restarting services...${NC}"
    
    stop_services
    echo
    start_services
}

# Show status
show_status() {
    echo -e "${CYAN}Service Status:${NC}"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    
    echo -e "\n${YELLOW}Backend (corduroy-backend):${NC}"
    systemctl status corduroy-backend --no-pager -l 2>/dev/null | head -10 || echo "Not installed"
    
    echo -e "\n${YELLOW}Frontend (corduroy-frontend):${NC}"
    systemctl status corduroy-frontend --no-pager -l 2>/dev/null | head -10 || echo "Not installed"
    
    echo -e "\n${YELLOW}Nginx:${NC}"
    systemctl status nginx --no-pager -l 2>/dev/null | head -10 || echo "Not installed"
    
    echo -e "\n${BLUE}────────────────────────────────────────${NC}"
    echo -e "${CYAN}Port Status:${NC}"
    echo -e "Backend  (8000): $(netstat -tlnp 2>/dev/null | grep ':8000' | awk '{print $6}' || echo 'Not listening')"
    echo -e "Frontend (3000): $(netstat -tlnp 2>/dev/null | grep ':3000' | awk '{print $6}' || echo 'Not listening')"
    echo -e "Nginx    (80):   $(netstat -tlnp 2>/dev/null | grep ':80' | awk '{print $6}' || echo 'Not listening')"
}

# Full deployment
full_deploy() {
    echo -e "${YELLOW}Running full deployment...${NC}"
    echo
    
    # Update Python dependencies
    echo -e "${BLUE}Updating Python dependencies...${NC}"
    cd "$APP_DIR"
    pip3 install -r requirements.lock --quiet --break-system-packages --ignore-installed
    echo -e "${GREEN}✓ Python dependencies updated${NC}"
    
    # Frontend is built locally and synced, just ensure standalone assets are set up
    echo -e "${BLUE}Setting up frontend standalone assets...${NC}"
    cd "$APP_DIR/frontend"
    if [ -d ".next/standalone" ]; then
        cp -r public .next/standalone/ 2>/dev/null || true
        cp -r .next/static .next/standalone/.next/ 2>/dev/null || true
        echo -e "${GREEN}✓ Frontend standalone assets configured${NC}"
    else
        echo -e "${RED}✗ Frontend build not found. Build locally and redeploy.${NC}"
    fi
    
    # Install services if not already
    if [ ! -f /etc/systemd/system/corduroy-backend.service ]; then
        install_services
    else
        # Just reload nginx config
        cp "$APP_DIR/nginx.conf" /etc/nginx/nginx.conf
        nginx -t && systemctl reload nginx
    fi
    
    # Restart services
    restart_services
    
    echo
    echo -e "${GREEN}✓ Deployment complete!${NC}"
}

# Show logs
show_logs() {
    echo -e "${CYAN}Recent Logs:${NC}"
    echo -e "${BLUE}────────────────────────────────────────${NC}"
    
    echo -e "\n${YELLOW}Backend logs:${NC}"
    journalctl -u corduroy-backend --no-pager -n 20 2>/dev/null || echo "No logs available"
    
    echo -e "\n${YELLOW}Frontend logs:${NC}"
    journalctl -u corduroy-frontend --no-pager -n 20 2>/dev/null || echo "No logs available"
}

# Main
check_root

case "${1:-status}" in
    "install")
        install_services
        ;;
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "deploy")
        full_deploy
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo "Usage: $0 {install|start|stop|restart|status|deploy|logs}"
        exit 1
        ;;
esac

