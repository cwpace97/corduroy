#!/usr/bin/env python3
import sqlite3
import os
import sys
from pathlib import Path

DB_PATH = "ski.db"
SQL_DIR = Path(__file__).parent / "sql"
#TODO: the current database (sqlite) does not support proper hashing


def execute_sql_file(cursor, sql_file_path):
    """Execute SQL commands from a file"""
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
        cursor.executescript(sql_content)


def execute_sql_directory(cursor, directory_path, description="SQL files"):
    """Execute all SQL files in a directory"""
    sql_files = sorted(directory_path.glob("*.sql"))
    
    if not sql_files:
        print(f"  ⚠️  No SQL files found in {directory_path}")
        return
    
    print(f"  - Executing {description}...")
    for sql_file in sql_files:
        print(f"    • {sql_file.name}")
        execute_sql_file(cursor, sql_file)


def init_database():
    """Initialize SQLite database with runs and lifts tables"""
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables from SQL files
    tables_dir = SQL_DIR / "tables"
    execute_sql_directory(cursor, tables_dir, "tables")
    
    # Create indexes from SQL files
    indexes_dir = SQL_DIR / "indexes"
    execute_sql_directory(cursor, indexes_dir, "indexes")
    
    # Create views from SQL files
    views_dir = SQL_DIR / "views"
    execute_sql_directory(cursor, views_dir, "views")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database initialized successfully at {DB_PATH}")


def reset_database():
    """Completely reset the database - drop all tables and views, then recreate"""
    
    print(f"⚠️  WARNING: This will DELETE ALL DATA in {DB_PATH}")
    print("Are you sure you want to continue? (yes/no): ", end="")
    
    # Get confirmation
    confirmation = input().strip().lower()
    
    if confirmation not in ['yes', 'y']:
        print("❌ Reset cancelled")
        return
    
    print("\n🗑️  Dropping all tables and views...")
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all views and drop them
    print("  - Dropping views...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    for view in views:
        view_name = view[0]
        print(f"    • {view_name}")
        cursor.execute(f'DROP VIEW IF EXISTS {view_name}')
    
    # Get all tables and drop them
    print("  - Dropping tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"    • {table_name}")
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("\n✅ All tables and views dropped")
    print("\n🔨 Recreating database structure...")
    
    # Reinitialize the database
    init_database()
    
    print("\n✅ Database reset complete! Ready for fresh scraper data.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "reset":
            reset_database()
        elif command == "init":
            init_database()
        else:
            print("Usage:")
            print("  python init_db.py           # Initialize database (default)")
            print("  python init_db.py init      # Initialize database")
            print("  python init_db.py reset     # Reset database (delete all data)")
    else:
        # Default behavior - just initialize
        init_database() 