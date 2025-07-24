"""
WebSocket endpoints for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.database import get_db
from app.core.websocket_manager import manager
from app.models.session import Session, SessionStatus
from app.models.participant import Participant, ParticipantType
from app.models.message import Message
from app.models.experiment import Experiment
from app.agents.agent_factory import AgentFactory
from app.schemas.websocket import ChatMessage, WebSocketMessage
import asyncio
import logging
import json
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/session/{session_id}")
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
        
        # Get message history
        messages_query = select(Message).where(
            Message.session_id == session.id
        ).order_by(Message.sequence_number)
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Get all participants
        participants_query = select(Participant).where(
            Participant.session_id == session.id
        )
        participants_result = await db.execute(participants_query)
        all_participants = participants_result.scalars().all()
        
        # Send session info and history to newly connected participant
        await manager.send_personal_message(
            {
                "type": "session_info",
                "session_id": str(session_id),
                "participants": [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "type": p.type.value,
                        "avatar": p.avatar,
                        "joined_at": p.joined_at.isoformat() if p.joined_at else None
                    } for p in all_participants
                ],
                "status": session.status.value,
                "message_history": [
                    {
                        "message_id": str(m.id),
                        "participant_id": str(m.participant_id),
                        "content": m.content,
                        "timestamp": m.timestamp.isoformat(),
                        "sequence_number": m.sequence_number
                    } for m in messages
                ]
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
                        "message_id": str(message.id),
                        "participant_id": str(participant_id),
                        "participant_name": participant.name,
                        "participant_type": participant.type.value,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                        "sequence_number": message.sequence_number
                    }
                )
                
                # Trigger AI responses if needed
                await trigger_ai_responses(session, message, db)
                
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
                await handle_task_completion(session, participant, db)
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
        await websocket.close(code=4000, reason="Internal error")


async def trigger_ai_responses(session: Session, human_message: Message, db: AsyncSession):
    """Trigger AI agent responses to a human message"""
    try:
        # Get AI participants in the session
        ai_participants_query = select(Participant).where(
            and_(
                Participant.session_id == session.id,
                Participant.type == ParticipantType.AI,
                Participant.left_at.is_(None)
            )
        )
        ai_participants_result = await db.execute(ai_participants_query)
        ai_participants = ai_participants_result.scalars().all()
        
        if not ai_participants:
            return
        
        # Get experiment configuration
        experiment = await db.get(Experiment, session.condition.experiment_id)
        if not experiment:
            return
        
        # Get recent message history for context
        recent_messages_query = select(Message).where(
            Message.session_id == session.id
        ).order_by(Message.sequence_number.desc()).limit(20)
        recent_messages_result = await db.execute(recent_messages_query)
        recent_messages = list(reversed(recent_messages_result.scalars().all()))
        
        # Process each AI participant
        for ai_participant in ai_participants:
            # Find AI configuration from experiment
            ai_config = None
            for role in experiment.config.get("roles", []):
                if role.get("name") == ai_participant.name and role.get("type") == "AI":
                    ai_config = role
                    break
            
            if not ai_config:
                continue
            
            # Create AI agent
            try:
                agent = AgentFactory.create_agent(
                    model=ai_config.get("model", ai_participant.ai_model),
                    persona=ai_config.get("persona", ""),
                    knowledge=ai_config.get("knowledge", {}),
                    strategy=ai_config.get("strategy", "")
                )
                
                # Generate response
                response = await agent.generate_response(
                    message_history=[{
                        "role": "human" if m.participant.type == ParticipantType.HUMAN else "assistant",
                        "content": m.content,
                        "name": m.participant.name
                    } for m in recent_messages],
                    scenario_context=experiment.config.get("scenario", {})
                )
                
                if response:
                    # Create AI message
                    ai_message = Message(
                        session_id=session.id,
                        participant_id=ai_participant.id,
                        content=response,
                        sequence_number=len(recent_messages) + 1,
                        metadata={"generated_by": "ai"}
                    )
                    db.add(ai_message)
                    await db.commit()
                    
                    # Broadcast AI message
                    await manager.broadcast_to_session(
                        str(session.id),
                        {
                            "type": "chat",
                            "message_id": str(ai_message.id),
                            "participant_id": str(ai_participant.id),
                            "participant_name": ai_participant.name,
                            "participant_type": "AI",
                            "content": response,
                            "timestamp": ai_message.timestamp.isoformat(),
                            "sequence_number": ai_message.sequence_number
                        }
                    )
                    
                    # Add small delay between AI responses
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error generating AI response for {ai_participant.name}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error in trigger_ai_responses: {e}")


async def handle_task_completion(session: Session, participant: Participant, db: AsyncSession):
    """Handle task completion signal"""
    try:
        # Update session status
        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        
        # Get experiment configuration
        experiment = await db.get(Experiment, session.condition.experiment_id)
        completion_trigger = experiment.config.get("scenario", {}).get("completionTrigger", {})
        
        # Create completion message
        completion_message = Message(
            session_id=session.id,
            participant_id=participant.id,
            content=completion_trigger.get("value", "task-complete"),
            message_type="system",
            metadata={
                "event": "task_completed",
                "triggered_by": str(participant.id)
            }
        )
        db.add(completion_message)
        
        await db.commit()
        
        # Broadcast completion to all participants
        await manager.broadcast_to_session(
            str(session.id),
            {
                "type": "session_completed",
                "completion_code": session.completion_code,
                "triggered_by": {
                    "participant_id": str(participant.id),
                    "participant_name": participant.name
                },
                "message": "The task has been completed. Thank you for participating!"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in handle_task_completion: {e}")