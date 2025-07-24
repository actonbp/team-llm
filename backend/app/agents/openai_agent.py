"""
OpenAI Agent implementation
"""
import openai
from typing import List, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from app.agents.base import Agent, AgentResponse, ConversationMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIAgent(Agent):
    """Agent powered by OpenAI models"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        openai.api_key = settings.OPENAI_API_KEY
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        task_instructions: str,
        last_message: Optional[ConversationMessage] = None
    ) -> AgentResponse:
        """Generate a response using OpenAI API"""
        
        # Build messages for the API
        messages = [
            {"role": "system", "content": self.build_system_prompt(task_instructions)}
        ]
        
        # Add conversation history
        for msg in conversation_history[-20:]:  # Last 20 messages for context
            role = "assistant" if msg.participant_name == self.name else "user"
            messages.append({
                "role": role,
                "content": f"{msg.participant_name}: {msg.content}"
            })
        
        try:
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model.split("/")[-1],  # Extract model name from identifier
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Sometimes add typos for realism
            import random
            if random.random() < 0.1:  # 10% chance
                content = self._add_typo(content)
            
            return AgentResponse(
                content=content,
                should_respond=True,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return AgentResponse(
                content="Sorry, I'm having trouble responding right now.",
                should_respond=True,
                metadata={"error": str(e)}
            )
    
    async def should_participate(
        self,
        conversation_history: List[ConversationMessage],
        last_message: Optional[ConversationMessage] = None
    ) -> bool:
        """Decide if the agent should respond"""
        
        if not last_message:
            return False
            
        # Always respond if directly mentioned
        if self.name.lower() in last_message.content.lower():
            return True
        
        # Check if the message relates to our knowledge
        message_lower = last_message.content.lower()
        for location in self.knowledge:
            if location.lower() in message_lower:
                for criterion in self.knowledge[location]:
                    if criterion.lower() in message_lower:
                        return True
        
        # Use a simple heuristic for now
        # In a more sophisticated version, we could use GPT to decide
        recent_responses = [
            msg for msg in conversation_history[-5:]
            if msg.participant_name == self.name
        ]
        
        # Don't respond too frequently
        if len(recent_responses) >= 2:
            return False
            
        # Random chance to participate
        import random
        return random.random() < 0.3
    
    def _add_typo(self, text: str) -> str:
        """Add a realistic typo to text"""
        import random
        
        typos = [
            # Missing last letter
            lambda s: s[:-1] if len(s) > 3 else s,
            # Double letter
            lambda s: s[:len(s)//2] + s[len(s)//2] + s[len(s)//2:] if len(s) > 2 else s,
            # Swap adjacent letters
            lambda s: s[:len(s)//2-1] + s[len(s)//2] + s[len(s)//2-1] + s[len(s)//2+1:] if len(s) > 3 else s,
        ]
        
        words = text.split()
        if words:
            # Pick a random word to typo
            word_idx = random.randint(0, len(words) - 1)
            if len(words[word_idx]) > 2:
                words[word_idx] = random.choice(typos)(words[word_idx])
        
        return " ".join(words)