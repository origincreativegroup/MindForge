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
class CaseyQuestionResponse:
    """Represents a question returned to the Casey UI."""

    question_id: int
    question: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    context: Optional[str] = None
    priority: int = 0
    follow_up_questions: Optional[List[str]] = field(default=None)


__all__ = ["ProjectQuestionCreate", "CaseyQuestionResponse", "ProjectType"]
