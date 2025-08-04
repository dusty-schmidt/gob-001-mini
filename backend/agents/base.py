# Filename: base.py
# Location: backend/agents/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.llms.base import BaseLLM
from langchain_openai import ChatOpenAI
from config.config_loader import config_loader
from .fallback_llm import FallbackLLM, fallback_manager
import logging

logger = logging.getLogger(__name__)


class LLMTier(Enum):
    """Different tiers of LLMs for different agent roles"""
    UTILITY = "utility"     # Fast utility tasks, routing, classification (gpt-3.5-turbo)
    CHAT = "chat"          # User-facing responses, balanced quality (gpt-4)
    PREMIUM = "premium"     # Best quality, complex reasoning (gpt-4-turbo)
    SPECIALIZED = "specialized"  # Domain-specific models


class AgentCapability(BaseModel):
    """Defines what an agent can do"""
    name: str
    description: str
    keywords: List[str]
    confidence_threshold: float = 0.7


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    description: str
    llm_tier: LLMTier
    system_prompt: str
    capabilities: List[AgentCapability]
    max_tokens: int = 1000
    temperature: float = 0.7


class BaseAgent(ABC):
    """Base class for all agents using LangChain"""

    def __init__(self, config: AgentConfig, api_key: str, agent_name: str = None, agent_type: str = "personas"):
        self.config = config
        self.agent_name = agent_name or config.name
        self.agent_type = agent_type
        self.api_key = api_key
        self.llm = self._create_llm(config.llm_tier, api_key)
        self.conversation_history: List[BaseMessage] = []

    def _create_llm(self, tier: LLMTier, api_key: str) -> FallbackLLM:
        """Create LLM with fallback capabilities"""
        # Log model usage if enabled
        system_config = config_loader.get_system_config()
        if system_config.log_model_usage:
            primary_config = config_loader.get_agent_config(self.agent_name, self.agent_type)
            logger.info(f"Creating LLM for {self.agent_name}: {primary_config.model.model_name}")

            if config_loader.is_fallback_enabled():
                fallback_config = config_loader.get_fallback_agent_config(self.agent_name, self.agent_type)
                logger.info(f"Fallback for {self.agent_name}: {fallback_config.model.model_name}")

        # Create fallback-aware LLM
        fallback_llm = FallbackLLM(self.agent_name, self.agent_type, api_key)

        # Register with fallback manager
        fallback_manager.register_agent(self.agent_name, fallback_llm)

        return fallback_llm
    
    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message and return response"""
        pass
    
    def can_handle(self, message: str) -> float:
        """Return confidence score (0-1) for handling this message"""
        message_lower = message.lower()
        total_score = 0.0

        for capability in self.config.capabilities:
            keyword_matches = sum(1 for keyword in capability.keywords
                                if keyword.lower() in message_lower)
            if keyword_matches > 0:
                # Give higher weight to matches - each match is worth more
                capability_score = min(keyword_matches * 0.3, 1.0)
                total_score += capability_score

        return min(total_score, 1.0)
    
    def add_to_history(self, human_msg: str, ai_msg: str):
        """Add interaction to conversation history"""
        self.conversation_history.extend([
            HumanMessage(content=human_msg),
            AIMessage(content=ai_msg)
        ])

        # Keep history manageable using configured limit
        system_config = config_loader.get_system_config()
        max_history = system_config.max_conversation_history
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return agent capabilities"""
        return self.config.capabilities
    
    def get_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "llm_tier": self.config.llm_tier.value,
            "capabilities": [cap.dict() for cap in self.config.capabilities]
        }
