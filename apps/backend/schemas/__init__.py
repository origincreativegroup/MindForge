"""Light‑weight schema objects used in the tests.

The real project employs Pydantic models for request/response validation.  To
keep the dependency footprint small for the kata's unit tests we implement the
minimal data structures as simple ``dataclasses``.  Only the fields exercised in
the tests are included.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..services.models import QuestionType, ProjectType


@dataclass
class ProjectQuestionCreate:
    """Schema used when creating a new project question."""

    project_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    priority: int = 2


@dataclass
class ProjectQuestionUpdate:
    """Schema used when updating a project question with an answer."""

    answer: str


@dataclass
class CaseyQuestionResponse:
    """Represents a question returned to the Casey UI."""

    question_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    context: Optional[str] = None
    priority: int = 0
    follow_up_questions: Optional[List[str]] = field(default=None)


@dataclass
class CreativeProjectCreate:
    """Schema used when creating a new creative project."""

    name: str
    project_type: ProjectType
    description: Optional[str] = None
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


@dataclass
class CreativeProject:
    """Simple representation of a creative project."""

    id: int
    name: str
    project_type: ProjectType
    description: Optional[str] = None


@dataclass
class ProjectUploadResponse:
    """Response returned after successfully uploading a project."""

    project_id: int
    filename: str


@dataclass
class ProjectAnalysisResponse:
    """Minimal analysis response for uploaded projects."""

    result: dict


__all__ = [
    "ProjectQuestionCreate",
    "ProjectQuestionUpdate",
    "CaseyQuestionResponse",
    "CreativeProjectCreate",
    "CreativeProject",
    "ProjectUploadResponse",
    "ProjectAnalysisResponse",
    "ProjectType",
]
