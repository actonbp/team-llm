"""
Pydantic schemas for Session-related operations
"""
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class SessionStatus(str, Enum):
    """Session status enumeration"""
    WAITING = "WAITING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


class SessionBase(BaseModel):
    """Base schema for sessions"""
    team_size: int = Field(..., ge=2, le=10, description="Required team size")
    required_humans: int = Field(..., ge=0, description="Number of human participants required")
    session_config: Dict[str, Any] = Field(default_factory=dict, description="Runtime configuration")


class SessionCreate(SessionBase):
    """Schema for creating a session"""
    condition_id: UUID = Field(..., description="Condition ID for this session")
    
    @validator('required_humans')
    def validate_humans(cls, v, values):
        """Ensure required_humans doesn't exceed team_size"""
        if 'team_size' in values and v > values['team_size']:
            raise ValueError("required_humans cannot exceed team_size")
        return v


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    status: Optional[SessionStatus] = None
    final_outcome: Optional[Dict[str, Any]] = None


class SessionResponse(SessionBase):
    """Schema for session responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    condition_id: UUID
    status: SessionStatus
    completion_code: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    final_outcome: Optional[Dict[str, Any]]
    
    # Computed fields
    participants_count: int = 0
    messages_count: int = 0


class SessionListResponse(BaseModel):
    """Schema for listing sessions"""
    sessions: List[SessionResponse]
    total: int
    page: int = 1
    page_size: int = 20


class SessionJoinRequest(BaseModel):
    """Schema for joining a session"""
    access_code: str = Field(..., description="Condition access code")
    participant_name: str = Field(..., min_length=1, max_length=50, description="Display name")
    external_id: Optional[str] = Field(None, description="External ID (e.g., Prolific ID)")
    avatar: Optional[str] = Field(None, description="Avatar selection")


class SessionJoinResponse(BaseModel):
    """Schema for session join response"""
    session_id: UUID
    participant_id: UUID
    participant_name: str
    team_size: int
    current_participants: int
    session_status: SessionStatus
    ws_url: str = Field(..., description="WebSocket URL for real-time communication")


class SessionLeaveRequest(BaseModel):
    """Schema for leaving a session"""
    participant_id: UUID
    reason: Optional[str] = Field(None, description="Reason for leaving")


class SessionCompleteRequest(BaseModel):
    """Schema for completing a session"""
    trigger_type: str = Field(..., description="What triggered completion")
    trigger_value: Optional[str] = Field(None, description="Associated value")
    final_outcome: Optional[Dict[str, Any]] = Field(None, description="Task outcome data")


class SessionStatsResponse(BaseModel):
    """Schema for session statistics"""
    total_sessions: int
    active_sessions: int
    waiting_sessions: int
    completed_sessions: int
    average_duration_minutes: Optional[float]
    average_team_size: Optional[float]
    sessions_by_condition: Dict[str, int]