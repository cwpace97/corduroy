echo ""
echo "Step 1: Starting Selenium Grid (Hub + Chromium Node)..."
echo "----------------------------------------"

# Start selenium hub and chromium node in detached mode
docker-compose -f scrapers/docker-compose.yml up -d selenium-hub chromium-node

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
echo "Step 2: Running all scrapers..."
echo "----------------------------------------"

# Array of scraper profiles
scrapers=("abasin" "copper" "loveland" "winterpark" "keystone" "breckenridge" "vail" "steamboat")
scraper_names=("Arapahoe Basin" "Copper Mountain" "Loveland" "Winter Park" "Keystone" "Breckenridge" "Vail" "Steamboat")

# Run each scraper sequentially
for i in "${!scrapers[@]}"; do
    profile="${scrapers[$i]}"
    name="${scraper_names[$i]}"
    
    echo ""
    echo "📍 Scraping ${name}..."
    
    # Run the scraper using docker-compose with the specific profile
    docker-compose -f scrapers/docker-compose.yml --profile "${profile}" up "${profile}-scraper"
    
    # Check exit code
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: ${name} scraper failed"
    else
        echo "✅ ${name} completed"
    fi
    
    # Clean up the scraper container
    docker-compose -f scrapers/docker-compose.yml --profile "${profile}" down "${profile}-scraper"
done

echo ""
echo "Step 3: Stopping Selenium Grid..."
echo "----------------------------------------"

# Stop selenium hub and chromium node
docker-compose -f scrapers/docker-compose.yml down selenium-hub chromium-node

echo ""
echo "============================================="
echo "✅ All scrapers completed!"
echo ""