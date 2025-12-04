#!/usr/bin/env python3
"""
One-time script to backfill 7 days of historical weather and SNOTEL data.
Run this locally to populate the database with historical data.

Usage:
    python scripts/backfill_historical_data.py

Requires:
    - .env file with DATABASE_URL or DATABASE_URL environment variable
    - requests library installed
    - python-dotenv library installed
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather.snotel_data_collector import SNOTELDataCollector


# Resort coordinates for Open-Meteo
RESORT_COORDINATES = {
    "Copper": {"latitude": 39.499982, "longitude": -106.155866},
    "Loveland": {"latitude": 39.680456, "longitude": -105.898216},
    "Breckenridge": {"latitude": 39.481096, "longitude": -106.068073},
    "Winter Park": {"latitude": 39.887187, "longitude": -105.764075},
    "Keystone": {"latitude": 39.603876, "longitude": -105.954666},
    "Arapahoe Basin": {"latitude": 39.642705, "longitude": -105.87223},
    "Vail": {"latitude": 39.638704, "longitude": -106.379194},
    "Crested Butte": {"latitude": 38.899762, "longitude": -106.954394},
    "Steamboat": {"latitude": 40.452263, "longitude": -106.770076},
    "Purgatory": {"latitude": 37.626489, "longitude": -107.819173},
    "Telluride": {"latitude": 37.921412, "longitude": -107.836462},
    "Monarch": {"latitude": 38.512454, "longitude": -106.335721},
}

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_db_connection():
    """Create database connection from DATABASE_URL"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Try psycopg3 first, fallback to psycopg2
    try:
        import psycopg
        USE_PSYCOPG3 = True
    except ImportError:
        try:
            import psycopg2
            USE_PSYCOPG3 = False
        except ImportError:
            raise ImportError("Neither psycopg nor psycopg2 installed")
    
    parsed = urlparse(database_url)
    db_password = unquote(parsed.password) if parsed.password else None
    if db_password and '%' in db_password:
        db_password = unquote(db_password)
    
    conn_params = {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': db_password,
        'sslmode': 'prefer'
    }
    
    if USE_PSYCOPG3:
        import psycopg
        conn_params['dbname'] = parsed.path.lstrip('/')
        return psycopg.connect(**conn_params)
    else:
        import psycopg2
        conn_params['database'] = parsed.path.lstrip('/')
        return psycopg2.connect(**conn_params)


def fetch_historical_weather(latitude: float, longitude: float, start_date: str, end_date: str):
    """Fetch historical daily weather data from Open-Meteo Archive API."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "America/Denver",
    }
    
    try:
        response = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error fetching data: {str(e)}")
        return None


def backfill_historical_weather(conn, begin_date: str, end_date: str):
    """Backfill historical weather data from Open-Meteo using daily aggregates."""
    print()
    print("=" * 60)
    print("Backfilling Historical Weather Data (Open-Meteo Daily)")
    print("=" * 60)
    print(f"Date Range: {begin_date} to {end_date}")
    print(f"Resorts: {len(RESORT_COORDINATES)}")
    print()
    
    cursor = conn.cursor()
    total_records = 0
    
    for resort_name, coords in RESORT_COORDINATES.items():
        print(f"📍 {resort_name}...")
        
        data = fetch_historical_weather(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            start_date=begin_date,
            end_date=end_date
        )
        
        if not data:
            print(f"  ⚠️  No data received")
            continue
        
        daily = data.get("daily", {})
        times = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        precipitations = daily.get("precipitation_sum", [])
        snowfalls = daily.get("snowfall_sum", [])
        
        records = 0
        for i, time_str in enumerate(times):
            observation_date = time_str  # Already in YYYY-MM-DD format
            
            t_max = temp_max[i] if i < len(temp_max) and temp_max[i] is not None else None
            precip = precipitations[i] if i < len(precipitations) and precipitations[i] is not None else None
            snow = snowfalls[i] if i < len(snowfalls) and snowfalls[i] is not None else None
            
            try:
                # Insert daily record with hour=0 to represent the full day
                # Store temp_max in temperature_f field
                cursor.execute("""
                    INSERT INTO WEATHER_DATA.historical_weather 
                        (resort_name, observation_date, observation_hour, temperature_f, precipitation_in, snowfall_in)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (resort_name, observation_date, observation_hour) DO UPDATE SET
                        temperature_f = EXCLUDED.temperature_f,
                        precipitation_in = EXCLUDED.precipitation_in,
                        snowfall_in = EXCLUDED.snowfall_in
                """, (resort_name, observation_date, 0, t_max, precip, snow))
                records += 1
            except Exception as e:
                print(f"  ⚠️  Error inserting record: {str(e)[:50]}")
        
        conn.commit()
        print(f"  ✅ Inserted {records} daily records")
        total_records += records
    
    print()
    print(f"✅ Total historical weather records: {total_records}")
    return total_records


def backfill_snotel_data(conn, begin_date: str, end_date: str):
    """Backfill SNOTEL data."""
    print()
    print("=" * 60)
    print("Backfilling SNOTEL Data")
    print("=" * 60)
    print(f"Date Range: {begin_date} to {end_date}")
    print()
    
    # Initialize collector
    collector = SNOTELDataCollector()
    print(f"Stations: {len(collector.unique_stations)}")
    print()
    
    # Collect data and generate SQL
    print("Fetching SNOTEL data from USDA API...")
    sql_output_file = "/tmp/snotel_backfill.sql"
    
    sql = collector.collect_and_generate_sql(
        begin_date=begin_date,
        end_date=end_date,
        duration="HOURLY",
        output_file=sql_output_file
    )
    
    # Count and execute statements
    with open(sql_output_file, 'r') as f:
        sql_content = f.read()
    
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    cursor = conn.cursor()
    success_count = 0
    error_count = 0
    
    print(f"Executing {len(statements)} SQL statements...")
    
    for i, statement in enumerate(statements):
        if statement and not statement.startswith('--'):
            try:
                cursor.execute(statement)
                conn.commit()
                success_count += 1
            except Exception as e:
                error_count += 1
                conn.rollback()
                # Only print first few errors
                if error_count <= 5:
                    print(f"  ⚠️  Warning: {str(e)[:80]}")
    
    print()
    print(f"✅ Executed {success_count} statements successfully")
    if error_count > 0:
        print(f"⚠️  {error_count} statements had warnings/errors")
    
    return success_count


def main():
    """Main entry point."""
    print("=" * 60)
    print("  Historical Data Backfill Script")
    print("=" * 60)
    
    # Check DATABASE_URL
    if not os.environ.get("DATABASE_URL"):
        print()
        print("❌ Error: DATABASE_URL not found")
        print()
        print("Add it to your .env file:")
        print("  DATABASE_URL=postgresql://user:pass@host:port/dbname")
        print()
        print("Or set it as an environment variable:")
        print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
        sys.exit(1)
    
    # Calculate date range: 7 days before today (not including today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today - timedelta(days=1)  # Yesterday
    begin_date = today - timedelta(days=7)  # 7 days ago
    
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print()
    print(f"Date Range: {begin_date_str} to {end_date_str}")
    print(f"  (7 days, not including today)")
    print()
    
    # Connect to database
    print("Connecting to database...")
    try:
        conn = get_db_connection()
        print("✅ Connected")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    try:
        # Backfill historical weather (Open-Meteo)
        weather_records = backfill_historical_weather(conn, begin_date_str, end_date_str)
        
        # Backfill SNOTEL data
        snotel_records = backfill_snotel_data(conn, begin_date_str, end_date_str)
        
        print()
        print("=" * 60)
        print("  Backfill Complete!")
        print("=" * 60)
        print(f"  Historical Weather Records: {weather_records}")
        print(f"  SNOTEL Statements Executed: {snotel_records}")
        print()
        
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

