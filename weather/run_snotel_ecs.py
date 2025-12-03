#!/usr/bin/env python3
"""
ECS-compatible entrypoint for SNOTEL data collection.
Runs every 3 hours, fetching hourly data for a 4-hour window.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add weather directory to path
sys.path.insert(0, str(Path(__file__).parent))

from snotel_data_collector import SNOTELDataCollector


def run_snotel_refresh():
    """Run SNOTEL data collection for hourly data from the past 4 hours"""
    print("=" * 60)
    print("Starting SNOTEL Weather Data Refresh")
    print("=" * 60)
    
    # Calculate 4-hour window
    # The SNOTEL API works with dates, so we need to include both today and potentially yesterday
    # to cover the 4-hour window (e.g., if it's 2 AM, we need yesterday's data too)
    now = datetime.now()
    four_hours_ago = now - timedelta(hours=4)
    
    # Use the dates that cover our 4-hour window
    begin_date_str = four_hours_ago.strftime("%Y-%m-%d")
    end_date_str = now.strftime("%Y-%m-%d")
    
    print(f"Duration: HOURLY")
    print(f"Time Window: {four_hours_ago.strftime('%Y-%m-%d %H:%M')} to {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"Date Range: {begin_date_str} to {end_date_str}")
    print()
    
    # Get DATABASE_URL from environment (will be injected by ECS from Secrets Manager)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    # Replace host.docker.internal with EC2 hostname if needed
    # In ECS, we'll connect directly to EC2 PostgreSQL
    database_url = database_url.replace("host.docker.internal", os.getenv("DB_HOST", "localhost"))
    
    # Set environment variable for the collector
    os.environ["DATABASE_URL"] = database_url
    
    # Output SQL file path
    sql_output_file = "/tmp/snotel_import.sql"
    
    try:
        # Initialize collector
        collector = SNOTELDataCollector()
        
        # Collect data and generate SQL
        print("Collecting SNOTEL data from USDA API...")
        sql = collector.collect_and_generate_sql(
            begin_date=begin_date_str,
            end_date=end_date_str,
            duration="HOURLY",
            output_file=sql_output_file
        )
        
        # Count observations
        obs_count = 0
        if os.path.exists(sql_output_file):
            with open(sql_output_file, 'r') as f:
                content = f.read()
                obs_count = content.count("INSERT INTO WEATHER_DATA.snotel_observations")
        
        print(f"✅ Generated SQL with {obs_count} observation records")
        print()
        
        # Execute SQL against database
        print("Executing SQL against database...")
        
        # Import database execution logic
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
                print("❌ Error: Neither psycopg nor psycopg2 installed")
                sys.exit(1)
        
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
        
        # Read and execute SQL file
        with open(sql_output_file, 'r') as f:
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
                    if 'INSERT' in statement or 'CREATE' in statement:
                        print(f"  ⚠️  Warning on statement {i+1}: {str(e)[:100]}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Executed {success_count} statements successfully")
        if error_count > 0:
            print(f"⚠️  {error_count} statements had warnings/errors")
        
        print()
        print("=" * 60)
        print("✅ SNOTEL data refresh complete!")
        print("=" * 60)
        print(f"Data imported:")
        print(f"  - Date Range: {begin_date_str} to {end_date_str}")
        print(f"  - Duration: HOURLY")
        print(f"  - Observations: {obs_count} records")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error during SNOTEL refresh: {str(e)}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_snotel_refresh()

