from datetime import datetime, date
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel

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
# Creative project schemas for the creative projects router
# ---------------------------------------------------------------------------

class ProjectType(str, Enum):
    website_mockup = "website_mockup"
    social_media = "social_media"
    print_graphic = "print_graphic"
    logo_design = "logo_design"
    ui_design = "ui_design"
    video = "video"
    branding = "branding"


# Import QuestionType and ProjectStatus from models for the project questioner
from .services.models import QuestionType, ProjectStatus


class CreativeProjectCreate(BaseModel):
    name: str
    project_type: ProjectType
    description: Optional[str] = None
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None


class CreativeProject(BaseModel):
    id: int
    name: str
    project_type: ProjectType
    description: Optional[str] = None
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    dimensions: Optional[str] = None
    color_palette: Optional[List[str]] = None
    extracted_text: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime

    class Config:
        orm_mode = True


class ProjectQuestionCreate(BaseModel):
    project_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    priority: int = 2


class ProjectQuestionOut(ProjectQuestionCreate):
    id: int
    is_answered: bool = False
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


# Keep the old ProjectQuestion schema for backward compatibility
class ProjectQuestion(BaseModel):
    id: int
    project_id: int
    question: str
    question_type: str
    is_answered: bool = False
    answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


# Project questioner schemas (Casey functionality)
class CaseyQuestionResponse(BaseModel):
    question_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    context: str
    priority: int
    follow_up_questions: Optional[List[str]] = None


# Enhanced creative project schemas for questioner (alternative to existing)
class CreativeProjectForQuestioner(BaseModel):
    title: str
    short_tagline: Optional[str] = None
    project_type: ProjectType
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
    extracted_text: Optional[str] = None
    dimensions: Optional[Dict[str, int]] = None
    color_palette: Optional[List[str]] = None


class CreativeProjectOutForQuestioner(CreativeProjectForQuestioner):
    id: int
    questions: List[ProjectQuestionOut] = []

    class Config:
        orm_mode = True


# Existing project schemas for backward compatibility
class ProjectQuestionUpdate(BaseModel):
    answer: str


class ProjectFileCreate(BaseModel):
    project_id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int


class ProjectFile(BaseModel):
    id: int
    project_id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        orm_mode = True


class ProjectInsightCreate(BaseModel):
    project_id: int
    insight_type: str
    title: str
    description: str
    confidence: float


class ProjectInsight(BaseModel):
    id: int
    project_id: int
    insight_type: str
    title: str
    description: str
    confidence: float
    created_at: datetime

    class Config:
        orm_mode = True


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
    dimensions: Optional[str] = None
