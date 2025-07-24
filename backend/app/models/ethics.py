"""
Ethics log model for tracking consent and ethical events
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum


class EthicsEventType(str, enum.Enum):
    """Types of ethics-related events"""
    CONSENT_FORM_VIEWED = "consent_form_viewed"
    CONSENT_GIVEN = "consent_given"
    CONSENT_DECLINED = "consent_declined"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    DEBRIEF_VIEWED = "debrief_viewed"
    DEBRIEF_ACKNOWLEDGED = "debrief_acknowledged"
    RECONSENT_REQUESTED = "reconsent_requested"
    RECONSENT_GIVEN = "reconsent_given"
    DATA_WITHDRAWAL_REQUESTED = "data_withdrawal_requested"
    DATA_WITHDRAWN = "data_withdrawn"


class EthicsLog(Base):
    """Ethics log for tracking participant consent and ethical events"""
    __tablename__ = "ethics_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    participant_id = Column(String, ForeignKey("participants.id"), nullable=False)
    event_type = Column(SQLEnum(EthicsEventType), nullable=False)
    
    # Event details
    details = Column(JSON)  # Additional event-specific data
    ip_address = Column(String)  # For audit trail
    user_agent = Column(String)  # Browser/client info
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    participant = relationship("Participant", back_populates="ethics_logs")
    
    def __repr__(self):
        return f"<EthicsLog {self.event_type} for Participant {self.participant_id} at {self.timestamp}>"