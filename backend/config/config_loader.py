# Filename: config_loader.py
# Location: backend/config/config_loader.py

import yaml
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for model settings"""
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    
@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    model: ModelConfig
    routing_confidence_threshold: Optional[float] = None

@dataclass
class SystemConfig:
    """System-wide configuration"""
    max_conversation_history: int = 20
    max_session_memory: int = 20
    log_level: str = "INFO"
    log_agent_routing: bool = True
    log_model_usage: bool = True
    enable_streaming: bool = False
    concurrent_requests: int = 10

@dataclass
class APIConfig:
    """API configuration"""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_max_tokens: int = 1000
    default_temperature: float = 0.7

class ConfigLoader:
    """Loads and manages application configuration"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Look for config.yaml in the project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._config = self._get_default_config()
                return self._config
            
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return self._config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            self._config = self._get_default_config()
            return self._config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'api': {
                'openrouter_base_url': 'https://openrouter.ai/api/v1',
                'default_max_tokens': 1000,
                'default_temperature': 0.7
            },
            'models': {
                'tiers': {
                    'utility': 'openai/gpt-3.5-turbo',
                    'chat': 'openai/gpt-4',
                    'premium': 'openai/gpt-4-turbo',
                    'specialized': 'openai/gpt-4'
                },
                'agents': {}
            },
            'agents': {
                'orchestrator': {
                    'temperature': 0.3,
                    'max_tokens': 500,
                    'routing_confidence_threshold': 0.3
                },
                'coding_assistant': {
                    'temperature': 0.2,
                    'max_tokens': 2000
                },
                'general_assistant': {
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            },
            'system': {
                'max_conversation_history': 20,
                'max_session_memory': 20,
                'log_level': 'INFO',
                'log_agent_routing': True,
                'log_model_usage': True,
                'enable_streaming': False,
                'concurrent_requests': 10
            }
        }
    
    def get_model_for_agent(self, agent_name: str, agent_type: str = "main") -> str:
        """Get the model name for a specific agent"""
        # Handle main agent
        if agent_name == "main" or agent_type == "main":
            main_config = self._config.get('models', {}).get('main', {})
            if isinstance(main_config, dict) and 'model' in main_config:
                return main_config['model']

        # Handle personas
        if agent_type == "personas":
            agent_config = self._config.get('models', {}).get('personas', {}).get(agent_name, {})
            if isinstance(agent_config, dict) and 'model' in agent_config:
                return agent_config['model']

        # Handle universal agents
        if agent_type == "universal":
            agent_config = self._config.get('models', {}).get('universal', {}).get(agent_name, {})
            if isinstance(agent_config, dict) and 'model' in agent_config:
                return agent_config['model']

        # Fallback to main agent model
        main_config = self._config.get('models', {}).get('main', {})
        if isinstance(main_config, dict) and 'model' in main_config:
            return main_config['model']

        # Ultimate fallback
        return 'openai/gpt-4'
    
    def get_agent_config(self, agent_name: str, agent_type: str = "main") -> AgentConfig:
        """Get complete configuration for an agent"""
        # Get model configuration from the models section
        if agent_type == "main" or agent_name == "main":
            model_config_section = self._config.get('models', {}).get('main', {})
        elif agent_type == "personas":
            model_config_section = self._config.get('models', {}).get('personas', {}).get(agent_name, {})
        elif agent_type == "universal":
            model_config_section = self._config.get('models', {}).get('universal', {}).get(agent_name, {})
        else:
            model_config_section = {}

        # Get agent settings from the agents section
        if agent_type == "main" or agent_name == "main":
            agent_settings = self._config.get('agents', {}).get('main', {})
        elif agent_type == "personas":
            agent_settings = self._config.get('agents', {}).get('personas', {}).get(agent_name, {})
        elif agent_type == "universal":
            agent_settings = self._config.get('agents', {}).get('universal', {}).get(agent_name, {})
        else:
            agent_settings = {}

        # Get model name
        model_name = self.get_model_for_agent(agent_name, agent_type)

        # Get settings with defaults from model config or agent settings
        if isinstance(model_config_section, dict):
            temperature = model_config_section.get('temperature',
                         agent_settings.get('temperature',
                         self._config.get('api', {}).get('default_temperature', 0.7)))
            max_tokens = model_config_section.get('max_tokens',
                        agent_settings.get('max_tokens',
                        self._config.get('api', {}).get('default_max_tokens', 1000)))
        else:
            temperature = agent_settings.get('temperature', self._config.get('api', {}).get('default_temperature', 0.7))
            max_tokens = agent_settings.get('max_tokens', self._config.get('api', {}).get('default_max_tokens', 1000))

        model_config = ModelConfig(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return AgentConfig(
            model=model_config,
            routing_confidence_threshold=agent_settings.get('routing_confidence_threshold')
        )
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        api_settings = self._config.get('api', {})
        return APIConfig(
            openrouter_base_url=api_settings.get('openrouter_base_url', 'https://openrouter.ai/api/v1'),
            default_max_tokens=api_settings.get('default_max_tokens', 1000),
            default_temperature=api_settings.get('default_temperature', 0.7)
        )
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        system_settings = self._config.get('system', {})
        return SystemConfig(
            max_conversation_history=system_settings.get('max_conversation_history', 20),
            max_session_memory=system_settings.get('max_session_memory', 20),
            log_level=system_settings.get('log_level', 'INFO'),
            log_agent_routing=system_settings.get('log_agent_routing', True),
            log_model_usage=system_settings.get('log_model_usage', True),
            enable_streaming=system_settings.get('enable_streaming', False),
            concurrent_requests=system_settings.get('concurrent_requests', 10)
        )
    
    def get_persona_config(self, persona_name: str) -> dict:
        """Get configuration for a specific persona"""
        return self._config.get('agents', {}).get('personas', {}).get(persona_name, {})

    def get_available_helpers(self, persona_name: str) -> list:
        """Get list of available helpers for a persona"""
        persona_config = self.get_persona_config(persona_name)
        return persona_config.get('available_helpers', [])

    def get_helper_threshold(self, persona_name: str) -> float:
        """Get helper summoning threshold for a persona"""
        persona_config = self.get_persona_config(persona_name)
        return persona_config.get('helper_threshold', 0.5)

    def get_top_level_config(self) -> dict:
        """Get top-level agent configuration"""
        return self._config.get('agents', {}).get('top_level', {})

    def get_persona_selection_threshold(self) -> float:
        """Get threshold for persona selection"""
        top_level_config = self.get_top_level_config()
        return top_level_config.get('persona_selection_threshold', 0.3)

    def get_routing_confidence_threshold(self) -> float:
        """Get routing confidence threshold for top-level agent"""
        top_level_config = self.get_top_level_config()
        return top_level_config.get('routing_confidence_threshold', 0.4)

    def list_personas(self) -> list:
        """Get list of available personas"""
        return list(self._config.get('models', {}).get('personas', {}).keys())

    def list_helpers(self) -> list:
        """Get list of available helpers"""
        return list(self._config.get('models', {}).get('helpers', {}).keys())

    def list_universal_agents(self) -> list:
        """Get list of universal agents"""
        return list(self._config.get('models', {}).get('universal', {}).keys())

    def get_fallback_config(self) -> dict:
        """Get fallback system configuration"""
        return self._config.get('agents', {}).get('fallback', {
            'enabled': True,
            'max_retries': 2,
            'retry_delay': 1.0,
            'fallback_notification': True
        })

    def get_fallback_model_for_agent(self, agent_name: str, agent_type: str = "main") -> str:
        """Get fallback model for a specific agent"""
        fallback_config = self.get_fallback_config()
        mapping = fallback_config.get('mapping', {})

        # Get the fallback name for this agent
        fallback_name = None
        if agent_type == "main" or agent_name == "main":
            fallback_name = mapping.get('main')
        elif agent_type == "personas":
            type_mapping = mapping.get('personas', {})
            fallback_name = type_mapping.get(agent_name)
        elif agent_type == "universal":
            type_mapping = mapping.get('universal', {})
            fallback_name = type_mapping.get(agent_name)

        # If no specific mapping, use main fallback
        if not fallback_name:
            fallback_name = "main_fallback"

        # Get the actual fallback model configuration
        fallback_models = self._config.get('models', {}).get('fallbacks', {})
        fallback_config = fallback_models.get(fallback_name, {})

        if isinstance(fallback_config, dict) and 'model' in fallback_config:
            return fallback_config['model']

        # Ultimate fallback to a known free model
        return "meta-llama/llama-3.2-3b-instruct:free"

    def get_fallback_agent_config(self, agent_name: str, agent_type: str = "main") -> AgentConfig:
        """Get complete fallback configuration for an agent"""
        fallback_config = self.get_fallback_config()
        mapping = fallback_config.get('mapping', {})

        # Get the fallback name for this agent
        fallback_name = None
        if agent_type == "main" or agent_name == "main":
            fallback_name = mapping.get('main', "main_fallback")
        elif agent_type == "personas":
            type_mapping = mapping.get('personas', {})
            fallback_name = type_mapping.get(agent_name, "main_fallback")
        elif agent_type == "universal":
            type_mapping = mapping.get('universal', {})
            fallback_name = type_mapping.get(agent_name, "main_fallback")

        # Get the fallback model configuration
        fallback_models = self._config.get('models', {}).get('fallbacks', {})
        fallback_model_config = fallback_models.get(fallback_name, {})

        # Extract settings
        model_name = fallback_model_config.get('model', "meta-llama/llama-3.2-3b-instruct:free")
        temperature = fallback_model_config.get('temperature', 0.7)
        max_tokens = fallback_model_config.get('max_tokens', 1000)

        model_config = ModelConfig(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return AgentConfig(
            model=model_config,
            routing_confidence_threshold=None
        )

    def is_fallback_enabled(self) -> bool:
        """Check if fallback system is enabled"""
        fallback_config = self.get_fallback_config()
        return fallback_config.get('enabled', True)

    def reload_config(self):
        """Reload configuration from file"""
        self.load_config()
        logger.info("Configuration reloaded")

# Global config instance
config_loader = ConfigLoader()
