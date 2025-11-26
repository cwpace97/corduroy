#!/usr/bin/env python3
"""Test PostgreSQL database connection"""

import os
import sys
from urllib.parse import urlparse, unquote
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Try psycopg3 first, fallback to psycopg2
try:
    import psycopg
    USE_PSYCOPG3 = True
except ImportError:
    try:
        import psycopg2
        USE_PSYCOPG3 = False
    except ImportError:
        print("❌ Neither psycopg nor psycopg2 installed")
        sys.exit(1)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("   Set it in your .env file or export it:")
    print("   export DATABASE_URL='postgresql://user:password@host.docker.internal:5432/app'")
    sys.exit(1)

print("🔍 Testing PostgreSQL connection...")
print(f"   Connection string: {DATABASE_URL.split('@')[0]}@****@{DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")

# Parse connection URL
parsed = urlparse(DATABASE_URL)

db_host = parsed.hostname or 'localhost'
db_port = parsed.port or 5432
db_user = parsed.username
# URL decode the password (in case it was URL encoded)
db_password = unquote(parsed.password) if parsed.password else None
db_name = parsed.path.lstrip('/')

print(f"\n📋 Connection details:")
print(f"   Host: {db_host}")
print(f"   Port: {db_port}")
print(f"   Database: {db_name}")
print(f"   User: {db_user}")
print(f"   Password: {'*' * len(db_password) if db_password else 'NOT SET'}")

if not db_password:
    print("\n❌ Password not found in connection string!")
    sys.exit(1)

# Parse SSL mode
sslmode = 'prefer'
if parsed.query:
    params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
    sslmode = params.get('sslmode', 'prefer')

print(f"   SSL Mode: {sslmode}")

# Test connection
print(f"\n🔌 Attempting connection...")
try:
    conn_params = {
        'host': db_host,
        'port': db_port,
        'user': db_user,
        'password': db_password,
        'sslmode': sslmode,
    }
    
    if USE_PSYCOPG3:
        conn_params['dbname'] = db_name
        conn = psycopg.connect(**conn_params)
    else:
        conn_params['database'] = db_name
        conn = psycopg2.connect(**conn_params)
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    
    print(f"✅ Connection successful!")
    print(f"   PostgreSQL version: {version[0][:60]}...")
    
    # Test schema access
    cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'SKI_DATA'")
    schema_exists = cursor.fetchone()
    if schema_exists:
        print(f"   ✅ SKI_DATA schema exists")
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'SKI_DATA'
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"   ✅ Found {len(tables)} table(s): {', '.join([t[0] for t in tables])}")
        else:
            print(f"   ⚠️  No tables found in SKI_DATA schema")
    else:
        print(f"   ⚠️  SKI_DATA schema does not exist")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ All tests passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"   Error: {e}")
    print(f"\n💡 Troubleshooting:")
    print(f"   1. Check that SSH tunnel is running")
    print(f"   2. Verify password is correct (check URL encoding)")
    print(f"   3. Test password encoding:")
    print(f"      python3 -c \"from urllib.parse import quote; print(quote('your_password', safe=''))\"")
    print(f"   4. Verify username exists in PostgreSQL")
    sys.exit(1)

