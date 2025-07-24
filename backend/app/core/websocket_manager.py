"""
WebSocket connection manager for real-time communication
"""
from typing import Dict, Set
from fastapi import WebSocket
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
            
            # Remove participant info
            del self._participant_info[websocket]
            
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


# Global connection manager instance
manager = ConnectionManager()