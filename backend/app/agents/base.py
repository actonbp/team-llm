"""
Base Agent class for AI team members
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class AgentResponse(BaseModel):
    """Response from an AI agent"""
    content: str
    should_respond: bool = True
    metadata: Dict[str, Any] = {}
    
    
class ConversationMessage(BaseModel):
    """A message in the conversation history"""
    participant_name: str
    participant_type: str
    content: str
    timestamp: datetime


class Agent(ABC):
    """Abstract base class for AI agents"""
    
    def __init__(
        self,
        name: str,
        model: str,
        persona: str,
        knowledge: Dict[str, Any],
        strategy: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.model = model
        self.persona = persona
        self.knowledge = knowledge
        self.strategy = strategy
        self.config = config or {}
        
    @abstractmethod
    async def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        task_instructions: str,
        last_message: Optional[ConversationMessage] = None
    ) -> AgentResponse:
        """Generate a response based on conversation history"""
        pass
    
    @abstractmethod
    async def should_participate(
        self,
        conversation_history: List[ConversationMessage],
        last_message: Optional[ConversationMessage] = None
    ) -> bool:
        """Decide if the agent should respond to the current message"""
        pass
    
    def format_knowledge(self) -> str:
        """Format agent's knowledge into a readable string"""
        lines = []
        for location, facts in self.knowledge.items():
            lines.append(f"\n{location}:")
            for criterion, value in facts.items():
                lines.append(f"  - {criterion}: {value}")
        return "\n".join(lines)
    
    def build_system_prompt(self, task_instructions: str) -> str:
        """Build the system prompt for the agent"""
        prompt_parts = [
            # Base persona
            self.persona,
            
            # Task context
            "\nTASK INSTRUCTIONS:",
            task_instructions,
            
            # Agent's unique knowledge
            "\nYOUR UNIQUE INFORMATION:",
            self.format_knowledge(),
            
            # Strategy hints
            f"\nSTRATEGY: {self.strategy}" if self.strategy else "",
            
            # General behavior rules
            "\nIMPORTANT RULES:",
            "- Keep messages under 250 characters",
            "- Respond naturally and conversationally",
            "- Share your unique information when relevant",
            "- Help the team work toward completing the task",
            "- Say 'task-complete' only when the team has agreed on a final ranking"
        ]
        
        return "\n".join(filter(None, prompt_parts))