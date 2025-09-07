from datetime import datetime
from typing import List, Optional
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
    raw_chunks: List[str] = []

class ProcessMapOut(BaseModel):
    id: int
    conversation_id: int
    steps: List[str]
    actors: List[str]
    tools: List[str]
    decisions: List[str]
    raw_chunks: List[str]
    created_at: datetime

    class Config:
        orm_mode = True

# Chat interaction schemas
class ChatTurn(BaseModel):
    user_text: str
