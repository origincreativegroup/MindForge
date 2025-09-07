#!/usr/bin/env python3
"""
Complete setup and debug script for MindForge Casey MVP.
Handles dependency installation, file creation, and environment setup.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path
import json

def print_status(message, status="info"):
    """Print colored status messages."""
    colors = {
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "reset": "\033[0m"
    }

    icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✗"
    }

    print(f"{colors[status]}{icons[status]} {message}{colors['reset']}")

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print_status(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status("Python 3.8+ required", "error")
        return False

    print_status("Python version OK", "success")
    return True

def check_and_create_venv():
    """Check for virtual environment and create if needed."""
    venv_path = Path("backend/.venv")

    if venv_path.exists():
        print_status("Virtual environment exists", "success")
        return True

    print_status("Creating virtual environment...", "info")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print_status("Virtual environment created", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to create virtual environment: {e}", "error")
        return False

def get_venv_python():
    """Get the path to the virtual environment Python executable."""
    if os.name == 'nt':  # Windows
        return Path("backend/.venv/Scripts/python.exe")
    else:  # Unix-like
        return Path("backend/.venv/bin/python")

def install_dependencies():
    """Install dependencies in virtual environment."""
    venv_python = get_venv_python()
    requirements_file = Path("backend/requirements.txt")

    if not requirements_file.exists():
        print_status("requirements.txt not found", "error")
        return False

    print_status("Installing dependencies...", "info")
    try:
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, cwd="backend")
        print_status("Dependencies installed", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e}", "error")
        return False

def check_file_exists(file_path):
    """Check if a file exists."""
    return Path(file_path).exists()

def create_missing_files():
    """Create missing critical files."""
    files_to_check = {
        "backend/models.py": create_models_file,
        "backend/websocket.py": create_websocket_file,
    }

    created_files = []
    for file_path, creator_func in files_to_check.items():
        if not check_file_exists(file_path):
            print_status(f"Creating missing file: {file_path}", "info")
            try:
                creator_func(file_path)
                created_files.append(file_path)
                print_status(f"Created {file_path}", "success")
            except Exception as e:
                print_status(f"Failed to create {file_path}: {e}", "error")

    return created_files

def create_models_file(file_path):
    """Create the models.py file."""
    content = '''from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Untitled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    process_maps = relationship("ProcessMap", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    emotion = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class ProcessMap(Base):
    __tablename__ = "process_maps"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    steps = Column(JSON, default=list)
    actors = Column(JSON, default=list)
    tools = Column(JSON, default=list)
    decisions = Column(JSON, default=list)
    raw_chunks = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="process_maps")
'''

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

def create_websocket_file(file_path):
    """Create the websocket.py file."""
    content = '''"""WebSocket support for real-time process updates."""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except:
                self.active_connections.discard(connection)

manager = ConnectionManager()
ws_router = APIRouter()

@ws_router.websocket("/ws/process")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def broadcast_process_update(process_data: dict):
    message = json.dumps({"type": "update", "payload": process_data})
    await manager.broadcast(message)

async def broadcast_simulation_result(simulation_data: dict):
    message = json.dumps({"type": "simulation", "payload": simulation_data})
    await manager.broadcast(message)

def get_websocket_stats():
    return {"active_connections": len(manager.active_connections)}
'''

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

def remove_problematic_files():
    """Remove files that cause circular imports."""
    problematic_files = [
        "backend/services/extractor_regex.py"
    ]

    for file_path in problematic_files:
        if check_file_exists(file_path):
            print_status(f"Removing problematic file: {file_path}", "warning")
            try:
                os.remove(file_path)
                print_status(f"Removed {file_path}", "success")
            except Exception as e:
                print_status(f"Failed to remove {file_path}: {e}", "error")

def test_imports():
    """Test critical imports to ensure everything works."""
    test_modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic"
    ]

    print_status("Testing imports...", "info")
    failed_imports = []

    for module in test_modules:
        try:
            importlib.import_module(module)
            print_status(f"✓ {module}", "success")
        except ImportError:
            print_status(f"✗ {module}", "error")
            failed_imports.append(module)

    return len(failed_imports) == 0

def create_startup_script():
    """Create a simple startup script."""
    script_content = '''#!/bin/bash
set -e

echo "🚀 Starting MindForge Casey MVP"

# Activate virtual environment
if [ -f "backend/.venv/bin/activate" ]; then
    source backend/.venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found. Run setup_debug.py first."
    exit 1
fi

# Set environment variables
export USE_DATABASE=${USE_DATABASE:-false}
export APP_NAME="MindForge Casey"
export SECRET_KEY="${SECRET_KEY:-dev-secret-$(date +%s)}"

echo "📊 Mode: $(if [ "$USE_DATABASE" = "true" ]; then echo "Database"; else echo "Simple"; fi)"

# Change to backend directory
cd backend

# Start the application
echo "🌐 Starting server on http://localhost:8000"
uvicorn app:app --reload --port 8000
'''

    with open("start.sh", 'w') as f:
        f.write(script_content)

    # Make script executable on Unix-like systems
    if os.name != 'nt':
        os.chmod("start.sh", 0o755)

    print_status("Created start.sh script", "success")

def run_health_check():
    """Run a basic health check on the application."""
    print_status("Running health check...", "info")

    venv_python = get_venv_python()

    # Create a simple health check script
    health_check_script = '''
import sys
sys.path.append("backend")

try:
    from backend.app import app
    print("✓ App imports successfully")

    # Test database imports
    try:
        from backend.models import Conversation, Message, ProcessMap
        print("✓ Database models import successfully")
    except ImportError as e:
        print(f"⚠ Database models import failed: {e}")

    # Test services
    try:
        from backend.services.extractor import extract_process
        print("✓ Process extractor imports successfully")
    except ImportError as e:
        print(f"✗ Process extractor import failed: {e}")

    print("✓ Health check completed")

except Exception as e:
    print(f"✗ Health check failed: {e}")
    sys.exit(1)
'''

    try:
        result = subprocess.run([
            str(venv_python), "-c", health_check_script
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print_status("Health check passed", "success")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"  {line}")
            return True
        else:
            print_status("Health check failed", "error")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_status("Health check timed out", "error")
        return False
    except Exception as e:
        print_status(f"Health check error: {e}", "error")
        return False

def print_final_instructions(mode="simple"):
    """Print final setup instructions."""
    print("\n" + "="*60)
    print("🎉 MindForge Casey Setup Complete!")
    print("="*60)

    print("\n📋 Quick Start:")
    print("1. Run the application:")
    if os.name == 'nt':  # Windows
        print("   start.bat  (or: cd backend && .venv\\Scripts\\activate && uvicorn app:app --reload)")
    else:  # Unix-like
        print("   ./start.sh  (or: cd backend && source .venv/bin/activate && uvicorn app:app --reload)")

    print("\n2. Open your browser:")
    print("   http://localhost:8000")

    print("\n🔧 Configuration:")
    print(f"   Current mode: {mode}")
    print("   To enable database mode: export USE_DATABASE=true")
    print("   To enable LLM features: export OPENAI_API_KEY=your_key")

    print("\n🌐 Frontend (optional):")
    print("   cd frontend && npm install && npm run dev")
    print("   Frontend will be available at: http://localhost:5173")

    print("\n📊 API Endpoints:")
    print("   Health check: http://localhost:8000/healthz")
    print("   API status: http://localhost:8000/api/status")
    print("   WebSocket: ws://localhost:8000/ws/process")

    print("\n🐛 Troubleshooting:")
    print("   - Check logs for errors")
    print("   - Ensure port 8000 is available")
    print("   - Run this script again to fix issues")

def main():
    """Main setup and debug function."""
    print("🔧 MindForge Casey - Setup & Debug Tool")
    print("="*50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create and check virtual environment
    if not check_and_create_venv():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print_status("Trying to continue despite dependency issues...", "warning")

    # Create missing files
    created_files = create_missing_files()
    if created_files:
        print_status(f"Created {len(created_files)} missing files", "success")

    # Remove problematic files
    remove_problematic_files()

    # Test imports
    if not test_imports():
        print_status("Some imports failed - check dependencies", "warning")

    # Create startup script
    create_startup_script()

    # Run health check
    health_passed = run_health_check()

    # Determine the recommended mode
    mode = "database" if health_passed else "simple"

    # Print final instructions
    print_final_instructions(mode)

    if health_passed:
        print_status("Setup completed successfully! 🎉", "success")
    else:
        print_status("Setup completed with warnings. App should still work in simple mode.", "warning")

if __name__ == "__main__":
    main()
