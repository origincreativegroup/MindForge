#!/bin/bash

# MindForge Casey Creative Projects Startup Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎨 Starting MindForge Casey Creative Projects…${NC}\n"

# Check if backend directory exists
if [ ! -d "apps/backend" ]; then
    echo "❌ Backend directory not found. Please run setup first."
    exit 1
fi

cd apps/backend

# Check if database exists
if [ ! -f "mindforge_creative.db" ]; then
    echo "🔄 Initializing creative projects database…"
    poetry run python init_creative_database.py
fi

# Start the application
echo -e "${GREEN}🚀 Starting server…${NC}"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "💖 Health Check: http://localhost:8000/healthz"
echo "🎨 Main Interface: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd ../..
poetry run uvicorn apps.backend.app:app --host 0.0.0.0 --port 8000 --reload
