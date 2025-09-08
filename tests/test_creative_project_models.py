"""Test the new creative project models."""

import pytest
from datetime import datetime
from apps.backend.services.models import (
    Base,
    ProjectType,
    CreativeProjectStatus,
    CreativeProject,
    ProjectQuestion,
    ProjectFile,
    ProjectInsight
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_creative_project_creation(db_session):
    """Test creating a new creative project."""
    project = CreativeProject(
        name="Test Website Mockup",
        project_type=ProjectType.WEBSITE_MOCKUP,
        status=CreativeProjectStatus.UPLOADED,
        description="A test website mockup project",
        original_filename="mockup.psd",
        file_path="/uploads/mockup.psd",
        file_size=1024000,
        mime_type="image/psd",
        project_metadata={"client": "Test Client", "version": "1.0"},
        extracted_text="Header Footer Navigation",
        color_palette=["#FF0000", "#00FF00", "#0000FF"],
        dimensions={"width": 1920, "height": 1080},
        tags=["website", "mockup", "responsive"]
    )
    
    db_session.add(project)
    db_session.commit()
    
    # Verify the project was created
    assert project.id is not None
    assert project.name == "Test Website Mockup"
    assert project.project_type == ProjectType.WEBSITE_MOCKUP
    assert project.status == CreativeProjectStatus.UPLOADED
    assert project.project_metadata["client"] == "Test Client"
    assert len(project.color_palette) == 3
    assert project.dimensions["width"] == 1920


def test_project_question_creation(db_session):
    """Test creating project questions."""
    # First create a project
    project = CreativeProject(
        name="Test Project",
        project_type=ProjectType.BRANDING,
        status=CreativeProjectStatus.NEEDS_INFO
    )
    db_session.add(project)
    db_session.commit()
    
    # Create a question for the project
    question = ProjectQuestion(
        project_id=project.id,
        question="What is the target audience for this branding project?",
        question_type="text",
        priority=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Verify the question was created and linked
    assert question.id is not None
    assert question.project_id == project.id
    assert question.question_type == "text"
    assert question.is_answered == 0
    assert question.priority == 1
    
    # Test relationship
    assert len(project.questions) == 1
    assert project.questions[0].question == "What is the target audience for this branding project?"


def test_project_file_creation(db_session):
    """Test creating project files."""
    # Create a project
    project = CreativeProject(
        name="Test Project",
        project_type=ProjectType.VIDEO
    )
    db_session.add(project)
    db_session.commit()
    
    # Create a file for the project
    project_file = ProjectFile(
        project_id=project.id,
        filename="video.mp4",
        file_path="/uploads/video.mp4",
        file_type="original",
        mime_type="video/mp4",
        file_size=50000000,
        processing_status="completed",
        processing_metadata={"duration": 120, "fps": 30}
    )
    db_session.add(project_file)
    db_session.commit()
    
    # Verify the file was created
    assert project_file.id is not None
    assert project_file.filename == "video.mp4"
    assert project_file.processing_metadata["duration"] == 120
    
    # Test relationship
    assert len(project.files) == 1
    assert project.files[0].mime_type == "video/mp4"


def test_project_insight_creation(db_session):
    """Test creating project insights."""
    # Create a project
    project = CreativeProject(
        name="Test Project",
        project_type=ProjectType.PRINT_GRAPHIC
    )
    db_session.add(project)
    db_session.commit()
    
    # Create an insight for the project
    insight = ProjectInsight(
        project_id=project.id,
        insight_type="design_analysis",
        title="Color Harmony Analysis",
        description="The color palette shows good contrast and accessibility",
        score=0.85,
        data={
            "contrast_ratio": 4.5,
            "accessibility_score": 0.9,
            "color_temperature": "warm"
        }
    )
    db_session.add(insight)
    db_session.commit()
    
    # Verify the insight was created
    assert insight.id is not None
    assert insight.insight_type == "design_analysis"
    assert insight.score == 0.85
    assert insight.data["contrast_ratio"] == 4.5
    
    # Test relationship
    assert len(project.insights) == 1
    assert project.insights[0].title == "Color Harmony Analysis"


def test_enum_values():
    """Test that enum values are correct."""
    # Test ProjectType enum
    assert ProjectType.WEBSITE_MOCKUP.value == "website_mockup"
    assert ProjectType.PRINT_GRAPHIC.value == "print_graphic"
    assert ProjectType.SOCIAL_MEDIA.value == "social_media"
    assert ProjectType.VIDEO.value == "video"
    assert ProjectType.BRANDING.value == "branding"
    assert ProjectType.PRESENTATION.value == "presentation"
    assert ProjectType.MOBILE_APP.value == "mobile_app"
    assert ProjectType.OTHER.value == "other"
    
    # Test CreativeProjectStatus enum
    assert CreativeProjectStatus.UPLOADED.value == "uploaded"
    assert CreativeProjectStatus.ANALYZING.value == "analyzing"
    assert CreativeProjectStatus.NEEDS_INFO.value == "needs_info"
    assert CreativeProjectStatus.IN_PROGRESS.value == "in_progress"
    assert CreativeProjectStatus.REVIEW.value == "review"
    assert CreativeProjectStatus.COMPLETED.value == "completed"
    assert CreativeProjectStatus.ARCHIVED.value == "archived"


def test_project_cascade_delete(db_session):
    """Test that deleting a project cascades to related objects."""
    # Create a project with related objects
    project = CreativeProject(
        name="Test Project for Deletion",
        project_type=ProjectType.OTHER
    )
    db_session.add(project)
    db_session.commit()
    
    # Add related objects
    question = ProjectQuestion(
        project_id=project.id,
        question="Test question",
        question_type="text"
    )
    project_file = ProjectFile(
        project_id=project.id,
        filename="test.jpg",
        file_path="/test.jpg",
        file_type="original"
    )
    insight = ProjectInsight(
        project_id=project.id,
        insight_type="test",
        title="Test Insight"
    )
    
    db_session.add_all([question, project_file, insight])
    db_session.commit()
    
    # Verify objects exist
    assert len(project.questions) == 1
    assert len(project.files) == 1
    assert len(project.insights) == 1
    
    # Delete the project
    db_session.delete(project)
    db_session.commit()
    
    # Verify all related objects were also deleted
    remaining_questions = db_session.query(ProjectQuestion).filter_by(project_id=project.id).all()
    remaining_files = db_session.query(ProjectFile).filter_by(project_id=project.id).all()
    remaining_insights = db_session.query(ProjectInsight).filter_by(project_id=project.id).all()
    
    assert len(remaining_questions) == 0
    assert len(remaining_files) == 0
    assert len(remaining_insights) == 0