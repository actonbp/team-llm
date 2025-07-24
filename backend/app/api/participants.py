"""
Participant management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.participant import Participant, ParticipantType, ConsentStatus
from app.models.session import Session, SessionStatus
from app.models.message import Message
from app.models.ethics import EthicsLog, EthicsEventType
from app.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    ParticipantListResponse,
    ConsentRequest,
    ConsentResponse,
    DataWithdrawalRequest,
    DataWithdrawalResponse,
    ParticipantStatsResponse,
    BulkParticipantCreate
)
from app.core.websocket_manager import manager
from app.agents.agent_factory import AgentFactory
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/session/{session_id}", response_model=ParticipantListResponse)
async def list_session_participants(
    session_id: UUID,
    include_left: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all participants in a session"""
    # Verify session exists
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Build query
    query = select(Participant).where(Participant.session_id == session_id)
    if not include_left:
        query = query.where(Participant.left_at.is_(None))
    
    result = await db.execute(query)
    participants = result.scalars().all()
    
    # Add message counts
    for participant in participants:
        messages_count = await db.scalar(
            select(func.count()).select_from(Message).where(Message.participant_id == participant.id)
        )
        participant.messages_count = messages_count
        
        # Calculate active duration
        if participant.joined_at:
            end_time = participant.left_at or datetime.utcnow()
            duration = (end_time - participant.joined_at).total_seconds() / 60
            participant.active_duration_minutes = round(duration, 2)
    
    # Count by type
    humans_count = sum(1 for p in participants if p.type == ParticipantType.HUMAN)
    ai_count = sum(1 for p in participants if p.type == ParticipantType.AI)
    
    return ParticipantListResponse(
        participants=participants,
        total=len(participants),
        humans_count=humans_count,
        ai_count=ai_count
    )


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    participant_data: ParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new participant (mainly for AI participants)"""
    # Verify session exists and is active
    session = await db.get(Session, participant_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.status not in [SessionStatus.WAITING, SessionStatus.ACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not accepting new participants"
        )
    
    # Create participant
    db_participant = Participant(
        session_id=participant_data.session_id,
        type=participant_data.type,
        name=participant_data.name,
        external_id=participant_data.external_id,
        ai_model=participant_data.ai_model,
        ai_config=participant_data.ai_config,
        avatar=participant_data.avatar,
        badge=participant_data.badge,
        consent_status=ConsentStatus.CONSENTED if participant_data.type == ParticipantType.AI else ConsentStatus.PENDING,
        joined_at=datetime.utcnow()
    )
    db.add(db_participant)
    await db.commit()
    await db.refresh(db_participant)
    
    # Notify other participants
    await manager.broadcast_to_session(
        participant_data.session_id,
        {
            "type": "participant_joined",
            "participant": {
                "id": str(db_participant.id),
                "name": db_participant.name,
                "type": db_participant.type.value,
                "avatar": db_participant.avatar
            }
        }
    )
    
    return db_participant


@router.post("/bulk", response_model=List[ParticipantResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_ai_participants(
    bulk_data: BulkParticipantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple AI participants for a session"""
    # Verify session
    session = await db.get(Session, bulk_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    created_participants = []
    for ai_config in bulk_data.ai_participants:
        db_participant = Participant(
            session_id=bulk_data.session_id,
            type=ParticipantType.AI,
            name=ai_config['name'],
            ai_model=ai_config['model'],
            ai_config=ai_config.get('config', {}),
            avatar=ai_config.get('avatar'),
            badge=ai_config.get('badge'),
            consent_status=ConsentStatus.CONSENTED,
            joined_at=datetime.utcnow()
        )
        db.add(db_participant)
        created_participants.append(db_participant)
    
    await db.commit()
    
    # Refresh all participants
    for participant in created_participants:
        await db.refresh(participant)
    
    # Notify about new AI participants
    await manager.broadcast_to_session(
        bulk_data.session_id,
        {
            "type": "ai_participants_added",
            "participants": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "avatar": p.avatar
                } for p in created_participants
            ]
        }
    )
    
    return created_participants


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(participant_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get participant details"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Add stats
    messages_count = await db.scalar(
        select(func.count()).select_from(Message).where(Message.participant_id == participant_id)
    )
    participant.messages_count = messages_count
    
    if participant.joined_at:
        end_time = participant.left_at or datetime.utcnow()
        duration = (end_time - participant.joined_at).total_seconds() / 60
        participant.active_duration_minutes = round(duration, 2)
    
    return participant


@router.put("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: UUID,
    update_data: ParticipantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update participant information"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(participant, field, value)
    
    await db.commit()
    await db.refresh(participant)
    
    return participant


@router.post("/{participant_id}/consent", response_model=ConsentResponse)
async def update_consent(
    participant_id: UUID,
    consent_data: ConsentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update participant consent status"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Update consent status
    if consent_data.consent_given:
        participant.consent_status = ConsentStatus.CONSENTED
        next_step = "proceed_to_session"
    else:
        participant.consent_status = ConsentStatus.DECLINED
        next_step = "exit_study"
    
    # Log ethics event
    ethics_log = EthicsLog(
        participant_id=participant_id,
        event_type=EthicsEventType.CONSENT_GIVEN if consent_data.consent_given else EthicsEventType.CONSENT_DECLINED,
        details={
            "consent_form_version": consent_data.consent_form_version,
            "additional_data": consent_data.additional_data
        },
        timestamp=datetime.utcnow()
    )
    db.add(ethics_log)
    
    await db.commit()
    await db.refresh(participant)
    
    return ConsentResponse(
        participant_id=participant_id,
        consent_status=participant.consent_status,
        timestamp=ethics_log.timestamp,
        next_step=next_step
    )


@router.post("/{participant_id}/withdraw", response_model=DataWithdrawalResponse)
async def withdraw_data(
    participant_id: UUID,
    withdrawal_data: DataWithdrawalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Withdraw participant data from the study"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    if not withdrawal_data.confirm_understanding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm understanding of withdrawal implications"
        )
    
    # Mark participant as withdrawn
    participant.is_withdrawn = True
    participant.consent_status = ConsentStatus.WITHDRAWN
    
    # Log ethics event
    ethics_log = EthicsLog(
        participant_id=participant_id,
        event_type=EthicsEventType.DATA_WITHDRAWN,
        details={
            "reason": withdrawal_data.reason,
            "previous_consent_status": participant.consent_status.value
        },
        timestamp=datetime.utcnow()
    )
    db.add(ethics_log)
    
    # In a real system, you might also:
    # - Anonymize or delete messages
    # - Remove from analytics
    # - Send confirmation email
    
    await db.commit()
    
    return DataWithdrawalResponse(
        participant_id=participant_id,
        withdrawal_confirmed=True,
        data_deleted=True,
        timestamp=ethics_log.timestamp,
        message="Your data has been withdrawn from the study. Thank you for your participation."
    )


@router.get("/{participant_id}/stats", response_model=ParticipantStatsResponse)
async def get_participant_stats(participant_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed statistics for a participant"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Calculate session duration
    session_duration = None
    if participant.joined_at:
        end_time = participant.left_at or datetime.utcnow()
        session_duration = (end_time - participant.joined_at).total_seconds() / 60
    
    # Count messages
    messages_sent = await db.scalar(
        select(func.count()).select_from(Message).where(Message.participant_id == participant_id)
    )
    
    # Get consent events
    consent_events_query = select(EthicsLog).where(
        EthicsLog.participant_id == participant_id
    ).order_by(EthicsLog.timestamp)
    
    consent_events_result = await db.execute(consent_events_query)
    consent_events = [
        {
            "event_type": log.event_type.value,
            "timestamp": log.timestamp.isoformat(),
            "details": log.details
        } for log in consent_events_result.scalars().all()
    ]
    
    return ParticipantStatsResponse(
        participant_id=participant_id,
        session_duration_minutes=round(session_duration, 2) if session_duration else None,
        messages_sent=messages_sent,
        consent_events=consent_events,
        joined_at=participant.joined_at,
        left_at=participant.left_at
    )


@router.post("/{participant_id}/reconsent", response_model=ConsentResponse)
async def reconsent_participant(
    participant_id: UUID,
    consent_data: ConsentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle post-debrief reconsent"""
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    # Verify participant completed the session
    session = await db.get(Session, participant.session_id)
    if session.status != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reconsent only available after session completion"
        )
    
    # Update consent status
    if consent_data.consent_given:
        participant.consent_status = ConsentStatus.RECONSENTED
        next_step = "thank_you"
    else:
        participant.consent_status = ConsentStatus.WITHDRAWN
        participant.is_withdrawn = True
        next_step = "data_withdrawal_confirmed"
    
    # Log ethics event
    ethics_log = EthicsLog(
        participant_id=participant_id,
        event_type=EthicsEventType.RECONSENT_GIVEN if consent_data.consent_given else EthicsEventType.RECONSENT_DECLINED,
        details={
            "consent_form_version": consent_data.consent_form_version,
            "post_debrief": True
        },
        timestamp=datetime.utcnow()
    )
    db.add(ethics_log)
    
    await db.commit()
    
    return ConsentResponse(
        participant_id=participant_id,
        consent_status=participant.consent_status,
        timestamp=ethics_log.timestamp,
        next_step=next_step
    )