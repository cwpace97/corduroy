#!/bin/bash
# Weather Forecast Refresh Script
# 
# This script collects weather forecasts from NWS and Open-Meteo APIs
# and imports them into the PostgreSQL database.
# Assumes SSH tunnel is already running (use start_tunnel.sh if needed).
#
# Usage:
#   ./refresh_forecasts.sh

set -e

# Script is at project root level
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEATHER_DIR="$PROJECT_ROOT/weather"

echo "=========================================="
echo "🌤️  Weather Forecast Refresh"
echo "=========================================="
echo ""

# Load environment variables from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "📁 Loading environment from .env..."
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "⚠️  Warning: .env file not found at $PROJECT_ROOT/.env"
    echo "   Make sure DATABASE_URL is set in your environment"
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    echo "   Please set it in your .env file or export it"
    exit 1
fi

# Replace host.docker.internal with localhost for non-Docker execution
# (Docker containers need host.docker.internal, but this script runs on the host)
DATABASE_URL="${DATABASE_URL//host.docker.internal/localhost}"
export DATABASE_URL

echo ""
echo "Fetching forecasts from NWS and Open-Meteo APIs..."
echo "------------------------------------------"

# Run the Python forecast script
cd "$PROJECT_ROOT"
python3 weather/run_forecast_ecs.py

EXEC_STATUS=$?

if [ $EXEC_STATUS -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Forecast refresh complete!"
    echo "=========================================="
    echo ""
    echo "Query the data:"
    echo "  SELECT * FROM WEATHER_DATA.weather_forecasts WHERE resort_name = 'Copper' ORDER BY valid_time;"
else
    echo ""
    echo "❌ Error running forecast refresh (exit code: $EXEC_STATUS)"
    exit $EXEC_STATUS
fi

