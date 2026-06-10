"""
Prompt Registry

Manages prompts through YAML configuration files instead of hardcoding them in agent files.
This allows for easy maintenance, versioning, and reuse of prompts across agents.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PromptRegistry:
    """
    Central registry for managing prompts loaded from YAML files.
    
    Features:
    - Load prompts from YAML configuration files
    - Cache loaded prompts for performance
    - Support for prompt templates with variables
    - Easy prompt versioning and management
    - Fallback to default prompts
    
    Usage:
        # Load a specific prompt
        prompt = PromptRegistry.get("planner", "strategy")
        
        # Load with format variables
        prompt = PromptRegistry.get("reviewer", "review")
        filled = prompt.format(deployment_yaml="...")
        
        # List all available prompts
        prompts = PromptRegistry.list_prompts("planner")
        
        # Reload prompts (useful for development)
        PromptRegistry.reload()
    """
    
    _prompts_dir = Path(__file__).parent / "data"
    _cache: Dict[str, Dict[str, str]] = {}
    _loaded = False
    
    @classmethod
    def _ensure_prompts_dir(cls) -> Path:
        """Ensure prompts directory exists."""
        cls._prompts_dir.mkdir(parents=True, exist_ok=True)
        return cls._prompts_dir
    
    @classmethod
    def load(cls) -> None:
        """Load all prompts from YAML files into cache."""
        prompts_dir = cls._ensure_prompts_dir()
        cls._cache = {}
        
        # Find all YAML files in prompts directory
        yaml_files = list(prompts_dir.glob("*.yaml")) + list(prompts_dir.glob("*.yml"))
        
        if not yaml_files:
            logger.warning(f"No prompt files found in {prompts_dir}")
            return
        
        for yaml_file in yaml_files:
            try:
                category = yaml_file.stem  # filename without extension
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    cls._cache[category] = data
                    logger.debug(f"Loaded prompts from {yaml_file.name}")
            except Exception as e:
                logger.error(f"Error loading prompts from {yaml_file.name}: {str(e)}")
        
        cls._loaded = True
        logger.info(f"Loaded prompts from {len(yaml_files)} files")
    
    @classmethod
    def get(cls, category: str, prompt_key: str) -> str:
        """
        Get a prompt by category and key.
        
        Args:
            category: Prompt category (e.g., "planner", "reviewer")
            prompt_key: Prompt identifier within category (e.g., "strategy", "review")
            
        Returns:
            Prompt template string
            
        Raises:
            KeyError: If prompt not found
        """
        # Load on first access
        if not cls._loaded:
            cls.load()
        
        if category not in cls._cache:
            raise KeyError(f"Prompt category '{category}' not found. Available: {list(cls._cache.keys())}")
        
        if prompt_key not in cls._cache[category]:
            available = list(cls._cache[category].keys())
            raise KeyError(f"Prompt '{prompt_key}' not found in category '{category}'. Available: {available}")
        
        return cls._cache[category][prompt_key]
    
    @classmethod
    def get_all(cls, category: str) -> Dict[str, str]:
        """
        Get all prompts in a category.
        
        Args:
            category: Prompt category
            
        Returns:
            Dictionary of all prompts in category
        """
        if not cls._loaded:
            cls.load()
        
        if category not in cls._cache:
            raise KeyError(f"Prompt category '{category}' not found")
        
        return cls._cache[category].copy()
    
    @classmethod
    def list_categories(cls) -> list:
        """Get list of all available prompt categories."""
        if not cls._loaded:
            cls.load()
        return list(cls._cache.keys())
    
    @classmethod
    def list_prompts(cls, category: str) -> list:
        """Get list of all prompts in a category."""
        if not cls._loaded:
            cls.load()
        
        if category not in cls._cache:
            return []
        
        return list(cls._cache[category].keys())
    
    @classmethod
    def reload(cls) -> None:
        """
        Reload all prompts from disk.
        
        Useful during development when prompt files are modified.
        """
        cls._loaded = False
        cls._cache = {}
        cls.load()
        logger.info("Prompt registry reloaded")
    
    @classmethod
    def set_prompts_dir(cls, directory: Path) -> None:
        """
        Set custom prompts directory.
        
        Args:
            directory: Path to directory containing prompt YAML files
        """
        cls._prompts_dir = Path(directory)
        cls.reload()
    
    @classmethod
    def get_prompts_dir(cls) -> Path:
        """Get current prompts directory."""
        return cls._prompts_dir


# Auto-load prompts on import
def _auto_load():
    """Auto-load prompts when module is imported."""
    try:
        PromptRegistry.load()
    except Exception as e:
        logger.warning(f"Failed to auto-load prompts: {str(e)}")


_auto_load()
