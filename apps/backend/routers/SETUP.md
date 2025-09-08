# Creative Projects Router Setup

## Installation

1. **Install Python Dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy pillow python-multipart pydantic
   ```

2. **Or use Poetry (if available)**
   ```bash
   poetry install
   ```

3. **Set Environment Variables**
   ```bash
   export USE_DATABASE=true
   export DATABASE_URL=sqlite:///./mindforge.db  # or your preferred database
   ```

## Testing the Implementation

Run the test suite to verify everything is working:

```bash
python test_creative_router.py
```

## Running the Server

Start the development server:

```bash
cd apps/backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Upload a Creative Project

```bash
curl -X POST "http://localhost:8000/api/creative/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example-design.png" \
  -F "project_name=Website Mockup" \
  -F "project_type=website_mockup" \
  -F "description=Homepage design for new website"
```

### List Projects

```bash
curl "http://localhost:8000/api/creative/projects"
```

### Get Casey's Next Question

```bash
curl "http://localhost:8000/api/creative/projects/1/casey-question"
```

### Chat with Casey

```bash
curl "http://localhost:8000/api/creative/projects/1/chat?message=What do you think about the colors?"
```

## Troubleshooting

### Import Errors
- Ensure all dependencies are installed
- Check Python path includes the project root
- Verify virtual environment is activated

### Database Errors
- Ensure DATABASE_URL is set correctly
- Check database permissions
- Run database migrations if needed

### File Upload Issues
- Check upload directory exists and is writable
- Verify file size is under 50MB limit
- Ensure file type is supported

### PIL/Image Analysis Issues
- Install Pillow: `pip install pillow`
- For advanced image analysis, consider additional packages:
  - `pip install opencv-python` for computer vision
  - `pip install scikit-image` for scientific image processing

## File Structure

```
apps/backend/
├── routers/
│   ├── creative_projects.py     # Main router implementation
│   └── README.md               # This documentation
├── services/
│   ├── project_questioner.py   # Casey questioning service
│   ├── creative_analyzer.py    # File analysis service
│   └── models.py               # Database models
├── schemas.py                  # Pydantic schemas
├── app.py                     # Main FastAPI application
└── db.py                      # Database configuration
```

## Next Steps

1. Install dependencies and test the implementation
2. Set up a proper database (PostgreSQL recommended for production)
3. Add more sophisticated image analysis capabilities
4. Implement video and document analysis
5. Enhance Casey's AI responses with LLM integration
6. Add user authentication and project permissions
7. Implement real-time chat with WebSocket support