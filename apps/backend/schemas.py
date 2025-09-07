from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


# Conversation schemas
class ConversationCreate(BaseModel):
    title: str | None = None


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
    emotion: str | None = None


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    emotion: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True


# Process map schemas
class ProcessMapCreate(BaseModel):
    steps: list[str] = []
    actors: list[str] = []
    tools: list[str] = []
    decisions: list[str] = []
    inputs: list[str] = []
    outputs: list[str] = []
    raw_chunks: list[str] = []


class ProcessMapOut(BaseModel):
    id: int
    conversation_id: int
    steps: list[str]
    actors: list[str]
    tools: list[str]
    decisions: list[str]
    inputs: list[str]
    outputs: list[str]
    raw_chunks: list[str]
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
    contact_info: str | None = None


class ClientOut(ClientCreate):
    id: int

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    title: str
    short_tagline: str | None = None
    status: ProjectStatus = ProjectStatus.pitch
    start_date: date | None = None
    end_date: date | None = None
    client_id: int | None = None
    disciplines: list[str] = []
    skill_ids: list[int] = []
    primary_tool_ids: list[int] = []
    tag_ids: list[int] = []
    collection_ids: list[int] = []
    hero_asset_id: int | None = None


class ProjectOut(ProjectCreate):
    id: int

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    project_id: int
    name: str
    person: str | None = None


class RoleOut(RoleCreate):
    id: int

    class Config:
        orm_mode = True


class DeliverableCreate(BaseModel):
    project_id: int
    name: str
    due_date: date | None = None
    status: str | None = None


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
    description: str | None = None


class CollectionOut(CollectionCreate):
    id: int

    class Config:
        orm_mode = True


class RightsConsentCreate(BaseModel):
    model_release_url: str | None = None
    property_release_url: str | None = None
    expiration: date | None = None
    nda_required: bool = False


class RightsConsentOut(RightsConsentCreate):
    id: int

    class Config:
        orm_mode = True


class AssetCreate(BaseModel):
    project_id: int
    type: AssetType
    src: str
    width: int | None = None
    height: int | None = None
    duration_s: int | None = None
    color_profile: str | None = None
    checksum: str | None = None
    alt_text: str | None = None
    transcript: str | None = None
    captions: str | None = None
    exif_meta: dict[str, str] | None = None
    rights_id: int | None = None
    visibility: AssetVisibility = AssetVisibility.public
    nda_group: str | None = None
    expires_at: datetime | None = None


class AssetOut(AssetCreate):
    id: int

    class Config:
        orm_mode = True


class CaseStudyCreate(BaseModel):
    project_id: int
    goal: str | None = None
    constraints: str | None = None
    process: str | None = None
    outcomes: str | None = None
    metrics: str | None = None
    behind_the_scenes: str | None = None
    lessons: str | None = None


class CaseStudyOut(CaseStudyCreate):
    id: int

    class Config:
        orm_mode = True


# Skill matrix --------------------------------------------------------------


class SkillCreate(BaseModel):
    name: str
    category: str | None = None
    level: int = 1


class SkillOut(SkillCreate):
    id: int

    class Config:
        orm_mode = True


class SkillEvidenceCreate(BaseModel):
    skill_id: int
    project_id: int | None = None
    note: str | None = None
    link: str | None = None


class SkillEvidenceOut(SkillEvidenceCreate):
    id: int

    class Config:
        orm_mode = True


class LearningGoalCreate(BaseModel):
    skill_id: int
    target_level: int
    due_date: date | None = None


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
