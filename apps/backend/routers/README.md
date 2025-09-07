# Creative Projects Router

This module implements a FastAPI router for handling creative project uploads, analysis, and interaction with Casey AI.

## Features

### File Upload & Analysis
- Upload creative project files (images, videos, documents)
- Automatic file validation and size checking
- Image analysis for dimensions and color palette extraction
- Project tagging based on type and content

### Casey AI Integration
- Interactive questioning system based on project type
- Context-aware follow-up questions
- Chat functionality for project feedback
- Intelligent response generation

### Project Management
- List and retrieve creative projects
- Filter by project type
- Track project questions and answers
- Store analysis insights and suggestions

## API Endpoints

### POST `/api/creative/upload`
Upload a creative project file and get initial questions from Casey.

**Parameters:**
- `file`: UploadFile - The project file to upload
- `project_name`: str - Name for the project
- `project_type`: ProjectType - Type of creative project
- `description`: str (optional) - Project description

**Response:** ProjectUploadResponse with project details, initial questions, and next steps

### GET `/api/creative/projects`
Get all creative projects with optional filtering.

**Parameters:**
- `skip`: int - Number of projects to skip (pagination)
- `limit`: int - Maximum number of projects to return
- `project_type`: ProjectType (optional) - Filter by project type

### GET `/api/creative/projects/{project_id}`
Get details for a specific project.

### GET `/api/creative/projects/{project_id}/casey-question`
Get the next question Casey should ask about the project.

### POST `/api/creative/projects/{project_id}/answer`
Answer a question about the project.

**Parameters:**
- `question_id`: int - ID of the question being answered
- `answer_data`: ProjectQuestionUpdate - The answer content

### POST `/api/creative/projects/{project_id}/analyze`
Run comprehensive analysis on the project.

### GET `/api/creative/projects/{project_id}/chat`
Chat with Casey about the project.

**Parameters:**
- `message`: str - User's message to Casey

## Project Types

The system supports the following project types:
- `website_mockup` - Website and web application designs
- `social_media` - Social media graphics and content
- `print_graphic` - Print design materials
- `logo_design` - Logo and brand identity designs
- `ui_design` - User interface designs
- `branding` - Brand identity and corporate design

## File Types Supported

### Images
- JPG, JPEG, PNG, GIF, BMP, WebP, SVG

### Videos
- MP4, MOV, AVI, MKV, WebM

### Documents
- PDF, PSD, AI, Sketch, Fig, XD

## Configuration

- **Upload Directory:** `uploads/creative/`
- **Max File Size:** 50MB
- **File Validation:** Extension-based with size limits

## Dependencies

The router requires the following Python packages:
- FastAPI
- SQLAlchemy
- PIL (Pillow) for image analysis
- python-multipart for file uploads

## Database Models

### CreativeProject
Stores project metadata, file information, and analysis results.

### ProjectQuestion
Stores Casey's questions and user answers for each project.

### ProjectFile
Stores additional files associated with a project.

### ProjectInsight
Stores analysis insights and suggestions for projects.

## Services

### CaseyProjectQuestioner
Generates contextual questions based on project type and manages the questioning workflow.

### CreativeProjectAnalyzer
Analyzes uploaded files to extract metadata, colors, dimensions, and generate insights.

## Error Handling

The router includes comprehensive error handling for:
- Invalid file types
- File size limits
- Missing files or projects
- Analysis failures (non-blocking)
- Database errors

## Security Considerations

- File type validation prevents dangerous uploads
- File size limits prevent DoS attacks
- Unique filename generation prevents conflicts
- Input sanitization for all user data