"""
Session management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.session import Session, SessionStatus
from app.models.participant import Participant, ParticipantType
from app.models.experiment import Condition, Experiment
from app.models.message import Message
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionListResponse,
    SessionJoinRequest,
    SessionJoinResponse,
    SessionLeaveRequest,
    SessionCompleteRequest,
    SessionStatsResponse
)
from app.core.websocket_manager import manager
from typing import List, Optional
from uuid import UUID
import secrets
import logging
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[SessionStatus] = None,
    condition_id: Optional[UUID] = None,
    include_stats: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all sessions with pagination and filtering"""
    query = select(Session)
    
    # Apply filters
    if status:
        query = query.where(Session.status == status)
    if condition_id:
        query = query.where(Session.condition_id == condition_id)
    
    # Get total count
    count_query = select(func.count()).select_from(Session)
    if status:
        count_query = count_query.where(Session.status == status)
    if condition_id:
        count_query = count_query.where(Session.condition_id == condition_id)
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Session.created_at.desc())
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Add participant and message counts if requested
    if include_stats:
        for session in sessions:
            participants_count = await db.scalar(
                select(func.count()).select_from(Participant).where(Participant.session_id == session.id)
            )
            messages_count = await db.scalar(
                select(func.count()).select_from(Message).where(Message.session_id == session.id)
            )
            session.participants_count = participants_count
            session.messages_count = messages_count
    
    return SessionListResponse(
        sessions=sessions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new session for a condition"""
    # Verify condition exists
    condition = await db.get(Condition, session_data.condition_id)
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found"
        )
    
    # Create session
    completion_code = secrets.token_urlsafe(12)
    db_session = Session(
        condition_id=session_data.condition_id,
        team_size=session_data.team_size,
        required_humans=session_data.required_humans,
        session_config=session_data.session_config,
        status=SessionStatus.WAITING,
        completion_code=completion_code
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    return db_session


@router.post("/join", response_model=SessionJoinResponse)
async def join_session(
    join_request: SessionJoinRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Join an available session using access code"""
    # Find condition by access code
    condition_query = select(Condition).where(Condition.access_code == join_request.access_code)
    condition_result = await db.execute(condition_query)
    condition = condition_result.scalar_one_or_none()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid access code"
        )
    
    # Find or create a suitable session
    session_query = select(Session).where(
        and_(
            Session.condition_id == condition.id,
            Session.status == SessionStatus.WAITING
        )
    ).options(selectinload(Session.participants))
    
    session_result = await db.execute(session_query)
    available_sessions = session_result.scalars().all()
    
    # Find a session with space
    db_session = None
    for session in available_sessions:
        current_participants = len([p for p in session.participants if not p.left_at])
        if current_participants < session.team_size:
            db_session = session
            break
    
    # Create new session if none available
    if not db_session:
        # Get experiment config to determine team size
        experiment = await db.get(Experiment, condition.experiment_id)
        roles = experiment.config.get("roles", [])
        team_size = len(roles)
        required_humans = sum(1 for r in roles if r.get("type") == "HUMAN")
        
        db_session = Session(
            condition_id=condition.id,
            team_size=team_size,
            required_humans=required_humans,
            session_config={},
            status=SessionStatus.WAITING,
            completion_code=secrets.token_urlsafe(12)
        )
        db.add(db_session)
        await db.flush()
    
    # Create participant
    db_participant = Participant(
        session_id=db_session.id,
        type=ParticipantType.HUMAN,
        name=join_request.participant_name,
        external_id=join_request.external_id,
        avatar=join_request.avatar,
        consent_status="pending",
        joined_at=datetime.utcnow()
    )
    db.add(db_participant)
    await db.commit()
    await db.refresh(db_participant)
    
    # Check if session should start
    await db.refresh(db_session)
    current_participants = await db.scalar(
        select(func.count()).select_from(Participant).where(
            and_(
                Participant.session_id == db_session.id,
                Participant.left_at.is_(None)
            )
        )
    )
    
    # Start session if we have enough participants
    if current_participants >= db_session.required_humans and db_session.status == SessionStatus.WAITING:
        db_session.status = SessionStatus.ACTIVE
        db_session.started_at = datetime.utcnow()
        
        # TODO: Initialize AI participants based on experiment config
        
        await db.commit()
    
    # Build WebSocket URL
    ws_scheme = "wss" if request.url.scheme == "https" else "ws"
    ws_url = f"{ws_scheme}://{request.headers['host']}/ws/session/{db_session.id}"
    
    return SessionJoinResponse(
        session_id=db_session.id,
        participant_id=db_participant.id,
        participant_name=db_participant.name,
        team_size=db_session.team_size,
        current_participants=current_participants,
        session_status=db_session.status,
        ws_url=ws_url
    )


@router.post("/{session_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_session(
    session_id: UUID,
    leave_request: SessionLeaveRequest,
    db: AsyncSession = Depends(get_db)
):
    """Leave a session"""
    # Verify session and participant
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    participant = await db.get(Participant, leave_request.participant_id)
    if not participant or participant.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found in this session"
        )
    
    # Mark participant as left
    participant.left_at = datetime.utcnow()
    
    # Check if session should be cancelled (no humans left)
    remaining_humans = await db.scalar(
        select(func.count()).select_from(Participant).where(
            and_(
                Participant.session_id == session_id,
                Participant.type == ParticipantType.HUMAN,
                Participant.left_at.is_(None)
            )
        )
    )
    
    if remaining_humans == 0 and session.status in [SessionStatus.WAITING, SessionStatus.ACTIVE]:
        session.status = SessionStatus.CANCELLED
        session.completed_at = datetime.utcnow()
    
    await db.commit()
    
    # Notify other participants via WebSocket
    await manager.broadcast_to_session(
        session_id,
        {
            "type": "participant_left",
            "participant_id": str(leave_request.participant_id),
            "participant_name": participant.name,
            "reason": leave_request.reason
        }
    )


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: UUID,
    complete_request: SessionCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Mark a session as completed"""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active sessions can be completed"
        )
    
    # Update session
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.utcnow()
    session.final_outcome = complete_request.final_outcome or {}
    
    await db.commit()
    await db.refresh(session)
    
    # Notify all participants
    await manager.broadcast_to_session(
        session_id,
        {
            "type": "session_completed",
            "completion_code": session.completion_code,
            "trigger_type": complete_request.trigger_type,
            "trigger_value": complete_request.trigger_value
        }
    )
    
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    include_stats: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get session details"""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if include_stats:
        participants_count = await db.scalar(
            select(func.count()).select_from(Participant).where(Participant.session_id == session_id)
        )
        messages_count = await db.scalar(
            select(func.count()).select_from(Message).where(Message.session_id == session_id)
        )
        session.participants_count = participants_count
        session.messages_count = messages_count
    
    return session


@router.get("/stats/summary", response_model=SessionStatsResponse)
async def get_session_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregate session statistics"""
    # Base query
    base_query = select(Session)
    if start_date:
        base_query = base_query.where(Session.created_at >= start_date)
    if end_date:
        base_query = base_query.where(Session.created_at <= end_date)
    
    # Get counts by status
    total_sessions = await db.scalar(select(func.count()).select_from(Session))
    active_sessions = await db.scalar(
        select(func.count()).select_from(Session).where(Session.status == SessionStatus.ACTIVE)
    )
    waiting_sessions = await db.scalar(
        select(func.count()).select_from(Session).where(Session.status == SessionStatus.WAITING)
    )
    completed_sessions = await db.scalar(
        select(func.count()).select_from(Session).where(Session.status == SessionStatus.COMPLETED)
    )
    
    # Calculate average duration for completed sessions
    duration_result = await db.execute(
        select(func.avg(
            func.extract('epoch', Session.completed_at - Session.started_at) / 60
        )).where(
            and_(
                Session.status == SessionStatus.COMPLETED,
                Session.started_at.is_not(None),
                Session.completed_at.is_not(None)
            )
        )
    )
    avg_duration = duration_result.scalar()
    
    # Average team size
    avg_team_size = await db.scalar(select(func.avg(Session.team_size)))
    
    # Sessions by condition
    condition_stats = await db.execute(
        select(
            Condition.name,
            func.count(Session.id)
        ).select_from(Session).join(Condition).group_by(Condition.name)
    )
    sessions_by_condition = {name: count for name, count in condition_stats}
    
    return SessionStatsResponse(
        total_sessions=total_sessions or 0,
        active_sessions=active_sessions or 0,
        waiting_sessions=waiting_sessions or 0,
        completed_sessions=completed_sessions or 0,
        average_duration_minutes=avg_duration,
        average_team_size=avg_team_size,
        sessions_by_condition=sessions_by_condition
    )


@router.post("/{session_id}/timeout", status_code=status.HTTP_204_NO_CONTENT)
async def timeout_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Mark a session as timed out (system use)"""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.status in [SessionStatus.WAITING, SessionStatus.ACTIVE]:
        session.status = SessionStatus.TIMEOUT
        session.completed_at = datetime.utcnow()
        await db.commit()
        
        # Notify participants
        await manager.broadcast_to_session(
            session_id,
            {"type": "session_timeout", "message": "Session has timed out"}
        )