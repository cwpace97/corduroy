import json
import sqlite3
import os
from datetime import datetime as dt
from pytz import timezone

from selenium import webdriver
from selenium.common.exceptions import *

# Database configuration
DB_PATH = os.environ.get('DB_PATH', '/data/ski.db')

def prepareAndSaveData(lifts: list[dict], runs: list[dict], location: str):
    """Prepare data and save to SQLite database instead of publishing to SNS"""
    # Deduplicate lifts and runs
    lifts_set = {each['liftName']: each for each in lifts}.values()
    runs_set = {each['runName']: each for each in runs}.values()
    
    # Get current date
    now = dt.now(tz=timezone("America/Denver"))
    formatted_date = now.strftime("%Y-%m-%d")
    
    # Save to database
    save_lifts_to_db(list(lifts_set), location, formatted_date)
    save_runs_to_db(list(runs_set), location, formatted_date)
    
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
    """Save lifts data to SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for lift in lifts:
        # Convert boolean to string for consistency
        lift_status = str(lift['liftStatus']).lower()
        
        # Insert or replace record
        cursor.execute('''
        INSERT OR REPLACE INTO lifts 
        (location, lift_name, lift_status, lift_type, updated_date, updated_at) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            location,
            lift['liftName'],
            lift_status,
            lift.get('liftType', 'Unknown'),
            date,
            dt.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(lifts)} lifts to database")

def save_runs_to_db(runs: list[dict], location: str, date: str):
    """Save runs data to SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for run in runs:
        # Convert boolean to string for consistency
        run_status = str(run['runStatus']).lower()
        run_groomed = run.get('runGroomed', False)
        
        # Insert or replace record
        cursor.execute('''
        INSERT OR REPLACE INTO runs 
        (location, run_name, run_difficulty, run_status, 
         updated_date, run_area, run_groomed, updated_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    conn.close()
    print(f"Saved {len(runs)} runs to database")

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