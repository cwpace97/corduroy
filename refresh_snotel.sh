#!/bin/bash
# SNOTEL Weather Data Refresh Script
# 
# This script collects SNOTEL weather data and imports it into the PostgreSQL database.
# Assumes SSH tunnel is already running (use start_tunnel.sh if needed).
#
# Usage:
#   ./refresh_snotel.sh                    # Default: last 7 days, daily data
#   ./refresh_snotel.sh --days 30          # Last 30 days
#   ./refresh_snotel.sh --hourly           # Hourly data (last 2 days default)
#   ./refresh_snotel.sh --begin 2025-11-01 --end 2025-11-30

set -e

# Script is at project root level
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEATHER_DIR="$PROJECT_ROOT/weather"
SQL_OUTPUT_FILE="$WEATHER_DIR/snotel_import.sql"

# Default parameters
DURATION="DAILY"
DAYS=7
BEGIN_DATE=""
END_DATE=""

# Help function
show_help() {
    echo "SNOTEL Weather Data Refresh Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --hourly              Collect hourly data (default: daily)"
    echo "  --daily               Collect daily data (default)"
    echo "  --days N              Number of days to look back (default: 7 for daily, 2 for hourly)"
    echo "  --begin YYYY-MM-DD    Start date (overrides --days)"
    echo "  --end YYYY-MM-DD      End date (default: today)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Last 7 days, daily data"
    echo "  $0 --days 30                 # Last 30 days, daily data"
    echo "  $0 --hourly                  # Last 2 days, hourly data"
    echo "  $0 --hourly --days 1         # Last 1 day, hourly data"
    echo "  $0 --begin 2025-11-01 --end 2025-11-30  # Specific date range"
    echo ""
    echo "Prerequisites:"
    echo "  - SSH tunnel must be running (use start_tunnel.sh)"
    echo "  - DATABASE_URL must be set in .env file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --hourly)
            DURATION="HOURLY"
            DAYS=2  # Default to 2 days for hourly data
            shift
            ;;
        --daily)
            DURATION="DAILY"
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        --begin)
            BEGIN_DATE="$2"
            shift 2
            ;;
        --end)
            END_DATE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Calculate dates if not explicitly provided
if [ -z "$END_DATE" ]; then
    END_DATE=$(date +%Y-%m-%d)
fi

if [ -z "$BEGIN_DATE" ]; then
    # macOS date command syntax
    if [[ "$OSTYPE" == "darwin"* ]]; then
        BEGIN_DATE=$(date -v-${DAYS}d +%Y-%m-%d)
    else
        # Linux date command syntax
        BEGIN_DATE=$(date -d "-${DAYS} days" +%Y-%m-%d)
    fi
fi

echo "=========================================="
echo "🏔️  SNOTEL Weather Data Refresh"
echo "=========================================="
echo "Duration:   $DURATION"
echo "Date Range: $BEGIN_DATE to $END_DATE"
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
echo "Step 1: Collecting SNOTEL data from USDA API..."
echo "------------------------------------------"

# Run the Python collector script from the weather directory
cd "$WEATHER_DIR"
python3 snotel_data_collector.py \
    --begin-date "$BEGIN_DATE" \
    --end-date "$END_DATE" \
    --duration "$DURATION" \
    --output "$SQL_OUTPUT_FILE"

if [ ! -f "$SQL_OUTPUT_FILE" ]; then
    echo "❌ Error: SQL file was not generated"
    exit 1
fi

# Count the number of observation inserts
OBS_COUNT=$(grep -c "INSERT INTO WEATHER_DATA.snotel_observations" "$SQL_OUTPUT_FILE" || echo "0")
echo ""
echo "✅ Generated SQL with $OBS_COUNT observation records"

echo ""
echo "Step 2: Executing SQL against database..."
echo "------------------------------------------"

# Execute the SQL file against the database using psql or Python
# First, try using psql if available
if command -v psql &> /dev/null; then
    echo "Using psql to execute SQL..."
    psql "$DATABASE_URL" -f "$SQL_OUTPUT_FILE"
    EXEC_STATUS=$?
else
    echo "psql not found, using Python to execute SQL..."
    
    # Create a temporary Python script to execute the SQL
    python3 << 'PYTHON_SCRIPT'
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

# Add project root to path for imports
project_root = Path(__file__).parent.parent if '__file__' in dir() else Path.cwd().parent
sys.path.insert(0, str(project_root))

try:
    import psycopg2
except ImportError:
    try:
        import psycopg as psycopg2
    except ImportError:
        print("❌ Error: Neither psycopg2 nor psycopg installed")
        sys.exit(1)

def get_db_connection():
    """Create database connection from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not set")
    
    parsed = urlparse(database_url)
    db_password = unquote(parsed.password) if parsed.password else None
    if db_password and '%' in db_password:
        db_password = unquote(db_password)
    
    return psycopg2.connect(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 5432,
        user=parsed.username,
        password=db_password,
        dbname=parsed.path.lstrip('/'),
        sslmode='prefer'
    )

def execute_sql_file(sql_file_path):
    """Execute SQL file against the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                success_count += 1
            except Exception as e:
                error_count += 1
                # Only print errors for actual failures, not comments
                if 'INSERT' in statement or 'CREATE' in statement:
                    print(f"  ⚠️  Warning on statement {i+1}: {str(e)[:100]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Executed {success_count} statements successfully")
    if error_count > 0:
        print(f"⚠️  {error_count} statements had warnings/errors")

# Execute the SQL file
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
sql_file = os.path.join(os.getcwd(), 'snotel_import.sql')
if os.path.exists(sql_file):
    execute_sql_file(sql_file)
else:
    # Try the weather directory
    sql_file = os.path.join(os.getcwd(), 'weather', 'snotel_import.sql')
    if os.path.exists(sql_file):
        execute_sql_file(sql_file)
    else:
        print(f"❌ SQL file not found")
        sys.exit(1)
PYTHON_SCRIPT
    EXEC_STATUS=$?
fi

if [ $EXEC_STATUS -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SNOTEL data refresh complete!"
    echo "=========================================="
    echo ""
    echo "Data imported:"
    echo "  - Date Range: $BEGIN_DATE to $END_DATE"
    echo "  - Duration: $DURATION"
    echo "  - Observations: $OBS_COUNT records"
    echo ""
    echo "Query the data:"
    echo "  SELECT * FROM WEATHER_DATA.v_resort_weather WHERE resort_name = 'Copper';"
else
    echo ""
    echo "❌ Error executing SQL (exit code: $EXEC_STATUS)"
    exit $EXEC_STATUS
fi
