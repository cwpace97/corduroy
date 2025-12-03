#!/usr/bin/env python3
"""
ECS-compatible entrypoint for weather forecast collection.
Runs every 6 hours, fetching forecasts from NWS and Open-Meteo APIs.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add weather directory to path
sys.path.insert(0, str(Path(__file__).parent))

from forecast_collector import ForecastCollector


def run_forecast_refresh():
    """Run forecast data collection for all resorts"""
    print("=" * 60)
    print("Starting Weather Forecast Refresh")
    print("=" * 60)
    
    forecast_time = datetime.now()
    print(f"Forecast Time: {forecast_time.strftime('%Y-%m-%d %H:%M:%S')}")
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
    sql_output_file = "/tmp/forecast_import.sql"
    
    try:
        # Initialize collector
        collector = ForecastCollector()
        
        # Fetch forecasts from all sources
        print("Fetching forecasts from NWS and Open-Meteo APIs...")
        forecasts = collector.fetch_all_forecasts()
        
        if not forecasts:
            print("⚠️  No forecasts collected")
            sys.exit(0)
        
        print(f"✅ Collected {len(forecasts)} forecast records")
        print()
        
        # Generate SQL INSERT statements (schema is handled by init_db.py)
        print("Generating SQL INSERT statements...")
        complete_sql = collector.generate_sql_inserts(forecasts)
        
        # Write to file
        with open(sql_output_file, 'w') as f:
            f.write(complete_sql)
        
        print(f"✅ Generated SQL with {len(forecasts)} forecast records")
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
                    # Commit after each successful statement to allow partial success
                    conn.commit()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    # Rollback the failed transaction so we can continue with next statement
                    conn.rollback()
                    if 'INSERT' in statement or 'CREATE' in statement:
                        print(f"  ⚠️  Warning on statement {i+1}: {str(e)[:100]}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Executed {success_count} statements successfully")
        if error_count > 0:
            print(f"⚠️  {error_count} statements had warnings/errors")
        
        print()
        print("=" * 60)
        print("✅ Weather forecast refresh complete!")
        print("=" * 60)
        print(f"Data imported:")
        print(f"  - Forecast Records: {len(forecasts)}")
        print(f"  - Forecast Time: {forecast_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - Sources: NWS, Open-Meteo")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error during forecast refresh: {str(e)}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_forecast_refresh()

