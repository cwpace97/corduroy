#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Load environment variables from .env file FIRST (before importing psycopg2)
PROJECT_ROOT = Path(__file__).parent
env_file = PROJECT_ROOT / ".env"

if env_file.exists():
    print("📁 Loading environment from .env...")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    # Only set if key doesn't already exist (don't override existing env vars)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value
    except Exception as e:
        print(f"⚠️  Warning: Error reading .env file: {e}")
        print("   Continuing with existing environment variables...")
else:
    print("⚠️  Warning: .env file not found at .env")
    print("   Make sure DATABASE_URL is set in your environment")

# Get database URL from environment variable (required)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL environment variable is required")
    print("   Set it in your .env file or export it")
    sys.exit(1)

# Replace host.docker.internal with localhost for non-Docker execution
# (Docker containers need host.docker.internal, but this script runs on the host)
DATABASE_URL = DATABASE_URL.replace("host.docker.internal", "localhost")

# Import psycopg AFTER loading environment (try psycopg3 first, fallback to psycopg2)
try:
    import psycopg
    USE_PSYCOPG3 = True
except ImportError:
    try:
        import psycopg2
        import psycopg2.extras
        USE_PSYCOPG3 = False
    except ImportError:
        print("❌ Error: Neither psycopg nor psycopg2 installed")
        sys.exit(1)

from urllib.parse import urlparse

SQL_DIR = Path(__file__).parent / "sql"


def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    if USE_PSYCOPG3:
        return psycopg.connect(DATABASE_URL)
    else:
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
        
        # Create WEATHER_DATA schema if it doesn't exist
        print("  - Creating WEATHER_DATA schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS WEATHER_DATA")
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
        # Drop all views in SKI_DATA and WEATHER_DATA schemas
        print("  - Dropping views...")
        for schema in ['SKI_DATA', 'WEATHER_DATA']:
            cursor.execute(f"""
                SELECT viewname 
                FROM pg_views 
                WHERE schemaname = '{schema}'
            """)
            views = cursor.fetchall()
            for view in views:
                view_name = view[0]
                print(f"    • {schema}.{view_name}")
                cursor.execute(f'DROP VIEW IF EXISTS {schema}.{view_name} CASCADE')
        
        # Drop all tables in SKI_DATA and WEATHER_DATA schemas
        print("  - Dropping tables...")
        for schema in ['SKI_DATA', 'WEATHER_DATA']:
            cursor.execute(f"""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = '{schema}'
            """)
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                print(f"    • {schema}.{table_name}")
                cursor.execute(f'DROP TABLE IF EXISTS {schema}.{table_name} CASCADE')
        
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
