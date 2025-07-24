"""
WebSocket endpoints for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.websocket_manager import manager
from app.models import Session, Participant, Message
from app.schemas.websocket import ChatMessage, WebSocketMessage
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    participant_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for chat communication"""
    try:
        # Verify session and participant
        session = await db.get(Session, session_id)
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        participant = await db.get(Participant, participant_id)
        if not participant or participant.session_id != session_id:
            await websocket.close(code=4004, reason="Invalid participant")
            return
        
        # Connect to session
        await manager.connect(websocket, session_id, participant_id, participant.name)
        
        # Send session info to newly connected participant
        await manager.send_personal_message(
            {
                "type": "session_info",
                "session_id": session_id,
                "participants": manager.get_session_participants(session_id),
                "status": session.status
            },
            websocket
        )
        
        # Handle messages
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type", "chat")
            
            if message_type == "chat":
                # Create message in database
                message = Message(
                    session_id=session_id,
                    participant_id=participant_id,
                    content=data.get("content", ""),
                    sequence_number=len(session.messages) + 1,
                    metadata=data.get("metadata", {})
                )
                db.add(message)
                await db.commit()
                
                # Broadcast to all participants in session
                await manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "chat",
                        "message_id": message.id,
                        "participant_id": participant_id,
                        "participant_name": participant.name,
                        "participant_type": participant.type.value,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                        "sequence_number": message.sequence_number
                    }
                )
                
                # Trigger AI responses if needed
                # TODO: Implement AI agent response logic
                
            elif message_type == "typing":
                # Broadcast typing indicator
                await manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "typing",
                        "participant_id": participant_id,
                        "participant_name": participant.name,
                        "is_typing": data.get("is_typing", False)
                    },
                    exclude=websocket
                )
            
            elif message_type == "task_complete":
                # Handle task completion signal
                await manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "task_complete",
                        "participant_id": participant_id,
                        "participant_name": participant.name
                    }
                )
                # TODO: Update session status and handle completion logic
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
        await websocket.close(code=4000, reason="Internal error")