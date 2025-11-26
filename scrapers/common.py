import json
import os
from datetime import datetime as dt
from pytz import timezone
from urllib.parse import urlparse
from contextlib import contextmanager
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import *
from sshtunnel import SSHTunnelForwarder

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root (parent of scrapers directory)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

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

# SSH Tunnel configuration
# Set these environment variables:
#   SSH_HOST or EC2_HOST - Your EC2 instance IP or hostname
#   SSH_USERNAME - SSH username (default: ubuntu)
#   SSH_KEY_PATH - Path to SSH private key (default: ~/.ssh/id_rsa)
#   SSH_PORT - SSH port (default: 22)
#
# Database configuration (for connection through SSH tunnel)
# Format: postgresql://username:password@localhost/database
# The tunnel automatically forwards to EC2 PostgreSQL
# Set DATABASE_URL with username and password (host/port are handled by tunnel)
SSH_HOST = os.getenv('SSH_HOST', os.getenv('EC2_HOST'))
SSH_USERNAME = os.getenv('SSH_USERNAME', 'ubuntu')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', os.path.expanduser('~/.ssh/id_rsa'))
SSH_PORT = int(os.getenv('SSH_PORT', '22'))

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ski_admin:password@localhost/app')

# PostgreSQL connection on EC2 (through tunnel)
DB_REMOTE_HOST = 'localhost'  # On EC2, PostgreSQL listens on localhost
DB_REMOTE_PORT = 5432  # PostgreSQL port on EC2
DB_LOCAL_PORT = None  # Will be set dynamically by tunnel


@contextmanager
def get_ssh_tunnel():
    """Create and manage SSH tunnel to EC2 PostgreSQL"""
    if not SSH_HOST:
        raise ValueError("SSH_HOST or EC2_HOST environment variable must be set")
    
    # Find an available local port
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        local_port = s.getsockname()[1]
    
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_pkey=SSH_KEY_PATH,
        remote_bind_address=(DB_REMOTE_HOST, DB_REMOTE_PORT),
        local_bind_address=('localhost', local_port)
    )
    
    try:
        tunnel.start()
        print(f"SSH tunnel established: localhost:{local_port} -> {SSH_HOST}:{DB_REMOTE_PORT}")
        yield local_port
    finally:
        tunnel.stop()
        print("SSH tunnel closed")


def get_db_connection(local_port=None):
    """Create and return a PostgreSQL database connection through SSH tunnel"""
    parsed = urlparse(DATABASE_URL)
    
    # Parse connection parameters
    # If local_port is provided (from tunnel), use it; otherwise use from URL
    db_host = parsed.hostname or 'localhost'
    db_port = local_port or parsed.port or 5432
    db_user = parsed.username
    db_password = parsed.password
    db_name = parsed.path.lstrip('/')
    
    # Parse SSL mode from query string (optional, since we're using SSH tunnel)
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
    """Prepare data and save to PostgreSQL database through SSH tunnel"""
    # Deduplicate lifts and runs
    lifts_set = {each['liftName']: each for each in lifts}.values()
    runs_set = {each['runName']: each for each in runs}.values()
    
    # Get current date
    now = dt.now(tz=timezone("America/Denver"))
    formatted_date = now.strftime("%Y-%m-%d")
    
    # Save to database using a single SSH tunnel for both operations
    with get_ssh_tunnel() as local_port:
        conn = get_db_connection(local_port=local_port)
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

def save_lifts_to_db(lifts: list[dict], location: str, date: str):
    """Save lifts data to PostgreSQL database through SSH tunnel
    
    Note: This creates its own tunnel. For better performance when saving both lifts and runs,
    use prepareAndSaveData() which uses a single tunnel for both operations.
    """
    with get_ssh_tunnel() as local_port:
        conn = get_db_connection(local_port=local_port)
        cursor = conn.cursor()
        
        try:
            for lift in lifts:
                # Convert boolean to string for consistency
                lift_status = str(lift['liftStatus']).lower()
                
                # Insert new record (views handle getting latest)
                cursor.execute('''
                INSERT INTO SKI_DATA.lifts 
                (location, lift_name, lift_status, lift_type, updated_date, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    location,
                    lift['liftName'],
                    lift_status,
                    lift.get('liftType', 'Unknown'),
                    date,
                    dt.now().isoformat()
                ))
            
            conn.commit()
            print(f"Saved {len(lifts)} lifts to database")
        except Exception as e:
            conn.rollback()
            print(f"Error saving lifts: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

def save_runs_to_db(runs: list[dict], location: str, date: str):
    """Save runs data to PostgreSQL database through SSH tunnel
    
    Note: This creates its own tunnel. For better performance when saving both lifts and runs,
    use prepareAndSaveData() which uses a single tunnel for both operations.
    """
    with get_ssh_tunnel() as local_port:
        conn = get_db_connection(local_port=local_port)
        cursor = conn.cursor()
        
        try:
            for run in runs:
                # Convert boolean to string for consistency
                run_status = str(run['runStatus']).lower()
                run_groomed = run.get('runGroomed', False)
                
                # Insert new record (views handle getting latest)
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
                    date,
                    run.get('runArea', ''),
                    run_groomed,
                    dt.now().isoformat()
                ))
            
            conn.commit()
            print(f"Saved {len(runs)} runs to database")
        except Exception as e:
            conn.rollback()
            print(f"Error saving runs: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

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