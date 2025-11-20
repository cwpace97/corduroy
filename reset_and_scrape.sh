#!/bin/bash

# Reset database and run all scrapers using Docker Compose
echo "🔄 Ski Resort Database Reset & Scrape Script"
echo "============================================="
echo ""

# Reset the database locally (no need for Docker for this)
echo "Step 1: Resetting database..."
python3 init_db.py reset

# Check if reset was successful
if [ $? -ne 0 ]; then
    echo "❌ Database reset failed or was cancelled"
    exit 1
fi

echo ""
echo "Step 2: Starting Selenium Grid (Hub + Chromium Node)..."
echo "----------------------------------------"

# Start selenium hub and chromium node in detached mode
docker-compose up -d selenium-hub chromium-node

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
echo "Step 3: Running all scrapers..."
echo "----------------------------------------"

# Array of scraper profiles
scrapers=("abasin" "copper" "loveland" "winterpark" "keystone" "breckenridge" "vail")
scraper_names=("Arapahoe Basin" "Copper Mountain" "Loveland" "Winter Park" "Keystone" "Breckenridge" "Vail")

# Run each scraper sequentially
for i in "${!scrapers[@]}"; do
    profile="${scrapers[$i]}"
    name="${scraper_names[$i]}"
    
    echo ""
    echo "📍 Scraping ${name}..."
    
    # Run the scraper using docker-compose with the specific profile
    docker-compose --profile "${profile}" up "${profile}-scraper"
    
    # Check exit code
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: ${name} scraper failed"
    else
        echo "✅ ${name} completed"
    fi
    
    # Clean up the scraper container
    docker-compose --profile "${profile}" down "${profile}-scraper"
done

echo ""
echo "Step 4: Stopping Selenium Grid..."
echo "----------------------------------------"

# Stop selenium hub and chromium node
docker-compose down selenium-hub chromium-node

echo ""
echo "============================================="
echo "✅ All scrapers completed!"
echo ""
echo "You can now start the backend and frontend:"
echo "  Terminal 1: ./start_backend.sh"
echo "  Terminal 2: ./start_frontend.sh"
echo ""
