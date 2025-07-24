"""
WebSocket connection manager for real-time communication
"""
from typing import Dict, Set, Optional, List
from fastapi import WebSocket
from datetime import datetime, timedelta
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for all sessions"""
    
    def __init__(self):
        # Maps session_id to set of connections
        self._connections: Dict[str, Set[WebSocket]] = {}
        # Maps connection to participant info
        self._participant_info: Dict[WebSocket, Dict] = {}
        # Maps connection to last activity time
        self._last_activity: Dict[WebSocket, datetime] = {}
        # Background task for health checks
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket, session_id: str, participant_id: str, participant_name: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to session connections
        if session_id not in self._connections:
            self._connections[session_id] = set()
        self._connections[session_id].add(websocket)
        
        # Store participant info
        self._participant_info[websocket] = {
            "session_id": session_id,
            "participant_id": participant_id,
            "participant_name": participant_name
        }
        
        # Track last activity
        self._last_activity[websocket] = datetime.utcnow()
        
        # Start health check task if not running
        if not self._health_check_task or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Participant {participant_name} ({participant_id}) connected to session {session_id}")
        
        # Notify others in session
        await self.broadcast_to_session(
            session_id,
            {
                "type": "participant_joined",
                "participant_id": participant_id,
                "participant_name": participant_name
            },
            exclude=websocket
        )
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        participant_info = self._participant_info.get(websocket)
        
        if participant_info:
            session_id = participant_info["session_id"]
            participant_id = participant_info["participant_id"]
            participant_name = participant_info["participant_name"]
            
            # Remove from connections
            if session_id in self._connections:
                self._connections[session_id].discard(websocket)
                if not self._connections[session_id]:
                    del self._connections[session_id]
            
            # Remove participant info and activity tracking
            del self._participant_info[websocket]
            if websocket in self._last_activity:
                del self._last_activity[websocket]
            
            logger.info(f"Participant {participant_name} ({participant_id}) disconnected from session {session_id}")
            
            # Notify others in session
            await self.broadcast_to_session(
                session_id,
                {
                    "type": "participant_left",
                    "participant_id": participant_id,
                    "participant_name": participant_name
                }
            )
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast a message to all connections in a session"""
        if session_id in self._connections:
            disconnected = set()
            for connection in self._connections[session_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to connection: {e}")
                        disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                await self.disconnect(connection)
    
    def get_session_participants(self, session_id: str) -> list:
        """Get list of participants in a session"""
        participants = []
        if session_id in self._connections:
            for connection in self._connections[session_id]:
                if connection in self._participant_info:
                    participants.append(self._participant_info[connection])
        return participants
    
    def get_session_count(self, session_id: str) -> int:
        """Get number of connections in a session"""
        return len(self._connections.get(session_id, set()))
    
    def update_activity(self, websocket: WebSocket):
        """Update last activity time for a connection"""
        if websocket in self._last_activity:
            self._last_activity[websocket] = datetime.utcnow()
    
    async def send_ping(self, websocket: WebSocket):
        """Send a ping message to check connection health"""
        try:
            await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat()})
            return True
        except Exception:
            return False
    
    async def _health_check_loop(self):
        """Background task to check connection health"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check all connections
                disconnected = set()
                for websocket in list(self._participant_info.keys()):
                    last_activity = self._last_activity.get(websocket)
                    if last_activity:
                        # If no activity for 60 seconds, send ping
                        if datetime.utcnow() - last_activity > timedelta(seconds=60):
                            if not await self.send_ping(websocket):
                                disconnected.add(websocket)
                        # If no activity for 120 seconds, consider disconnected
                        elif datetime.utcnow() - last_activity > timedelta(seconds=120):
                            disconnected.add(websocket)
                
                # Clean up disconnected connections
                for websocket in disconnected:
                    await self.disconnect(websocket)
                    
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get detailed statistics for a session"""
        participants = self.get_session_participants(session_id)
        return {
            "session_id": session_id,
            "participant_count": len(participants),
            "participants": participants,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def broadcast_to_participants(self, participant_ids: List[str], message: dict):
        """Broadcast a message to specific participants"""
        for websocket, info in self._participant_info.items():
            if info["participant_id"] in participant_ids:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to participant {info['participant_id']}: {e}")


# Global connection manager instance
manager = ConnectionManager()