"""
Creative Projects Database Models for MindForge
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CreativeProject(Base):
    """Main creative projects table"""
    __tablename__ = "creative_projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    project_type = Column(String(50), nullable=False)
    status = Column(String(50), default='uploaded')
    description = Column(Text)
    original_filename = Column(String(500))
    file_path = Column(String(1000))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    metadata = Column(JSON, default={})
    extracted_text = Column(Text)
    color_palette = Column(JSON)
    dimensions = Column(JSON)
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship("ProjectQuestion", back_populates="project")
    insights = relationship("ProjectInsight", back_populates="project")
    comments = relationship("ProjectComment", back_populates="project")
    activities = relationship("ProjectActivity", back_populates="project")

class TeamMember(Base):
    """Team members table"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100))
    avatar_url = Column(String(500))
    is_active = Column(Integer, default=1)
    permissions = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = relationship("ProjectComment", foreign_keys="[ProjectComment.author_id]", back_populates="author")
    activities = relationship("ProjectActivity", back_populates="user")

class ProjectQuestion(Base):
    """Project questions table"""
    __tablename__ = "project_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('creative_projects.id'), nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(String(50))
    options = Column(JSON)
    answer = Column(Text)
    is_answered = Column(Integer, default=0)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime)
    
    # Relationships
    project = relationship("CreativeProject", back_populates="questions")

class ProjectInsight(Base):
    """Project insights table"""
    __tablename__ = "project_insights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('creative_projects.id'), nullable=False)
    insight_type = Column(String(100))
    title = Column(String(255))
    description = Column(Text)
    score = Column(Float)
    data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("CreativeProject", back_populates="insights")

class ProjectShare(Base):
    """Project shares table"""
    __tablename__ = "project_shares"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('creative_projects.id'), nullable=False)
    shared_by = Column(Integer, ForeignKey('team_members.id'), nullable=False)
    shared_with = Column(Integer, ForeignKey('team_members.id'))
    share_token = Column(String(255), unique=True, nullable=False)
    permissions = Column(JSON, default={"view": True, "comment": False, "edit": False})
    expires_at = Column(DateTime)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectComment(Base):
    """Project comments table"""
    __tablename__ = "project_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('creative_projects.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('team_members.id'), nullable=False)
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default='general')
    metadata = Column(JSON, default={})
    is_resolved = Column(Integer, default=0)
    resolved_by = Column(Integer, ForeignKey('team_members.id'))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("CreativeProject", back_populates="comments")
    author = relationship("TeamMember", foreign_keys=[author_id], back_populates="comments")

class ProjectActivity(Base):
    """Project activity table"""
    __tablename__ = "project_activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('creative_projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('team_members.id'), nullable=False)
    activity_type = Column(String(100), nullable=False)
    description = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("CreativeProject", back_populates="activities")
    user = relationship("TeamMember", back_populates="activities")