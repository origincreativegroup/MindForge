"""
Creative Projects Schemas for MindForge API
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schemas
class ProjectBase(BaseModel):
    name: str
    project_type: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    project_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    id: int
    status: str
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    extracted_text: Optional[str] = None
    color_palette: Optional[Dict[str, Any]] = None
    dimensions: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Team Member schemas
class TeamMemberBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = None

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberResponse(TeamMemberBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool = True
    permissions: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    question: str
    question_type: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class QuestionCreate(QuestionBase):
    project_id: int
    priority: Optional[int] = 1

class QuestionUpdate(BaseModel):
    answer: Optional[str] = None
    is_answered: Optional[bool] = None

class QuestionResponse(QuestionBase):
    id: int
    project_id: int
    answer: Optional[str] = None
    is_answered: bool = False
    priority: int = 1
    created_at: datetime
    answered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Insight schemas
class InsightBase(BaseModel):
    insight_type: str
    title: str
    description: Optional[str] = None
    score: Optional[float] = None

class InsightCreate(InsightBase):
    project_id: int
    data: Optional[Dict[str, Any]] = None

class InsightResponse(InsightBase):
    id: int
    project_id: int
    data: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentBase(BaseModel):
    content: str
    comment_type: Optional[str] = "general"

class CommentCreate(CommentBase):
    project_id: int
    metadata: Optional[Dict[str, Any]] = None

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_resolved: Optional[bool] = None

class CommentResponse(CommentBase):
    id: int
    project_id: int
    author_id: int
    metadata: Dict[str, Any] = {}
    is_resolved: bool = False
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Activity schemas
class ActivityBase(BaseModel):
    activity_type: str
    description: Optional[str] = None

class ActivityCreate(ActivityBase):
    project_id: int
    user_id: int
    metadata: Optional[Dict[str, Any]] = None

class ActivityResponse(ActivityBase):
    id: int
    project_id: int
    user_id: int
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

# Upload schemas
class UploadResponse(BaseModel):
    message: str
    project: ProjectResponse
    analysis: Optional[Dict[str, Any]] = None

# List response schemas
class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int

class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int

class InsightListResponse(BaseModel):
    insights: List[InsightResponse]
    total: int

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int

class ActivityListResponse(BaseModel):
    activities: List[ActivityResponse]
    total: int

# Status schemas
class StatusResponse(BaseModel):
    api_version: str
    endpoints: Dict[str, str]
    upload_config: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]