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
    Float,
    Table,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

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


class CreativeProjectStatus(PyEnum):
    """Lifecycle stages for creative projects used in tests."""

    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    NEEDS_INFO = "needs_info"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectType(PyEnum):
    """Supported project types."""

    # Lowercase names for legacy compatibility
    branding = "branding"
    website_mockup = "website_mockup"
    social_media = "social_media"
    print_design = "print_design"
    illustration = "illustration"
    photography = "photography"
    video_production = "video_production"
    ui_ux = "ui_ux"
    packaging = "packaging"
    logo_design = "logo_design"

    # Additional types used by questioner and services
    print_graphic = "print_graphic"
    video = "video"
    ui_design = "ui_design"
    presentation = "presentation"
    mobile_app = "mobile_app"
    other = "other"

    # Uppercase aliases for convenience in other modules
    WEBSITE_MOCKUP = "website_mockup"
    SOCIAL_MEDIA = "social_media"
    PRINT_GRAPHIC = "print_graphic"
    VIDEO = "video"
    LOGO_DESIGN = "logo_design"
    UI_DESIGN = "ui_design"
    BRANDING = "branding"
    PRESENTATION = "presentation"
    MOBILE_APP = "mobile_app"
    OTHER = "other"


class QuestionType(PyEnum):
    """Supported question formats."""

    text = "text"
    choice = "choice"
    boolean = "boolean"


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


class CreativeProject(Base):
    """Minimal creative project model used in tests."""

    __tablename__ = "creative_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    project_type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(CreativeProjectStatus), default=CreativeProjectStatus.UPLOADED, nullable=False)
    description = Column(Text, nullable=True)
    original_filename = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    project_metadata = Column(JSON, default=dict)
    extracted_text = Column(Text, nullable=True)
    color_palette = Column(JSON, nullable=True)
    dimensions = Column(JSON, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = relationship("ProjectQuestion", back_populates="project", cascade="all, delete-orphan")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    insights = relationship("ProjectInsight", back_populates="project", cascade="all, delete-orphan")


class ProjectQuestion(Base):
    """Questions associated with a creative project."""

    __tablename__ = "project_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(String(50))
    options = Column(JSON, nullable=True)
    answer = Column(Text, nullable=True)
    is_answered = Column(Integer, default=0)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

    project = relationship("CreativeProject", back_populates="questions")


class ProjectFile(Base):
    """Files uploaded for a creative project."""

    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), default="original")
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    processing_status = Column(String(50), default="pending")
    processing_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("CreativeProject", back_populates="files")


class ProjectInsight(Base):
    """Analysis insights for a creative project."""

    __tablename__ = "project_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("creative_projects.id"), nullable=False)
    insight_type = Column(String(100))
    title = Column(String(255))
    description = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("CreativeProject", back_populates="insights")


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
    name = Column(String, nullable=True)  # Alias for title for reporting compatibility
    short_tagline = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.pitch, nullable=False)
    project_type = Column(String, default="general", nullable=False)  # For reporting service
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    disciplines = Column(JSON, default=list)
    dimensions = Column(JSON, default=dict)  # For reporting service
    color_palette = Column(JSON, default=list)  # For reporting service
    tags = Column(JSON, default=list)  # For reporting service
    hero_asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)

    # Analysis fields
    project_type = Column(Enum(ProjectType), nullable=True)
    file_path = Column(String, nullable=True)
    dimensions = Column(JSON, nullable=True)  # {"width": int, "height": int}
    color_palette = Column(JSON, default=list)  # List of hex color strings
    extracted_text = Column(Text, nullable=True)

    client = relationship("Client", back_populates="projects")
    hero_asset = relationship("Asset", foreign_keys=[hero_asset_id])
    assets = relationship("Asset", foreign_keys="Asset.project_id", back_populates="project", cascade="all, delete-orphan")
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

    project = relationship("Project", foreign_keys=[project_id], back_populates="assets")
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


