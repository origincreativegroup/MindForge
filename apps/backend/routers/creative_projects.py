from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from pathlib import Path
import mimetypes
import json
from datetime import datetime

from ..db import get_db
from ..services.models import CreativeProject, ProjectQuestion, ProjectFile, ProjectInsight
from ..schemas import (
    CreativeProjectCreate, CreativeProject as ProjectSchema,
    ProjectUploadResponse, CaseyQuestionResponse, ProjectQuestionUpdate,
    ProjectAnalysisResponse, ProjectType
)
from ..services.project_questioner import CaseyProjectQuestioner
from ..services.creative_analyzer import CreativeProjectAnalyzer

router = APIRouter(prefix="/api/creative", tags=["creative-projects"])

# Initialize services
questioner = CaseyProjectQuestioner()
analyzer = CreativeProjectAnalyzer()

# File upload settings
UPLOAD_DIRECTORY = "uploads/creative"
ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
    'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
    'document': ['.pdf', '.psd', '.ai', '.sketch', '.fig', '.xd']
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=ProjectUploadResponse)
async def upload_creative_project(
    file: UploadFile = File(...),
    project_name: str = Form(...),
    project_type: ProjectType = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a creative project file and get initial questions from Casey"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_ext = Path(file.filename).suffix.lower()
    if not _is_allowed_file(file_ext):
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported"
        )

    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Create upload directory
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Generate unique filename
    file_path = _generate_file_path(file.filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create project record
    project_data = CreativeProjectCreate(
        name=project_name,
        project_type=project_type,
        description=description,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type
    )

    db_project = CreativeProject(**project_data.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Analyze the uploaded file
    try:
        analysis_result = await analyzer.analyze_project(db_project, file_path)
        
        # Update project with analysis results
        if analysis_result.get('dimensions'):
            db_project.dimensions = analysis_result['dimensions']
        if analysis_result.get('color_palette'):
            db_project.color_palette = analysis_result['color_palette']
        if analysis_result.get('extracted_text'):
            db_project.extracted_text = analysis_result['extracted_text']
        if analysis_result.get('tags'):
            db_project.tags = analysis_result['tags']
            
        db.commit()
        db.refresh(db_project)
        
    except Exception as e:
        print(f"Analysis failed: {e}")  # Log error but don't fail upload

    # Generate initial questions
    initial_questions = questioner.generate_initial_questions(db_project)

    # Save questions to database
    db_questions = []
    for q in initial_questions:
        db_question = ProjectQuestion(**q.dict())
        db.add(db_question)
        db_questions.append(db_question)

    db.commit()

    # Refresh project with questions
    db.refresh(db_project)

    # Generate next steps
    next_steps = _generate_next_steps(db_project)

    return ProjectUploadResponse(
        project=db_project,
        questions=db_questions,
        next_steps=next_steps
    )


@router.get("/projects", response_model=List[ProjectSchema])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    project_type: Optional[ProjectType] = None,
    db: Session = Depends(get_db)
):
    """Get all creative projects"""
    query = db.query(CreativeProject)

    if project_type:
        query = query.filter(CreativeProject.project_type == project_type)

    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects/{project_id}/casey-question", response_model=Optional[CaseyQuestionResponse])
def get_casey_question(project_id: int, db: Session = Depends(get_db)):
    """Get the next question Casey should ask about this project"""
    project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    casey_question = questioner.get_next_question_for_casey(project)
    return casey_question


@router.post("/projects/{project_id}/answer")
def answer_question(
    project_id: int,
    question_id: int,
    answer_data: ProjectQuestionUpdate,
    db: Session = Depends(get_db)
):
    """Answer a question about the project"""
    
    # Get project and question
    project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    question = db.query(ProjectQuestion).filter(
        ProjectQuestion.id == question_id,
        ProjectQuestion.project_id == project_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update question with answer
    question.answer = answer_data.answer
    question.is_answered = True
    question.answered_at = datetime.utcnow()

    db.commit()

    # Generate follow-up questions
    follow_up_questions = questioner.generate_follow_up_questions(project, question)

    # Save follow-up questions
    for q in follow_up_questions:
        db_question = ProjectQuestion(**q.dict())
        db.add(db_question)

    db.commit()

    return {
        "message": "Answer recorded",
        "follow_up_questions": len(follow_up_questions),
        "next_question": questioner.get_next_question_for_casey(project)
    }


@router.post("/projects/{project_id}/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project(project_id: int, db: Session = Depends(get_db)):
    """Run comprehensive analysis on the project"""
    project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Run analysis
    analysis_result = await analyzer.comprehensive_analysis(project)

    # Save insights to database
    insights = []
    for insight_data in analysis_result.get('insights', []):
        # Only extract expected fields and ensure correct types
        insight = ProjectInsight(
            project_id=project_id,
            title=insight_data.get('title'),
            description=insight_data.get('description'),
            confidence=int(insight_data.get('confidence', 0)) if insight_data.get('confidence') is not None else None
        )
        db.add(insight)
        insights.append(insight)

    db.commit()

    return ProjectAnalysisResponse(
        project_id=project_id,
        analysis_complete=True,
        insights=insights,
        suggestions=analysis_result.get('suggestions', []),
        color_palette=project.color_palette,
        dimensions=project.dimensions
    )


@router.get("/projects/{project_id}/chat")
def chat_about_project(
    project_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    """Chat with Casey about the project"""
    project = db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Generate Casey's response based on project context
    casey_response = _generate_casey_chat_response(project, message)

    return {
        "casey_response": casey_response,
        "suggested_actions": _get_suggested_actions(project, message)
    }


# Helper functions

def _is_allowed_file(file_ext: str) -> bool:
    """Check if file extension is allowed"""
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if file_ext in extensions:
            return True
    return False


def _generate_file_path(filename: str) -> str:
    """Generate unique file path"""
    import uuid
    file_ext = Path(filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    return os.path.join(UPLOAD_DIRECTORY, unique_filename)


def _generate_next_steps(project: CreativeProject) -> List[str]:
    """Generate next steps based on project type and state"""
    base_steps = [
        "Answer Casey's questions to get personalized feedback",
        "Review the automated analysis results",
        "Get specific recommendations for improvement"
    ]

    if project.project_type == ProjectType.website_mockup:
        base_steps.append("Check responsive design considerations")
        base_steps.append("Validate accessibility compliance")
    elif project.project_type == ProjectType.social_media:
        base_steps.append("Verify platform-specific requirements")
        base_steps.append("Check brand consistency")
    elif project.project_type == ProjectType.print_graphic:
        base_steps.append("Review print specifications")
        base_steps.append("Check color profile compatibility")

    return base_steps


def _generate_casey_chat_response(project: CreativeProject, user_message: str) -> str:
    """Generate Casey's chat response"""
    # This would integrate with your existing LLM service
    # For now, return a contextual response

    context_responses = {
        "colors": f"Looking at your {project.project_type.value}, I notice you're using {len(project.color_palette or [])} colors. Let me help you optimize the color palette.",
        "feedback": f"I'd be happy to give you feedback on your {project.project_type.value}! What specific aspect would you like me to focus on?",
        "improve": f"There are several ways we could improve this {project.project_type.value}. Based on my analysis, here are my top suggestions...",
        "help": f"I'm here to help with your {project.project_type.value} project! What would you like to know?"
    }

    # Simple keyword matching for demo
    message_lower = user_message.lower()
    for keyword, response in context_responses.items():
        if keyword in message_lower:
            return response

    return f"That's an interesting question about your {project.project_type.value} project. Let me analyze this further and get back to you with specific insights."


def _get_suggested_actions(project: CreativeProject, user_message: str) -> List[str]:
    """Get suggested actions based on the chat message"""
    return [
        "Run comprehensive analysis",
        "Answer remaining questions",
        "Export project summary",
        "Share with team"
    ]