#!/usr/bin/env python3
"""
Historical Weather Lambda Handler
Runs once daily, fetching daily temperature (high/low) and precipitation data from Open-Meteo
for the previous 3 days (not including today).

Uses daily aggregates (temperature_2m_max, temperature_2m_min) to properly capture
daily high and low temperatures, matching the backfill script behavior.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


# Resort coordinates - same as in resort_snotel_mapping.json
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


def get_database_url() -> str:
    """Get DATABASE_URL from Secrets Manager"""
    database_url_secret_name = os.environ.get("DATABASE_URL_SECRET_NAME")
    if not database_url_secret_name:
        raise ValueError("DATABASE_URL_SECRET_NAME environment variable not set")
    
    try:
        import boto3
        secrets_client = boto3.client("secretsmanager")
        secret_response = secrets_client.get_secret_value(SecretId=database_url_secret_name)
        return secret_response["SecretString"]
    except Exception as e:
        raise ValueError(f"Failed to retrieve DATABASE_URL from Secrets Manager: {e}")


def fetch_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch historical daily weather data from Open-Meteo Archive API.
    
    Uses daily aggregates to get proper high/low temperatures for each day.
    
    Args:
        latitude: Resort latitude
        longitude: Resort longitude
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        API response data or None if request failed
    """
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


def generate_sql_inserts(resort_name: str, data: Dict[str, Any]) -> List[str]:
    """
    Generate SQL INSERT statements for historical weather data.
    
    Uses daily aggregates from Open-Meteo to properly capture high/low temps.
    Stores as observation_hour=0 to represent the full day's data.
    
    Args:
        resort_name: Name of the resort
        data: API response data from Open-Meteo (daily format)
    
    Returns:
        List of SQL INSERT statements
    """
    inserts = []
    
    daily = data.get("daily", {})
    times = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    precipitations = daily.get("precipitation_sum", [])
    snowfalls = daily.get("snowfall_sum", [])
    
    for i, time_str in enumerate(times):
        # time_str is already in YYYY-MM-DD format for daily data
        observation_date = time_str
        
        t_max = temp_max[i] if i < len(temp_max) and temp_max[i] is not None else None
        t_min = temp_min[i] if i < len(temp_min) and temp_min[i] is not None else None
        precip = precipitations[i] if i < len(precipitations) and precipitations[i] is not None else None
        snow = snowfalls[i] if i < len(snowfalls) and snowfalls[i] is not None else None
        
        # Build INSERT statement with upsert
        t_max_val = str(t_max) if t_max is not None else "NULL"
        t_min_val = str(t_min) if t_min is not None else "NULL"
        precip_val = str(precip) if precip is not None else "NULL"
        snow_val = str(snow) if snow is not None else "NULL"
        
        # Insert daily record with hour=0 to represent the full day
        insert = f"""INSERT INTO WEATHER_DATA.historical_weather 
    (resort_name, observation_date, observation_hour, temperature_f, temp_min_f, precipitation_in, snowfall_in)
VALUES ('{resort_name}', '{observation_date}', 0, {t_max_val}, {t_min_val}, {precip_val}, {snow_val})
ON CONFLICT (resort_name, observation_date, observation_hour) DO UPDATE SET
    temperature_f = EXCLUDED.temperature_f,
    temp_min_f = EXCLUDED.temp_min_f,
    precipitation_in = EXCLUDED.precipitation_in,
    snowfall_in = EXCLUDED.snowfall_in;"""
        
        inserts.append(insert)
    
    return inserts


def lambda_handler(event: dict, context) -> dict:
    """Main Lambda handler function"""
    print("=" * 60)
    print("Starting Historical Weather Data Refresh (Open-Meteo)")
    print("=" * 60)
    
    # Calculate date range: 3 days before today (not including today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today - timedelta(days=1)  # Yesterday
    begin_date = today - timedelta(days=3)  # 3 days ago
    
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Date Range: {begin_date_str} to {end_date_str} (3 days, not including today)")
    print(f"Resorts: {len(RESORT_COORDINATES)}")
    print()
    
    try:
        # Get DATABASE_URL from Secrets Manager
        database_url = get_database_url()
        os.environ["DATABASE_URL"] = database_url
        
        # Collect all SQL statements
        all_inserts = []
        
        for resort_name, coords in RESORT_COORDINATES.items():
            print(f"📍 {resort_name}...")
            
            data = fetch_historical_weather(
                latitude=coords["latitude"],
                longitude=coords["longitude"],
                start_date=begin_date_str,
                end_date=end_date_str
            )
            
            if data:
                inserts = generate_sql_inserts(resort_name, data)
                all_inserts.extend(inserts)
                print(f"  ✅ Generated {len(inserts)} records")
            else:
                print(f"  ⚠️  No data received")
        
        print()
        print(f"Total SQL statements: {len(all_inserts)}")
        
        if not all_inserts:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No historical weather data collected",
                    "date_range": f"{begin_date_str} to {end_date_str}"
                })
            }
        
        # Execute SQL against database
        print()
        print("Executing SQL against database...")
        
        from urllib.parse import urlparse, unquote
        
        # Try psycopg3 first (better support), fallback to psycopg2
        try:
            import psycopg
            USE_PSYCOPG3 = True
        except ImportError:
            try:
                import psycopg2
                USE_PSYCOPG3 = False
            except ImportError:
                error_msg = "Neither psycopg nor psycopg2 installed"
                print(f"❌ Error: {error_msg}")
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": error_msg})
                }
        
        # Parse DATABASE_URL and connect
        parsed = urlparse(database_url)
        db_password = unquote(parsed.password) if parsed.password else None
        if db_password and '%' in db_password:
            db_password = unquote(db_password)
        
        # Build connection parameters
        conn_params = {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': db_password,
            'sslmode': 'prefer'
        }
        
        if USE_PSYCOPG3:
            conn_params['dbname'] = parsed.path.lstrip('/')
            conn = psycopg.connect(**conn_params)
        else:
            conn_params['database'] = parsed.path.lstrip('/')
            conn = psycopg2.connect(**conn_params)
        
        cursor = conn.cursor()
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(all_inserts):
            try:
                cursor.execute(statement)
                conn.commit()
                success_count += 1
            except Exception as e:
                error_count += 1
                conn.rollback()
                if i < 5:  # Only print first few errors
                    print(f"  ⚠️  Warning on statement {i+1}: {str(e)[:100]}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Executed {success_count} statements successfully")
        if error_count > 0:
            print(f"⚠️  {error_count} statements had warnings/errors")
        
        print()
        print("=" * 60)
        print("✅ Historical weather data refresh complete!")
        print("=" * 60)
        print(f"Data imported:")
        print(f"  - Date Range: {begin_date_str} to {end_date_str}")
        print(f"  - Resorts: {len(RESORT_COORDINATES)}")
        print(f"  - Records: {success_count}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Historical weather data refresh complete",
                "date_range": f"{begin_date_str} to {end_date_str}",
                "resorts": len(RESORT_COORDINATES),
                "records_inserted": success_count,
                "records_with_errors": error_count
            })
        }
        
    except Exception as e:
        error_msg = f"Error during historical weather refresh: {str(e)}"
        print(f"❌ {error_msg}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_msg})
        }

