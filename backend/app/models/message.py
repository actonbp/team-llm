"""
Message model for chat communications
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Message(Base):
    """Message model for chat communications"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    participant_id = Column(String, ForeignKey("participants.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, default="chat")  # chat, system, notification
    
    # Metadata
    sequence_number = Column(Integer, nullable=False)  # Order within session
    metadata = Column(JSON)  # Additional data (e.g., AI generation params)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    participant = relationship("Participant", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} from {self.participant_id} at {self.timestamp}>"