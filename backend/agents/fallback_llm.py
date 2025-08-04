# Filename: fallback_llm.py
# Location: backend/agents/fallback_llm.py

import asyncio
import logging
from typing import List, Any, Optional
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from config.config_loader import config_loader

logger = logging.getLogger(__name__)


class FallbackLLM:
    """LLM wrapper with automatic fallback capabilities"""
    
    def __init__(self, agent_name: str, agent_type: str, api_key: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.api_key = api_key
        
        # Get configurations
        self.primary_config = config_loader.get_agent_config(agent_name, agent_type)
        self.fallback_config = config_loader.get_fallback_agent_config(agent_name, agent_type)
        self.fallback_settings = config_loader.get_fallback_config()
        
        # Create primary and fallback LLMs
        self.primary_llm = self._create_llm(self.primary_config)
        self.fallback_llm = self._create_llm(self.fallback_config) if config_loader.is_fallback_enabled() else None
        
        # Track fallback usage
        self.using_fallback = False
        self.fallback_reason = None
        
    def _create_llm(self, agent_config) -> ChatOpenAI:
        """Create a ChatOpenAI instance from agent config"""
        api_config = config_loader.get_api_config()
        
        return ChatOpenAI(
            model=agent_config.model.model_name,
            openai_api_key=self.api_key,
            openai_api_base=api_config.openrouter_base_url,
            temperature=agent_config.model.temperature,
            max_tokens=agent_config.model.max_tokens
        )
    
    async def agenerate(self, messages_list: List[List[BaseMessage]], **kwargs) -> Any:
        """Generate response with automatic fallback"""
        if not config_loader.is_fallback_enabled():
            return await self.primary_llm.agenerate(messages_list, **kwargs)
        
        max_retries = self.fallback_settings.get('max_retries', 2)
        retry_delay = self.fallback_settings.get('retry_delay', 1.0)
        
        # Try primary model first
        for attempt in range(max_retries + 1):
            try:
                if self.using_fallback:
                    logger.info(f"Using fallback model for {self.agent_name}: {self.fallback_config.model.model_name}")
                    response = await self.fallback_llm.agenerate(messages_list, **kwargs)
                else:
                    response = await self.primary_llm.agenerate(messages_list, **kwargs)
                
                # Success - reset fallback status if we were using it
                if self.using_fallback:
                    logger.info(f"Fallback successful for {self.agent_name}")
                
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if this is a credit/quota/payment error
                is_credit_error = any(keyword in error_msg for keyword in [
                    'insufficient', 'quota', 'credit', 'payment', 'billing', 
                    'limit', 'exceeded', '402', 'payment required', 'balance'
                ])
                
                # Check if this is a rate limit error
                is_rate_limit = any(keyword in error_msg for keyword in [
                    'rate limit', 'too many requests', '429', 'throttle'
                ])
                
                logger.warning(f"Error with {self.agent_name} (attempt {attempt + 1}): {e}")
                
                # If it's a credit error or we've exhausted retries, switch to fallback
                if is_credit_error or attempt >= max_retries:
                    if not self.using_fallback and self.fallback_llm:
                        logger.warning(f"Switching {self.agent_name} to fallback model due to: {e}")
                        self.using_fallback = True
                        self.fallback_reason = "credit_exhausted" if is_credit_error else "max_retries_exceeded"
                        
                        # Try fallback immediately
                        try:
                            response = await self.fallback_llm.agenerate(messages_list, **kwargs)
                            logger.info(f"Fallback successful for {self.agent_name}")
                            return response
                        except Exception as fallback_error:
                            logger.error(f"Fallback also failed for {self.agent_name}: {fallback_error}")
                            raise fallback_error
                    else:
                        # Already using fallback or no fallback available
                        raise e
                
                # For rate limits or other temporary errors, wait and retry
                if is_rate_limit and attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Rate limited, waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                elif attempt < max_retries:
                    await asyncio.sleep(retry_delay)
        
        # If we get here, all retries failed
        raise Exception(f"All attempts failed for {self.agent_name}")
    
    def get_status(self) -> dict:
        """Get current status of the LLM"""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "using_fallback": self.using_fallback,
            "fallback_reason": self.fallback_reason,
            "primary_model": self.primary_config.model.model_name,
            "fallback_model": self.fallback_config.model.model_name if self.fallback_llm else None,
            "fallback_enabled": config_loader.is_fallback_enabled()
        }
    
    def reset_fallback(self):
        """Reset to primary model (useful for testing or manual recovery)"""
        if self.using_fallback:
            logger.info(f"Resetting {self.agent_name} from fallback to primary model")
            self.using_fallback = False
            self.fallback_reason = None
    
    def force_fallback(self, reason: str = "manual"):
        """Force switch to fallback model"""
        if self.fallback_llm and not self.using_fallback:
            logger.info(f"Manually switching {self.agent_name} to fallback model")
            self.using_fallback = True
            self.fallback_reason = reason
    
    def get_current_model(self) -> str:
        """Get the currently active model name"""
        if self.using_fallback:
            return self.fallback_config.model.model_name
        else:
            return self.primary_config.model.model_name
    
    def should_notify_fallback(self) -> bool:
        """Check if user should be notified about fallback usage"""
        return (self.using_fallback and 
                self.fallback_settings.get('fallback_notification', True))


class FallbackManager:
    """Global manager for tracking fallback status across all agents"""
    
    def __init__(self):
        self.agents = {}
    
    def register_agent(self, agent_name: str, fallback_llm: FallbackLLM):
        """Register an agent's fallback LLM"""
        self.agents[agent_name] = fallback_llm
    
    def get_system_status(self) -> dict:
        """Get overall system fallback status"""
        status = {
            "total_agents": len(self.agents),
            "agents_using_fallback": 0,
            "agents_status": {}
        }
        
        for agent_name, fallback_llm in self.agents.items():
            agent_status = fallback_llm.get_status()
            status["agents_status"][agent_name] = agent_status
            
            if agent_status["using_fallback"]:
                status["agents_using_fallback"] += 1
        
        return status
    
    def reset_all_fallbacks(self):
        """Reset all agents to primary models"""
        for fallback_llm in self.agents.values():
            fallback_llm.reset_fallback()
    
    def force_all_fallbacks(self, reason: str = "manual"):
        """Force all agents to use fallback models"""
        for fallback_llm in self.agents.values():
            fallback_llm.force_fallback(reason)


# Global fallback manager instance
fallback_manager = FallbackManager()
