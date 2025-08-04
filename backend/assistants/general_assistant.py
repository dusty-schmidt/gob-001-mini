# Filename: general_assistant.py
# Location: backend/assistants/general_assistant.py

from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from agents.base import BaseAgent, AgentConfig, LLMTier, AgentCapability


class GeneralAssistant(BaseAgent):
    """General purpose assistant for broad range of topics"""
    
    def __init__(self, api_key: str):
        config = AgentConfig(
            name="general_assistant",
            description="Helpful general assistant for various topics and conversations",
            llm_tier=LLMTier.UTILITY,  # Utility model for general queries (fast/cheap)
            system_prompt=self._get_system_prompt(),
            capabilities=[
                AgentCapability(
                    name="general_help",
                    description="General assistance, conversation, and information",
                    keywords=["hello", "hi", "help", "question", "explain", "tell", "what", 
                             "how", "why", "when", "where", "general", "chat", "talk"]
                ),
                AgentCapability(
                    name="information",
                    description="Provide information and answer questions on various topics",
                    keywords=["information", "facts", "explain", "definition", "meaning",
                             "history", "science", "news", "weather", "calculate"]
                )
            ],
            temperature=0.7  # More creative for general conversation
        )
        super().__init__(config, api_key, "general_assistant", "personas")
    
    def _get_system_prompt(self) -> str:
        return """You are a helpful, knowledgeable, and friendly general assistant.

Your role:
- Provide helpful information and answers on a wide range of topics
- Engage in natural, friendly conversation
- Be informative yet concise
- Ask clarifying questions when needed
- Admit when you don't know something
- Suggest when a specialist might be more helpful

Guidelines:
- Be warm and approachable in your responses
- Provide accurate information to the best of your knowledge
- Keep responses focused and relevant
- Use clear, easy-to-understand language
- Be encouraging and supportive

You're here to help with general questions, casual conversation, and to provide a friendly interface when specialized help isn't needed."""
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process general requests and conversations"""
        
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
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
