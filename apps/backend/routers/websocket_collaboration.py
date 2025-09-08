"""
WebSocket router for real-time collaboration features.
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.websocket_manager import (
    connection_manager,
    WebSocketMessageHandler,
    get_realtime_stats
)

router = APIRouter()


@router.websocket("/ws/collaboration")
async def websocket_collaboration_endpoint(
    websocket: WebSocket,
    project_id: int = Query(..., description="Project ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time collaboration features.
    Supports project-based collaboration, comments, presence, and Casey AI interactions.
    """
    message_handler = WebSocketMessageHandler(db)
    
    await connection_manager.connect(websocket, user_id, project_id)
    
    try:
        # Send initial connection confirmation
        await connection_manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "project_id": project_id,
                "user_id": user_id,
                "timestamp": connection_manager.user_presence.get(project_id, {}).get(user_id, {}).get("last_seen")
            },
            user_id,
            project_id
        )
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await message_handler.handle_message(websocket, user_id, project_id, message)
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": "now"
                    },
                    user_id,
                    project_id
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id, project_id)


@router.get("/api/realtime/stats")
async def get_collaboration_stats():
    """Get real-time collaboration statistics"""
    return get_realtime_stats()


@router.get("/api/realtime/project/{project_id}/users")
async def get_project_active_users(project_id: int):
    """Get list of users currently active in a project"""
    users = connection_manager.get_project_users(project_id)
    presence = connection_manager.user_presence.get(project_id, {})
    
    return {
        "project_id": project_id,
        "active_users": users,
        "user_count": len(users),
        "presence": presence
    }


@router.post("/api/realtime/project/{project_id}/notify/casey/start")
async def notify_casey_start(project_id: int):
    """Trigger Casey analysis start notification"""
    from ..services.websocket_manager import notify_casey_analysis_start
    await notify_casey_analysis_start(project_id)
    return {"message": "Casey analysis start notification sent"}


@router.post("/api/realtime/project/{project_id}/notify/casey/complete")
async def notify_casey_complete(project_id: int, insights_count: int = 0):
    """Trigger Casey analysis complete notification"""
    from ..services.websocket_manager import notify_casey_analysis_complete
    await notify_casey_analysis_complete(project_id, insights_count)
    return {"message": "Casey analysis complete notification sent"}


@router.post("/api/realtime/project/{project_id}/notify/team/join")
async def notify_team_member_join(project_id: int, user_name: str):
    """Trigger new team member notification"""
    from ..services.websocket_manager import notify_new_team_member
    await notify_new_team_member(project_id, user_name)
    return {"message": "Team member join notification sent"}