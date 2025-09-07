#!/bin/bash

# Simple Mac launcher that can be double-clicked from Finder
# Save this file as "launch-casey.command" and make it executable

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Clear the terminal for a clean start
clear

# Welcome message
echo "🚀 MindForge Casey - Quick Launcher for Mac"
echo "==========================================="
echo
echo "This will start the MindForge Casey process mapping assistant."
echo

# Check if the main startup script exists
if [[ -f "start-mac.sh" ]]; then
    echo "✅ Found start-mac.sh - using Mac-optimized script"
    chmod +x start-mac.sh
    ./start-mac.sh
elif [[ -f "start.sh" ]]; then
    echo "✅ Found start.sh - using standard script"
    chmod +x start.sh
    ./start.sh
elif [[ -f "setup_debug.py" ]]; then
    echo "⚙️ No startup script found, but found setup script"
    echo "🔧 Running setup first..."
    python3 setup_debug.py
    echo
    echo "✅ Setup complete! Starting application..."
    if [[ -f "start-mac.sh" ]]; then
        chmod +x start-mac.sh
        ./start-mac.sh
    elif [[ -f "start.sh" ]]; then
        chmod +x start.sh
        ./start.sh
    else
        echo "❌ No startup script was created. Manual setup required."
        echo
        echo "Please run these commands:"
        echo "cd backend"
        echo "source .venv/bin/activate"
        echo "uvicorn app:app --reload --port 8000"
    fi
else
    echo "❌ Setup required!"
    echo
    echo "This appears to be a fresh installation."
    echo "Please run the setup first:"
    echo
    echo "python3 setup_debug.py"
    echo
    echo "Or manually set up the environment:"
    echo "cd backend"
    echo "python3 -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    echo "uvicorn app:app --reload --port 8000"
fi

echo
echo "Press any key to close this window..."
read -n 1
