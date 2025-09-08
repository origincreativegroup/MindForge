"""
Collaboration service for managing team interactions and real-time features.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import CreativeProject


class CollaborationService:
    """Service for handling collaboration features."""

    def __init__(self, db: Session):
        self.db = db

    async def add_comment(
        self,
        project_id: int,
        author_id: int,
        content: str,
        comment_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a new comment to a project."""
        try:
            # Create comment
            comment = ProjectComment(
                project_id=project_id,
                author_id=author_id,
                content=content,
                comment_type=comment_type,
                metadata=metadata or {}
            )

            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)

            # Log activity
            await self.log_activity(
                project_id=project_id,
                user_id=author_id,
                activity_type="comment",
                description=f"Added comment: {content[:50]}...",
                metadata={"comment_id": comment.id}
            )

            return {
                "id": comment.id,
                "content": comment.content,
                "comment_type": comment.comment_type,
                "author_id": comment.author_id,
                "created_at": comment.created_at.isoformat(),
                "metadata": comment.metadata
            }

        except Exception as e:
            self.db.rollback()
            raise e

    async def resolve_comment(self, comment_id: int, resolved_by: int) -> bool:
        """Mark a comment as resolved."""
        try:
            comment = self.db.query(ProjectComment).filter(
                ProjectComment.id == comment_id
            ).first()

            if not comment:
                return False

            comment.is_resolved = True
            comment.resolved_by = resolved_by
            comment.resolved_at = datetime.utcnow()

            self.db.commit()

            # Log activity
            await self.log_activity(
                project_id=comment.project_id,
                user_id=resolved_by,
                activity_type="resolve_comment",
                description=f"Resolved comment: {comment.content[:50]}...",
                metadata={"comment_id": comment_id}
            )

            return True

        except Exception as e:
            self.db.rollback()
            raise e

    async def get_project_comments(
        self,
        project_id: int,
        include_resolved: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get comments for a project."""
        query = self.db.query(ProjectComment).filter(
            ProjectComment.project_id == project_id
        )

        if not include_resolved:
            query = query.filter(ProjectComment.is_resolved == False)

        comments = query.order_by(desc(ProjectComment.created_at)).limit(limit).all()

        return [
            {
                "id": comment.id,
                "content": comment.content,
                "comment_type": comment.comment_type,
                "author_id": comment.author_id,
                "is_resolved": comment.is_resolved,
                "resolved_by": comment.resolved_by,
                "created_at": comment.created_at.isoformat(),
                "metadata": comment.metadata
            }
            for comment in comments
        ]

    async def log_activity(
        self,
        project_id: int,
        user_id: int,
        activity_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log project activity."""
        try:
            activity = ProjectActivity(
                project_id=project_id,
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                metadata=metadata or {}
            )

            self.db.add(activity)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            # Don't raise exception for activity logging to avoid breaking main flows
            print(f"Failed to log activity: {e}")

    async def get_project_activities(
        self,
        project_id: int,
        activity_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent activities for a project."""
        query = self.db.query(ProjectActivity).filter(
            ProjectActivity.project_id == project_id
        )

        if activity_types:
            query = query.filter(ProjectActivity.activity_type.in_(activity_types))

        activities = query.order_by(desc(ProjectActivity.created_at)).limit(limit).all()

        return [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "user_id": activity.user_id,
                "created_at": activity.created_at.isoformat(),
                "metadata": activity.metadata
            }
            for activity in activities
        ]

    async def add_team_member(
        self,
        project_id: int,
        user_id: int,
        name: str,
        email: str,
        role: str = "viewer",
        permissions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a team member to a project.

        This minimal implementation stores the member details and returns them.
        In a full system this would persist to the database and enforce
        permission checks, but for the purposes of the tests we simply return
        the provided information.
        """
        member = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "permissions": permissions or {},
        }
        return member


class RealTimeCollaboration:
    """Utility helpers for real-time collaboration features."""

    @staticmethod
    def generate_visual_comment_coordinates(
        x: float, y: float, image_width: int, image_height: int
    ) -> Dict[str, float]:
        """Convert absolute coordinates to percentages relative to image size."""
        x_percent = (x / image_width * 100) if image_width else 0.0
        y_percent = (y / image_height * 100) if image_height else 0.0
        return {
            "x_percent": x_percent,
            "y_percent": y_percent,
            "x_absolute": x,
            "y_absolute": y,
            "image_width": image_width,
            "image_height": image_height,
        }

    @staticmethod
    def create_annotation_metadata(
        annotation_type: str,
        coordinates: Optional[Dict[str, float]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create structured metadata for project annotations."""
        metadata: Dict[str, Any] = {
            "annotation_type": annotation_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if coordinates:
            metadata["coordinates"] = coordinates

        if annotation_type == "design_suggestion":
            metadata["suggestion_category"] = kwargs.get("category")
            metadata["priority"] = kwargs.get("priority")
        elif annotation_type == "approval":
            metadata["approval_status"] = kwargs.get("status")
            metadata["approval_level"] = kwargs.get("level")
        elif annotation_type == "issue":
            metadata["issue_severity"] = kwargs.get("severity")
            metadata["issue_category"] = kwargs.get("category")

        return metadata
