"""
Participant model for humans and AI agents
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum


class ParticipantType(str, enum.Enum):
    """Participant type enumeration"""
    HUMAN = "human"
    AI = "ai"


class ConsentStatus(str, enum.Enum):
    """Consent status for participants"""
    NOT_STARTED = "not_started"
    INITIAL_CONSENT = "initial_consent"
    TASK_COMPLETED = "task_completed"
    DEBRIEFED = "debriefed"
    FINAL_CONSENT = "final_consent"
    WITHDRAWN = "withdrawn"


class Participant(Base):
    """Participant model for both humans and AI agents"""
    __tablename__ = "participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    type = Column(SQLEnum(ParticipantType), nullable=False)
    
    # Identification
    name = Column(String, nullable=False)  # Display name in chat
    external_id = Column(String)  # Prolific ID or other external identifier
    
    # For AI participants
    ai_model = Column(String)  # e.g., "openai/gpt-4"
    ai_config = Column(JSON)  # Persona, knowledge, etc.
    
    # For human participants
    avatar = Column(String)  # Avatar selection
    badge = Column(String)  # Public condition badge
    
    # Consent and ethics
    consent_status = Column(SQLEnum(ConsentStatus), default=ConsentStatus.NOT_STARTED)
    is_withdrawn = Column(Boolean, default=False)
    
    # Timing
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("Session", back_populates="participants")
    messages = relationship("Message", back_populates="participant", cascade="all, delete-orphan")
    ethics_logs = relationship("EthicsLog", back_populates="participant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Participant {self.name} ({self.type}) in Session {self.session_id}>"