"""Collaboration service for managing project comments and activities."""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..services.models import ProjectComment, ProjectActivity


class CollaborationService:
    """Service for managing project collaboration features."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_project_comments(self, project_id: int) -> List[Dict[str, Any]]:
        """Get comments for a project."""
        comments = self.db.query(ProjectComment).filter(
            ProjectComment.project_id == project_id
        ).all()
        
        return [
            {
                "id": comment.id,
                "project_id": comment.project_id,
                "author": {
                    "id": comment.author_id,
                    "name": comment.author_name
                },
                "content": comment.content,
                "comment_type": comment.comment_type,
                "is_resolved": comment.is_resolved,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat()
            }
            for comment in comments
        ]
    
    async def get_project_activity(self, project_id: int) -> List[Dict[str, Any]]:
        """Get activity log for a project."""
        activities = self.db.query(ProjectActivity).filter(
            ProjectActivity.project_id == project_id
        ).all()
        
        return [
            {
                "id": activity.id,
                "project_id": activity.project_id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "actor_name": activity.actor_name,
                "metadata": activity.activity_metadata,  # Map back to expected field name
                "created_at": activity.created_at.isoformat()
            }
            for activity in activities
        ]
    
    async def add_comment(self, project_id: int, author_name: str, content: str, 
                         comment_type: str = "general", author_id: Optional[int] = None) -> Dict[str, Any]:
        """Add a comment to a project."""
        comment = ProjectComment(
            project_id=project_id,
            author_id=author_id,
            author_name=author_name,
            content=content,
            comment_type=comment_type
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        
        return {
            "id": comment.id,
            "project_id": comment.project_id,
            "author": {
                "id": comment.author_id,
                "name": comment.author_name
            },
            "content": comment.content,
            "comment_type": comment.comment_type,
            "is_resolved": comment.is_resolved,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        }
    
    async def add_activity(self, project_id: int, activity_type: str, description: str,
                          actor_name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add an activity log entry for a project."""
        activity = ProjectActivity(
            project_id=project_id,
            activity_type=activity_type,
            description=description,
            actor_name=actor_name,
            activity_metadata=metadata or {}  # Use the renamed field
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return {
            "id": activity.id,
            "project_id": activity.project_id,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "actor_name": activity.actor_name,
            "metadata": activity.activity_metadata,  # Map back to expected field name
            "created_at": activity.created_at.isoformat()
        }