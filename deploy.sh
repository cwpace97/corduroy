#!/bin/bash

# Corduroy Ski Resort Scraper Deployment Script
# This script manages the dockerized web scrapers for ski resort data collection

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_FILE="ski.db"
PROJECT_NAME="corduroy"

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}     Corduroy Ski Resort Scraper Manager     ${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  init                 Initialize the SQLite database"
    echo "  build               Build the Docker images"
    echo "  start-grid          Start Selenium Grid (hub + chromium node)"
    echo "  stop-grid           Stop Selenium Grid"
    echo "  run [SCRAPER]       Run a specific scraper (copper, loveland, winterpark, abasin, all)"
    echo "  clean               Stop and remove all containers"
    echo "  logs [SCRAPER]      Show logs for a specific scraper"
    echo "  shell               Open a shell in the scraper container"
    echo "  status              Show status of all containers"
    echo "  help                Show this help message"
    echo
    echo "Examples:"
    echo "  $0 init                    # Initialize database"
    echo "  $0 build                   # Build Docker images"
    echo "  $0 start-grid              # Start Selenium Grid"
    echo "  $0 run copper              # Run Copper Mountain scraper"
    echo "  $0 run abasin              # Run Arapahoe Basin scraper"
    echo "  $0 run all                 # Run all scrapers sequentially"
    echo "  $0 logs copper             # Show logs for Copper scraper"
    echo "  $0 clean                   # Clean up all containers"
    echo
}

init_database() {
    echo -e "${YELLOW}Initializing SQLite database...${NC}"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python 3 is required but not found. Please install Python 3.${NC}"
        return 1
    fi
    
    # Run database initialization script
    echo -e "${BLUE}Setting up database schema and tables...${NC}"
    if python3 init_db.py; then
        echo -e "${GREEN}Database initialization completed successfully${NC}"
        
        # Show database info
        if [ -f "$DB_FILE" ]; then
            local db_size=$(du -h "$DB_FILE" | cut -f1)
            echo -e "${BLUE}Database created: ${DB_FILE} (${db_size})${NC}"
        fi
    else
        echo -e "${RED}Failed to initialize database${NC}"
        return 1
    fi
}

build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    docker-compose build
    echo -e "${GREEN}Docker images built successfully${NC}"
}

start_selenium_grid() {
    echo -e "${YELLOW}Starting Selenium Grid (Hub + Chromium Node)...${NC}"
    
    # Pull the latest seleniarm images
    echo -e "${BLUE}Pulling latest seleniarm images...${NC}"
    docker pull seleniarm/hub:latest
    docker pull seleniarm/node-chromium:latest
    
    # Start the selenium hub and chromium node
    docker-compose up -d selenium-hub chromium-node
    
    # Wait for selenium hub to be ready
    echo -e "${BLUE}Waiting for Selenium Grid to be ready...${NC}"
    sleep 5
    
    # Check if selenium hub is accessible
    for i in {1..30}; do
        if curl -s http://localhost:4444/wd/hub/status > /dev/null; then
            echo -e "${GREEN}Selenium Grid is ready${NC}"
            echo -e "${BLUE}Selenium Grid UI: http://localhost:4444/ui${NC}"
            return 0
        fi
        echo -e "${YELLOW}Waiting for Selenium Grid... ($i/30)${NC}"
        sleep 2
    done
    
    echo -e "${RED}Selenium Grid failed to start properly${NC}"
    return 1
}

stop_selenium_grid() {
    echo -e "${YELLOW}Stopping Selenium Grid...${NC}"
    docker-compose stop selenium-hub chromium-node
    docker-compose rm -f selenium-hub chromium-node
    echo -e "${GREEN}Selenium Grid stopped successfully${NC}"
}

run_scraper() {
    local scraper=$1
    
    if [ -z "$scraper" ]; then
        echo -e "${RED}ERROR: Please specify a scraper: copper, loveland, winterpark, abasin, or all${NC}"
        return 1
    fi
    
    # Ensure Selenium Grid is running
    if ! curl -s http://localhost:4444/wd/hub/status > /dev/null; then
        echo -e "${YELLOW}WARNING: Selenium Grid not detected. Starting it first...${NC}"
        start_selenium_grid
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to start Selenium Grid${NC}"
            return 1
        fi
    fi
    
    case "$scraper" in
        "copper")
            echo -e "${YELLOW}Running Copper Mountain scraper...${NC}"
            docker-compose --profile copper up --build
            echo -e "${GREEN}Copper Mountain scraper completed${NC}"
            ;;
        "loveland")
            echo -e "${YELLOW}Running Loveland scraper...${NC}"
            docker-compose --profile loveland up --build
            echo -e "${GREEN}Loveland scraper completed${NC}"
            ;;
        "winterpark")
            echo -e "${YELLOW}Running Winter Park scraper...${NC}"
            docker-compose --profile winterpark up --build
            echo -e "${GREEN}Winter Park scraper completed${NC}"
            ;;
        "abasin")
            echo -e "${YELLOW}Running Arapahoe Basin scraper...${NC}"
            docker-compose --profile abasin up --build
            echo -e "${GREEN}Arapahoe Basin scraper completed${NC}"
            ;;
        "all")
            echo -e "${YELLOW}Running all scrapers sequentially...${NC}"
            run_scraper "copper"
            run_scraper "loveland" 
            run_scraper "winterpark"
            run_scraper "abasin"
            echo -e "${GREEN}All scrapers completed successfully${NC}"
            ;;
        *)
            echo -e "${RED}ERROR: Unknown scraper: $scraper${NC}"
            echo -e "${BLUE}Available scrapers: copper, loveland, winterpark, abasin, all${NC}"
            return 1
            ;;
    esac
}

show_logs() {
    local scraper=$1
    
    if [ -z "$scraper" ]; then
        echo -e "${RED}ERROR: Please specify a scraper: copper, loveland, winterpark, abasin, selenium-hub, or chromium-node${NC}"
        return 1
    fi
    
    local container_name=""
    case "$scraper" in
        "selenium-hub"|"chromium-node")
            container_name="$scraper"
            ;;
        *)
            container_name="${PROJECT_NAME}-${scraper}-scraper"
            ;;
    esac
    
    echo -e "${BLUE}Showing logs for ${scraper}...${NC}"
    docker logs "$container_name" || echo -e "${YELLOW}WARNING: Container may not exist or be running${NC}"
}

clean_containers() {
    echo -e "${YELLOW}Cleaning up containers...${NC}"
    docker-compose down --remove-orphans
    docker-compose --profile copper down --remove-orphans 2>/dev/null || true
    docker-compose --profile loveland down --remove-orphans 2>/dev/null || true
    docker-compose --profile winterpark down --remove-orphans 2>/dev/null || true
    docker-compose --profile abasin down --remove-orphans 2>/dev/null || true
    docker-compose --profile init down --remove-orphans 2>/dev/null || true
    echo -e "${GREEN}Cleanup completed successfully${NC}"
}

open_shell() {
    echo -e "${BLUE}Opening shell in scraper container...${NC}"
    docker-compose run --rm copper-scraper /bin/bash
}

show_status() {
    echo -e "${BLUE}Container Status:${NC}"
    docker ps -a --filter "name=${PROJECT_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    docker ps -a --filter "name=selenium-hub" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    docker ps -a --filter "name=chromium-node" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    
    if [ -f "$DB_FILE" ]; then
        local db_size=$(du -h "$DB_FILE" | cut -f1)
        echo -e "${GREEN}Database file: ${DB_FILE} (${db_size})${NC}"
    else
        echo -e "${YELLOW}WARNING: Database file not found. Run '$0 init' to create it.${NC}"
    fi
    
    echo
    # Check Selenium Grid status
    if curl -s http://localhost:4444/wd/hub/status > /dev/null; then
        echo -e "${GREEN}Selenium Grid: RUNNING (http://localhost:4444/ui)${NC}"
    else
        echo -e "${YELLOW}Selenium Grid: STOPPED${NC}"
    fi
}

# Main script logic
case "${1:-help}" in
    "init")
        print_header
        init_database
        ;;
    "build")
        print_header
        build_images
        ;;
    "start-grid")
        print_header
        start_selenium_grid
        ;;
    "stop-grid")
        print_header
        stop_selenium_grid
        ;;
    "run")
        print_header
        run_scraper "$2"
        ;;
    "logs")
        print_header
        show_logs "$2"
        ;;
    "clean")
        print_header
        clean_containers
        ;;
    "shell")
        print_header
        open_shell
        ;;
    "status")
        print_header
        show_status
        ;;
    "help"|"-h"|"--help"|"")
        print_header
        print_usage
        ;;
    *)
        print_header
        echo -e "${RED}ERROR: Unknown command: $1${NC}"
        echo
        print_usage
        exit 1
        ;;
esac 