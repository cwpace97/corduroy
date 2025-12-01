#!/bin/bash

# Array of scraper profiles
scrapers=("abasin" "copper" "loveland" "winterpark" "keystone" "breckenridge" "vail" "steamboat" "crestedbutte" "purgatory" "telluride")
scraper_names=("Arapahoe Basin" "Copper Mountain" "Loveland" "Winter Park" "Keystone" "Breckenridge" "Vail" "Steamboat" "Crested Butte" "Purgatory" "Telluride")

# Function to display usage
usage() {
    echo "Usage: $0 [-r resort_name]"
    echo ""
    echo "Options:"
    echo "  -r, --resort    Run scraper for a single resort (optional)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Available resorts:"
    for i in "${!scrapers[@]}"; do
        echo "  ${scrapers[$i]} - ${scraper_names[$i]}"
    done
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all scrapers"
    echo "  $0 -r crestedbutte    # Run only Crested Butte scraper"
    echo "  $0 --resort vail      # Run only Vail scraper"
    exit 0
}

# Parse command line arguments
SINGLE_RESORT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--resort)
            SINGLE_RESORT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate single resort if provided
if [ -n "$SINGLE_RESORT" ]; then
    VALID_RESORT=false
    RESORT_INDEX=-1
    for i in "${!scrapers[@]}"; do
        if [ "${scrapers[$i]}" = "$SINGLE_RESORT" ]; then
            VALID_RESORT=true
            RESORT_INDEX=$i
            break
        fi
    done
    
    if [ "$VALID_RESORT" = false ]; then
        echo "❌ Error: Unknown resort '$SINGLE_RESORT'"
        echo ""
        echo "Available resorts:"
        for i in "${!scrapers[@]}"; do
            echo "  ${scrapers[$i]} - ${scraper_names[$i]}"
        done
        exit 1
    fi
fi

echo ""
echo "Step 1: Starting Selenium Grid (Hub + Chromium Node)..."
echo "----------------------------------------"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from .env"
else
    echo "⚠️  Warning: .env file not found"
fi

# Start selenium hub and chromium node in detached mode
docker-compose -f scrapers/docker-compose.yml --env-file .env up -d selenium-hub chromium-node

# Wait for selenium hub to be ready
echo "⏳ Waiting for Selenium Hub to be ready..."
sleep 10

# Check if selenium hub is running
if ! docker ps | grep -q selenium-hub; then
    echo "❌ Selenium Hub failed to start"
    exit 1
fi

echo "✅ Selenium Grid is ready"
echo ""

if [ -n "$SINGLE_RESORT" ]; then
    echo "Step 2: Running scraper for ${scraper_names[$RESORT_INDEX]}..."
else
    echo "Step 2: Running all scrapers..."
fi
echo "----------------------------------------"

# Determine which scrapers to run
if [ -n "$SINGLE_RESORT" ]; then
    # Run single resort
    profile="$SINGLE_RESORT"
    name="${scraper_names[$RESORT_INDEX]}"
    
    echo ""
    echo "📍 Scraping ${name}..."
    
    # Run the scraper using docker-compose with the specific profile
    docker-compose -f scrapers/docker-compose.yml --env-file .env --profile "${profile}" up "${profile}-scraper"
    
    # Check exit code
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: ${name} scraper failed"
    else
        echo "✅ ${name} completed"
    fi
    
    # Clean up the scraper container
    docker-compose -f scrapers/docker-compose.yml --env-file .env --profile "${profile}" down "${profile}-scraper"
else
    # Run each scraper sequentially
    for i in "${!scrapers[@]}"; do
        profile="${scrapers[$i]}"
        name="${scraper_names[$i]}"
        
        echo ""
        echo "📍 Scraping ${name}..."
        
        # Run the scraper using docker-compose with the specific profile
        docker-compose -f scrapers/docker-compose.yml --env-file .env --profile "${profile}" up "${profile}-scraper"
        
        # Check exit code
        if [ $? -ne 0 ]; then
            echo "⚠️  Warning: ${name} scraper failed"
        else
            echo "✅ ${name} completed"
        fi
        
        # Clean up the scraper container
        docker-compose -f scrapers/docker-compose.yml --env-file .env --profile "${profile}" down "${profile}-scraper"
    done
fi

echo ""
echo "Step 3: Stopping Selenium Grid..."
echo "----------------------------------------"

# Stop selenium hub and chromium node
docker-compose -f scrapers/docker-compose.yml --env-file .env down selenium-hub chromium-node

echo ""
echo "============================================="
if [ -n "$SINGLE_RESORT" ]; then
    echo "✅ ${scraper_names[$RESORT_INDEX]} scraper completed!"
else
    echo "✅ All scrapers completed!"
fi
echo ""
