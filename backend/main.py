# Filename: main.py
# Location: backend/main.py

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import our agent system
from agents.orchestrator import OrchestratorAgent
from agents.registry import agent_registry
from agents.fallback_llm import fallback_manager
from assistants.coding_assistant import CodingAssistant
from assistants.general_assistant import GeneralAssistant
from config.config_loader import config_loader

# Setup logging from configuration
system_config = config_loader.get_system_config()
logging.basicConfig(level=getattr(logging, system_config.log_level))
logger = logging.getLogger(__name__)

load_dotenv("../.env")  # Load environment variables from parent directory .env file

app = FastAPI(title="Agentic Framework API", version="1.0.0")

# Allow CORS for frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory session-based memory store
chat_memory = {}

# Request model
class Message(BaseModel):
    message: str
    sessionId: str = "default"

# Response model
class ChatResponse(BaseModel):
    reply: str
    agent_used: str
    confidence: float = 0.0
    using_fallback: bool = False
    fallback_reason: Optional[str] = None
    current_model: Optional[str] = None

# Global orchestrator agent
orchestrator: OrchestratorAgent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup"""
    global orchestrator

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your_openrouter_api_key_here':
        logger.error("OpenRouter API key not configured!")
        raise RuntimeError("OpenRouter API key not configured")

    logger.info("Initializing agent system...")

    # Create and register agents
    coding_assistant = CodingAssistant(api_key)
    general_assistant = GeneralAssistant(api_key)

    # Register agents (general as fallback)
    agent_registry.register_agent(coding_assistant)
    agent_registry.register_agent(general_assistant, is_fallback=True)

    # Create orchestrator
    orchestrator = OrchestratorAgent(api_key)

    logger.info(f"Agent system initialized with {len(agent_registry.agents)} agents")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(msg: Message):
    """Main chat endpoint using agent system"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Agent system not initialized")

    try:
        # Get session memory
        memory = chat_memory.setdefault(msg.sessionId, [])

        # Process message through orchestrator
        context = {"session_id": msg.sessionId, "history": memory}
        reply = await orchestrator.process(msg.message, context)

        # Update memory
        memory.append({"role": "user", "content": msg.message})
        memory.append({"role": "assistant", "content": reply})

        # Keep memory manageable using configuration
        system_config = config_loader.get_system_config()
        max_memory = system_config.max_session_memory
        if len(memory) > max_memory:
            memory = memory[-max_memory:]
            chat_memory[msg.sessionId] = memory

        # Extract agent info from reply if routed
        agent_used = "orchestrator"
        confidence = 1.0

        if reply.startswith("[Routed to "):
            agent_used = reply.split("]")[0].replace("[Routed to ", "")
            # Find the agent and get confidence
            best_agent, conf = agent_registry.find_best_agent(msg.message)
            if best_agent:
                confidence = conf

        # Check fallback status
        fallback_status = orchestrator.llm.get_status()
        using_fallback = fallback_status["using_fallback"]
        fallback_reason = fallback_status["fallback_reason"]
        current_model = fallback_status["primary_model"]

        # Add fallback notification to reply if needed
        if using_fallback and orchestrator.llm.should_notify_fallback():
            fallback_notice = f"\n\n⚠️ Note: Currently using fallback model ({fallback_status['fallback_model']}) due to {fallback_reason.replace('_', ' ')}."
            reply += fallback_notice

        return ChatResponse(
            reply=reply,
            agent_used=agent_used,
            confidence=confidence,
            using_fallback=using_fallback,
            fallback_reason=fallback_reason,
            current_model=current_model
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/agents")
async def list_agents():
    """List all available agents and their capabilities"""
    return {
        "agents": agent_registry.list_agents(),
        "capabilities": agent_registry.get_capabilities_summary()
    }

@app.get("/api/fallback/status")
async def get_fallback_status():
    """Get current fallback status for all agents"""
    return fallback_manager.get_system_status()

@app.post("/api/fallback/reset")
async def reset_fallbacks():
    """Reset all agents to primary models"""
    fallback_manager.reset_all_fallbacks()
    return {"message": "All agents reset to primary models"}

@app.post("/api/fallback/force")
async def force_fallbacks():
    """Force all agents to use fallback models"""
    fallback_manager.force_all_fallbacks("manual_override")
    return {"message": "All agents switched to fallback models"}
