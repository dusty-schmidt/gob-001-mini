# Filename: top_level_orchestrator.py
# Location: backend/agents/top_level_orchestrator.py

from typing import Dict, Any, List
from langchain.schema import HumanMessage, SystemMessage
from .base import BaseAgent, AgentConfig, LLMTier, AgentCapability
from config.config_loader import config_loader
import logging

logger = logging.getLogger(__name__)


class TopLevelOrchestrator(BaseAgent):
    """Top-level orchestrator that routes to specialized personas"""
    
    def __init__(self, api_key: str):
        config = AgentConfig(
            name="top_level_orchestrator",
            description="Top-level agent that routes requests to specialized personas",
            llm_tier=LLMTier.PREMIUM,  # Use smartest model
            system_prompt=self._get_system_prompt(),
            capabilities=[
                AgentCapability(
                    name="persona_routing",
                    description="Route user requests to appropriate persona agents",
                    keywords=["help", "question", "need", "want", "how", "what", "why"]
                )
            ],
            temperature=0.3  # Lower temperature for consistent routing
        )
        super().__init__(config, api_key, "top_level")
        self.personas = {}  # Will be populated with persona instances
    
    def register_persona(self, persona_name: str, persona_instance):
        """Register a persona agent"""
        self.personas[persona_name] = persona_instance
        logger.info(f"Registered persona: {persona_name}")
    
    def _get_system_prompt(self) -> str:
        available_personas = config_loader.list_personas()
        personas_text = "\n".join([f"- {name}" for name in available_personas])
        
        return f"""You are the Top-Level Orchestrator, the smartest agent responsible for routing user requests to the most appropriate specialized persona.

Your role:
1. Analyze user messages to understand their intent, domain, and complexity
2. Route to the best persona agent based on their specializations
3. Use the main persona as fallback for general queries
4. Provide helpful responses while maintaining context

Available personas:
{personas_text}

Persona specializations:
- main: General conversation, basic questions, greetings
- developer: Software engineering, programming, technical architecture
- researcher: Research, analysis, fact-checking, academic work
- creative: Creative writing, brainstorming, artistic projects
- business: Business strategy, analysis, planning, professional communication

Guidelines:
- Be intelligent and thoughtful in your routing decisions
- Route to specialists when their expertise is clearly needed
- Handle simple greetings and very basic questions yourself
- Explain your routing decisions when helpful
- Maintain conversation context across interactions
- Consider the complexity and domain of the request"""
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message and route to appropriate persona or handle directly"""
        
        # Analyze message to determine best persona
        best_persona = await self._select_persona(message, context)
        
        if best_persona and best_persona in self.personas:
            logger.info(f"Routing to persona: {best_persona}")
            
            try:
                response = await self.personas[best_persona].process(message, context)
                
                # Add routing context to response
                routed_response = f"[Routed to {best_persona} persona]\n\n{response}"
                
                # Add to our history for context
                self.add_to_history(message, routed_response)
                
                return routed_response
                
            except Exception as e:
                logger.error(f"Error routing to {best_persona}: {e}")
                # Fall back to handling ourselves
                return await self._handle_directly(message, context)
        
        # Handle directly if no good persona found
        logger.info("Handling directly by top-level orchestrator")
        return await self._handle_directly(message, context)
    
    async def _select_persona(self, message: str, context: Dict[str, Any] = None) -> str:
        """Select the best persona for the message"""
        
        # Use LLM to analyze and select persona
        analysis_prompt = f"""Analyze this user message and select the most appropriate persona to handle it.

User message: "{message}"

Available personas:
- main: General conversation, basic questions, greetings
- developer: Software engineering, programming, technical architecture  
- researcher: Research, analysis, fact-checking, academic work
- creative: Creative writing, brainstorming, artistic projects
- business: Business strategy, analysis, planning, professional communication

Consider:
1. The domain and complexity of the request
2. The specific expertise needed
3. Whether it's a simple greeting or complex task

Respond with just the persona name (main, developer, researcher, creative, or business) that would best handle this request."""
        
        try:
            messages = [
                SystemMessage(content="You are an expert at analyzing user requests and selecting the appropriate specialist."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            selected_persona = response.generations[0][0].text.strip().lower()
            
            # Validate the selection
            available_personas = config_loader.list_personas()
            if selected_persona in available_personas:
                return selected_persona
            else:
                logger.warning(f"Invalid persona selected: {selected_persona}, defaulting to main")
                return "main"
                
        except Exception as e:
            logger.error(f"Error in persona selection: {e}")
            return "main"  # Default fallback
    
    async def _handle_directly(self, message: str, context: Dict[str, Any] = None) -> str:
        """Handle message directly without routing"""
        
        # Prepare messages for LLM
        messages = [
            SystemMessage(content=self.config.system_prompt),
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
            logger.error(f"Error in top-level direct handling: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
