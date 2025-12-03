#!/usr/bin/env python3
"""
Forecast Lambda Handler
Runs every 6 hours, fetching forecasts from Open-Meteo API.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add weather directory to path
weather_path = Path(__file__).parent / "weather"
sys.path.insert(0, str(weather_path))

from forecast_collector import ForecastCollector


def get_database_url():
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


def lambda_handler(event: dict, context) -> dict:
    """Main Lambda handler function"""
    print("=" * 60)
    print("Starting Weather Forecast Refresh")
    print("=" * 60)
    
    forecast_time = datetime.now()
    print(f"Forecast Time: {forecast_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get DATABASE_URL from Secrets Manager
        database_url = get_database_url()
        os.environ["DATABASE_URL"] = database_url
        
        # Output SQL file path
        sql_output_file = "/tmp/forecast_import.sql"
        
        # Initialize collector
        collector = ForecastCollector()
        
        # Fetch forecasts from Open-Meteo
        print("Fetching forecasts from Open-Meteo API...")
        forecasts = collector.fetch_all_forecasts()
        
        if not forecasts:
            print("⚠️  No forecasts collected")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No forecasts collected",
                    "forecast_time": forecast_time.isoformat()
                })
            }
        
        print(f"✅ Collected {len(forecasts)} forecast records")
        print()
        
        # Generate SQL INSERT statements
        print("Generating SQL INSERT statements...")
        complete_sql = collector.generate_sql_inserts(forecasts)
        
        # Write to file
        with open(sql_output_file, 'w') as f:
            f.write(complete_sql)
        
        print(f"✅ Generated SQL with {len(forecasts)} forecast records")
        print()
        
        # Execute SQL against database
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
                    conn.commit()
                    success_count += 1
                except Exception as e:
                    error_count += 1
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
        print(f"  - Source: Open-Meteo")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Forecast refresh complete",
                "forecast_time": forecast_time.isoformat(),
                "forecast_records": len(forecasts),
                "statements_executed": success_count,
                "statements_with_errors": error_count,
                "source": "Open-Meteo"
            })
        }
        
    except Exception as e:
        error_msg = f"Error during forecast refresh: {str(e)}"
        print(f"❌ {error_msg}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_msg})
        }

