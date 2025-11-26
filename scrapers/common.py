import json
import os
from datetime import datetime as dt
from pytz import timezone
from urllib.parse import urlparse, unquote
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import *
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
# Try psycopg3 first (better support), fallback to psycopg2
try:
    import psycopg
    USE_PSYCOPG3 = True
except ImportError:
    try:
        import psycopg2
        USE_PSYCOPG3 = False
    except ImportError:
        raise ImportError("Neither psycopg nor psycopg2 installed. Install with: pip install psycopg or pip install psycopg2-binary")

# Database configuration
# Format: postgresql://username:password@host:port/database
# Note: Assumes SSH tunnel is already running separately on host machine
# For local (non-Docker): postgresql://user:password@localhost:5432/app
# For Docker containers: postgresql://user:password@host.docker.internal:5432/app
# Read DATABASE_URL at function call time, not module import time
# This ensures environment variables are properly set by docker-compose
def get_database_url():
    """Get DATABASE_URL from environment, loading .env if needed"""
    load_dotenv(dotenv_path=env_path)
    return os.getenv('DATABASE_URL')


def get_db_connection():
    """Create and return a PostgreSQL database connection
    
    Assumes SSH tunnel is already running separately.
    Connect to localhost:5432 (or port specified in DATABASE_URL).
    """
    # Get DATABASE_URL at function call time (not module import time)
    # This ensures docker-compose environment variables are properly loaded
    database_url = get_database_url()
    
    parsed = urlparse(database_url)
    
    # Parse connection parameters
    db_host = parsed.hostname or 'localhost'
    db_port = parsed.port or 5432
    db_user = parsed.username
    # URL decode password in case it was URL encoded (handles special characters)
    db_password = unquote(parsed.password) if parsed.password else None
    db_name = parsed.path.lstrip('/')
    
    if not db_password:
        raise ValueError("Password not found in DATABASE_URL")
    
    # Check if password was already decoded (double-encoding issue)
    if '%' in db_password:
        db_password = unquote(db_password)
    
    # Parse SSL mode from query string (optional, SSL not required through tunnel)
    sslmode = 'prefer'  # default, SSL not required through tunnel
    if parsed.query:
        params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
        sslmode = params.get('sslmode', 'prefer')
    
    # Build connection parameters
    conn_params = {
        'host': db_host,
        'port': db_port,
        'user': db_user,
        'password': db_password,
        'sslmode': sslmode,
    }
    
    if USE_PSYCOPG3:
        conn_params['dbname'] = db_name
        return psycopg.connect(**conn_params)
    else:
        conn_params['database'] = db_name
        return psycopg2.connect(**conn_params)

def prepareAndSaveData(lifts: list[dict], runs: list[dict], location: str):
    """Prepare data and save to PostgreSQL database
    
    Note: Assumes SSH tunnel is already running separately.
    Connect to localhost:5432 (or port specified in DATABASE_URL).
    """
    # Deduplicate lifts and runs
    lifts_set = {each['liftName']: each for each in lifts}.values()
    runs_set = {each['runName']: each for each in runs}.values()
    
    # Get current date
    now = dt.now(tz=timezone("America/Denver"))
    formatted_date = now.strftime("%Y-%m-%d")
    
    # Save to database (assumes tunnel is already running)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Save lifts
        for lift in list(lifts_set):
            lift_status = str(lift['liftStatus']).lower()
            cursor.execute('''
            INSERT INTO SKI_DATA.lifts 
            (location, lift_name, lift_status, lift_type, updated_date, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                location,
                lift['liftName'],
                lift_status,
                lift.get('liftType', 'Unknown'),
                formatted_date,
                dt.now().isoformat()
            ))
        
        # Save runs
        for run in list(runs_set):
            run_status = str(run['runStatus']).lower()
            run_groomed = run.get('runGroomed', False)
            cursor.execute('''
            INSERT INTO SKI_DATA.runs 
            (location, run_name, run_difficulty, run_status, 
             updated_date, run_area, run_groomed, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                location,
                run['runName'],
                run.get('runDifficulty', 'Unknown'),
                run_status,
                formatted_date,
                run.get('runArea', ''),
                run_groomed,
                dt.now().isoformat()
            ))
        
        conn.commit()
        print(f"Saved {len(list(lifts_set))} lifts and {len(list(runs_set))} runs to database")
    except Exception as e:
        conn.rollback()
        print(f"Error saving data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    # Create message for logging (backward compatibility)
    message = {
        "updatedDate": formatted_date,
        "location": location,
        "lifts": list(lifts_set),
        "runs": list(runs_set)
    }
    print(f"Data saved to database for {location}: {len(lifts_set)} lifts, {len(runs_set)} runs")
    return json.dumps(message)

# Keep legacy function for backward compatibility
def prepareForExport(lifts: list[dict], runs: list[dict], location: str):
    """Legacy function - now redirects to prepareAndSaveData"""
    return prepareAndSaveData(lifts, runs, location)

def isElementPresent(driver: webdriver.Chrome, lookupType: str, locatorKey: str):
    try:
        driver.find_element(lookupType, locatorKey)
        return True
    except NoSuchElementException as nse:
        return False
    except StaleElementReferenceException as sere:
        return False

def safeSearch(driver: webdriver.Chrome, lookupType: str, locatorKey: str):
    if isElementPresent(driver, lookupType, locatorKey):
        return driver.find_element(lookupType, locatorKey)
    return False