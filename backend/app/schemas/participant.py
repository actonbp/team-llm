"""
Pydantic schemas for Participant-related operations
"""
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ParticipantType(str, Enum):
    """Participant type enumeration"""
    HUMAN = "HUMAN"
    AI = "AI"


class ConsentStatus(str, Enum):
    """Consent status enumeration"""
    PENDING = "pending"
    CONSENTED = "consented"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"
    RECONSENTED = "reconsented"


class ParticipantBase(BaseModel):
    """Base schema for participants"""
    name: str = Field(..., min_length=1, max_length=50, description="Display name")
    type: ParticipantType = Field(default=ParticipantType.HUMAN)
    external_id: Optional[str] = Field(None, description="External ID (e.g., Prolific ID)")
    avatar: Optional[str] = Field(None, description="Avatar selection")
    badge: Optional[str] = Field(None, description="Public condition badge")


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant"""
    session_id: UUID
    ai_model: Optional[str] = Field(None, description="AI model name (for AI participants)")
    ai_config: Optional[Dict[str, Any]] = Field(None, description="AI configuration")
    
    @validator('ai_model')
    def validate_ai_fields(cls, v, values):
        """Ensure AI fields are provided for AI participants"""
        if values.get('type') == ParticipantType.AI and not v:
            raise ValueError("ai_model is required for AI participants")
        return v


class ParticipantUpdate(BaseModel):
    """Schema for updating a participant"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar: Optional[str] = None
    badge: Optional[str] = None
    consent_status: Optional[ConsentStatus] = None


class ParticipantResponse(ParticipantBase):
    """Schema for participant responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    session_id: UUID
    ai_model: Optional[str]
    consent_status: ConsentStatus
    is_withdrawn: bool
    joined_at: datetime
    left_at: Optional[datetime]
    
    # Computed fields
    messages_count: int = 0
    active_duration_minutes: Optional[float] = None


class ParticipantListResponse(BaseModel):
    """Schema for listing participants"""
    participants: List[ParticipantResponse]
    total: int
    humans_count: int = 0
    ai_count: int = 0


class ConsentRequest(BaseModel):
    """Schema for consent submission"""
    consent_given: bool = Field(..., description="Whether consent was given")
    consent_form_version: str = Field(..., description="Version of the consent form")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Any additional consent data")


class ConsentResponse(BaseModel):
    """Schema for consent response"""
    participant_id: UUID
    consent_status: ConsentStatus
    timestamp: datetime
    next_step: str = Field(..., description="What the participant should do next")


class DataWithdrawalRequest(BaseModel):
    """Schema for data withdrawal request"""
    reason: Optional[str] = Field(None, description="Reason for withdrawal")
    confirm_understanding: bool = Field(..., description="Confirms understanding of withdrawal implications")


class DataWithdrawalResponse(BaseModel):
    """Schema for data withdrawal response"""
    participant_id: UUID
    withdrawal_confirmed: bool
    data_deleted: bool
    timestamp: datetime
    message: str


class ParticipantStatsResponse(BaseModel):
    """Schema for participant statistics"""
    participant_id: UUID
    session_duration_minutes: Optional[float]
    messages_sent: int
    consent_events: List[Dict[str, Any]]
    joined_at: datetime
    left_at: Optional[datetime]


class BulkParticipantCreate(BaseModel):
    """Schema for creating multiple AI participants"""
    session_id: UUID
    ai_participants: List[Dict[str, Any]] = Field(..., description="List of AI participant configurations")
    
    @validator('ai_participants')
    def validate_ai_configs(cls, v):
        """Ensure all AI participant configs have required fields"""
        for config in v:
            if 'name' not in config:
                raise ValueError("Each AI participant must have a name")
            if 'model' not in config:
                raise ValueError("Each AI participant must have a model")
        return v