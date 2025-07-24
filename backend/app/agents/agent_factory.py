"""
Agent Factory for creating AI agents based on configuration
"""
from typing import Dict, Any
from app.agents.base import Agent
from app.agents.openai_agent import OpenAIAgent
from app.agents.anthropic_agent import AnthropicAgent


class AgentFactory:
    """Factory for creating agents based on model provider"""
    
    @staticmethod
    def create_agent(
        name: str,
        model: str,
        persona: str,
        knowledge: Dict[str, Any],
        strategy: str = None,
        config: Dict[str, Any] = None
    ) -> Agent:
        """Create an agent based on the model identifier"""
        
        # Parse model identifier (format: provider/model-name)
        if "/" in model:
            provider, model_name = model.split("/", 1)
        else:
            # Default to OpenAI if no provider specified
            provider = "openai"
            model_name = model
        
        provider = provider.lower()
        
        # Create appropriate agent based on provider
        if provider == "openai":
            return OpenAIAgent(
                name=name,
                model=model,
                persona=persona,
                knowledge=knowledge,
                strategy=strategy,
                config=config
            )
        elif provider == "anthropic":
            return AnthropicAgent(
                name=name,
                model=model,
                persona=persona,
                knowledge=knowledge,
                strategy=strategy,
                config=config
            )
        else:
            raise ValueError(f"Unknown model provider: {provider}")
    
    @staticmethod
    def create_agents_from_config(experiment_config: Dict[str, Any]) -> Dict[str, Agent]:
        """Create all AI agents from an experiment configuration"""
        agents = {}
        
        for role in experiment_config.get("roles", []):
            if role["type"] == "AI":
                agent = AgentFactory.create_agent(
                    name=role["name"],
                    model=role["model"],
                    persona=role["persona"],
                    knowledge=role.get("knowledge", {}),
                    strategy=role.get("strategy"),
                    config=role.get("config", {})
                )
                agents[role["name"]] = agent
        
        return agents