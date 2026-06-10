"""
Base Agent Class

Provides a common interface and shared functionality for all agents in the workflow.
All specialized agents should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging


logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics recorded during agent execution."""
    
    execution_time: float = 0.0
    tokens_used: int = 0
    api_calls: int = 0
    cache_hits: int = 0
    errors: int = 0
    retries: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_name: str = ""
    status: str = "pending"  # pending, running, success, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "api_calls": self.api_calls,
            "cache_hits": self.cache_hits,
            "errors": self.errors,
            "retries": self.retries,
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "status": self.status,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the workflow.
    
    Provides common interface and shared functionality including:
    - Execution lifecycle management
    - Result validation
    - Retry logic
    - Metrics collection
    - Error handling
    
    Subclasses must implement:
    - execute(state): Main agent logic
    - validate(result): Validation of output
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (e.g., "planner", "reviewer")
            max_retries: Maximum number of retries on failure
        """
        self.name = name
        self.max_retries = max_retries
        self.metrics = ExecutionMetrics(agent_name=name)
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._retry_count = 0
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent's output
        """
        pass
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """
        Validate the agent's output.
        
        Override in subclass for specific validation logic.
        
        Args:
            result: Output from execute()
            
        Returns:
            True if result is valid, False otherwise
        """
        return result is not None and isinstance(result, dict)
    
    def retry(self) -> bool:
        """
        Determine whether to retry after a failure.
        
        Override in subclass for custom retry logic.
        
        Returns:
            True if should retry, False otherwise
        """
        can_retry = self._retry_count < self.max_retries
        if can_retry:
            self._retry_count += 1
            self.metrics.retries += 1
        return can_retry
    
    def record_metrics(self) -> Dict[str, Any]:
        """
        Record and return execution metrics.
        
        Override in subclass to collect additional metrics.
        
        Returns:
            Dictionary of collected metrics
        """
        return self.metrics.to_dict()
    
    def _handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors during execution.
        
        Args:
            error: Exception that occurred
            context: Additional context about where error occurred
        """
        self.metrics.errors += 1
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    def _reset(self) -> None:
        """Reset agent state for new execution."""
        self._retry_count = 0
        self.metrics = ExecutionMetrics(agent_name=self.name)
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make agent callable for use in graph nodes.
        
        This is the primary interface for using agents in LangGraph.
        Handles execution lifecycle and error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent's output
        """
        self._reset()
        self.metrics.status = "running"
        
        try:
            # Execute agent logic
            result = self.execute(state)
            
            # Validate result
            if not self.validate(result):
                raise ValueError(f"Invalid result from {self.name}: {result}")
            
            # Record success
            self.metrics.status = "success"
            self.logger.info(f"{self.name} executed successfully")
            
            return result
            
        except Exception as e:
            self._handle_error(e, f"{self.name} execution")
            self.metrics.status = "failed"
            
            # Attempt retry if possible
            if self.retry():
                self.logger.info(f"Retrying {self.name} (attempt {self._retry_count})")
                return self(state)  # Recursive retry
            
            # If no more retries, add error to state
            error_msg = f"{self.name} failed after {self.max_retries} retries: {str(e)}"
            state.setdefault("errors", []).append(error_msg)
            self.logger.error(error_msg)
            
            return state


class StatefulAgent(BaseAgent):
    """
    Agent with state persistence capability.
    
    Tracks intermediate results and maintains execution state.
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        """Initialize stateful agent."""
        super().__init__(name, max_retries)
        self._execution_history = []
        self._current_result = None
    
    def get_history(self) -> list:
        """Get execution history."""
        return self._execution_history.copy()
    
    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Get last execution result."""
        return self._current_result
    
    def _record_result(self, result: Dict[str, Any]) -> None:
        """Record execution result in history."""
        self._current_result = result
        self._execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "metrics": self.metrics.to_dict(),
        })


class ComposableAgent(BaseAgent):
    """
    Agent that can compose multiple sub-agents.
    
    Useful for complex workflows that involve multiple steps.
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        """Initialize composable agent."""
        super().__init__(name, max_retries)
        self._sub_agents: Dict[str, BaseAgent] = {}
    
    def add_sub_agent(self, key: str, agent: BaseAgent) -> None:
        """
        Add a sub-agent.
        
        Args:
            key: Identifier for the sub-agent
            agent: BaseAgent instance to add
        """
        self._sub_agents[key] = agent
    
    def execute_sub_agent(self, key: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific sub-agent.
        
        Args:
            key: Identifier of sub-agent to execute
            state: Current state
            
        Returns:
            Updated state
        """
        if key not in self._sub_agents:
            raise KeyError(f"Sub-agent '{key}' not found")
        
        return self._sub_agents[key](state)
    
    def get_sub_agents(self) -> Dict[str, BaseAgent]:
        """Get all sub-agents."""
        return self._sub_agents.copy()
