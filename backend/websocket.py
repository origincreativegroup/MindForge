"""
WebSocket support for real-time process updates and annotations.
Supports the frontend's real-time visualization features.
"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.process_subscribers: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, process_id: str = "default"):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)

        if process_id not in self.process_subscribers:
            self.process_subscribers[process_id] = set()
        self.process_subscribers[process_id].add(websocket)

    def disconnect(self, websocket: WebSocket, process_id: str = "default"):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        if process_id in self.process_subscribers:
            self.process_subscribers[process_id].discard(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except:
            # Connection might be closed
            self.active_connections.discard(websocket)

    async def broadcast_to_process(self, message: str, process_id: str = "default"):
        """Broadcast a message to all subscribers of a specific process."""
        if process_id not in self.process_subscribers:
            return

        dead_connections = set()
        for connection in self.process_subscribers[process_id]:
            try:
                await connection.send_text(message)
            except:
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn, process_id)

    async def broadcast_to_all(self, message: str):
        """Broadcast a message to all active connections."""
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.active_connections.discard(conn)

# Global connection manager
manager = ConnectionManager()

# WebSocket router
ws_router = APIRouter()

@ws_router.websocket("/ws/process")
async def websocket_process_endpoint(websocket: WebSocket, process_id: str = "default"):
    """
    WebSocket endpoint for real-time process updates.
    Supports process visualization, annotations, and live updates.
    """
    await manager.connect(websocket, process_id)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "status": "connected",
                "process_id": process_id
            }),
            websocket
        )

        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket, process_id)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON"}),
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, process_id)

async def handle_websocket_message(message: dict, websocket: WebSocket, process_id: str):
    """Handle incoming WebSocket messages from clients."""

    msg_type = message.get("type")

    if msg_type == "ping":
        # Heartbeat/keepalive
        await manager.send_personal_message(
            json.dumps({"type": "pong"}),
            websocket
        )

    elif msg_type == "annotation":
        # User added an annotation - broadcast to others
        annotation = message.get("payload", {})
        await manager.broadcast_to_process(
            json.dumps({
                "type": "annotation",
                "payload": annotation,
                "sender": "user"
            }),
            process_id
        )

    elif msg_type == "process_update":
        # Process was updated - broadcast to all viewers
        process_data = message.get("payload", {})
        await manager.broadcast_to_process(
            json.dumps({
                "type": "update",
                "payload": process_data
            }),
            process_id
        )

    elif msg_type == "cursor_position":
        # User cursor position for collaborative editing
        position = message.get("payload", {})
        await manager.broadcast_to_process(
            json.dumps({
                "type": "cursor",
                "payload": position,
                "sender": websocket
            }),
            process_id
        )

    elif msg_type == "subscribe":
        # Subscribe to specific process updates
        new_process_id = message.get("process_id", process_id)
        if new_process_id != process_id:
            manager.disconnect(websocket, process_id)
            await manager.connect(websocket, new_process_id)

    else:
        # Unknown message type
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": f"Unknown message type: {msg_type}"
            }),
            websocket
        )

# Helper functions for sending updates from other parts of the application

async def broadcast_process_update(process_data: dict, process_id: str = "default"):
    """
    Broadcast process updates to all connected clients.
    Call this from other parts of the application when processes are updated.
    """
    message = json.dumps({
        "type": "update",
        "payload": process_data,
        "timestamp": asyncio.get_event_loop().time()
    })
    await manager.broadcast_to_process(message, process_id)

async def broadcast_annotation(annotation: dict, process_id: str = "default"):
    """
    Broadcast annotations to connected clients.
    """
    message = json.dumps({
        "type": "annotation",
        "payload": annotation,
        "sender": "system"
    })
    await manager.broadcast_to_process(message, process_id)

async def broadcast_simulation_result(simulation_data: dict, process_id: str = "default"):
    """
    Broadcast simulation results to connected clients.
    """
    message = json.dumps({
        "type": "simulation",
        "payload": simulation_data
    })
    await manager.broadcast_to_process(message, process_id)

# Alternative WebSocket endpoint for general notifications
@ws_router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for general application notifications.
    """
    await websocket.accept()
    manager.active_connections.add(websocket)

    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": "Connected to MindForge Casey notifications"
        }))

        # Keep connection alive and handle any incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        manager.active_connections.discard(websocket)

# Health check for WebSocket connections
def get_websocket_stats():
    """Get statistics about active WebSocket connections."""
    return {
        "total_connections": len(manager.active_connections),
        "process_subscribers": {
            pid: len(subs) for pid, subs in manager.process_subscribers.items()
        }
    }
