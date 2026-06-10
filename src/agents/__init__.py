"""Agents package initialization"""

# Base agent classes
from .base import (
    BaseAgent,
    StatefulAgent,
    ComposableAgent,
    ExecutionMetrics,
)

# Agent implementations (node functions for backward compatibility)
from .planner import planner_node, PlannerAgent
from .implementer import implement_node, ImplementerAgent
from .reviewer import review_node, ReviewerAgent
from .decision import decision_node, DecisionAgent
from .reporting import report_node, ReporterAgent

__all__ = [
    # Base classes
    "BaseAgent",
    "StatefulAgent",
    "ComposableAgent",
    "ExecutionMetrics",
    # Agent classes
    "PlannerAgent",
    "ImplementerAgent",
    "ReviewerAgent",
    "DecisionAgent",
    "ReporterAgent",
    # Node functions (backward compatibility)
    "planner_node",
    "implement_node",
    "review_node",
    "decision_node",
    "report_node",
]
