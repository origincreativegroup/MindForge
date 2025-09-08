from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON

from ..models import Project, Base
from ..db import get_db

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100))  # designer, reviewer, client, admin
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    permissions = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class ProjectShare(Base):
    __tablename__ = "project_shares"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    shared_by = Column(Integer, ForeignKey("team_members.id"), nullable=False)
    shared_with = Column(Integer, ForeignKey("team_members.id"))  # null for public links
    share_token = Column(String(255), unique=True, nullable=False)
    permissions = Column(JSON, default={"view": True, "comment": False, "edit": False})
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProjectComment(Base):
    __tablename__ = "project_comments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("team_members.id"), nullable=False)
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general")  # general, suggestion, issue, approval
    metadata_json = Column(JSON, default={})  # coordinates for visual comments, etc.
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("team_members.id"))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProjectActivity(Base):
    __tablename__ = "project_activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("team_members.id"), nullable=False)
    activity_type = Column(String(100), nullable=False)  # upload, comment, share, analyze, etc.
    description = Column(Text)
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class CollaborationService:
    """Service for managing team collaboration features"""

    def __init__(self, db: Session):
        self.db = db

    async def share_project(self, project_id: int, shared_by: int, 
                          shared_with: Optional[int] = None,
                          permissions: Dict[str, bool] = None,
                          expires_in_hours: Optional[int] = None) -> Dict[str, Any]:
        """Share a project with team members or create public link"""
        
        import secrets
        
        if permissions is None:
            permissions = {"view": True, "comment": True, "edit": False}
        
        # Generate unique share token
        share_token = secrets.token_urlsafe(32)
        
        # Calculate expiry
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        # Create share record
        project_share = ProjectShare(
            project_id=project_id,
            shared_by=shared_by,
            shared_with=shared_with,
            share_token=share_token,
            permissions=permissions,
            expires_at=expires_at
        )
        
        self.db.add(project_share)
        self.db.commit()
        self.db.refresh(project_share)
        
        # Log activity
        await self.log_activity(
            project_id=project_id,
            user_id=shared_by,
            activity_type="project_shared",
            description=f"Project shared {'publicly' if not shared_with else 'with team member'}",
            metadata={"share_id": project_share.id, "permissions": permissions}
        )
        
        return {
            "share_id": project_share.id,
            "share_token": share_token,
            "share_url": f"/shared/{share_token}",
            "permissions": permissions,
            "expires_at": expires_at
        }

    async def add_comment(self, project_id: int, author_id: int, 
                         content: str, comment_type: str = "general",
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a comment to a project"""
        
        if metadata is None:
            metadata = {}
        
        comment = ProjectComment(
            project_id=project_id,
            author_id=author_id,
            content=content,
            comment_type=comment_type,
            metadata_json=metadata
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        
        # Log activity
        await self.log_activity(
            project_id=project_id,
            user_id=author_id,
            activity_type="comment_added",
            description=f"Added {comment_type} comment",
            metadata={"comment_id": comment.id}
        )
        
        # Get author info for response
        author = self.db.query(TeamMember).filter(TeamMember.id == author_id).first()
        
        return {
            "comment_id": comment.id,
            "content": content,
            "comment_type": comment_type,
            "author": {
                "name": author.name if author else "Unknown",
                "avatar_url": author.avatar_url if author else None
            },
            "created_at": comment.created_at,
            "metadata": metadata
        }

    async def resolve_comment(self, comment_id: int, resolved_by: int) -> bool:
        """Mark a comment as resolved"""
        
        comment = self.db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
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
            activity_type="comment_resolved",
            description="Resolved comment",
            metadata={"comment_id": comment_id}
        )
        
        return True

    async def get_project_comments(self, project_id: int, 
                                 include_resolved: bool = True) -> List[Dict[str, Any]]:
        """Get all comments for a project"""
        
        query = self.db.query(ProjectComment).filter(ProjectComment.project_id == project_id)
        
        if not include_resolved:
            query = query.filter(ProjectComment.is_resolved == False)
        
        comments = query.order_by(ProjectComment.created_at.desc()).all()
        
        # Enrich with author information
        result = []
        for comment in comments:
            author = self.db.query(TeamMember).filter(TeamMember.id == comment.author_id).first()
            resolved_by_user = None
            if comment.resolved_by:
                resolved_by_user = self.db.query(TeamMember).filter(TeamMember.id == comment.resolved_by).first()
            
            result.append({
                "id": comment.id,
                "content": comment.content,
                "comment_type": comment.comment_type,
                "metadata": comment.metadata_json,
                "is_resolved": comment.is_resolved,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "resolved_at": comment.resolved_at,
                "author": {
                    "id": author.id if author else None,
                    "name": author.name if author else "Unknown",
                    "avatar_url": author.avatar_url if author else None,
                    "role": author.role if author else None
                },
                "resolved_by": {
                    "id": resolved_by_user.id if resolved_by_user else None,
                    "name": resolved_by_user.name if resolved_by_user else None
                } if resolved_by_user else None
            })
        
        return result

    async def get_project_activity(self, project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activity timeline for a project"""
        
        activities = (self.db.query(ProjectActivity)
                     .filter(ProjectActivity.project_id == project_id)
                     .order_by(ProjectActivity.created_at.desc())
                     .limit(limit)
                     .all())
        
        result = []
        for activity in activities:
            user = self.db.query(TeamMember).filter(TeamMember.id == activity.user_id).first()
            
            result.append({
                "id": activity.id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "metadata": activity.metadata_json,
                "created_at": activity.created_at,
                "user": {
                    "id": user.id if user else None,
                    "name": user.name if user else "System",
                    "avatar_url": user.avatar_url if user else None,
                    "role": user.role if user else None
                }
            })
        
        return result

    async def log_activity(self, project_id: int, user_id: int, 
                          activity_type: str, description: str = None,
                          metadata: Dict[str, Any] = None):
        """Log an activity for a project"""
        
        if metadata is None:
            metadata = {}
        
        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata_json=metadata
        )
        
        self.db.add(activity)
        self.db.commit()

    async def get_team_members(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get list of team members"""
        
        query = self.db.query(TeamMember)
        if active_only:
            query = query.filter(TeamMember.is_active == True)
        
        members = query.all()
        
        return [{
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "role": member.role,
            "avatar_url": member.avatar_url,
            "is_active": member.is_active,
            "permissions": member.permissions,
            "created_at": member.created_at
        } for member in members]

    async def check_project_access(self, project_id: int, user_id: int, 
                                 required_permission: str = "view") -> bool:
        """Check if user has access to a project"""
        
        # Check if user is project owner (simplified logic)
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Check if project is shared with user
        share = (self.db.query(ProjectShare)
                .filter(ProjectShare.project_id == project_id)
                .filter(ProjectShare.shared_with == user_id)
                .filter(ProjectShare.is_active == True)
                .first())
        
        if share:
            # Check if share has expired
            if share.expires_at and share.expires_at < datetime.utcnow():
                return False
            
            # Check permission
            return share.permissions.get(required_permission, False)
        
        # Check if user has admin role or owns the project
        user = self.db.query(TeamMember).filter(TeamMember.id == user_id).first()
        if user and user.role == "admin":
            return True
        
        return False

    async def get_shared_projects(self, user_id: int) -> List[Dict[str, Any]]:
        """Get projects shared with a user"""
        
        shares = (self.db.query(ProjectShare)
                 .filter(ProjectShare.shared_with == user_id)
                 .filter(ProjectShare.is_active == True)
                 .all())
        
        result = []
        for share in shares:
            # Check if share has expired
            if share.expires_at and share.expires_at < datetime.utcnow():
                continue
            
            project = self.db.query(Project).filter(Project.id == share.project_id).first()
            if project:
                shared_by = self.db.query(TeamMember).filter(TeamMember.id == share.shared_by).first()
                
                result.append({
                    "project": {
                        "id": project.id,
                        "name": project.title,  # Note: using 'title' field from existing Project model
                        "project_type": "creative",  # Default since existing model doesn't have this field
                        "status": project.status.value if project.status else None,
                        "created_at": getattr(project, 'created_at', None)
                    },
                    "share": {
                        "permissions": share.permissions,
                        "shared_at": share.created_at,
                        "expires_at": share.expires_at
                    },
                    "shared_by": {
                        "name": shared_by.name if shared_by else "Unknown",
                        "role": shared_by.role if shared_by else None
                    }
                })
        
        return result

    async def create_casey_collaboration_summary(self, project_id: int) -> str:
        """Generate a Casey-style summary of project collaboration"""
        
        # Get project info
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return "Project not found."
        
        # Get comments and activity
        comments = await self.get_project_comments(project_id)
        activities = await self.get_project_activity(project_id, limit=20)
        
        # Generate summary
        summary_parts = [
            f"Here's the collaboration summary for '{project.title}':\n"
        ]
        
        # Comment summary
        total_comments = len(comments)
        unresolved_comments = len([c for c in comments if not c['is_resolved']])
        
        if total_comments > 0:
            summary_parts.append(f"💬 **Comments**: {total_comments} total, {unresolved_comments} unresolved")
            
            # Most recent feedback
            recent_comment = comments[0] if comments else None
            if recent_comment:
                summary_parts.append(f"   Latest: \"{recent_comment['content'][:100]}...\" by {recent_comment['author']['name']}")
        else:
            summary_parts.append("💬 **Comments**: No comments yet")
        
        # Activity summary
        if activities:
            summary_parts.append(f"\n📈 **Recent Activity** ({len(activities)} actions):")
            for activity in activities[:3]:  # Show last 3 activities
                summary_parts.append(f"   • {activity['description']} by {activity['user']['name']}")
        
        # Team involvement
        involved_users = set()
        for comment in comments:
            involved_users.add(comment['author']['name'])
        for activity in activities:
            involved_users.add(activity['user']['name'])
        
        if involved_users:
            summary_parts.append(f"\n👥 **Team Members Involved**: {', '.join(involved_users)}")
        
        # Next steps suggestion
        if unresolved_comments > 0:
            summary_parts.append(f"\n🎯 **Suggested Next Steps**: Address {unresolved_comments} unresolved comments for project completion")
        elif total_comments == 0:
            summary_parts.append(f"\n🎯 **Suggested Next Steps**: Share with team for feedback and review")
        else:
            summary_parts.append(f"\n🎯 **Status**: All feedback addressed - ready for final review!")
        
        return "\n".join(summary_parts)


class NotificationService:
    """Service for managing notifications about project updates"""

    def __init__(self, db: Session):
        self.db = db

    async def notify_project_shared(self, project_id: int, shared_with: int, shared_by: int):
        """Send notification when project is shared"""
        # Implementation would integrate with email/notification system
        pass

    async def notify_comment_added(self, project_id: int, comment_id: int, mentioned_users: List[int] = None):
        """Send notification when comment is added"""
        # Implementation would notify project participants
        pass

    async def notify_project_updated(self, project_id: int, update_type: str):
        """Send notification when project is updated"""
        # Implementation would notify all project participants
        pass


# Real-time collaboration utilities

class RealTimeCollaboration:
    """Utilities for real-time collaboration features"""

    @staticmethod
    def generate_visual_comment_coordinates(x: float, y: float, image_width: int, image_height: int) -> Dict[str, float]:
        """Generate standardized coordinates for visual comments on images"""
        return {
            "x_percent": (x / image_width) * 100,
            "y_percent": (y / image_height) * 100,
            "x_absolute": x,
            "y_absolute": y,
            "image_width": image_width,
            "image_height": image_height
        }

    @staticmethod
    def create_annotation_metadata(comment_type: str, coordinates: Dict = None, **kwargs) -> Dict[str, Any]:
        """Create metadata for different types of annotations"""
        metadata = {
            "annotation_type": comment_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if coordinates:
            metadata["coordinates"] = coordinates
        
        if comment_type == "design_suggestion":
            metadata.update({
                "suggestion_category": kwargs.get("category", "general"),
                "priority": kwargs.get("priority", "medium")
            })
        elif comment_type == "approval":
            metadata.update({
                "approval_status": kwargs.get("status", "pending"),
                "approval_level": kwargs.get("level", "standard")
            })
        elif comment_type == "issue":
            metadata.update({
                "issue_severity": kwargs.get("severity", "medium"),
                "issue_category": kwargs.get("category", "design")
            })
        
        return metadata


# Integration helpers

def setup_collaboration_tables(engine):
    """Create collaboration tables in database"""
    # Import here to ensure all models are loaded
    from . import collaboration
    Base.metadata.create_all(bind=engine)

def get_collaboration_service(db: Session = None) -> CollaborationService:
    """Get collaboration service instance"""
    if db is None:
        db = next(get_db())
    return CollaborationService(db)