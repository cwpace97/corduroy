#!/bin/bash

# Start Backend Server Script
echo "🚀 Starting Ski Resort Dashboard Backend..."
echo "GraphQL API will be available at: http://localhost:8000/graphql"
echo ""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📦 Loading environment from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set. Create a .env file with:"
    echo "    DATABASE_URL=postgresql://user:password@host:5432/dbname"
    echo ""
    echo "💡 For EC2 PostgreSQL, start the tunnel first:"
    echo "    ./start_tunnel.sh"
    exit 1
fi

# Replace the host in DATABASE_URL with localhost (for SSH tunnel)
# Format: postgresql://user:password@host:port/database
# Extract parts and rebuild with localhost
DATABASE_URL=$(echo "$DATABASE_URL" | sed -E 's|(@)[^:]+(:)|@localhost:|')
export DATABASE_URL

echo "🔗 Connecting via localhost (tunnel)..."
echo "   ${DATABASE_URL%%@*}@localhost:${DATABASE_URL##*localhost:}"

# Start the backend server
python -m uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000

