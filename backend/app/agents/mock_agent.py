"""
Mock Agent implementation for testing without API keys
"""
import random
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.agents.base import Agent, AgentResponse, ConversationMessage


class MockAgent(Agent):
    """Mock agent for testing that simulates AI behavior"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_templates = [
            "I think {option} is a good choice because {reason}",
            "Based on {criterion}, I'd suggest {option}",
            "Have we considered {option}? It has {benefit}",
            "I agree with {participant} about {topic}",
            "{option} seems like the best option for {criterion}",
            "My information shows that {option} has {attribute}",
            "Let's go with {option}, it fits our needs",
            "What about {option}? It could work well",
            "I'd rank {option} highly for {reason}",
        ]
        
    async def generate_response(
        self,
        conversation_history: List[ConversationMessage],
        task_instructions: str,
        last_message: Optional[ConversationMessage] = None
    ) -> AgentResponse:
        """Generate a mock response based on agent's knowledge"""
        
        # Simulate thinking time
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Check if we should complete the task
        if len(conversation_history) > 15 and random.random() < 0.2:
            return AgentResponse(
                content="I think we've reached a consensus. task-complete",
                should_respond=True,
                metadata={"mock": True}
            )
        
        # Generate response based on knowledge
        response = self._generate_contextual_response(conversation_history)
        
        # Add occasional typos for realism
        if random.random() < 0.1:
            response = self._add_typo(response)
            
        return AgentResponse(
            content=response,
            should_respond=True,
            metadata={
                "mock": True,
                "model": "mock",
                "thinking_time": random.uniform(0.5, 2.0)
            }
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
        
        # Check if message relates to our knowledge
        message_lower = last_message.content.lower()
        for location in self.knowledge:
            if location.lower() in message_lower:
                return random.random() < 0.7  # 70% chance to respond
        
        # Check recent participation
        recent_responses = [
            msg for msg in conversation_history[-5:]
            if msg.participant_name == self.name
        ]
        
        # Don't dominate conversation
        if len(recent_responses) >= 2:
            return False
            
        # Random chance to participate
        return random.random() < 0.3
    
    def _generate_contextual_response(self, history: List[ConversationMessage]) -> str:
        """Generate a response based on agent's knowledge and conversation context"""
        
        # Pick a random piece of knowledge
        if self.knowledge:
            location = random.choice(list(self.knowledge.keys()))
            criteria = self.knowledge[location]
            if criteria:
                criterion = random.choice(list(criteria.keys()))
                value = criteria[criterion]
                
                # Pick a template and fill it
                template = random.choice(self.response_templates)
                
                # Get a participant name from history if available
                other_participants = [
                    msg.participant_name for msg in history[-5:]
                    if msg.participant_name != self.name
                ]
                participant = random.choice(other_participants) if other_participants else "everyone"
                
                # Fill in the template
                response = template.format(
                    option=location,
                    reason=f"{criterion} is {value}",
                    criterion=criterion,
                    benefit=f"{criterion}: {value}",
                    participant=participant,
                    topic=location,
                    attribute=f"{criterion}: {value}"
                )
                
                return response[:250]  # Keep under character limit
        
        # Fallback responses
        fallbacks = [
            "That's an interesting point to consider.",
            "I see what you mean. Let me think about that.",
            "Good observation! What do others think?",
            "That could work. Any other suggestions?",
            "I'm learning a lot from this discussion.",
        ]
        
        return random.choice(fallbacks)
    
    def _add_typo(self, text: str) -> str:
        """Add a realistic typo to text"""
        words = text.split()
        if not words:
            return text
            
        # Pick a random word
        word_idx = random.randint(0, len(words) - 1)
        word = words[word_idx]
        
        if len(word) > 3:
            typo_type = random.choice(['missing', 'double', 'swap'])
            
            if typo_type == 'missing':
                # Remove last letter
                words[word_idx] = word[:-1]
            elif typo_type == 'double':
                # Double a letter
                pos = random.randint(1, len(word) - 1)
                words[word_idx] = word[:pos] + word[pos] + word[pos:]
            elif typo_type == 'swap':
                # Swap adjacent letters
                if len(word) > 4:
                    pos = random.randint(1, len(word) - 2)
                    word_list = list(word)
                    word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
                    words[word_idx] = ''.join(word_list)
        
        return ' '.join(words)