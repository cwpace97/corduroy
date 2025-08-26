#!/usr/bin/env python3
import sqlite3
import os
from pathlib import Path

DB_PATH = "ski.db"
#TODO: the current database (sqlite) does not support proper hashing

def init_database():
    """Initialize SQLite database with runs and lifts tables"""
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create runs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        run_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location || run_name)))) STORED,
        location TEXT NOT NULL,
        location_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location)))) STORED,
        run_name TEXT NOT NULL,
        run_difficulty TEXT,
        run_status TEXT NOT NULL,
        updated_date TEXT NOT NULL,
        run_area TEXT,
        run_groomed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create lifts table  
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lifts (
        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        lift_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location || lift_name)))) STORED,
        location TEXT NOT NULL,
        location_id TEXT GENERATED ALWAYS AS (lower(hex(quote(location)))) STORED,
        lift_name TEXT NOT NULL,
        lift_status TEXT NOT NULL,
        lift_type TEXT,
        updated_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_location_date ON runs(location, updated_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_name ON runs(run_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_difficulty ON runs(run_difficulty)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(run_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_run_id_date ON runs(run_id, updated_date)')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lifts_location_date ON lifts(location, updated_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lifts_name ON lifts(lift_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lifts_status ON lifts(lift_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_lifts_lift_id_date ON lifts(lift_id, updated_date)')
    
    # create views for latest runs and lifts (most recent entry per run_id/lift_id)
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_locations AS
    SELECT DISTINCT
        location,
        LOWER(HEX(QUOTE(location))) AS location_id,
        MAX(updated_date) AS updated_date
    FROM runs
    GROUP BY location
    UNION
    SELECT DISTINCT
        location,
        LOWER(HEX(QUOTE(location))) AS location_id,
        MAX(updated_date) AS updated_date
    FROM lifts
    GROUP BY location;
    ''')
    
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_runs AS
    SELECT DISTINCT
        location,
        run_name,
        run_difficulty,
        LOWER(HEX(QUOTE(location))) || '-' || LOWER(HEX(QUOTE(run_name))) AS run_id,
        MAX(updated_date) AS updated_date
    FROM runs
    GROUP BY location, run_name, run_difficulty
    ''')
    
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_lifts AS
    SELECT DISTINCT
        location,
        lift_name,
        lift_type,
        LOWER(HEX(QUOTE(location))) || '-' || LOWER(HEX(QUOTE(lift_name))) AS lift_id,
        MAX(updated_date) AS updated_date
    FROM lifts
    GROUP BY location, lift_name, lift_type
    ''')
    
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_current_runs AS
    SELECT * FROM runs r1
    WHERE r1.updated_date = (
        SELECT MAX(r2.updated_date) 
        FROM runs r2 
        WHERE r2.run_id = r1.run_id
    )
    ''')
    
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS v_current_lifts AS
    SELECT * FROM lifts l1
    WHERE l1.updated_date = (
        SELECT MAX(l2.updated_date) 
        FROM lifts l2 
        WHERE l2.lift_id = l1.lift_id
    )
    ''')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_database() 