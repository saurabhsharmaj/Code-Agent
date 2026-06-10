# LLM Factory Pattern Guide

## Overview

The LLM Factory centralizes all LLM instance management across the application, following the factory design pattern. This enables:

- **Multi-model routing** - Use different models for different agents
- **Testing & mocking** - Easy to swap LLMs for testing
- **Failover strategies** - Handle model failures gracefully
- **Cost optimization** - Track and optimize LLM usage
- **Configuration management** - Centralized configuration via environment variables

## Benefits

### ✅ No LLM Creation in Nodes

**Before (Anti-pattern):**
```python
# ❌ BAD - LLM created inside every node
def planner_node(state):
    planner_llm = ChatGroq(model="llama-3.3-70b", temperature=0.3)
    response = planner_llm.invoke(prompt)
```

**After (Best Practice):**
```python
# ✅ GOOD - LLM obtained from factory
def planner_node(state):
    llm = LLMFactory.get_planner_llm()
    response = llm.invoke(prompt)
```

### Why This Matters

1. **Separation of Concerns** - LLM configuration is separate from business logic
2. **Testability** - Easy to mock LLMs for unit tests
3. **Flexibility** - Change models without touching node code
4. **Performance** - LLM instances are cached and reused
5. **Maintainability** - Configuration in one place

---

## Usage

### Basic Usage

```python
from src.llm.factory import LLMFactory

# Get agent-specific LLMs
planner_llm = LLMFactory.get_planner_llm()
implementer_llm = LLMFactory.get_implementer_llm()
reviewer_llm = LLMFactory.get_reviewer_llm()
decision_llm = LLMFactory.get_decision_llm()

# All LLMs are cached and reused
same_llm = LLMFactory.get_planner_llm()  # Returns cached instance
```

### Generic Approach

```python
# Use any agent type dynamically
llm = LLMFactory.get_llm("planner")
llm = LLMFactory.get_llm("implementer")
llm = LLMFactory.get_llm("reviewer")
llm = LLMFactory.get_llm("decision")
```

---

## Configuration

### Environment Variables

Set model and parameters via environment variables:

```bash
# Global settings
export GROQ_API_KEY=your_api_key

# Agent-specific models
export PLANNER_MODEL=llama-3.3-70b-versatile
export IMPLEMENTER_MODEL=llama-3.3-70b-versatile
export REVIEWER_MODEL=llama-3.3-70b-versatile
export DECISION_MODEL=llama-3.3-70b-versatile

# Agent-specific temperatures (creativity)
export PLANNER_TEMPERATURE=0.3
export IMPLEMENTER_TEMPERATURE=0.1
export REVIEWER_TEMPERATURE=0.2
export DECISION_TEMPERATURE=0.1

# Agent-specific max tokens
export PLANNER_MAX_TOKENS=2000
export IMPLEMENTER_MAX_TOKENS=1500
export REVIEWER_MAX_TOKENS=2000
export DECISION_MAX_TOKENS=1000
```

### Programmatic Configuration

```python
from src.llm.factory import LLMFactory, LLMConfig

# Create custom configuration
config = LLMConfig()

# Modify configuration
config.model_config["planner"]["model"] = "gpt-4-turbo"
config.model_config["planner"]["temperature"] = 0.5

# Apply configuration
LLMFactory.initialize(config)
```

### Runtime Model Updates

```python
# Change model at runtime
LLMFactory.update_model("planner", "claude-3-opus")

# Next call will use new model
llm = LLMFactory.get_planner_llm()  # Uses claude-3-opus
```

---

## Testing

### Enable Test Mode

```python
from src.llm.factory import LLMFactory
from langchain_core.language_model import BaseLanguageModel

# Create a mock LLM (implement your own)
class MockLLM(BaseLanguageModel):
    def invoke(self, input):
        return type('Response', (), {'content': '{"mock": "response"}'})()

# Enable test mode
mock_llm = MockLLM()
LLMFactory.set_test_mode(enabled=True, mock_llm=mock_llm)

# All subsequent calls return mock
llm = LLMFactory.get_planner_llm()  # Returns mock_llm
```

### Unit Test Example

```python
import pytest
from src.llm.factory import LLMFactory

@pytest.fixture
def mock_llm():
    """Fixture providing mock LLM"""
    class MockLLM:
        def invoke(self, prompt):
            return type('Response', (), {'content': '{"test": "data"}'})()
    
    return MockLLM()

def test_planner_with_mock(mock_llm):
    """Test planner with mocked LLM"""
    # Enable test mode
    LLMFactory.set_test_mode(enabled=True, mock_llm=mock_llm)
    
    # Run test
    from src.agents.planner import planner_node
    state = {"task": "Test task"}
    result = planner_node(state)
    
    # Verify
    assert result is not None
    
    # Disable test mode
    LLMFactory.set_test_mode(enabled=False)
```

### Clear Cache Between Tests

```python
def test_one():
    # Use default LLM
    llm = LLMFactory.get_planner_llm()
    # ... test ...

def test_two():
    # Clear cache to ensure fresh instance
    LLMFactory.clear_cache()
    llm = LLMFactory.get_planner_llm()
    # ... test ...
```

---

## Advanced Usage

### Multi-Model Routing

```python
# Route different agents to different models based on complexity
config = LLMConfig()
config.model_config["planner"]["model"] = "gpt-4"  # Complex planning
config.model_config["implementer"]["model"] = "gpt-3.5"  # Standard implementation
config.model_config["reviewer"]["model"] = "gpt-4"  # Complex review
config.model_config["decision"]["model"] = "gpt-3.5"  # Simple decision

LLMFactory.initialize(config)
```

### Cost Optimization

```python
# Use cheaper models for less critical tasks
config = LLMConfig()
config.model_config["decision"]["model"] = "llama-3.3-70b"  # Cheap
config.model_config["reviewer"]["model"] = "gpt-4"  # More accurate, higher cost

LLMFactory.initialize(config)
```

### Failover Strategy

```python
class FailoverLLMFactory(LLMFactory):
    """Extended factory with failover support"""
    
    @classmethod
    def _get_llm(cls, agent_type):
        try:
            return super()._get_llm(agent_type)
        except Exception as e:
            print(f"Failed to get {agent_type} LLM, using fallback")
            # Use fallback model
            return ChatGroq(model="llama-3.3-70b")
```

### Monitoring & Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingLLMFactory(LLMFactory):
    """Extended factory with logging"""
    
    @classmethod
    def _get_llm(cls, agent_type):
        llm = super()._get_llm(agent_type)
        config = cls.get_config()
        model = config.model_config[agent_type]["model"]
        logger.info(f"LLM for {agent_type}: {model}")
        return llm
```

---

## Architecture

### Class Structure

```
LLMConfig
├── api_key: str
└── model_config: Dict[str, Dict]
    ├── planner: {model, temperature, max_tokens}
    ├── implementer: {model, temperature, max_tokens}
    ├── reviewer: {model, temperature, max_tokens}
    └── decision: {model, temperature, max_tokens}

LLMFactory
├── _config: LLMConfig
├── _instances: Dict[str, BaseLanguageModel]  (cache)
├── _test_mode: bool
├── _mock_llm: BaseLanguageModel
├── get_planner_llm()
├── get_implementer_llm()
├── get_reviewer_llm()
├── get_decision_llm()
├── set_test_mode()
├── clear_cache()
└── update_model()
```

### Data Flow

```
Agent Node
    ↓
LLMFactory.get_agent_llm()
    ↓
Check Cache → Hit? → Return Cached LLM
    ↓ Miss
Check Test Mode → Enabled? → Return Mock LLM
    ↓ Disabled
Get Config
    ↓
Create ChatGroq with Config
    ↓
Cache Instance
    ↓
Return LLM
```

---

## Migration Guide

### Updating Existing Code

**Before:**
```python
from langchain_groq import ChatGroq

def my_node(state):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=2000,
        api_key=os.getenv("GROQ_API_KEY")
    )
    response = llm.invoke(prompt)
```

**After:**
```python
from src.llm.factory import LLMFactory

def my_node(state):
    llm = LLMFactory.get_planner_llm()  # or appropriate agent type
    response = llm.invoke(prompt)
```

---

## Best Practices

✅ **DO:**
- Get LLMs from factory in node functions
- Use agent-specific factory methods
- Configure via environment variables
- Clear cache in tests
- Use mocking for unit tests

❌ **DON'T:**
- Create ChatGroq instances in nodes
- Hardcode model names in node code
- Share LLM instances across agents without caching
- Forget to disable test mode after tests
- Use global LLM variables

---

## Examples

### Complete Agent Implementation

```python
from src.llm.factory import LLMFactory
from langchain_core.prompts import PromptTemplate

PROMPT = PromptTemplate(
    input_variables=["input"],
    template="Process: {input}"
)

def my_agent_node(state):
    """Example agent using factory"""
    try:
        # Get LLM from factory (best practice)
        llm = LLMFactory.get_planner_llm()
        
        # Format prompt
        prompt = PROMPT.format(input=state["input"])
        
        # Invoke
        response = llm.invoke(prompt)
        
        # Process response
        return {
            "output": response.content,
            "errors": []
        }
    except Exception as e:
        return {
            "output": None,
            "errors": [str(e)]
        }
```

### Complete Test

```python
import pytest
from src.llm.factory import LLMFactory
from src.agents.planner import planner_node

def test_planner_with_mock():
    """Test planner with mock LLM"""
    
    # Create mock
    class MockResponse:
        content = '{"plan": "test", "strategy": "test"}'
    
    class MockLLM:
        def invoke(self, prompt):
            return MockResponse()
    
    # Setup
    mock_llm = MockLLM()
    LLMFactory.set_test_mode(enabled=True, mock_llm=mock_llm)
    
    try:
        # Test
        state = {
            "task": "Create deployment",
            "plan": "",
            "deployment_config": {},
            "deployment_yaml": "",
            "review": {},
            "decision": "",
            "retries": 0,
            "max_retries": 3,
            "errors": [],
            "final_output": None
        }
        
        result = planner_node(state)
        
        # Verify
        assert result["plan"] == "test"
        assert len(result["errors"]) == 0
    
    finally:
        # Cleanup
        LLMFactory.set_test_mode(enabled=False)
        LLMFactory.clear_cache()
```

---

## Environment Configuration Example

```bash
# .env file
GROQ_API_KEY=gsk_your_api_key_here

# Use different models for different agents
PLANNER_MODEL=llama-3.3-70b-versatile
PLANNER_TEMPERATURE=0.3
PLANNER_MAX_TOKENS=2000

IMPLEMENTER_MODEL=llama-3.3-70b-versatile
IMPLEMENTER_TEMPERATURE=0.1
IMPLEMENTER_MAX_TOKENS=1500

REVIEWER_MODEL=llama-3.3-70b-versatile
REVIEWER_TEMPERATURE=0.2
REVIEWER_MAX_TOKENS=2000

DECISION_MODEL=llama-3.3-70b-versatile
DECISION_TEMPERATURE=0.1
DECISION_MAX_TOKENS=1000
```

---

## Summary

The LLM Factory Pattern provides:

1. **Centralized management** of all LLM instances
2. **Easy configuration** via environment variables
3. **Testability** with mock support
4. **Performance** through instance caching
5. **Flexibility** for model routing and failover
6. **Best practices** enforcement in codebase

**Key Takeaway:** Always use `LLMFactory.get_agent_llm()` in node functions instead of creating LLM instances directly.

