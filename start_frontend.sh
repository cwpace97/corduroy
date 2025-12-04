#!/bin/bash

# Start Frontend Server Script
echo "🎨 Starting Ski Resort Dashboard Frontend..."
echo "Web app will be available at: http://localhost:5173"
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start the frontend server
npm run dev