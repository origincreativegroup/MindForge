import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import logging

from .models import CreativeProject, TeamMember, ProjectComment, ProjectActivity
from .collaboration import CollaborationService

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration"""

    def __init__(self):
        # Active connections: {project_id: {user_id: websocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # User presence: {project_id: {user_id: {"status", "last_seen", "cursor_position"}}}
        self.user_presence: Dict[int, Dict[int, Dict[str, Any]]] = {}
        # Connection metadata: {websocket_id: {"user_id", "project_id", "connected_at"}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, project_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Initialize project connection group if not exists
        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}
            self.user_presence[project_id] = {}
        
        # Store connection
        self.active_connections[project_id][user_id] = websocket
        
        # Store metadata
        connection_id = f"{user_id}_{project_id}_{datetime.utcnow().timestamp()}"
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "project_id": project_id,
            "connected_at": datetime.utcnow(),
            "websocket": websocket
        }
        
        # Update presence
        self.user_presence[project_id][user_id] = {
            "status": "online",
            "last_seen": datetime.utcnow().isoformat(),
            "cursor_position": None,
            "current_view": "project_overview"
        }
        
        # Notify other users about new connection
        await self.broadcast_user_presence(project_id)
        
        logger.info(f"User {user_id} connected to project {project_id}")

    def disconnect(self, user_id: int, project_id: int):
        """Remove a WebSocket connection"""
        if project_id in self.active_connections:
            if user_id in self.active_connections[project_id]:
                del self.active_connections[project_id][user_id]
            
            if user_id in self.user_presence[project_id]:
                del self.user_presence[project_id][user_id]
            
            # Clean up empty project groups
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
                if project_id in self.user_presence:
                    del self.user_presence[project_id]
        
        # Clean up metadata
        to_remove = []
        for conn_id, metadata in self.connection_metadata.items():
            if metadata["user_id"] == user_id and metadata["project_id"] == project_id:
                to_remove.append(conn_id)
        
        for conn_id in to_remove:
            del self.connection_metadata[conn_id]
        
        logger.info(f"User {user_id} disconnected from project {project_id}")

    async def send_personal_message(self, message: dict, user_id: int, project_id: int):
        """Send a message to a specific user"""
        if project_id in self.active_connections:
            if user_id in self.active_connections[project_id]:
                websocket = self.active_connections[project_id][user_id]
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    # Connection is broken, clean it up
                    self.disconnect(user_id, project_id)

    async def broadcast_to_project(self, message: dict, project_id: int, exclude_user: Optional[int] = None):
        """Broadcast a message to all users in a project"""
        if project_id not in self.active_connections:
            return
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections[project_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id, project_id)

    async def broadcast_user_presence(self, project_id: int):
        """Broadcast current user presence to all project members"""
        if project_id not in self.user_presence:
            return
        
        presence_data = {
            "type": "user_presence",
            "project_id": project_id,
            "users": self.user_presence[project_id],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_project(presence_data, project_id)

    async def update_user_cursor(self, user_id: int, project_id: int, x: float, y: float):
        """Update user's cursor position and broadcast to others"""
        if project_id in self.user_presence and user_id in self.user_presence[project_id]:
            self.user_presence[project_id][user_id]["cursor_position"] = {"x": x, "y": y}
            
            cursor_data = {
                "type": "cursor_update",
                "user_id": user_id,
                "project_id": project_id,
                "position": {"x": x, "y": y},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.broadcast_to_project(cursor_data, project_id, exclude_user=user_id)

    async def update_user_view(self, user_id: int, project_id: int, view: str):
        """Update what view/section the user is currently looking at"""
        if project_id in self.user_presence and user_id in self.user_presence[project_id]:
            self.user_presence[project_id][user_id]["current_view"] = view
            self.user_presence[project_id][user_id]["last_seen"] = datetime.utcnow().isoformat()
            
            await self.broadcast_user_presence(project_id)

    def get_project_users(self, project_id: int) -> List[int]:
        """Get list of users currently connected to a project"""
        if project_id in self.active_connections:
            return list(self.active_connections[project_id].keys())
        return []

    def get_connection_count(self, project_id: int) -> int:
        """Get number of users connected to a project"""
        if project_id in self.active_connections:
            return len(self.active_connections[project_id])
        return 0


# Global connection manager instance
connection_manager = ConnectionManager()

class RealTimeCollaborationService:
    """Service for handling real-time collaboration events"""

    def __init__(self, db: Session):
        self.db = db
        self.collaboration_service = CollaborationService(db)

    async def handle_new_comment(self, comment_data: Dict[str, Any], author_id: int, project_id: int):
        """Handle real-time comment creation"""
        
        # Create comment in database
        comment_result = await self.collaboration_service.add_comment(
            project_id=project_id,
            author_id=author_id,
            content=comment_data["content"],
            comment_type=comment_data.get("comment_type", "general"),
            metadata=comment_data.get("metadata", {})
        )
        
        # Broadcast to all project members
        broadcast_data = {
            "type": "new_comment",
            "project_id": project_id,
            "comment": comment_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id)
        
        return comment_result

    async def handle_comment_resolution(self, comment_id: int, resolved_by: int, project_id: int):
        """Handle real-time comment resolution"""
        
        # Resolve comment in database
        success = await self.collaboration_service.resolve_comment(comment_id, resolved_by)
        
        if success:
            # Broadcast resolution to all project members
            broadcast_data = {
                "type": "comment_resolved",
                "project_id": project_id,
                "comment_id": comment_id,
                "resolved_by": resolved_by,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await connection_manager.broadcast_to_project(broadcast_data, project_id)
        
        return success

    async def handle_project_update(self, project_id: int, update_type: str, update_data: Dict[str, Any], user_id: int):
        """Handle real-time project updates"""
        
        # Log activity
        await self.collaboration_service.log_activity(
            project_id=project_id,
            user_id=user_id,
            activity_type=f"realtime_{update_type}",
            description=f"Real-time {update_type}: {update_data.get('description', '')}",
            metadata=update_data
        )
        
        # Broadcast update
        broadcast_data = {
            "type": "project_update",
            "project_id": project_id,
            "update_type": update_type,
            "data": update_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id)

    async def handle_live_drawing(self, project_id: int, user_id: int, drawing_data: Dict[str, Any]):
        """Handle live drawing/annotation events"""
        
        broadcast_data = {
            "type": "live_drawing",
            "project_id": project_id,
            "user_id": user_id,
            "drawing_data": drawing_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id, exclude_user=user_id)

    async def handle_casey_typing(self, project_id: int, is_typing: bool):
        """Handle Casey AI typing indicators"""
        
        broadcast_data = {
            "type": "casey_typing",
            "project_id": project_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id)

    async def handle_casey_analysis_progress(self, project_id: int, progress: float, stage: str):
        """Handle Casey analysis progress updates"""
        
        broadcast_data = {
            "type": "analysis_progress",
            "project_id": project_id,
            "progress": progress,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id)


# WebSocket message handlers

class WebSocketMessageHandler:
    """Handles incoming WebSocket messages"""

    def __init__(self, db: Session):
        self.db = db
        self.realtime_service = RealTimeCollaborationService(db)

    async def handle_message(self, websocket: WebSocket, user_id: int, project_id: int, message: Dict[str, Any]):
        """Route incoming messages to appropriate handlers"""
        
        message_type = message.get("type")
        
        try:
            if message_type == "ping":
                await self.handle_ping(websocket, message)
            elif message_type == "cursor_move":
                await self.handle_cursor_move(user_id, project_id, message)
            elif message_type == "view_change":
                await self.handle_view_change(user_id, project_id, message)
            elif message_type == "typing_indicator":
                await self.handle_typing_indicator(user_id, project_id, message)
            elif message_type == "add_comment":
                await self.handle_add_comment(user_id, project_id, message)
            elif message_type == "resolve_comment":
                await self.handle_resolve_comment(user_id, project_id, message)
            elif message_type == "live_drawing":
                await self.handle_live_drawing(user_id, project_id, message)
            elif message_type == "request_sync":
                await self.handle_sync_request(websocket, user_id, project_id)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message {message_type}: {e}")
            error_response = {
                "type": "error",
                "message": f"Failed to process {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(error_response))

    async def handle_ping(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle ping messages"""
        pong_response = {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "original_timestamp": message.get("timestamp")
        }
        await websocket.send_text(json.dumps(pong_response))

    async def handle_cursor_move(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle cursor movement"""
        position = message.get("position", {})
        x = position.get("x", 0)
        y = position.get("y", 0)
        
        await connection_manager.update_user_cursor(user_id, project_id, x, y)

    async def handle_view_change(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle view/section changes"""
        view = message.get("view", "project_overview")
        await connection_manager.update_user_view(user_id, project_id, view)

    async def handle_typing_indicator(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle typing indicators"""
        is_typing = message.get("is_typing", False)
        
        broadcast_data = {
            "type": "user_typing",
            "user_id": user_id,
            "project_id": project_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.broadcast_to_project(broadcast_data, project_id, exclude_user=user_id)

    async def handle_add_comment(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle real-time comment addition"""
        comment_data = message.get("comment_data", {})
        await self.realtime_service.handle_new_comment(comment_data, user_id, project_id)

    async def handle_resolve_comment(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle real-time comment resolution"""
        comment_id = message.get("comment_id")
        if comment_id:
            await self.realtime_service.handle_comment_resolution(comment_id, user_id, project_id)

    async def handle_live_drawing(self, user_id: int, project_id: int, message: Dict[str, Any]):
        """Handle live drawing/annotation"""
        drawing_data = message.get("drawing_data", {})
        await self.realtime_service.handle_live_drawing(project_id, user_id, drawing_data)

    async def handle_sync_request(self, websocket: WebSocket, user_id: int, project_id: int):
        """Handle request for current state synchronization"""
        
        # Get current project state
        project = self.db.query(CreativeProject).filter(CreativeProject.id == project_id).first()
        if not project:
            return
        
        # Get recent comments
        recent_comments = await self.realtime_service.collaboration_service.get_project_comments(
            project_id, include_resolved=True
        )
        
        # Get current user presence
        presence = connection_manager.user_presence.get(project_id, {})
        
        sync_data = {
            "type": "sync_response",
            "project_id": project_id,
            "project_state": {
                "name": project.name,
                "project_type": project.project_type.value if hasattr(project.project_type, 'value') else str(project.project_type),
                "created_at": project.created_at.isoformat()
            },
            "recent_comments": recent_comments[-10:],  # Last 10 comments
            "user_presence": presence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket.send_text(json.dumps(sync_data))


# Periodic tasks for real-time features

class RealTimeTaskManager:
    """Manages periodic tasks for real-time features"""

    def __init__(self):
        self.running = False
        self.tasks = []

    async def start_periodic_tasks(self):
        """Start all periodic tasks"""
        if self.running:
            return
        
        self.running = True
        
        # Start tasks
        self.tasks = [
            asyncio.create_task(self.cleanup_stale_connections()),
            asyncio.create_task(self.update_user_activity()),
            asyncio.create_task(self.broadcast_system_updates())
        ]
        
        logger.info("Real-time periodic tasks started")

    async def stop_periodic_tasks(self):
        """Stop all periodic tasks"""
        self.running = False
        
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
        
        logger.info("Real-time periodic tasks stopped")

    async def cleanup_stale_connections(self):
        """Clean up stale WebSocket connections"""
        while self.running:
            try:
                # Check for stale connections every 30 seconds
                await asyncio.sleep(30)
                
                # Implementation would check for inactive connections
                # and clean them up
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    async def update_user_activity(self):
        """Update user activity status"""
        while self.running:
            try:
                # Update every 60 seconds
                await asyncio.sleep(60)
                
                # Mark users as away if no activity for 5 minutes
                current_time = datetime.utcnow()
                
                for project_id, users in connection_manager.user_presence.items():
                    for user_id, presence in users.items():
                        last_seen = datetime.fromisoformat(presence["last_seen"])
                        if (current_time - last_seen).total_seconds() > 300:  # 5 minutes
                            if presence["status"] != "away":
                                presence["status"] = "away"
                                await connection_manager.broadcast_user_presence(project_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in activity update task: {e}")

    async def broadcast_system_updates(self):
        """Broadcast system-wide updates"""
        while self.running:
            try:
                # Check for system updates every 5 minutes
                await asyncio.sleep(300)
                
                # This could include things like:
                # - New feature announcements
                # - System maintenance notifications
                # - Performance updates
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system updates task: {e}")


# Global task manager
task_manager = RealTimeTaskManager()

# Utility functions

async def notify_casey_analysis_start(project_id: int):
    """Notify users that Casey is starting analysis"""
    broadcast_data = {
        "type": "casey_analysis_start",
        "project_id": project_id,
        "message": "Casey is analyzing your project…",
        "timestamp": datetime.utcnow().isoformat()
    }

    await connection_manager.broadcast_to_project(broadcast_data, project_id)


async def notify_casey_analysis_complete(project_id: int, insights_count: int):
    """Notify users that Casey has completed analysis"""
    broadcast_data = {
        "type": "casey_analysis_complete",
        "project_id": project_id,
        "insights_count": insights_count,
        "message": f"Casey found {insights_count} insights about your project!",
        "timestamp": datetime.utcnow().isoformat()
    }

    await connection_manager.broadcast_to_project(broadcast_data, project_id)


async def notify_new_team_member(project_id: int, user_name: str):
    """Notify users about new team member joining"""
    broadcast_data = {
        "type": "new_team_member",
        "project_id": project_id,
        "user_name": user_name,
        "message": f"{user_name} joined the project",
        "timestamp": datetime.utcnow().isoformat()
    }

    await connection_manager.broadcast_to_project(broadcast_data, project_id)


# Connection statistics

def get_realtime_stats() -> Dict[str, Any]:
    """Get real-time connection statistics"""
    total_connections = sum(
        len(users) for users in connection_manager.active_connections.values()
    )

    active_projects = len(connection_manager.active_connections)

    return {
        "total_connections": total_connections,
        "active_projects": active_projects,
        "projects": {
            project_id: len(users) 
            for project_id, users in connection_manager.active_connections.items()
        },
        "timestamp": datetime.utcnow().isoformat()
    }