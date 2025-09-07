"""Database models for MindForge."""

from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Date,
    Boolean,
    Enum,
    Table,
    Index,
)
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
    inputs = Column(JSON, default=list)
    outputs = Column(JSON, default=list)
    raw_chunks = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="process_maps")


# ---------------------------------------------------------------------------
# Creative project inventory models
# ---------------------------------------------------------------------------


class ProjectStatus(PyEnum):
    """Lifecycle stages for a project."""

    pitch = "pitch"
    in_progress = "in_progress"
    shipped = "shipped"
    archived = "archived"


class AssetType(PyEnum):
    """Supported media types."""

    image = "image"
    video = "video"
    audio = "audio"
    pdf = "pdf"
    three_d = "3d"
    url = "url"


class AssetVisibility(PyEnum):
    """Access policy for assets."""

    public = "public"
    gated = "gated"
    private = "private"


# Association tables --------------------------------------------------------

project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
    Index("ix_project_skills_skill_id", "skill_id"),
)

project_tools = Table(
    "project_tools",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("tool_id", ForeignKey("tools.id"), primary_key=True),
)

project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
    Index("ix_project_tags_tag_id", "tag_id"),
)

collection_projects = Table(
    "collection_projects",
    Base.metadata,
    Column("collection_id", ForeignKey("collections.id"), primary_key=True),
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    contact_info = Column(String, nullable=True)

    projects = relationship("Project", back_populates="client")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    short_tagline = Column(String, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.pitch, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    disciplines = Column(JSON, default=list)
    hero_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)

    client = relationship("Client", back_populates="projects")
    hero_asset = relationship("Asset", foreign_keys=[hero_asset_id])
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="project", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="project", cascade="all, delete-orphan")
    case_study = relationship("CaseStudy", back_populates="project", uselist=False)
    skills = relationship("Skill", secondary=project_skills, back_populates="projects")
    tools = relationship("Tool", secondary=project_tools, back_populates="projects")
    tags = relationship("Tag", secondary=project_tags, back_populates="projects")
    collections = relationship("Collection", secondary=collection_projects, back_populates="projects")


Index(
    "ix_projects_title_trigram",
    Project.title,
    postgresql_using="gin",
    postgresql_ops={"title": "gin_trgm_ops"},
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    person = Column(String, nullable=True)

    project = relationship("Project", back_populates="roles")


class Deliverable(Base):
    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, nullable=True)

    project = relationship("Project", back_populates="deliverables")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    projects = relationship("Project", secondary=project_tools, back_populates="tools")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)

    projects = relationship("Project", secondary=project_tags, back_populates="tags")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    projects = relationship("Project", secondary=collection_projects, back_populates="collections")


class RightsConsent(Base):
    __tablename__ = "rights_consents"

    id = Column(Integer, primary_key=True)
    model_release_url = Column(String, nullable=True)
    property_release_url = Column(String, nullable=True)
    expiration = Column(Date, nullable=True)
    nda_required = Column(Boolean, default=False)

    assets = relationship("Asset", back_populates="rights")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    type = Column(Enum(AssetType), nullable=False)
    src = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_s = Column(Integer, nullable=True)
    color_profile = Column(String, nullable=True)
    checksum = Column(String, nullable=True)
    alt_text = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    captions = Column(Text, nullable=True)
    exif_meta = Column(JSON, nullable=True)
    rights_id = Column(Integer, ForeignKey("rights_consents.id"), nullable=True)
    visibility = Column(Enum(AssetVisibility), default=AssetVisibility.public, nullable=False)
    nda_group = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="assets")
    rights = relationship("RightsConsent", back_populates="assets")
    whitelist_entries = relationship(
        "AssetWhitelist", back_populates="asset", cascade="all, delete-orphan"
    )


class AssetWhitelist(Base):
    __tablename__ = "asset_whitelists"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    account_email = Column(String, nullable=False)

    asset = relationship("Asset", back_populates="whitelist_entries")


class CaseStudy(Base):
    __tablename__ = "case_studies"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    goal = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    process = Column(Text, nullable=True)
    outcomes = Column(Text, nullable=True)
    metrics = Column(Text, nullable=True)
    behind_the_scenes = Column(Text, nullable=True)
    lessons = Column(Text, nullable=True)

    project = relationship("Project", back_populates="case_study")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)
    level = Column(Integer, default=1)

    projects = relationship("Project", secondary=project_skills, back_populates="skills")
    evidence = relationship("SkillEvidence", back_populates="skill", cascade="all, delete-orphan")
    goals = relationship("LearningGoal", back_populates="skill", cascade="all, delete-orphan")


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    note = Column(Text, nullable=True)
    link = Column(String, nullable=True)

    skill = relationship("Skill", back_populates="evidence")
    project = relationship("Project")


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    target_level = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=True)

    skill = relationship("Skill", back_populates="goals")


# ---------------------------------------------------------------------------
# Enhanced Creative project models for comprehensive project management
# ---------------------------------------------------------------------------

class ProjectType(PyEnum):
    """Project types for creative projects."""
    
    website_mockup = "website_mockup"
    social_media = "social_media"
    print_graphic = "print_graphic"
    logo_design = "logo_design"
    ui_design = "ui_design"
    branding = "branding"


class CommentType(PyEnum):
    """Types of comments that can be added to projects."""
    
    general = "general"
    feedback = "feedback"
    approval = "approval"
    revision = "revision"
    question = "question"


class UserRole(PyEnum):
    """User roles for team management."""
    
    admin = "admin"
    creative_director = "creative_director"
    designer = "designer"
    client = "client"
    viewer = "viewer"


class AnalyticsEventType(PyEnum):
    """Types of analytics events to track."""
    
    project_created = "project_created"
    project_uploaded = "project_uploaded"
    comment_added = "comment_added"
    analysis_run = "analysis_run"
    report_generated = "report_generated"
    user_session = "user_session"
    collaboration_event = "collaboration_event"


# User and team management models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.designer, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("CreativeProject", back_populates="created_by")
    comments = relationship("ProjectComment", back_populates="user")
    analytics_events = relationship("AnalyticsEvent", back_populates="user")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    permissions = Column(JSON, nullable=True)  # Custom permissions per project
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("CreativeProject", back_populates="team_members")
    user = relationship("User")


class CreativeProject(Base):
    __tablename__ = "creative_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    project_type = Column(Enum(ProjectType), nullable=False)
    description = Column(Text, nullable=True)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    color_palette = Column(JSON, nullable=True)
    extracted_text = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Project metadata
    status = Column(String, default="draft", nullable=False)  # draft, in_review, approved, completed
    priority = Column(String, default="medium", nullable=False)  # low, medium, high, urgent
    deadline = Column(DateTime(timezone=True), nullable=True)
    client_info = Column(JSON, nullable=True)
    brand_guidelines = Column(JSON, nullable=True)
    
    # Analysis results
    accessibility_score = Column(Integer, nullable=True)  # 0-100
    design_quality_score = Column(Integer, nullable=True)  # 0-100
    trend_alignment_score = Column(Integer, nullable=True)  # 0-100
    
    # Relationships
    created_by = relationship("User", back_populates="projects")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    questions = relationship("ProjectQuestion", back_populates="project", cascade="all, delete-orphan")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    insights = relationship("ProjectInsight", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("ProjectComment", back_populates="project", cascade="all, delete-orphan")
    analytics_events = relationship("AnalyticsEvent", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("ProjectReport", back_populates="project", cascade="all, delete-orphan")


class ProjectComment(Base):
    __tablename__ = "project_comments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    comment_type = Column(Enum(CommentType), default=CommentType.general, nullable=False)
    
    # Position and context for design feedback
    metadata = Column(JSON, nullable=True)  # coordinates, element_id, etc.
    
    # Comment thread support
    parent_comment_id = Column(Integer, ForeignKey("project_comments.id"), nullable=True)
    
    # Status tracking
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("CreativeProject", back_populates="comments")
    user = relationship("User", back_populates="comments")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    parent_comment = relationship("ProjectComment", remote_side=[id])
    replies = relationship("ProjectComment", back_populates="parent_comment")


class ProjectQuestion(Base):
    __tablename__ = "project_questions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    is_answered = Column(Boolean, default=False, nullable=False)
    answer = Column(Text, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    answered_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("CreativeProject", back_populates="questions")
    answered_by = relationship("User")


class ProjectFile(Base):
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_current_version = Column(Boolean, default=True, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("CreativeProject", back_populates="files")
    uploaded_by = relationship("User")


class ProjectInsight(Base):
    __tablename__ = "project_insights"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    insight_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Integer, nullable=False)  # 0-100
    actionable = Column(Boolean, default=True, nullable=False)
    priority = Column(String, default="medium", nullable=False)  # low, medium, high
    metadata = Column(JSON, nullable=True)  # Additional data for the insight
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("CreativeProject", back_populates="insights")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(AnalyticsEventType), nullable=False)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Event data
    event_data = Column(JSON, nullable=True)
    session_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Integer, nullable=True)  # For session events

    # Relationships
    project = relationship("CreativeProject", back_populates="analytics_events")
    user = relationship("User", back_populates="analytics_events")


class ProjectReport(Base):
    __tablename__ = "project_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    report_type = Column(String, nullable=False)  # pdf, html, json, csv
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Report metadata
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_config = Column(JSON, nullable=True)  # Configuration used to generate report
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("CreativeProject", back_populates="reports")
    generated_by = relationship("User")
