#!/usr/bin/env python3
"""GraphQL resolvers for querying ski resort data"""

import psycopg2
import psycopg2.extras
import os
from typing import List, Optional
from .schema import ResortSummary, Lift, Run, RunsByDifficulty, HistoryDataPoint, RecentlyOpened, GlobalRecentlyOpened, RecentlyOpenedWithLocation


# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_all_resorts() -> List[ResortSummary]:
    """Get summary data for all ski resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get all unique locations
    cursor.execute("SELECT DISTINCT location FROM SKI_DATA.v_locations ORDER BY location")
    locations = [row['location'] for row in cursor.fetchall()]
    
    resorts = []
    for location in locations:
        resort = get_resort_by_location(location)
        if resort:
            resorts.append(resort)
    
    conn.close()
    return resorts


def get_resort_by_location(location: str) -> Optional[ResortSummary]:
    """Get detailed data for a specific resort"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get current lifts for this location with date opened
    cursor.execute("""
        SELECT 
            v.lift_name, 
            v.lift_type, 
            v.lift_status, 
            v.updated_date,
            (SELECT MIN(updated_date) 
             FROM SKI_DATA.lifts 
             WHERE location = v.location 
             AND lift_name = v.lift_name 
             AND lift_status = 'true') as date_opened
        FROM SKI_DATA.v_lifts_current v
        WHERE v.location = %s
        ORDER BY v.lift_name
    """, (location,))
    
    lifts_data = cursor.fetchall()
    lifts = []
    open_lifts = 0
    closed_lifts = 0
    last_updated = ""
    
    for row in lifts_data:
        lift_status = "Open" if row['lift_status'] in ['Open', 'open', True, 1, '1', 'true', 'True'] else "Closed"
        lifts.append(Lift(
            lift_name=row['lift_name'],
            lift_type=row['lift_type'] or "Unknown",
            lift_status=lift_status,
            date_opened=row['date_opened'] if lift_status == "Open" else None
        ))
        if lift_status == "Open":
            open_lifts += 1
        else:
            closed_lifts += 1
        
        if row['updated_date'] and (not last_updated or row['updated_date'] > last_updated):
            last_updated = row['updated_date']
    
    # Get current runs for this location with date opened
    cursor.execute("""
        SELECT 
            v.run_name, 
            v.run_difficulty, 
            v.run_status, 
            v.run_area, 
            v.run_groomed, 
            v.updated_date,
            (SELECT MIN(updated_date) 
             FROM SKI_DATA.runs 
             WHERE location = v.location 
             AND run_name = v.run_name 
             AND run_status = 'true') as date_opened
        FROM SKI_DATA.v_runs_current v
        WHERE v.location = %s
        ORDER BY v.run_name
    """, (location,))
    
    runs_data = cursor.fetchall()
    runs = []
    open_runs = 0
    closed_runs = 0
    
    # Track runs by difficulty (open runs only)
    difficulty_counts = {
        'green': 0,
        'blue': 0,
        'black': 0,
        'double_black': 0,
        'terrain_park': 0,
        'other': 0
    }
    
    for row in runs_data:
        run_status = "Open" if row['run_status'] in ['Open', 'open', True, 1, '1', 'true', 'True'] else "Closed"
        difficulty = (row['run_difficulty'] or "Unknown").lower().strip()
        
        runs.append(Run(
            run_name=row['run_name'],
            run_difficulty=row['run_difficulty'] or "Unknown",
            run_status=run_status,
            run_area=row['run_area'],
            run_groomed=bool(row['run_groomed']),
            date_opened=row['date_opened'] if run_status == "Open" else None
        ))
        
        if run_status == "Open":
            open_runs += 1
            
            # Categorize by difficulty
            if 'green' in difficulty or 'easiest' in difficulty or 'beginner' in difficulty:
                difficulty_counts['green'] += 1
            elif 'blue' in difficulty or 'intermediate' in difficulty or 'more difficult' in difficulty:
                difficulty_counts['blue'] += 1
            elif 'double' in difficulty or 'expert' in difficulty or 'most difficult' in difficulty:
                difficulty_counts['double_black'] += 1
            elif 'black' in difficulty or 'advanced' in difficulty or 'difficult' in difficulty:
                difficulty_counts['black'] += 1
            elif 'park' in difficulty or 'terrain' in difficulty:
                difficulty_counts['terrain_park'] += 1
            else:
                difficulty_counts['other'] += 1
        else:
            closed_runs += 1
        
        if row['updated_date'] and (not last_updated or row['updated_date'] > last_updated):
            last_updated = row['updated_date']
    
    # Get lifts history (last 7 days)
    cursor.execute("""
        SELECT updated_date as date, open_count
        FROM SKI_DATA.v_lifts_history
        WHERE location = %s
        ORDER BY updated_date DESC
        LIMIT 7
    """, (location,))
    
    lifts_history_data = cursor.fetchall()
    lifts_history = [
        HistoryDataPoint(date=row['date'], open_count=row['open_count'])
        for row in reversed(lifts_history_data)  # Reverse to show oldest to newest
    ]
    
    # Get runs history (last 7 days)
    cursor.execute("""
        SELECT updated_date as date, open_count
        FROM SKI_DATA.v_runs_history
        WHERE location = %s
        ORDER BY updated_date DESC
        LIMIT 7
    """, (location,))
    
    runs_history_data = cursor.fetchall()
    runs_history = [
        HistoryDataPoint(date=row['date'], open_count=row['open_count'])
        for row in reversed(runs_history_data)  # Reverse to show oldest to newest
    ]
    
    # Get recently opened lifts (top 3)
    cursor.execute("""
        SELECT lift_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.lifts
        WHERE location = %s AND lift_status = 'true'
        GROUP BY lift_name
        ORDER BY date_opened DESC
        LIMIT 3
    """, (location,))
    
    recently_opened_lifts_data = cursor.fetchall()
    recently_opened_lifts = [
        RecentlyOpened(name=row['lift_name'], date_opened=row['date_opened'])
        for row in recently_opened_lifts_data
    ]
    
    # Get recently opened runs (top 3)
    cursor.execute("""
        SELECT run_name, MIN(updated_date) as date_opened
        FROM SKI_DATA.runs
        WHERE location = %s AND run_status = 'true'
        GROUP BY run_name
        ORDER BY date_opened DESC
        LIMIT 3
    """, (location,))
    
    recently_opened_runs_data = cursor.fetchall()
    recently_opened_runs = [
        RecentlyOpened(name=row['run_name'], date_opened=row['date_opened'])
        for row in recently_opened_runs_data
    ]
    
    conn.close()
    
    # Return None if no data found for this location
    if not lifts and not runs:
        return None
    
    return ResortSummary(
        location=location,
        total_lifts=len(lifts),
        open_lifts=open_lifts,
        closed_lifts=closed_lifts,
        total_runs=len(runs),
        open_runs=open_runs,
        closed_runs=closed_runs,
        runs_by_difficulty=RunsByDifficulty(
            green=difficulty_counts['green'],
            blue=difficulty_counts['blue'],
            black=difficulty_counts['black'],
            double_black=difficulty_counts['double_black'],
            terrain_park=difficulty_counts['terrain_park'],
            other=difficulty_counts['other']
        ),
        last_updated=last_updated or "Unknown",
        lifts=lifts,
        runs=runs,
        lifts_history=lifts_history,
        runs_history=runs_history,
        recently_opened_lifts=recently_opened_lifts,
        recently_opened_runs=recently_opened_runs
    )


def get_global_recently_opened() -> GlobalRecentlyOpened:
    """Get recently opened lifts and runs across all resorts"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get top 10 recently opened lifts across all locations
    cursor.execute("""
        SELECT lift_name, location, MIN(updated_date) as date_opened
        FROM SKI_DATA.lifts
        WHERE lift_status = 'true'
        GROUP BY location, lift_name
        ORDER BY date_opened DESC
        LIMIT 10
    """)
    
    lifts_data = cursor.fetchall()
    lifts = [
        RecentlyOpenedWithLocation(
            name=row['lift_name'],
            location=row['location'],
            date_opened=row['date_opened']
        )
        for row in lifts_data
    ]
    
    # Get top 10 recently opened runs across all locations
    cursor.execute("""
        SELECT run_name, location, MIN(updated_date) as date_opened
        FROM SKI_DATA.runs
        WHERE run_status = 'true'
        GROUP BY location, run_name
        ORDER BY date_opened DESC
        LIMIT 10
    """)
    
    runs_data = cursor.fetchall()
    runs = [
        RecentlyOpenedWithLocation(
            name=row['run_name'],
            location=row['location'],
            date_opened=row['date_opened']
        )
        for row in runs_data
    ]
    
    conn.close()
    
    return GlobalRecentlyOpened(lifts=lifts, runs=runs)

