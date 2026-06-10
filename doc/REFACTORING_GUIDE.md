# Code Refactoring Guide

## Overview
The codebase has been refactored from a flat, hyphenated directory structure to a modern, modular architecture following Python packaging best practices.

## Directory Structure Changes

### Old Structure
```
root/
├── main.py
├── routes.py
├── common/
│   ├── agentstatus.py
│   ├── k8s_generator.py
│   └── reviewoutput.py
├── planner-agent/
│   └── planner_node.py
├── implement-agent/
│   └── implement_node.py
├── review-agent/
│   └── review_node.py
├── decision-agent/
│   └── decision_node.py
└── report-agent/
    └── report_node.py
```

### New Structure
```
root/
├── src/
│   ├── __init__.py
│   ├── main.py (entry point)
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner/
│   │   │   ├── __init__.py
│   │   │   └── planner.py
│   │   ├── implementer/
│   │   │   ├── __init__.py
│   │   │   └── implementer.py
│   │   ├── reviewer/
│   │   │   ├── __init__.py
│   │   │   └── reviewer.py
│   │   ├── decision/
│   │   │   ├── __init__.py
│   │   │   └── decision.py
│   │   ├── reporting/
│   │   │   ├── __init__.py
│   │   │   └── reporter.py
│   │   ├── security/
│   │   └── compliance/
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── checkpoints.py
│   │   └── persistence.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── kubernetes/
│   │   │   ├── __init__.py
│   │   │   └── k8s_generator.py
│   │   ├── aws/
│   │   ├── jira/
│   │   ├── servicenow/
│   │   ├── github/
│   │   └── database/
│   │
│   ├── graphs/
│   │   ├── __init__.py
│   │   ├── deployment_graph/
│   │   │   ├── __init__.py
│   │   │   └── builder.py
│   │   ├── incident_graph/
│   │   ├── code_review_graph/
│   │   └── rag_graph/
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── providers/
│   │   ├── prompts/
│   │   ├── guardrails/
│   │   └── routing/
│   │
│   ├── memory/
│   │   ├── vector/
│   │   ├── episodic/
│   │   ├── semantic/
│   │   └── session/
│   │
│   ├── observability/
│   │   ├── tracing/
│   │   ├── metrics/
│   │   ├── logging/
│   │   └── evaluations/
│   │
│   ├── security/
│   │   ├── pii/
│   │   ├── secrets/
│   │   ├── policies/
│   │   └── approvals/
│   │
│   ├── api/
│   │   ├── rest/
│   │   ├── websocket/
│   │   └── grpc/
│   │
│   ├── config/
│   └── tests/
│
├── main_entry.py (backward compatibility)
├── main.py (see main_entry.py)
└── requirements.txt
```

## Key Changes

### 1. Agent Files
- **Old**: `planner-agent/planner_node.py`
- **New**: `src/agents/planner/planner.py`
  - Removed hyphenation (Python best practice)
  - Organized under agents/ with descriptive naming
  - Importable as: `from src.agents.planner import planner_node`

### 2. State Management
- **Old**: `common/agentstatus.py`
- **New**: `src/state/schemas.py`
  - Dedicated state module with additional capabilities:
    - `schemas.py` - State definitions
    - `checkpoints.py` - Workflow checkpoints
    - `persistence.py` - State persistence layer

### 3. Tools
- **Old**: `common/k8s_generator.py`
- **New**: `src/tools/kubernetes/k8s_generator.py`
  - Organized by tool type
  - Easy to extend with additional tools (AWS, Jira, etc.)

### 4. Workflow Graph
- **Old**: Defined inline in main.py
- **New**: `src/graphs/deployment_graph/builder.py`
  - Separated graph construction logic
  - Extensible for multiple graph types

### 5. LLM Management
- **Old**: Inline LLM initialization
- **New**: `src/llm/providers/__init__.py`
  - Centralized LLM provider configuration
  - Easy provider switching (Groq, OpenAI, etc.)

## Import Changes

### Old Import Style
```python
from common.agentstatus import AgentState
from planner-agent.planner_node import planner_node
from common.k8s_generator import K8sDeploymentGenerator
```

### New Import Style
```python
from src.state.schemas import AgentState
from src.agents.planner import planner_node
from src.tools.kubernetes import K8sDeploymentGenerator
from src.graphs.deployment_graph import build_deployment_graph
```

## Running the Application

### Method 1: Direct Execution
```bash
cd src
python main.py
```

### Method 2: Using Entry Point
```bash
python main_entry.py
```

### Method 3: Programmatic Usage
```python
from src.main import run_k8s_deployment_flow

task = "Your deployment task..."
result = run_k8s_deployment_flow(task, max_retries=3)
```

## Migration Path

If you have custom code using the old structure:

1. **Update imports:**
   ```python
   # Old
   from common.agentstatus import AgentState
   
   # New
   from src.state.schemas import AgentState
   ```

2. **Use new module paths:**
   ```python
   # Old
   from planner-agent.planner_node import planner_node
   
   # New
   from src.agents.planner import planner_node
   ```

3. **Access tools:**
   ```python
   # Old
   from common.k8s_generator import K8sDeploymentGenerator
   
   # New
   from src.tools.kubernetes import K8sDeploymentGenerator
   ```

## Benefits of New Structure

✅ **Scalability** - Easy to add new agents, tools, and modules
✅ **Maintainability** - Clear separation of concerns
✅ **Extensibility** - Dedicated modules for future features (security, compliance, observability)
✅ **Standards** - Follows Python packaging best practices
✅ **IDE Support** - Better code completion and navigation
✅ **Testing** - Easier to test isolated components
✅ **Documentation** - Self-documenting module structure

## Backward Compatibility

The `main_entry.py` file provides a backward-compatible entry point that imports from the new structure while maintaining the same API.

## Future Enhancements

The new structure supports:
- Additional agents (security, compliance)
- Multiple graph types (incident response, code review, RAG)
- Advanced memory systems (vector, episodic, semantic)
- Comprehensive observability (tracing, metrics, logging)
- Security modules (PII protection, secrets management)
- Multiple API endpoints (REST, WebSocket, gRPC)

## Configuration

Place environment variables in `.env`:
```
GROQ_API_KEY=your_api_key_here
```

## Questions?

Refer to individual module `__init__.py` files for module-specific documentation and exports.
