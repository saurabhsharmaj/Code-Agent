# LLM Factory Refactoring Complete

## Overview

All LLM instances have been refactored to use the **Factory Pattern**, eliminating direct LLM creation inside agent nodes.

## What Changed

### ❌ Before (Anti-pattern)
```python
# In each agent file - LLM created directly
planner_llm = ChatGroq(model="llama-3.3-70b", temperature=0.3)
implementer_llm = ChatGroq(model="llama-3.3-70b", temperature=0.1)
reviewer_llm = ChatGroq(model="llama-3.3-70b", temperature=0.2)
decision_llm = ChatGroq(model="llama-3.3-70b", temperature=0.1)

def planner_node(state):
    response = planner_llm.invoke(prompt)  # Direct usage
```

### ✅ After (Best Practice)
```python
# Central factory management
from src.llm.factory import LLMFactory

def planner_node(state):
    llm = LLMFactory.get_planner_llm()  # Factory method
    response = llm.invoke(prompt)
```

## Files Modified

### Agent Files (All Updated)
- ✅ `src/agents/planner/planner.py` - Uses `LLMFactory.get_planner_llm()`
- ✅ `src/agents/implementer/implementer.py` - Uses `LLMFactory.get_implementer_llm()`
- ✅ `src/agents/reviewer/reviewer.py` - Uses `LLMFactory.get_reviewer_llm()`
- ✅ `src/agents/decision/decision.py` - Uses `LLMFactory.get_decision_llm()`

### New Files Created
- ✅ `src/llm/factory.py` - LLMFactory class with caching
- ✅ `src/llm/config.py` - Configuration presets
- ✅ `src/tests/test_llm_factory.py` - Comprehensive tests
- ✅ `LLM_FACTORY_GUIDE.md` - Complete usage guide

### Updated Files
- ✅ `src/llm/__init__.py` - Exports LLMFactory
- ✅ `src/llm/providers/__init__.py` - Updated exports

## Key Features

### 1. **Centralized Management**
All LLM instances created and configured in one place:
```python
# Get agent-specific LLMs
planner_llm = LLMFactory.get_planner_llm()
implementer_llm = LLMFactory.get_implementer_llm()
reviewer_llm = LLMFactory.get_reviewer_llm()
decision_llm = LLMFactory.get_decision_llm()
```

### 2. **Instance Caching**
LLM instances are created once and reused:
```python
llm1 = LLMFactory.get_planner_llm()  # Creates instance
llm2 = LLMFactory.get_planner_llm()  # Returns cached instance (same object)
assert llm1 is llm2  # True
```

### 3. **Environment-Based Configuration**
Configure models and parameters via environment variables:
```bash
export GROQ_API_KEY=your_api_key
export PLANNER_MODEL=llama-3.3-70b-versatile
export PLANNER_TEMPERATURE=0.3
export PLANNER_MAX_TOKENS=2000

export IMPLEMENTER_MODEL=llama-3.3-70b-versatile
export IMPLEMENTER_TEMPERATURE=0.1
export IMPLEMENTER_MAX_TOKENS=1500

export REVIEWER_MODEL=llama-3.3-70b-versatile
export REVIEWER_TEMPERATURE=0.2
export REVIEWER_MAX_TOKENS=2000

export DECISION_MODEL=llama-3.3-70b-versatile
export DECISION_TEMPERATURE=0.1
export DECISION_MAX_TOKENS=1000
```

### 4. **Test Mode Support**
Easy mocking for unit tests:
```python
from src.llm.factory import LLMFactory

# Create mock
mock_llm = MockLLM()

# Enable test mode
LLMFactory.set_test_mode(enabled=True, mock_llm=mock_llm)

# All factory calls return mock
llm = LLMFactory.get_planner_llm()  # Returns mock_llm

# Disable after test
LLMFactory.set_test_mode(enabled=False)
LLMFactory.clear_cache()
```

### 5. **Runtime Configuration Updates**
Update models without restarting:
```python
# Change model at runtime
LLMFactory.update_model("planner", "gpt-4-turbo")

# Next call uses new model
llm = LLMFactory.get_planner_llm()  # Uses gpt-4-turbo
```

### 6. **Configuration Presets**
Built-in configurations for different scenarios:

```python
from src.llm.config import PRODUCTION_CONFIG, COST_OPTIMIZED_CONFIG

# Production uses GPT-4 for quality
# Cost-optimized uses Llama for cheaper models
```

Or set via environment:
```bash
export LLM_CONFIG=production      # High-quality GPT-4 models
export LLM_CONFIG=cost-optimized  # Budget-friendly models
export LLM_CONFIG=development     # Creative, experimental
export LLM_CONFIG=default         # Balanced (default)
```

## Benefits

### ✅ **Testing & Mocking**
```python
def test_planner():
    mock_llm = MockLLM()
    LLMFactory.set_test_mode(True, mock_llm)
    
    result = planner_node(state)
    
    assert result["plan"] == expected_plan
    LLMFactory.set_test_mode(False)
```

### ✅ **Multi-Model Routing**
```python
# Use different models for different agents
LLMFactory.update_model("planner", "gpt-4")          # High-quality planning
LLMFactory.update_model("implementer", "gpt-3.5")    # Faster implementation
LLMFactory.update_model("reviewer", "gpt-4")         # Thorough review
LLMFactory.update_model("decision", "gpt-3.5")       # Quick decisions
```

### ✅ **Failover Strategies**
```python
class FailoverLLMFactory(LLMFactory):
    @classmethod
    def _get_llm(cls, agent_type):
        try:
            return super()._get_llm(agent_type)
        except Exception:
            # Fallback to cheaper model
            return ChatGroq(model="llama-3.3-70b")
```

### ✅ **Cost Optimization**
```python
# Monitor and optimize API costs
LLMFactory.update_model("decision", "llama-3.3-70b")  # Cheaper model
LLMFactory.update_model("reviewer", "gpt-4")           # Worth the cost
```

### ✅ **Configuration Management**
```python
# Adjust all agents from one place
config = LLMFactory.get_config()
config.model_config["planner"]["max_tokens"] = 3000
```

## Architecture

```
Node Function
    ↓
LLMFactory.get_agent_llm()
    ↓
    ├─ Return Cached? → Yes → Return Cached Instance
    ├─ Test Mode? → Yes → Return Mock LLM
    └─ Create New Instance
           ↓
    Read LLMConfig
           ↓
    Create ChatGroq with Config
           ↓
    Cache Instance
           ↓
    Return LLM
```

## Usage Examples

### Basic Usage
```python
from src.llm.factory import LLMFactory

# In any agent node
def my_agent_node(state):
    llm = LLMFactory.get_planner_llm()  # or appropriate agent type
    response = llm.invoke(prompt)
    return result
```

### With Configuration
```python
from src.llm.factory import LLMFactory, LLMConfig

# Custom configuration
config = LLMConfig()
config.model_config["planner"]["model"] = "gpt-4"

LLMFactory.initialize(config)

# Now all factory calls use custom config
```

### With Testing
```python
from src.llm.factory import LLMFactory

class MockLLM:
    def invoke(self, prompt):
        return type('Response', (), {'content': '{"mock": "data"}'})()

# Enable test mode
LLMFactory.set_test_mode(True, MockLLM())

# Test
result = planner_node(state)

# Cleanup
LLMFactory.set_test_mode(False)
LLMFactory.clear_cache()
```

## Testing

Run the comprehensive test suite:
```bash
pytest src/tests/test_llm_factory.py -v
```

Test coverage includes:
- ✅ Factory initialization
- ✅ Instance caching
- ✅ Test mode support
- ✅ Configuration management
- ✅ Model updates
- ✅ Error handling
- ✅ Integration with agents

## Migration Complete

All agents have been migrated:

| Agent | Status | Uses Factory | Tests |
|-------|--------|--------------|-------|
| Planner | ✅ Complete | ✅ Yes | ✅ Included |
| Implementer | ✅ Complete | ✅ Yes | ✅ Included |
| Reviewer | ✅ Complete | ✅ Yes | ✅ Included |
| Decision | ✅ Complete | ✅ Yes | ✅ Included |
| Reporting | ✅ Complete | N/A (no LLM) | ✅ Included |

## Documentation

- **Full Guide:** `LLM_FACTORY_GUIDE.md`
- **This Summary:** `LLM_FACTORY_REFACTORING.md`
- **Configuration:** `src/llm/config.py`
- **Implementation:** `src/llm/factory.py`
- **Tests:** `src/tests/test_llm_factory.py`

## Best Practices

✅ **DO:**
- Use factory methods in node functions
- Configure via environment variables
- Mock in unit tests
- Clear cache between tests
- Use config presets

❌ **DON'T:**
- Create ChatGroq directly in nodes
- Hardcode model names
- Forget to disable test mode
- Use global LLM variables
- Share LLM instances without factory

## Environment Configuration Template

```bash
# .env file
GROQ_API_KEY=gsk_your_key_here

# Configuration preset
LLM_CONFIG=default  # or: production, cost-optimized, development

# Or override specific agents
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

## Summary

✅ **LLM Factory Pattern Implemented**
- All agents use factory pattern
- No direct LLM creation in nodes
- Centralized configuration management
- Full caching and performance optimization
- Complete test support with mocking
- Production-ready implementation

**Key Benefit:** Flexible, testable, and maintainable LLM management across all agents.

See `LLM_FACTORY_GUIDE.md` for complete documentation and examples.

