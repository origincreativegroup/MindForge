#!/bin/bash

# Development startup with auto-reload

export DEBUG=true
export LOG_LEVEL=DEBUG

echo "🔄 Starting in development mode with auto-reload…"
echo "🎨 Frontend: http://localhost:5173"
echo "🚀 Backend: http://localhost:8000"
echo ""

# Start frontend and backend concurrently
trap 'kill 0' SIGINT

cd apps/frontend && pnpm dev &
cd apps/backend && poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000 &

wait
