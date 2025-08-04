# Filename: orchestrator.py
# Location: backend/agents/orchestrator.py

from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from .base import BaseAgent, AgentConfig, LLMTier, AgentCapability
from .registry import agent_registry
from config.config_loader import config_loader
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Main orchestrator agent that routes to specialized assistants"""
    
    def __init__(self, api_key: str):
        config = AgentConfig(
            name="orchestrator",
            description="Main agent that routes requests to specialized assistants",
            llm_tier=LLMTier.UTILITY,  # Utility model for routing decisions
            system_prompt=self._get_system_prompt(),
            capabilities=[
                AgentCapability(
                    name="routing",
                    description="Route user requests to appropriate specialist agents",
                    keywords=["help", "question", "need", "want", "how", "what", "why"]
                )
            ],
            temperature=0.3  # Lower temperature for consistent routing
        )
        super().__init__(config, api_key, "main", "main")
    
    def _get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent, responsible for routing user requests to the most appropriate specialist agent.

Your role:
1. Analyze user messages to understand their intent and domain
2. Route to the best specialist agent based on capabilities
3. If no specialist is suitable, handle general queries yourself
4. Provide helpful responses while maintaining context

Available specialist agents and their capabilities:
{agent_capabilities}

Guidelines:
- Be concise and helpful
- Route to specialists when their expertise is clearly needed
- Handle simple greetings and general questions yourself
- Explain your routing decisions when helpful
- Maintain conversation context across interactions"""
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message and route to appropriate agent or handle directly"""

        # Find best agent for this message (excluding orchestrator)
        best_agent, confidence = agent_registry.find_best_agent(message)

        logger.info(f"Best agent found: {best_agent.config.name if best_agent else 'None'} (confidence: {confidence:.2f})")

        # Get routing threshold from configuration
        agent_config = config_loader.get_agent_config("main", "main")
        routing_threshold = agent_config.routing_confidence_threshold or 0.4

        # If we found a good specialist agent and it's not the orchestrator, route to it
        if best_agent and best_agent.config.name != "orchestrator" and confidence > routing_threshold:
            logger.info(f"Routing to {best_agent.config.name} (confidence: {confidence:.2f})")

            try:
                response = await best_agent.process(message, context)

                # Add routing context to response
                routed_response = f"[Routed to {best_agent.config.name}]\n\n{response}"

                # Add to our history for context
                self.add_to_history(message, routed_response)

                return routed_response

            except Exception as e:
                logger.error(f"Error routing to {best_agent.config.name}: {e}")
                # Fall back to handling ourselves
                return await self._handle_directly(message, context)

        # Handle directly if no good specialist found
        logger.info("Handling directly by orchestrator")
        return await self._handle_directly(message, context)
    
    async def _handle_directly(self, message: str, context: Dict[str, Any] = None) -> str:
        """Handle message directly without routing"""
        
        # Prepare messages for LLM
        messages = [
            SystemMessage(content=self._get_formatted_system_prompt()),
            *self.conversation_history,
            HumanMessage(content=message)
        ]
        
        try:
            # Get response from LLM
            response = await self.llm.agenerate([messages])
            ai_response = response.generations[0][0].text.strip()
            
            # Add to history
            self.add_to_history(message, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in orchestrator direct handling: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    def _get_formatted_system_prompt(self) -> str:
        """Get system prompt with current agent capabilities"""
        capabilities = agent_registry.get_capabilities_summary()
        capabilities_text = "\n".join([
            f"- {name}: {', '.join(caps)}" 
            for name, caps in capabilities.items() 
            if name != "orchestrator"
        ])
        
        return self.config.system_prompt.format(
            agent_capabilities=capabilities_text or "No specialist agents currently available"
        )
