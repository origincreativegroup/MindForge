from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
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
