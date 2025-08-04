# Filename: registry.py
# Location: backend/agents/registry.py

from typing import Dict, List, Optional, Tuple
from .base import BaseAgent
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing and routing to different agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.fallback_agent: Optional[BaseAgent] = None
    
    def register_agent(self, agent: BaseAgent, is_fallback: bool = False):
        """Register an agent in the registry"""
        self.agents[agent.config.name] = agent
        
        if is_fallback:
            self.fallback_agent = agent
        
        logger.info(f"Registered agent: {agent.config.name} (fallback: {is_fallback})")
    
    def find_best_agent(self, message: str) -> Tuple[BaseAgent, float]:
        """Find the best agent to handle a message"""
        best_agent = None
        best_score = 0.0
        
        # Check all agents for capability match
        for agent in self.agents.values():
            score = agent.can_handle(message)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        # Use fallback if no good match found
        if best_score < 0.3 and self.fallback_agent:
            return self.fallback_agent, 0.5
        
        # Return best match or fallback
        return best_agent or self.fallback_agent, best_score
    
    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [agent.get_info() for agent in self.agents.values()]
    
    def get_capabilities_summary(self) -> Dict[str, List[str]]:
        """Get summary of all agent capabilities"""
        summary = {}
        for agent in self.agents.values():
            capabilities = []
            for cap in agent.get_capabilities():
                capabilities.extend(cap.keywords)
            summary[agent.config.name] = capabilities
        return summary


# Global registry instance
agent_registry = AgentRegistry()
