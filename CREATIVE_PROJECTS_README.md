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
