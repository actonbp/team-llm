"""
Session model for team interactions
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Session(Base):
    """Session model representing a single team interaction"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    condition_id = Column(String, ForeignKey("conditions.id"), nullable=False)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.WAITING, nullable=False)
    
    # Session configuration
    team_size = Column(Integer, nullable=False)
    required_humans = Column(Integer, nullable=False)
    session_config = Column(JSON)  # Runtime configuration
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Completion data
    completion_code = Column(String, unique=True)
    final_outcome = Column(JSON)  # Task outcome data
    
    # Relationships
    condition = relationship("Condition", back_populates="sessions")
    participants = relationship("Participant", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.timestamp")
    
    def __repr__(self):
        return f"<Session {self.id} - Status: {self.status}>"