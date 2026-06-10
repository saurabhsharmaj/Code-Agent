# Base Agent Class Architecture

## Overview

All agents now inherit from the `BaseAgent` abstract class, providing a unified interface with common functionality including execution lifecycle management, result validation, retry logic, and metrics collection.

## Class Hierarchy

```
BaseAgent (abstract)
├── PlannerAgent
├── ImplementerAgent
├── ReviewerAgent
├── DecisionAgent
├── ReporterAgent
├── StatefulAgent (mixin for state persistence)
└── ComposableAgent (mixin for sub-agents)
```

## Base Agent Class

### BaseAgent

Abstract base class that all agents inherit from. Provides:

- **Execution Lifecycle**: `__call__()` method handles execution, validation, and error handling
- **Metrics Collection**: Automatic tracking of execution time, errors, retries
- **Retry Logic**: Configurable retry mechanism with automatic retry attempts
- **Error Handling**: Centralized error handling and logging
- **Validation**: Result validation before returning

### Key Methods

```python
class BaseAgent(ABC):
    def __init__(self, name: str, max_retries: int = 3)
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main agent logic - must be implemented by subclass"""
        pass
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """Validate output - override in subclass for custom validation"""
        pass
    
    def retry(self) -> bool:
        """Determine if retry is possible"""
        pass
    
    def record_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        pass
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Make agent callable - handles lifecycle automatically"""
        pass
```

## Execution Lifecycle

When you call an agent (using `__call__`), it automatically:

1. **Reset** - Clear previous state
2. **Execute** - Run the `execute()` method
3. **Validate** - Check result is valid
4. **Record** - Mark as successful
5. **On Error**:
   - Log error
   - Attempt retry if available
   - Add error to state if retries exhausted

```python
# Automatic lifecycle
agent = PlannerAgent(name="planner", max_retries=3)
result = agent(state)  # Handles all lifecycle automatically
```

## Metrics Collection

Every agent automatically tracks:

```python
@dataclass
class ExecutionMetrics:
    execution_time: float
    tokens_used: int
    api_calls: int
    cache_hits: int
    errors: int
    retries: int
    timestamp: str
    agent_name: str
    status: str  # pending, running, success, failed
```

Access metrics:

```python
agent = ReviewerAgent(name="reviewer")
result = agent(state)

# Get metrics
metrics = agent.record_metrics()
print(f"Status: {metrics['status']}")
print(f"Execution Time: {metrics['execution_time']}s")
print(f"Errors: {metrics['errors']}")
print(f"Retries: {metrics['retries']}")
```

## Agent Implementations

### PlannerAgent

Creates deployment strategies from user requirements.

```python
from src.agents import PlannerAgent

agent = PlannerAgent(name="planner")
state = {
    "task": "Create deployment for Node.js app",
    "errors": []
}
result = agent(state)

# Returns:
# {
#     "plan": "Strategy description...",
#     "deployment_config": {...},
#     "errors": []
# }
```

**Methods:**
- `execute(state)` - Generates deployment plan using LLM
- `validate(result)` - Checks for valid plan and config

### ImplementerAgent

Generates Kubernetes YAML files from deployment config.

```python
from src.agents import ImplementerAgent

agent = ImplementerAgent(name="implementer")
state = {
    "deployment_config": {...},
    "errors": []
}
result = agent(state)

# Returns:
# {
#     "deployment_yaml": "---\napiVersion: ...",
#     "errors": []
# }
```

**Methods:**
- `execute(state)` - Generates K8s YAML manifests
- `validate(result)` - Checks for valid YAML

### ReviewerAgent

Reviews deployments for best practices and security.

```python
from src.agents import ReviewerAgent

agent = ReviewerAgent(name="reviewer")
state = {
    "deployment_yaml": "...",
    "errors": []
}
result = agent(state)

# Returns:
# {
#     "review": {
#         "score": 8,
#         "issues": [...],
#         "recommendation": "...",
#         "strengths": [...],
#         "improvements": [...]
#     },
#     "errors": []
# }
```

**Methods:**
- `execute(state)` - Reviews deployment quality
- `validate(result)` - Checks for valid review

### DecisionAgent

Makes approve/retry decisions based on review scores.

```python
from src.agents import DecisionAgent

agent = DecisionAgent(name="decision")
state = {
    "review": {"score": 8, ...},
    "retries": 0,
    "max_retries": 3,
    "errors": []
}
result = agent(state)

# Returns:
# {
#     "decision": "approve",  # or "retry" or "reject"
#     "errors": []
# }
```

**Methods:**
- `execute(state)` - Makes approval decision
- `validate(result)` - Checks for valid decision

### ReporterAgent

Generates final reports and saves output files.

```python
from src.agents import ReporterAgent

agent = ReporterAgent(name="reporter")
state = {
    "task": "...",
    "plan": "...",
    "deployment_yaml": "...",
    "review": {...},
    "decision": "approve",
    "errors": []
}
result = agent(state)

# Returns:
# {
#     "final_output": "...",
#     "output_path": "/path/to/outputs/20260610_143022",
#     "errors": []
# }
```

**Methods:**
- `execute(state)` - Generates and saves reports
- `validate(result)` - Checks for output files

## Advanced Agent Types

### StatefulAgent

Maintains execution history and intermediate results.

```python
from src.agents import StatefulAgent

class MyStatefulAgent(StatefulAgent):
    def execute(self, state):
        # Your logic here
        pass

agent = MyStatefulAgent(name="my-agent")
result = agent(state)

# Access history
history = agent.get_history()
last_result = agent.get_last_result()
```

**Methods:**
- `get_history()` - Get all execution results
- `get_last_result()` - Get most recent result
- `_record_result(result)` - Internal: record result

### ComposableAgent

Compose multiple sub-agents into a complex workflow.

```python
from src.agents import ComposableAgent, PlannerAgent, ReviewerAgent

class ComplexAgent(ComposableAgent):
    def execute(self, state):
        # Execute planner
        state = self.execute_sub_agent("planner", state)
        
        # Execute reviewer
        state = self.execute_sub_agent("reviewer", state)
        
        return state

agent = ComplexAgent(name="complex")
agent.add_sub_agent("planner", PlannerAgent())
agent.add_sub_agent("reviewer", ReviewerAgent())

result = agent(state)
```

**Methods:**
- `add_sub_agent(key, agent)` - Add a sub-agent
- `execute_sub_agent(key, state)` - Execute specific sub-agent
- `get_sub_agents()` - Get all sub-agents

## Backward Compatibility

All agents maintain backward compatibility through node functions:

```python
# Old way (still works)
from src.agents import planner_node

result = planner_node(state)

# New way (preferred)
from src.agents import PlannerAgent

agent = PlannerAgent(name="planner")
result = agent(state)
```

## Using Agents in LangGraph

The node functions work directly with LangGraph:

```python
from langgraph.graph import StateGraph
from src.agents import planner_node, implement_node

graph_builder = StateGraph(AgentState)

# Old way (still works)
graph_builder.add_node("planner", planner_node)

# Or use agent directly
planner = PlannerAgent(name="planner")
graph_builder.add_node("planner", planner)  # Callable via __call__
```

## Error Handling

Agents automatically handle errors with retry logic:

```python
agent = PlannerAgent(name="planner", max_retries=3)

state = {"task": "..."}
result = agent(state)

# If error occurs:
# 1. Error is logged
# 2. Error count incremented
# 3. Retry attempted (up to max_retries)
# 4. If retries exhausted, error added to state

if result.get("errors"):
    print(f"Agent failed: {result['errors']}")
```

## Best Practices

### ✅ DO

1. **Use agent classes in new code**
   ```python
   agent = PlannerAgent(name="planner")
   result = agent(state)
   ```

2. **Set appropriate max_retries**
   ```python
   agent = ReviewerAgent(name="reviewer", max_retries=2)
   ```

3. **Check metrics after execution**
   ```python
   agent(state)
   metrics = agent.record_metrics()
   log_metrics(metrics)
   ```

4. **Inherit for custom agents**
   ```python
   class CustomAgent(BaseAgent):
       def execute(self, state):
           # Your logic
           pass
       
       def validate(self, result):
           # Your validation
           pass
   ```

5. **Use error handling**
   ```python
   result = agent(state)
   if result.get("errors"):
       handle_errors(result["errors"])
   ```

### ❌ DON'T

1. **Don't create nodes directly for new workflows**
   ```python
   # Old way - avoid in new code
   result = planner_node(state)
   ```

2. **Don't manually implement retry logic**
   ```python
   # Don't do this - BaseAgent handles it
   for attempt in range(3):
       try:
           result = agent(state)
       except:
           pass
   ```

3. **Don't modify internal state directly**
   ```python
   # Don't do this
   agent.metrics.status = "success"
   agent._retry_count = 5
   ```

4. **Don't forget to handle errors**
   ```python
   # Always check
   result = agent(state)
   if result.get("errors"):
       # Handle errors
   ```

## Testing with BaseAgent

```python
import pytest
from unittest.mock import MagicMock
from src.agents import PlannerAgent

def test_planner_agent():
    # Create agent
    agent = PlannerAgent(name="planner")
    
    # Prepare state
    state = {"task": "Test task"}
    
    # Execute
    result = agent(state)
    
    # Verify
    assert result.get("plan") is not None
    assert result.get("deployment_config") is not None
    
    # Check metrics
    metrics = agent.record_metrics()
    assert metrics["status"] == "success"
    assert metrics["errors"] == 0
```

## Configuration

Agents read configuration from environment variables:

```bash
# Agent-specific configuration
PLANNER_MODEL=llama-3.3-70b-versatile
PLANNER_TEMPERATURE=0.3
PLANNER_MAX_TOKENS=2000

REVIEWER_MODEL=gpt-4-turbo
REVIEWER_TEMPERATURE=0.2
REVIEWER_MAX_TOKENS=3000
```

## Migration Guide

### From Node Functions to Agent Classes

**Before (old way):**
```python
from src.agents import planner_node

def my_workflow():
    state = {"task": "..."}
    state = planner_node(state)
    state = implement_node(state)
    return state
```

**After (new way):**
```python
from src.agents import PlannerAgent, ImplementerAgent

def my_workflow():
    state = {"task": "..."}
    
    planner = PlannerAgent(name="planner")
    state = planner(state)
    
    implementer = ImplementerAgent(name="implementer")
    state = implementer(state)
    
    return state
```

## Summary

| Feature | BaseAgent | Benefit |
|---------|-----------|---------|
| **Unified Interface** | All agents same methods | Consistency |
| **Automatic Lifecycle** | Built-in error handling | Reliability |
| **Metrics** | Automatic tracking | Observability |
| **Retry Logic** | Built-in retry mechanism | Resilience |
| **Validation** | Validate results | Quality |
| **Logging** | Automatic logging | Debugging |
| **Testing** | Easy mocking | Testability |
| **Extensibility** | Inherit for custom agents | Flexibility |

See `src/agents/base.py` for complete implementation details.
