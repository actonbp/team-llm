"""
Experiment and Condition models
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Experiment(Base):
    """Experiment model representing a research study"""
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    config = Column(JSON, nullable=False)  # Full experiment configuration
    version = Column(Integer, default=1)
    created_by = Column(String)  # Researcher ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conditions = relationship("Condition", back_populates="experiment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Experiment {self.name}>"


class Condition(Base):
    """Experimental condition within an experiment"""
    __tablename__ = "conditions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, ForeignKey("experiments.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    parameters = Column(JSON, nullable=False)  # Condition-specific parameters
    access_code = Column(String, unique=True, index=True)  # For participant access
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    experiment = relationship("Experiment", back_populates="conditions")
    sessions = relationship("Session", back_populates="condition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Condition {self.name} for Experiment {self.experiment_id}>"