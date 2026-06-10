# Quick Reference - New Directory Structure

## Module Locations

### 🤖 Agents
```
src/agents/
├── planner/          → Task planning
├── implementer/      → Implementation (formerly "implement")
├── reviewer/         → Code/deployment review
├── decision/         → Decision making
├── reporting/        → Report generation (formerly "report")
├── security/         → Security checks (placeholder)
└── compliance/       → Compliance checks (placeholder)
```

**Import:** `from src.agents.planner import planner_node`

### 📊 State Management
```
src/state/
├── schemas.py        → AgentState TypedDict
├── checkpoints.py    → Workflow checkpoints
└── persistence.py    → State persistence layer
```

**Import:** `from src.state.schemas import AgentState`

### 🔧 Tools
```
src/tools/
├── kubernetes/       → K8s utilities (k8s_generator.py)
├── aws/              → AWS integrations (placeholder)
├── jira/             → Jira integration (placeholder)
├── servicenow/       → ServiceNow integration (placeholder)
├── github/           → GitHub integration (placeholder)
└── database/         → Database tools (placeholder)
```

**Import:** `from src.tools.kubernetes import K8sDeploymentGenerator`

### 📈 Graphs
```
src/graphs/
├── deployment_graph/      → K8s deployment workflow (builder.py)
├── incident_graph/        → Incident response (placeholder)
├── code_review_graph/     → Code review workflow (placeholder)
└── rag_graph/            → RAG workflow (placeholder)
```

**Import:** `from src.graphs.deployment_graph import build_deployment_graph`

### 🧠 LLM
```
src/llm/
├── providers/        → LLM provider implementations
├── prompts/          → Prompt templates (placeholder)
├── guardrails/       → Output guardrails (placeholder)
└── routing/          → LLM routing logic (placeholder)
```

**Import:** `from src.llm.providers import get_llm`

### 💾 Memory
```
src/memory/
├── vector/           → Vector embeddings (placeholder)
├── episodic/         → Event-based memory (placeholder)
├── semantic/         → Semantic information (placeholder)
└── session/          → Session memory (placeholder)
```

### 🔍 Observability
```
src/observability/
├── tracing/          → Distributed tracing (placeholder)
├── metrics/          → Metrics collection (placeholder)
├── logging/          → Centralized logging (placeholder)
└── evaluations/      → Model evaluations (placeholder)
```

### 🔒 Security
```
src/security/
├── pii/              → PII protection (placeholder)
├── secrets/          → Secrets management (placeholder)
├── policies/         → Security policies (placeholder)
└── approvals/        → Approval workflows (placeholder)
```

### 🌐 API
```
src/api/
├── rest/             → REST endpoints (placeholder)
├── websocket/        → WebSocket connections (placeholder)
└── grpc/             → gRPC services (placeholder)
```

### ⚙️ Other
```
src/
├── config/           → Configuration (placeholder)
├── tests/            → Test modules
└── main.py           → Main entry point
```

---

## Common Tasks

### Run the Application
```bash
# Option 1: Direct
python src/main.py

# Option 2: Via entry point
python main_entry.py

# Option 3: Programmatic
from src.main import run_k8s_deployment_flow
run_k8s_deployment_flow(task)
```

### Add a New Agent
1. Create `src/agents/my_agent/`
2. Create `__init__.py` and `my_agent.py`
3. Define your node function
4. Update `src/agents/__init__.py`
5. Add to graph in `src/graphs/deployment_graph/builder.py`

### Add a New Tool
1. Create `src/tools/my_tool/`
2. Create `__init__.py` and implementation
3. Update `src/tools/__init__.py`

### Use a Component
```python
# Agents
from src.agents.planner import planner_node

# State
from src.state.schemas import AgentState
from src.state.persistence import StateStore

# Tools
from src.tools.kubernetes import K8sDeploymentGenerator

# Graphs
from src.graphs.deployment_graph import build_deployment_graph
```

---

## File Mappings

| Old Location | New Location | Module |
|---|---|---|
| `planner-agent/planner_node.py` | `src/agents/planner/planner.py` | planner_node |
| `implement-agent/implement_node.py` | `src/agents/implementer/implementer.py` | implement_node |
| `review-agent/review_node.py` | `src/agents/reviewer/reviewer.py` | review_node |
| `decision-agent/decision_node.py` | `src/agents/decision/decision.py` | decision_node |
| `report-agent/report_node.py` | `src/agents/reporting/reporter.py` | report_node |
| `common/agentstatus.py` | `src/state/schemas.py` | AgentState |
| `common/k8s_generator.py` | `src/tools/kubernetes/k8s_generator.py` | K8sDeploymentGenerator |
| `common/reviewoutput.py` | `src/state/schemas.py` | ReviewOutput |
| `main.py` | `src/main.py` | run_k8s_deployment_flow |

---

## Directory Tree

```
Code-Agent/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner/
│   │   ├── implementer/
│   │   ├── reviewer/
│   │   ├── decision/
│   │   ├── reporting/
│   │   ├── security/
│   │   └── compliance/
│   ├── state/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   ├── checkpoints.py
│   │   └── persistence.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── kubernetes/
│   │   ├── aws/
│   │   ├── jira/
│   │   ├── servicenow/
│   │   ├── github/
│   │   └── database/
│   ├── graphs/
│   │   ├── __init__.py
│   │   ├── deployment_graph/
│   │   ├── incident_graph/
│   │   ├── code_review_graph/
│   │   └── rag_graph/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── providers/
│   │   ├── prompts/
│   │   ├── guardrails/
│   │   └── routing/
│   ├── memory/
│   │   ├── vector/
│   │   ├── episodic/
│   │   ├── semantic/
│   │   └── session/
│   ├── observability/
│   │   ├── tracing/
│   │   ├── metrics/
│   │   ├── logging/
│   │   └── evaluations/
│   ├── security/
│   │   ├── pii/
│   │   ├── secrets/
│   │   ├── policies/
│   │   └── approvals/
│   ├── api/
│   │   ├── rest/
│   │   ├── websocket/
│   │   └── grpc/
│   ├── config/
│   └── tests/
├── main.py (entry point wrapper)
├── main_entry.py (alternative entry point)
├── requirements.txt
├── REFACTORING_GUIDE.md
├── REFACTORING_COMPLETE.md
└── (other project files)
```

---

## What's Implemented ✅

- ✅ Full state management (schemas, checkpoints, persistence)
- ✅ All 5 agents (planner, implementer, reviewer, decision, reporting)
- ✅ Kubernetes tools (generator, validator)
- ✅ Deployment graph builder
- ✅ LLM providers interface
- ✅ Main execution framework

## What's Ready to Implement 🚀

- 🚀 Additional agents (security, compliance)
- 🚀 More tools (AWS, Jira, ServiceNow, GitHub)
- 🚀 Additional graphs (incident, code review, RAG)
- 🚀 Memory systems (vector, episodic, semantic)
- 🚀 Observability (tracing, metrics, logging)
- 🚀 Security modules (PII, secrets, policies)
- 🚀 API endpoints (REST, WebSocket, gRPC)

---

**See REFACTORING_GUIDE.md for detailed information**

