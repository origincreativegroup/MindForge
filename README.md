MindForge Casey — README (Updated)
An interactive process-extraction MVP with:
Live Mermaid swimlane graph (steps, actors, tools, decisions)
Clickable nodes → targeted follow‑ups
Edit mode with inline modal editor (owner/SLA/inputs/outputs/notes/parallel group)
Scenario overlays colored by simulated load with real-time Scale slider
Predicted cycle time
Drag‑to‑reorder steps
Export SVG/PNG
Snapshot diffs
Actor-level SLA & capacity controls
Deadlines & dependencies with Look‑Ahead and Look‑Back views
Discovery Mode chips + Ask next best question
Polished UI: command palette, toasts, tour, tooltips, friendly empty states
Repository Layout
backend/ – FastAPI application and services.
frontend/ – React + D3 client built with Vite.
tests/ – unit tests for backend services.
run.sh – convenience script to start the backend.
Quick Start
Run everything (backend only)
./run.sh
# open http://localhost:8000
The script creates a virtual environment, installs dependencies, exports APP_NAME and SECRET_KEY, and launches Uvicorn on port 8000.
Manual backend setup
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
Manual steps mirror the script above.
Frontend development
cd frontend
npm install
npm run dev   # starts Vite dev server on http://localhost:5173 by default
Development scripts and dependencies are defined in package.json.
Notable API Endpoints
POST /api/conversations/{id}/message_stream
GET /api/conversations/{id}/latest_process
GET /api/conversations/{id}/simulate?scale=1.5
POST /api/conversations/{id}/edit (edit|delete|insert_after)
POST /api/conversations/{id}/reorder
POST /api/conversations/{id}/meta (structured fields)
GET /api/conversations/{id}/diff
GET /api/conversations/{id}/next_question (Discovery Mode)
Workforce Intelligence Matrix endpoints (classify, scenario, rebalance) live under /api/workforce/*.
Configuration
USE_DATABASE – toggles database-backed mode vs. in-memory AI processing
WEBSOCKET_ENABLED – enable/disable WebSocket support (disabled by default)
DATABASE_URL – connection string, defaults to SQLite ./mindforge.db
APP_NAME, SECRET_KEY – exported in run.sh for local development
LLM integration: configure OPENAI_API_KEY, OPENAI_BASE_URL, etc., in services/llm_client.py to connect a model provider
Testing
Run the test suite with:
pytest
Tests cover emotion scoring, parsing, memory utilities, process intelligence, and workforce matrix logic.
Extending
The backend falls back to an advanced AI-powered in-memory mode when USE_DATABASE is false, leveraging AdvancedCaseyAI for insights and recommendations. Additional LLM or vector-store providers can be wired into services/llm_client.py and the extractor modules for richer functionality.
