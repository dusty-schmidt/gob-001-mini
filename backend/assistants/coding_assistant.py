# Filename: coding_assistant.py
# Location: backend/assistants/coding_assistant.py

from typing import Dict, Any
from langchain.schema import HumanMessage, SystemMessage
from agents.base import BaseAgent, AgentConfig, LLMTier, AgentCapability


class CodingAssistant(BaseAgent):
    """Specialized assistant for coding and programming tasks"""
    
    def __init__(self, api_key: str):
        config = AgentConfig(
            name="coding_assistant",
            description="Expert programming assistant for code help, debugging, and technical questions",
            llm_tier=LLMTier.CHAT,  # Chat model for quality user responses
            system_prompt=self._get_system_prompt(),
            capabilities=[
                AgentCapability(
                    name="programming",
                    description="Help with programming, coding, and software development",
                    keywords=["code", "programming", "python", "javascript", "debug", "function", 
                             "class", "algorithm", "bug", "error", "syntax", "api", "framework",
                             "library", "database", "sql", "html", "css", "react", "node"]
                ),
                AgentCapability(
                    name="technical_help",
                    description="Technical problem solving and architecture advice",
                    keywords=["architecture", "design", "pattern", "best practice", "performance",
                             "optimization", "security", "deployment", "testing", "git", "microservices",
                             "containers", "docker", "kubernetes", "devops", "scalability", "distributed"]
                )
            ],
            temperature=0.2  # Lower temperature for more precise code
        )
        super().__init__(config, api_key, "coding_assistant", "personas")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior Software Engineer and Coding Assistant with expertise across multiple programming languages and technologies.

Your specialties:
- Writing clean, efficient, and well-documented code
- Debugging and troubleshooting technical issues
- Explaining programming concepts clearly
- Providing best practices and architectural guidance
- Code reviews and optimization suggestions

Guidelines:
- Always provide working, tested code examples when possible
- Explain your reasoning and approach
- Include comments in code for clarity
- Suggest best practices and potential improvements
- Ask clarifying questions when requirements are unclear
- Consider security, performance, and maintainability

Languages you excel in: Python, JavaScript, TypeScript, React, Node.js, SQL, HTML/CSS, and more.

Be practical, precise, and helpful in your responses."""
    
    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process coding-related requests"""
        
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
            return f"I apologize, but I encountered an error while processing your coding request: {str(e)}"
