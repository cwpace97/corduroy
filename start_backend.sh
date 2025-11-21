#!/bin/bash

# Start Backend Server Script
echo "🚀 Starting Ski Resort Dashboard Backend..."
echo "GraphQL API will be available at: http://localhost:8000/graphql"
echo ""

# Check if database exists
if [ ! -f "ski.db" ]; then
    echo "⚠️  Database not found. Initializing..."
    python init_db.py
fi

# Start the backend server
python -m uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000

