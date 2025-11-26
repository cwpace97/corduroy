#!/usr/bin/env python3
import psycopg2
import psycopg2.extras
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Get database URL from environment variable (required)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL environment variable is required")
    print("   Set it in your .env file or export it")
    sys.exit(1)

SQL_DIR = Path(__file__).parent / "sql"


def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    return psycopg2.connect(DATABASE_URL)


def execute_sql_file(cursor, sql_file_path):
    """Execute SQL commands from a file"""
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
        # Split by semicolon and execute each statement
        # Filter out empty statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"    ⚠️  Warning executing {sql_file_path.name}: {e}")
                    # Continue with other statements


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
    """Initialize PostgreSQL database with runs and lifts tables"""
    
    # Create database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create SKI_DATA schema if it doesn't exist
        print("  - Creating SKI_DATA schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS SKI_DATA")
        conn.commit()
        
        # Create tables from SQL files
        tables_dir = SQL_DIR / "tables"
        execute_sql_directory(cursor, tables_dir, "tables")
        conn.commit()
        
        # Create indexes from SQL files
        indexes_dir = SQL_DIR / "indexes"
        execute_sql_directory(cursor, indexes_dir, "indexes")
        conn.commit()
        
        # Create views from SQL files
        views_dir = SQL_DIR / "views"
        execute_sql_directory(cursor, views_dir, "views")
        conn.commit()
        
        print(f"\n✅ Database initialized successfully")
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def reset_database():
    """Completely reset the database - drop all tables and views, then recreate"""
    
    print(f"⚠️  WARNING: This will DELETE ALL DATA in the database")
    print("Are you sure you want to continue? (yes/no): ", end="")
    
    # Get confirmation
    confirmation = input().strip().lower()
    
    if confirmation not in ['yes', 'y']:
        print("❌ Reset cancelled")
        return
    
    print("\n🗑️  Dropping all tables and views...")
    
    # Create database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Drop all views in SKI_DATA schema
        print("  - Dropping views...")
        cursor.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'SKI_DATA'
        """)
        views = cursor.fetchall()
        for view in views:
            view_name = view[0]
            print(f"    • {view_name}")
            cursor.execute(f'DROP VIEW IF EXISTS SKI_DATA.{view_name} CASCADE')
        
        # Drop all tables in SKI_DATA schema
        print("  - Dropping tables...")
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'SKI_DATA'
        """)
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            print(f"    • {table_name}")
            cursor.execute(f'DROP TABLE IF EXISTS SKI_DATA.{table_name} CASCADE')
        
        conn.commit()
        print("\n✅ All tables and views dropped")
        
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
    
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
