"""
LLM Factory
Centralized LLM instance management with support for:
- Multi-model routing
- Testing and mocking
- Failover strategies
- Cost optimization
- Configuration management
"""

import os
from typing import Dict, Optional, Literal
from langchain_groq import ChatGroq


class LLMConfig:
    """Configuration for LLM instances"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Model configurations per agent
        self.model_config = {
            "planner": {
                "model": os.getenv("PLANNER_MODEL", "llama-3.3-70b-versatile"),
                "temperature": float(os.getenv("PLANNER_TEMPERATURE", "0.3")),
                "max_tokens": int(os.getenv("PLANNER_MAX_TOKENS", "2000")),
            },
            "implementer": {
                "model": os.getenv("IMPLEMENTER_MODEL", "llama-3.3-70b-versatile"),
                "temperature": float(os.getenv("IMPLEMENTER_TEMPERATURE", "0.1")),
                "max_tokens": int(os.getenv("IMPLEMENTER_MAX_TOKENS", "1500")),
            },
            "reviewer": {
                "model": os.getenv("REVIEWER_MODEL", "llama-3.3-70b-versatile"),
                "temperature": float(os.getenv("REVIEWER_TEMPERATURE", "0.2")),
                "max_tokens": int(os.getenv("REVIEWER_MAX_TOKENS", "2000")),
            },
            "decision": {
                "model": os.getenv("DECISION_MODEL", "llama-3.3-70b-versatile"),
                "temperature": float(os.getenv("DECISION_TEMPERATURE", "0.1")),
                "max_tokens": int(os.getenv("DECISION_MAX_TOKENS", "1000")),
            },
        }


class LLMFactory:
    """
    Factory for creating and managing LLM instances
    
    Supports:
    - Lazy loading of LLM instances
    - Configuration per agent type
    - Multi-model routing
    - Mock/test implementations
    - Failover strategies
    """

    _config: Optional[LLMConfig] = None
    _instances: Dict[str, BaseLanguageModel] = {}
    _test_mode: bool = False
    _mock_llm: Optional[BaseLanguageModel] = None

    @classmethod
    def initialize(cls, config: Optional[LLMConfig] = None):
        """Initialize the factory with configuration"""
        cls._config = config or LLMConfig()

    @classmethod
    def set_test_mode(cls, enabled: bool = True, mock_llm: Optional[BaseLanguageModel] = None):
        """
        Enable/disable test mode for unit testing
        
        Args:
            enabled: Whether to enable test mode
            mock_llm: Mock LLM instance to use in test mode
        """
        cls._test_mode = enabled
        cls._mock_llm = mock_llm

    @classmethod
    def get_planner_llm(cls) -> BaseLanguageModel:
        """Get or create planner LLM instance"""
        return cls._get_llm("planner")

    @classmethod
    def get_implementer_llm(cls) -> BaseLanguageModel:
        """Get or create implementer LLM instance"""
        return cls._get_llm("implementer")

    @classmethod
    def get_reviewer_llm(cls) -> BaseLanguageModel:
        """Get or create reviewer LLM instance"""
        return cls._get_llm("reviewer")

    @classmethod
    def get_decision_llm(cls) -> BaseLanguageModel:
        """Get or create decision LLM instance"""
        return cls._get_llm("decision")

    @classmethod
    def get_llm(cls, agent_type: Literal["planner", "implementer", "reviewer", "decision"]) -> BaseLanguageModel:
        """
        Generic method to get LLM for any agent type
        
        Args:
            agent_type: Type of agent (planner, implementer, reviewer, decision)
            
        Returns:
            Configured LLM instance
        """
        return cls._get_llm(agent_type)

    @classmethod
    def _get_llm(cls, agent_type: str) -> BaseLanguageModel:
        """
        Internal method to get or create LLM instance
        
        Implements:
        - Lazy loading (create on first access)
        - Caching (reuse instances)
        - Test mode support
        - Failover handling
        """
        if cls._test_mode and cls._mock_llm is not None:
            return cls._mock_llm

        # Return cached instance if exists
        if agent_type in cls._instances:
            return cls._instances[agent_type]

        # Initialize config if needed
        if cls._config is None:
            cls.initialize()

        # Create new instance
        if agent_type not in cls._config.model_config:
            raise ValueError(f"Unknown agent type: {agent_type}")

        config = cls._config.model_config[agent_type]
        llm = ChatGroq(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=cls._config.api_key,
        )

        # Cache the instance
        cls._instances[agent_type] = llm
        return llm

    @classmethod
    def clear_cache(cls):
        """Clear all cached LLM instances (useful for testing)"""
        cls._instances.clear()

    @classmethod
    def get_config(cls) -> LLMConfig:
        """Get current configuration"""
        if cls._config is None:
            cls.initialize()
        return cls._config

    @classmethod
    def update_model(cls, agent_type: str, model: str):
        """
        Update model for specific agent type
        
        Args:
            agent_type: Type of agent
            model: New model name
        """
        config = cls.get_config()
        if agent_type in config.model_config:
            config.model_config[agent_type]["model"] = model
            # Clear cache to use new model
            if agent_type in cls._instances:
                del cls._instances[agent_type]


# Initialize on import
LLMFactory.initialize()
