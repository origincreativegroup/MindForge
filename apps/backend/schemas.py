from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator

# Conversation schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        orm_mode = True

# Message schemas
class MessageCreate(BaseModel):
    role: str
    content: str
    emotion: Optional[str] = None

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    emotion: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Process map schemas
class ProcessMapCreate(BaseModel):
    steps: List[str] = []
    actors: List[str] = []
    tools: List[str] = []
    decisions: List[str] = []
    inputs: List[str] = []
    outputs: List[str] = []
    raw_chunks: List[str] = []

class ProcessMapOut(BaseModel):
    id: int
    conversation_id: int
    steps: List[str]
    actors: List[str]
    tools: List[str]
    decisions: List[str]
    inputs: List[str]
    outputs: List[str]
    raw_chunks: List[str]
    created_at: datetime

    class Config:
        orm_mode = True

# Chat interaction schemas
class ChatTurn(BaseModel):
    user_text: str


# ---------------------------------------------------------------------------
# Creative project inventory schemas
# ---------------------------------------------------------------------------


class ProjectStatus(str, Enum):
    pitch = "pitch"
    in_progress = "in_progress"
    shipped = "shipped"
    archived = "archived"


class AssetType(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"
    pdf = "pdf"
    three_d = "3d"
    url = "url"


class AssetVisibility(str, Enum):
    public = "public"
    gated = "gated"
    private = "private"


class ClientCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None


class ClientOut(ClientCreate):
    id: int

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    title: str
    short_tagline: Optional[str] = None
    status: ProjectStatus = ProjectStatus.pitch
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: Optional[int] = None
    disciplines: List[str] = []
    skill_ids: List[int] = []
    primary_tool_ids: List[int] = []
    tag_ids: List[int] = []
    collection_ids: List[int] = []
    hero_asset_id: Optional[int] = None


class ProjectOut(ProjectCreate):
    id: int

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    project_id: int
    name: str
    person: Optional[str] = None


class RoleOut(RoleCreate):
    id: int

    class Config:
        orm_mode = True


class DeliverableCreate(BaseModel):
    project_id: int
    name: str
    due_date: Optional[date] = None
    status: Optional[str] = None


class DeliverableOut(DeliverableCreate):
    id: int

    class Config:
        orm_mode = True


class ToolCreate(BaseModel):
    name: str


class ToolOut(ToolCreate):
    id: int

    class Config:
        orm_mode = True


class TagCreate(BaseModel):
    name: str


class TagOut(TagCreate):
    id: int

    class Config:
        orm_mode = True


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionOut(CollectionCreate):
    id: int

    class Config:
        orm_mode = True


class RightsConsentCreate(BaseModel):
    model_release_url: Optional[str] = None
    property_release_url: Optional[str] = None
    expiration: Optional[date] = None
    nda_required: bool = False


class RightsConsentOut(RightsConsentCreate):
    id: int

    class Config:
        orm_mode = True


class AssetCreate(BaseModel):
    project_id: int
    type: AssetType
    src: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration_s: Optional[int] = None
    color_profile: Optional[str] = None
    checksum: Optional[str] = None
    alt_text: Optional[str] = None
    transcript: Optional[str] = None
    captions: Optional[str] = None
    exif_meta: Optional[Dict[str, str]] = None
    rights_id: Optional[int] = None
    visibility: AssetVisibility = AssetVisibility.public
    nda_group: Optional[str] = None
    expires_at: Optional[datetime] = None


class AssetOut(AssetCreate):
    id: int

    class Config:
        orm_mode = True


class CaseStudyCreate(BaseModel):
    project_id: int
    goal: Optional[str] = None
    constraints: Optional[str] = None
    process: Optional[str] = None
    outcomes: Optional[str] = None
    metrics: Optional[str] = None
    behind_the_scenes: Optional[str] = None
    lessons: Optional[str] = None


class CaseStudyOut(CaseStudyCreate):
    id: int

    class Config:
        orm_mode = True


# Skill matrix --------------------------------------------------------------


class SkillCreate(BaseModel):
    name: str
    category: Optional[str] = None
    level: int = 1


class SkillOut(SkillCreate):
    id: int

    class Config:
        orm_mode = True


class SkillEvidenceCreate(BaseModel):
    skill_id: int
    project_id: Optional[int] = None
    note: Optional[str] = None
    link: Optional[str] = None


class SkillEvidenceOut(SkillEvidenceCreate):
    id: int

    class Config:
        orm_mode = True


class LearningGoalCreate(BaseModel):
    skill_id: int
    target_level: int
    due_date: Optional[date] = None


class LearningGoalOut(LearningGoalCreate):
    id: int

    class Config:
        orm_mode = True


class SkillStats(BaseModel):
    name: str
    evidence_count: int


class SkillGap(BaseModel):
    skill_id: int
    name: str
    current_level: int
    target_level: int
    gap: int


# ---------------------------------------------------------------------------
# Casey AI Creative Project Analysis Schemas
# ---------------------------------------------------------------------------

class ProjectType(str, Enum):
    WEBSITE_MOCKUP = "website_mockup"
    PRINT_GRAPHIC = "print_graphic"
    SOCIAL_MEDIA = "social_media"
    VIDEO = "video"
    BRANDING = "branding"
    PRESENTATION = "presentation"
    MOBILE_APP = "mobile_app"
    OTHER = "other"

class CreativeProjectStatus(str, Enum):
    UPLOADED = "uploaded"
    ANALYZING = "analyzing"
    NEEDS_INFO = "needs_info"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class QuestionType(str, Enum):
    TEXT = "text"
    CHOICE = "choice"
    NUMBER = "number"
    DATE = "date"
    FILE = "file"
    BOOLEAN = "boolean"
    COLOR = "color"
    URL = "url"

# Base schemas

class ProjectFileBase(BaseModel):
    filename: str
    file_type: str = "original"
    mime_type: Optional[str] = None

class ProjectFileCreate(ProjectFileBase):
    file_path: str
    file_size: Optional[int] = None

class ProjectFile(ProjectFileBase):
    id: int
    project_id: int
    file_path: str
    file_size: Optional[int] = None
    processing_status: str = "pending"
    processing_metadata: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        orm_mode = True

class ProjectQuestionBase(BaseModel):
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    priority: int = Field(default=1, ge=1, le=3)

class ProjectQuestionCreate(ProjectQuestionBase):
    project_id: int

class ProjectQuestionUpdate(BaseModel):
    answer: Optional[str] = None
    is_answered: Optional[bool] = None

class ProjectQuestion(ProjectQuestionBase):
    id: int
    project_id: int
    answer: Optional[str] = None
    is_answered: bool = False
    created_at: datetime
    answered_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CreativeProjectBase(BaseModel):
    name: str
    project_type: ProjectType
    description: Optional[str] = None

class CreativeProjectCreate(CreativeProjectBase):
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class CreativeProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CreativeProjectStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class CreativeProject(CreativeProjectBase):
    id: int
    status: CreativeProjectStatus
    metadata: Dict[str, Any] = {}
    extracted_text: Optional[str] = None
    color_palette: Optional[List[str]] = None
    dimensions: Optional[Dict[str, int]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    # Relationships
    questions: List[ProjectQuestion] = []
    files: List[ProjectFile] = []

    class Config:
        orm_mode = True

class ProjectInsightBase(BaseModel):
    insight_type: str
    title: str
    description: str
    score: Optional[float] = Field(None, ge=0.0, le=1.0)
    data: Dict[str, Any] = {}

class ProjectInsightCreate(ProjectInsightBase):
    project_id: int

class ProjectInsight(ProjectInsightBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Response schemas

class ProjectUploadResponse(BaseModel):
    project: CreativeProject
    questions: List[ProjectQuestion]
    next_steps: List[str]

class ProjectAnalysisResponse(BaseModel):
    project_id: int
    analysis_complete: bool
    insights: List[ProjectInsight]
    suggestions: List[str]
    color_palette: Optional[List[str]] = None
    dimensions: Optional[Dict[str, int]] = None

class CaseyQuestionResponse(BaseModel):
    question_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    context: str  # Why Casey is asking this question
    priority: int
    follow_up_questions: Optional[List[str]] = None

# Project type specific schemas

class WebsiteProjectMetadata(BaseModel):
    target_audience: Optional[str] = None
    device_type: Optional[str] = None  # desktop, mobile, tablet
    page_type: Optional[str] = None    # homepage, landing, product, etc.
    framework: Optional[str] = None    # react, wordpress, etc.
    color_scheme: Optional[str] = None
    layout_style: Optional[str] = None

class SocialMediaProjectMetadata(BaseModel):
    platform: Optional[str] = None     # instagram, facebook, twitter, etc.
    post_type: Optional[str] = None    # story, feed, ad, etc.
    campaign_goal: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None

class VideoProjectMetadata(BaseModel):
    duration: Optional[float] = None
    format: Optional[str] = None       # mp4, mov, etc.
    resolution: Optional[str] = None   # 1080p, 4K, etc.
    purpose: Optional[str] = None      # commercial, educational, social, etc.
    style: Optional[str] = None        # animation, live-action, etc.

class PrintProjectMetadata(BaseModel):
    print_size: Optional[str] = None   # A4, Letter, Business Card, etc.
    print_type: Optional[str] = None   # flyer, brochure, poster, etc.
    color_mode: Optional[str] = None   # CMYK, RGB
    bleed: Optional[bool] = None
    finish: Optional[str] = None       # matte, gloss, etc.
