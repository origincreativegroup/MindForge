from pydantic import BaseModel, Field
from typing import Optional

class SkillIn(BaseModel):
    name: str = Field(..., min_length=1)
    level: Optional[int] = Field(None, ge=0, le=5)
    category: Optional[str] = None
    notes: Optional[str] = None

class SkillOut(SkillIn):
    id: int
