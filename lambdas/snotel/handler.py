#!/usr/bin/env python3
"""
SNOTEL Lambda Handler
Runs once daily, fetching hourly data for the previous 3 days (through yesterday 23:59:59).

Note: USDA AWDB API uses exclusive end_date, so end_date=today gets data
through yesterday's last hour.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add weather directory to path
weather_path = Path(__file__).parent / "weather"
sys.path.insert(0, str(weather_path))

from snotel_data_collector import SNOTELDataCollector


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
    print("Starting SNOTEL Weather Data Refresh")
    print("=" * 60)
    
    # Calculate date range: 3 days before today (through yesterday 23:59:59)
    # USDA AWDB API uses exclusive end_date, so:
    # - end_date = today means data through yesterday 23:59:59
    # - begin_date = 3 days ago
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today  # API is exclusive, so this gets data through yesterday 23:59:59
    begin_date = today - timedelta(days=3)  # 3 days ago
    
    begin_date_str = begin_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Duration: HOURLY")
    print(f"Date Range: {begin_date_str} to {end_date_str} (exclusive end, gets data through yesterday)")
    print()
    
    try:
        # Get DATABASE_URL from Secrets Manager
        database_url = get_database_url()
        os.environ["DATABASE_URL"] = database_url
        
        # Output SQL file path
        sql_output_file = "/tmp/snotel_import.sql"
        
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
        print("✅ SNOTEL data refresh complete!")
        print("=" * 60)
        print(f"Data imported:")
        print(f"  - Date Range: {begin_date_str} to {end_date_str}")
        print(f"  - Duration: HOURLY")
        print(f"  - Observations: {obs_count} records")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "SNOTEL data refresh complete",
                "date_range": f"{begin_date_str} to {end_date_str}",
                "observations": obs_count,
                "statements_executed": success_count,
                "statements_with_errors": error_count
            })
        }
        
    except Exception as e:
        error_msg = f"Error during SNOTEL refresh: {str(e)}"
        print(f"❌ {error_msg}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_msg})
        }
