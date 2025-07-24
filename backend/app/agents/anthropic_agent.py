"""
Anthropic Agent implementation
"""
from typing import List, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from app.agents.base import Agent, AgentResponse, ConversationMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class AnthropicAgent(Agent):
    """Agent powered by Anthropic's Claude models"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize Anthropic client when API is available
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        task_instructions: str,
        last_message: Optional[ConversationMessage] = None
    ) -> AgentResponse:
        """Generate a response using Anthropic API"""
        
        # TODO: Implement Anthropic API integration
        # For now, return a placeholder response
        return AgentResponse(
            content="I'm an Anthropic agent (coming soon!)",
            should_respond=True,
            metadata={"model": self.model}
        )
    
    async def should_participate(
        self,
        conversation_history: List[ConversationMessage],
        last_message: Optional[ConversationMessage] = None
    ) -> bool:
        """Decide if the agent should respond"""
        
        # Use same logic as OpenAI agent for now
        if not last_message:
            return False
            
        if self.name.lower() in last_message.content.lower():
            return True
            
        import random
        return random.random() < 0.3