"""
LLM Factory Configuration
Defines default and environment-based configurations for all agents
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration Defaults
DEFAULT_CONFIG = {
    "planner": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "Strategic planning and requirement analysis"
    },
    "implementer": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1,
        "max_tokens": 1500,
        "description": "Code/config generation with precision"
    },
    "reviewer": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2,
        "max_tokens": 2000,
        "description": "Quality review and best practices checking"
    },
    "decision": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1,
        "max_tokens": 1000,
        "description": "Deterministic decision making"
    }
}

# Recommended Configurations for Different Use Cases

PRODUCTION_CONFIG = {
    "planner": {
        "model": "gpt-4-turbo",
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "High-quality planning with GPT-4"
    },
    "implementer": {
        "model": "gpt-4-turbo",
        "temperature": 0.1,
        "max_tokens": 1500,
        "description": "Reliable implementation with GPT-4"
    },
    "reviewer": {
        "model": "gpt-4-turbo",
        "temperature": 0.2,
        "max_tokens": 2000,
        "description": "Thorough review with GPT-4"
    },
    "decision": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": 1000,
        "description": "Fast decisions with GPT-3.5"
    }
}

COST_OPTIMIZED_CONFIG = {
    "planner": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.3,
        "max_tokens": 1500,
        "description": "Fast planning with open model"
    },
    "implementer": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1,
        "max_tokens": 1200,
        "description": "Quick implementation with open model"
    },
    "reviewer": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "max_tokens": 1500,
        "description": "Cost-effective review"
    },
    "decision": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.1,
        "max_tokens": 800,
        "description": "Fast decisions with open model"
    }
}

DEVELOPMENT_CONFIG = {
    "planner": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.5,
        "max_tokens": 2000,
        "description": "Creative planning for development"
    },
    "implementer": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.3,
        "max_tokens": 1500,
        "description": "Flexible implementation for prototyping"
    },
    "reviewer": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.3,
        "max_tokens": 2000,
        "description": "Exploratory review for development"
    },
    "decision": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2,
        "max_tokens": 1000,
        "description": "Flexible decisions for development"
    }
}

# Select active configuration based on environment
ACTIVE_CONFIG_ENV = os.getenv("LLM_CONFIG", "default").lower()

CONFIG_MAP = {
    "default": DEFAULT_CONFIG,
    "production": PRODUCTION_CONFIG,
    "cost-optimized": COST_OPTIMIZED_CONFIG,
    "development": DEVELOPMENT_CONFIG,
}

ACTIVE_CONFIG = CONFIG_MAP.get(ACTIVE_CONFIG_ENV, DEFAULT_CONFIG)

print(f"[LLM Config] Using '{ACTIVE_CONFIG_ENV}' configuration")
