#!/bin/bash

# MindForge Casey Creative Projects - Comprehensive Setup Script

# This script sets up the complete creative project management system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.11"
NODE_VERSION="16"
PROJECT_DIR="$(pwd)"
BACKEND_DIR="$PROJECT_DIR/apps/backend"
FRONTEND_DIR="$PROJECT_DIR/apps/frontend"
UPLOAD_DIR="$BACKEND_DIR/uploads"
DATABASE_URL="sqlite:///./mindforge_creative.db"

echo -e "${BLUE}🎨 MindForge Casey Creative Projects Setup${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Create project structure
setup_project_structure() {
    print_info "Setting up creative project structure…"
    
    # Create directories for creative projects
    mkdir -p "$BACKEND_DIR"/{models,schemas,routers,services}/creative
    mkdir -p "$UPLOAD_DIR"/{creative,temp}
    mkdir -p logs
    
    # Create necessary files if they don't exist
    touch "$BACKEND_DIR"/models/creative/__init__.py
    touch "$BACKEND_DIR"/schemas/creative/__init__.py  
    touch "$BACKEND_DIR"/routers/creative/__init__.py
    touch "$BACKEND_DIR"/services/creative/__init__.py
    
    print_status "Creative project structure created"
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements…"
    
    # Check Python
    if command_exists python3; then
        PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" = "$PYTHON_VERSION" ]]; then
            print_status "Python $PYTHON_VER ✓"
        else
            print_error "Python $PYTHON_VERSION or higher required. Found: $PYTHON_VER"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python $PYTHON_VERSION or higher."
        exit 1
    fi
    
    # Check Node.js (optional for frontend)
    if command_exists node; then
        NODE_VER=$(node --version | cut -d'v' -f2)
        print_status "Node.js $NODE_VER ✓"
    else
        print_warning "Node.js not found. Frontend features will be limited."
    fi
    
    # Check poetry
    if command_exists poetry; then
        print_status "Poetry ✓"
    else
        print_warning "Poetry not found. Installing poetry..."
        pip3 install --user poetry
    fi
    
    # Check pnpm
    if command_exists pnpm; then
        print_status "pnpm ✓"
    else
        print_warning "pnpm not found. Installing pnpm..."
        npm install -g pnpm
    fi
    
    # Check git
    if command_exists git; then
        print_status "Git ✓"
    else
        print_warning "Git not found. Version control features will be limited."
    fi
}

# Setup Python environment
setup_python_environment() {
    print_info "Setting up Python environment…"
    
    # Check if already installed
    if poetry show >/dev/null 2>&1; then
        print_status "Python dependencies already installed"
    else
        print_info "Installing Python dependencies..."
        poetry install --no-interaction
        print_status "Python dependencies installed"
    fi
}

# Install system dependencies
install_system_dependencies() {
    print_info "Installing system dependencies…"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_info "Detected Debian/Ubuntu system"
            if sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx 2>/dev/null; then
                print_status "System dependencies installed (apt)"
            else
                print_warning "Could not install system dependencies. Please install tesseract-ocr manually."
            fi
        elif command_exists yum; then
            # RedHat/CentOS
            print_info "Detected RedHat/CentOS system"
            if sudo yum install -y tesseract tesseract-langpack-eng mesa-libGL 2>/dev/null; then
                print_status "System dependencies installed (yum)"
            else
                print_warning "Could not install system dependencies. Please install tesseract manually."
            fi
        else
            print_warning "Unknown Linux distribution. Please install tesseract-ocr manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Detected macOS system"
        if command_exists brew; then
            if brew install tesseract 2>/dev/null; then
                print_status "System dependencies installed (brew)"
            else
                print_warning "Could not install tesseract via brew. Please install manually."
            fi
        else
            print_warning "Homebrew not found. Please install tesseract manually."
        fi
    else
        print_warning "Unknown operating system. Please install tesseract-ocr manually."
    fi
}

# Setup database
setup_database() {
    print_info "Setting up creative projects database…"
    
    cd "$BACKEND_DIR"
    
    # Create database initialization script
    cat > init_creative_database.py << 'EOF'
#!/usr/bin/env python3
"""
Creative Projects Database initialization script for MindForge
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindforge_creative.db")

def create_tables():
    """Create all necessary tables for creative projects"""
    
    engine = create_engine(DATABASE_URL)
    
    # Creative projects tables
    with engine.connect() as conn:
        # Main projects table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS creative_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                project_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'uploaded',
                description TEXT,
                original_filename VARCHAR(500),
                file_path VARCHAR(1000),
                file_size INTEGER,
                mime_type VARCHAR(100),
                metadata JSON DEFAULT '{}',
                extracted_text TEXT,
                color_palette JSON,
                dimensions JSON,
                tags JSON DEFAULT '[]',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Project questions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                question_type VARCHAR(50),
                options JSON,
                answer TEXT,
                is_answered INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                answered_at DATETIME,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id)
            )
        """))
        
        # Project insights table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                insight_type VARCHAR(100),
                title VARCHAR(255),
                description TEXT,
                score REAL,
                data JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id)
            )
        """))
        
        # Team members table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(100),
                avatar_url VARCHAR(500),
                is_active INTEGER DEFAULT 1,
                permissions JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Project shares table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                shared_by INTEGER NOT NULL,
                shared_with INTEGER,
                share_token VARCHAR(255) UNIQUE NOT NULL,
                permissions JSON DEFAULT '{"view": true, "comment": false, "edit": false}',
                expires_at DATETIME,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (shared_by) REFERENCES team_members (id),
                FOREIGN KEY (shared_with) REFERENCES team_members (id)
            )
        """))
        
        # Project comments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                comment_type VARCHAR(50) DEFAULT 'general',
                metadata JSON DEFAULT '{}',
                is_resolved INTEGER DEFAULT 0,
                resolved_by INTEGER,
                resolved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (author_id) REFERENCES team_members (id),
                FOREIGN KEY (resolved_by) REFERENCES team_members (id)
            )
        """))
        
        # Project activity table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                activity_type VARCHAR(100) NOT NULL,
                description TEXT,
                metadata JSON DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES creative_projects (id),
                FOREIGN KEY (user_id) REFERENCES team_members (id)
            )
        """))
        
        conn.commit()
    
    print("✅ Creative projects database tables created successfully!")

def create_sample_data():
    """Create sample data for testing"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Create a sample team member
        conn.execute(text("""
            INSERT OR IGNORE INTO team_members (id, name, email, role)
            VALUES (1, 'Casey AI', 'casey@mindforge.ai', 'ai_assistant')
        """))
        
        # Create a sample user
        conn.execute(text("""
            INSERT OR IGNORE INTO team_members (id, name, email, role) 
            VALUES (2, 'Demo User', 'demo@example.com', 'designer')
        """))
        
        conn.commit()
    
    print("✅ Sample data created!")

if __name__ == "__main__":
    print("🎨 Initializing MindForge Creative Projects Database…")
    create_tables()
    create_sample_data()
    print("🎉 Creative projects database setup complete!")
EOF
    
    # Run database initialization
    poetry run python init_creative_database.py
    print_status "Creative projects database initialized"
}

# Create environment configuration
create_environment_config() {
    print_info "Creating environment configuration…"
    
    cd "$BACKEND_DIR"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# MindForge Casey Creative Projects Configuration

# Database
DATABASE_URL=sqlite:///./mindforge_creative.db

# Application Settings
USE_DATABASE=true
DEBUG=true
HOST=0.0.0.0
PORT=8000

# File Upload Settings
UPLOAD_DIRECTORY=uploads/creative
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.mp4,.mov,.avi,.mkv,.webm,.pdf,.psd,.ai,.sketch,.fig,.xd

# Analysis Settings
ENABLE_OCR=true
ENABLE_VIDEO_ANALYSIS=true
ENABLE_COLOR_ANALYSIS=true

# AI Integration (Optional - add your API key)
# OPENAI_API_KEY=your_openai_api_key_here
# CASEY_LLM_MODEL=gpt-4

# Security (Generate new keys for production)
SECRET_KEY=your-secret-key-here-please-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "http://127.0.0.1:8000"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mindforge_creative.log
EOF
        print_status "Environment configuration created"
        print_warning "Remember to update the SECRET_KEY and add your OpenAI API key for full AI features"
    else
        print_status "Environment configuration already exists"
    fi
}

# Setup frontend dependencies
setup_frontend_environment() {
    print_info "Setting up frontend environment…"
    
    cd "$PROJECT_DIR"
    
    # Check if already installed
    if [ -d "node_modules" ]; then
        print_status "Frontend dependencies already installed"
    else
        print_info "Installing frontend dependencies..."
        pnpm install
        print_status "Frontend dependencies installed"
    fi
}

# Create startup script
create_startup_script() {
    print_info "Creating startup scripts…"
    
    cd "$PROJECT_DIR"
    
    # Create main startup script
    cat > start_mindforge.sh << 'EOF'
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
EOF
    
    chmod +x start_mindforge.sh
    
    # Create development script
    cat > dev_start.sh << 'EOF'
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
EOF
    
    chmod +x dev_start.sh
    
    print_status "Startup scripts created"
}

# Create testing script
create_testing_script() {
    print_info "Creating testing utilities…"
    
    cd "$PROJECT_DIR"
    
    # Create test script
    cat > test_creative_system.py << 'EOF'
#!/usr/bin/env python3
"""
Creative Projects System test script for MindForge
"""

import requests
import json
import os
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check: PASS")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ API status: PASS")
            print(f"   Version: {data.get('api_version', 'N/A')}")
            return True
        else:
            print(f"❌ API status: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API status: ERROR - {e}")
        return False

def test_creative_projects_endpoint():
    """Test creative projects endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/creative/projects")
        if response.status_code == 200:
            print("✅ Creative projects endpoint: PASS")
            return True
        else:
            print(f"❌ Creative projects endpoint: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Creative projects endpoint: ERROR - {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 Running MindForge Creative Projects System Tests\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("API Status", test_api_status),
        ("Creative Projects Endpoint", test_creative_projects_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Creative projects system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_creative_system.py [test_name]")
        print("Available tests: health, status, projects, all")
        sys.exit(0)
    
    test_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if test_name == "health":
        test_health_check()
    elif test_name == "status":
        test_api_status()
    elif test_name == "projects":
        test_creative_projects_endpoint()
    else:
        run_all_tests()
EOF
    
    chmod +x test_creative_system.py
    print_status "Testing utilities created"
}

# Create documentation
create_documentation() {
    print_info "Creating creative projects documentation…"
    
    # Create README for creative projects
    cat > CREATIVE_PROJECTS_README.md << 'EOF'
# 🎨 MindForge Casey Creative Projects

An AI-powered creative project analysis and collaboration platform that helps teams create better designs through intelligent feedback, automated analysis, and seamless collaboration.

## 🚀 Features

### Core Functionality
- **Smart Project Analysis**: Upload creative projects and get AI-powered insights
- **Casey AI Assistant**: Chat with Casey about your projects for personalized feedback
- **Multi-format Support**: Images, videos, PDFs, and design files
- **Real-time Collaboration**: Team comments, sharing, and activity tracking

### Advanced Analysis
- **Design Principles Evaluation**: Visual hierarchy, color harmony, typography
- **Accessibility Compliance**: WCAG guidelines and contrast checking
- **Platform Optimization**: Social media, web, and print-specific recommendations
- **Trend Analysis**: Current design trends and industry best practices

### Team Features
- **Project Sharing**: Secure sharing with customizable permissions
- **Visual Comments**: Pin comments directly to design elements
- **Activity Timeline**: Track all project changes and discussions
- **Analytics Dashboard**: Team productivity and project insights

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend)
- Git (optional)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/origincreativegroup/MindForge.git
   cd MindForge
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the application**:
   ```bash
   ./start_mindforge.sh
   ```

4. **Open your browser**:
   - Main Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/healthz

### Development Mode

To run both frontend and backend in development mode:
```bash
./dev_start.sh
```

This starts:
- Frontend (React + Vite): http://localhost:5173
- Backend (FastAPI): http://localhost:8000

## 🎯 Usage

### Basic Workflow

1. **Upload a Project**: Upload your creative work (image, video, PDF, design file)
2. **Chat with Casey**: Ask questions and get AI-powered feedback
3. **Team Collaboration**: Share with team members for comments and review
4. **Analysis & Reports**: Generate comprehensive reports and insights
5. **Iterate & Improve**: Use recommendations to enhance your designs

### API Usage

The system provides a comprehensive REST API. Visit `/docs` for interactive documentation.

**Example: Upload a project**
```bash
curl -X POST "http://localhost:8000/api/creative/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-design.jpg" \
     -F "project_name=My Design" \
     -F "project_type=website_mockup"
```

## 🧪 Testing

Run the system tests:
```bash
# Start the server first
./start_mindforge.sh

# In another terminal, run tests
python test_creative_system.py
```

## 📁 Project Structure

```
MindForge/
├── apps/
│   ├── backend/          # FastAPI backend
│   │   ├── models/       # Database models
│   │   ├── routers/      # API routes
│   │   ├── services/     # Business logic
│   │   └── uploads/      # File uploads
│   └── frontend/         # React frontend
├── packages/             # Shared packages
├── setup.sh             # Setup script
├── start_mindforge.sh   # Production startup
├── dev_start.sh         # Development startup
└── test_creative_system.py  # System tests
```

## 🔧 Configuration

Environment variables can be set in `apps/backend/.env`:

```env
# Database
DATABASE_URL=sqlite:///./mindforge_creative.db

# AI Integration
OPENAI_API_KEY=your_api_key_here

# File Uploads
UPLOAD_DIRECTORY=uploads/creative
MAX_FILE_SIZE=52428800

# Analysis Features
ENABLE_OCR=true
ENABLE_VIDEO_ANALYSIS=true
ENABLE_COLOR_ANALYSIS=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## 📄 License

See [LICENSE](LICENSE) file for details.

---

Built with FastAPI, React, SQLAlchemy, and powered by AI ✨
EOF
    
    print_status "Creative projects documentation created"
}

# Main setup function
main() {
    print_info "Starting MindForge Creative Projects setup…"
    
    check_requirements
    setup_project_structure
    setup_python_environment
    setup_frontend_environment
    install_system_dependencies
    setup_database
    create_environment_config
    create_startup_script
    create_testing_script
    create_documentation
    
    echo ""
    print_status "🎉 MindForge Creative Projects setup complete!"
    echo ""
    print_info "Next steps:"
    echo "  1. ./start_mindforge.sh     - Start the application"
    echo "  2. ./dev_start.sh          - Start in development mode"
    echo "  3. python test_creative_system.py - Run system tests"
    echo ""
    print_info "Documentation:"
    echo "  • CREATIVE_PROJECTS_README.md - Creative projects guide"
    echo "  • http://localhost:8000/docs  - API documentation"
    echo ""
    print_warning "Don't forget to:"
    echo "  • Set your OPENAI_API_KEY in apps/backend/.env for AI features"
    echo "  • Change the SECRET_KEY in production"
}

# Run main function
main "$@"