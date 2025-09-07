#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for Mac terminal
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="ℹ️"
GEAR="⚙️"
GLOBE="🌐"

echo -e "${PURPLE}${ROCKET} Starting MindForge Casey MVP on macOS${NC}"
echo "=================================================="

# Function to print colored status messages
print_status() {
    local color=$1
    local emoji=$2
    local message=$3
    echo -e "${color}${emoji} ${message}${NC}"
}

# Function to send macOS notification
send_notification() {
    local title=$1
    local message=$2
    local sound=${3:-"default"}

    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"$message\" with title \"$title\" sound name \"$sound\""
    fi
}

# Function to open URL in default browser
open_browser() {
    local url=$1
    if command -v open >/dev/null 2>&1; then
        open "$url"
    fi
}

# Check if we're actually on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_status "$RED" "$ERROR" "This script is designed for macOS. Use start.sh for other Unix systems."
    exit 1
fi

# Check if Homebrew is installed (common on Mac)
if command -v brew >/dev/null 2>&1; then
    print_status "$CYAN" "$INFO" "Homebrew detected"

    # Check if Python3 is available via Homebrew
    if brew list python@3.11 >/dev/null 2>&1 || brew list python@3.10 >/dev/null 2>&1 || brew list python@3.9 >/dev/null 2>&1; then
        print_status "$GREEN" "$CHECK" "Homebrew Python found"
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_status "$BLUE" "$INFO" "Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [[ ! -f "backend/.venv/bin/activate" ]]; then
    print_status "$RED" "$ERROR" "Virtual environment not found!"
    echo
    echo "Please run one of the following to set up your environment:"
    echo "  python3 setup_debug.py  (recommended)"
    echo "  OR"
    echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    echo
    send_notification "MindForge Casey" "Setup required - virtual environment not found" "Basso"
    exit 1
fi

# Activate virtual environment
print_status "$YELLOW" "$GEAR" "Activating virtual environment..."
source backend/.venv/bin/activate

if [[ -z "$VIRTUAL_ENV" ]]; then
    print_status "$RED" "$ERROR" "Failed to activate virtual environment"
    exit 1
fi

print_status "$GREEN" "$CHECK" "Virtual environment activated: $(basename $VIRTUAL_ENV)"

# Set environment variables with Mac-friendly defaults
export USE_DATABASE="${USE_DATABASE:-false}"
export APP_NAME="${APP_NAME:-MindForge Casey}"
export SECRET_KEY="${SECRET_KEY:-dev-secret-$(date +%s)}"

# Set macOS-specific environment variables
export PYTHONUNBUFFERED=1  # Better for real-time output
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  # Fix for some macOS Python issues

print_status "$CYAN" "$INFO" "Configuration:"
echo "  📊 Database Mode: $(if [ "$USE_DATABASE" = "true" ]; then echo "Enabled"; else echo "Disabled (Simple Mode)"; fi)"
echo "  🔑 API Key: $(if [ -n "$OPENAI_API_KEY" ]; then echo "Set"; else echo "Not set (LLM features disabled)"; fi)"
echo "  🐍 Python: $(python --version 2>&1)"

# Change to backend directory
cd backend

# Check if required packages are installed
print_status "$YELLOW" "$GEAR" "Checking dependencies..."

if ! python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    print_status "$RED" "$ERROR" "Required packages not installed!"
    echo
    echo "Installing packages..."
    pip install -r requirements.txt
fi

print_status "$GREEN" "$CHECK" "Dependencies verified"

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_status "$YELLOW" "$WARNING" "Port 8000 is already in use"

    # Try to find an alternative port
    for port in 8001 8002 8003 8004 8005; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_status "$CYAN" "$INFO" "Using alternative port: $port"
            PORT=$port
            break
        fi
    done

    if [[ -z "$PORT" ]]; then
        print_status "$RED" "$ERROR" "No available ports found in range 8000-8005"
        exit 1
    fi
else
    PORT=8000
    print_status "$GREEN" "$CHECK" "Port 8000 is available"
fi

# Create a function to handle cleanup on script exit
cleanup() {
    print_status "$YELLOW" "$WARNING" "Shutting down MindForge Casey..."
    send_notification "MindForge Casey" "Server stopped" "Purr"

    # Kill any background processes we might have started
    if [[ -n "$SERVER_PID" ]]; then
        kill $SERVER_PID 2>/dev/null || true
    fi

    echo
    print_status "$BLUE" "$INFO" "Thanks for using MindForge Casey!"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Start the application
echo
print_status "$GREEN" "$ROCKET" "Starting MindForge Casey server..."
echo "  🌐 URL: http://localhost:$PORT"
echo "  📋 API Status: http://localhost:$PORT/api/status"
echo "  🔧 Health Check: http://localhost:$PORT/healthz"
echo
print_status "$CYAN" "$INFO" "Press Ctrl+C to stop the server"
echo

# Send startup notification
send_notification "MindForge Casey" "Server starting on port $PORT" "Glass"

# Start server in background to get PID
uvicorn app:app --reload --port $PORT --host 0.0.0.0 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null 2>&1; then
    print_status "$GREEN" "$CHECK" "Server started successfully (PID: $SERVER_PID)"
    send_notification "MindForge Casey" "Server running on http://localhost:$PORT" "Hero"

    # Wait 3 seconds then open browser automatically
    sleep 3
    print_status "$BLUE" "$GLOBE" "Opening browser..."
    open_browser "http://localhost:$PORT"

    # Show some helpful tips
    echo
    echo "💡 Helpful tips:"
    echo "  • The web interface should open automatically"
    echo "  • Try describing a work process to get started"
    echo "  • Upload files (PDF, CSV, TXT) to analyze processes"
    echo "  • Use the scale slider to simulate different loads"
    echo
    echo "🔧 Advanced usage:"
    echo "  • Enable database mode: export USE_DATABASE=true"
    echo "  • Add LLM features: export OPENAI_API_KEY=your_key"
    echo "  • Run frontend: cd ../frontend && npm run dev"
    echo

    # Wait for the server process
    wait $SERVER_PID
else
    print_status "$RED" "$ERROR" "Failed to start server"
    send_notification "MindForge Casey" "Failed to start server" "Basso"
    exit 1
fi
