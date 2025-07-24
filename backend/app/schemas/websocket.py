"""
WebSocket message schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message schema"""
    type: str = "chat"
    content: str
    metadata: Optional[Dict[str, Any]] = None


class WebSocketMessage(BaseModel):
    """Generic WebSocket message schema"""
    type: str
    data: Dict[str, Any]


class TypingIndicator(BaseModel):
    """Typing indicator schema"""
    type: str = "typing"
    is_typing: bool


class TaskCompleteSignal(BaseModel):
    """Task completion signal schema"""
    type: str = "task_complete"
    outcome: Optional[Dict[str, Any]] = None