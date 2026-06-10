# Base Agent Architecture Diagram

## Class Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      BaseAgent (Abstract)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Abstract Methods:                                        │   │
│  │  • execute(state) → Dict                                │   │
│  │                                                           │   │
│  │ Concrete Methods:                                        │   │
│  │  • __call__(state) - Lifecycle manager                 │   │
│  │  • validate(result) - Default validation               │   │
│  │  • retry() - Check if retry possible                   │   │
│  │  • record_metrics() - Get execution metrics            │   │
│  │  • _handle_error(error, context)                       │   │
│  │  • _reset() - Clear retry state                        │   │
│  │                                                           │   │
│  │ Properties:                                              │   │
│  │  • name: str                                            │   │
│  │  • max_retries: int                                     │   │
│  │  • metrics: ExecutionMetrics                           │   │
│  │  • logger: logging.Logger                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │ inherits
                 ┌────────────┼────────────┬──────────────┬──────────────────┐
                 │            │            │              │                  │
        ┌────────┴─────┐ ┌────┴───────┐ ┌─┴──────┐ ┌─────┴──────┐  ┌────────┴────┐
        │ Planner      │ │ Implementer│ │Reviewer│ │ Decision   │  │ Reporter    │
        │    Agent     │ │   Agent    │ │ Agent  │ │   Agent    │  │   Agent     │
        └──────────────┘ └────────────┘ └────────┘ └────────────┘  └─────────────┘
                                  ▲
                                  │ extends
                    ┌─────────────┴──────────────┐
                    │                            │
           ┌────────┴───────┐         ┌──────────┴───────┐
           │ StatefulAgent  │         │ComposableAgent   │
           │ (with history) │         │ (with sub-agents)│
           └────────────────┘         └──────────────────┘
```

## Execution Lifecycle Flow

```
Input State
    │
    ▼
┌─────────────────────────┐
│ agent(state)           │
│ Calls __call__()       │
└────────┬────────────────┘
         │
         ▼
    ┌─────────────┐
    │ _reset()    │  Clear retry count, create new metrics
    └────┬────────┘
         │
         ▼
    ┌──────────────────┐
    │ metrics.status = │  Mark as "running"
    │ "running"        │
    └────┬─────────────┘
         │
         ▼
    ┌─────────────────────────┐
    │ execute(state)          │  Main agent logic
    │ (Must be implemented)   │
    └────┬────────────────────┘
         │
         ├─ Success ─────────┐
         │                   │
         │                   ▼
         │            ┌──────────────────────┐
         │            │ validate(result)     │
         │            │ Check if valid       │
         │            └────┬─────────────────┘
         │                 │
         │                 ├─ Valid ────────┐
         │                 │                │
         │                 │                ▼
         │                 │         ┌──────────────┐
         │                 │         │ metrics.     │
         │                 │         │ status =     │
         │                 │         │ "success"    │
         │                 │         └────┬─────────┘
         │                 │              │
         │                 │              ▼
         │                 │         ┌──────────────┐
         │                 │         │ record_      │
         │                 │         │ metrics()    │
         │                 │         └────┬─────────┘
         │                 │              │
         │                 │              ▼
         │                 │         ┌──────────────┐
         │                 │         │ Return       │
         │                 │         │ result       │
         │                 │         └──────────────┘
         │                 │
         │                 └─ Invalid ────┐
         │                                 │
         ▼                                 ▼
    ┌──────────────────┐         ┌───────────────────────┐
    │ Exception Caught │         │ ValueError: Invalid   │
    │ _handle_error()  │         │ result                │
    └────┬─────────────┘         └──────┬────────────────┘
         │                             │
         ├─────────────────────────────┤
         │
         ▼
    ┌─────────────────┐
    │ metrics.errors  │  Increment error count
    │ += 1            │
    │ metrics.status  │  Set to "failed"
    │ = "failed"      │
    └────┬────────────┘
         │
         ▼
    ┌──────────────────────┐
    │ retry()              │  Check if can retry
    │ _retry_count < max?  │
    └────┬─────────┬───────┘
         │         │
    Can Retry    Exhausted
         │         │
         ▼         ▼
    Recursive  ┌─────────────────┐
    Call to    │ Add error to    │
    __call__   │ state["errors"] │
    (attempt   │ log.error()     │
     +1)       │ Return state    │
               └─────────────────┘
```

## Agent Responsibilities

```
┌────────────────────────────────────────┐
│         PlannerAgent                   │
├────────────────────────────────────────┤
│ Input:  state["task"]                  │
│ Output: state["plan"]                  │
│         state["deployment_config"]     │
│ Logic:  LLM planning → Parse JSON     │
│ Errors: JSON parsing, LLM failures    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│      ImplementerAgent                  │
├────────────────────────────────────────┤
│ Input:  state["deployment_config"]     │
│ Output: state["deployment_yaml"]       │
│ Logic:  Validate config → Generate    │
│         K8s manifests                  │
│ Errors: Invalid config, gen errors    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│       ReviewerAgent                    │
├────────────────────────────────────────┤
│ Input:  state["deployment_yaml"]       │
│ Output: state["review"]                │
│         (score, issues, strengths)     │
│ Logic:  LLM review → Parse JSON       │
│ Errors: JSON parsing, LLM failures    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│      DecisionAgent                     │
├────────────────────────────────────────┤
│ Input:  state["review"]                │
│         state["retries"]               │
│         state["max_retries"]           │
│ Output: state["decision"]              │
│         ("approve", "retry", "reject") │
│ Logic:  LLM decision → Parse JSON     │
│ Errors: JSON parsing, LLM failures    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│      ReporterAgent                     │
├────────────────────────────────────────┤
│ Input:  Full state with all outputs    │
│ Output: state["final_output"]          │
│         state["output_path"]           │
│ Logic:  Generate reports → Save files  │
│ Errors: File I/O, permission errors    │
└────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│ User Task    │
│ "Deploy app" │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ PlannerAgent         │
│ Creates strategy     │
└──────┬───────────────┘
       │
       ├─ plan: "Deploy Node.js app..."
       ├─ deployment_config: {...}
       │
       ▼
┌──────────────────────┐
│ ImplementerAgent     │
│ Generates YAML       │
└──────┬───────────────┘
       │
       ├─ deployment_yaml: "---\napiVersion..."
       │
       ▼
┌──────────────────────┐
│ ReviewerAgent        │
│ Reviews deployment   │
└──────┬───────────────┘
       │
       ├─ review:
       │  ├─ score: 8/10
       │  ├─ issues: [...]
       │  ├─ strengths: [...]
       │
       ▼
┌──────────────────────┐
│ DecisionAgent        │
│ Makes decision       │
└──────┬───────────────┘
       │
       ├─ decision: "approve" | "retry" | "reject"
       │
       ├─ "approve" ──────┐
       │                  │
       │                  ▼
       │          ┌──────────────────┐
       │          │ ReporterAgent    │
       │          │ Generates report │
       │          └──────┬───────────┘
       │                 │
       │                 ├─ final_output: "Complete!"
       │                 ├─ output_path: "./outputs/..."
       │
       ├─ "retry" ────────┐
       │                  │
       │                  └─ Loop back to ImplementerAgent
       │                     (increment retry count)
       │
       └─ "reject" ───────┐
                          │
                          └─ ReporterAgent with rejection
```

## Metrics Tracking

```
Each Agent Tracks:

ExecutionMetrics
├─ execution_time: float
│  └─ Time taken to execute
│
├─ tokens_used: int
│  └─ LLM tokens consumed
│
├─ api_calls: int
│  └─ Number of API calls
│
├─ cache_hits: int
│  └─ LLM cache hits
│
├─ errors: int
│  └─ Number of errors encountered
│
├─ retries: int
│  └─ Number of retry attempts
│
├─ timestamp: str
│  └─ When execution occurred
│
├─ agent_name: str
│  └─ Name of agent
│
└─ status: str
   └─ "pending" | "running" | "success" | "failed"
```

## Error Handling Strategy

```
Error Occurs
    │
    ▼
┌──────────────────────────────────┐
│ Exception Caught                 │
│ _handle_error(error, context)    │
│  • Increment error count         │
│  • Log with context              │
│  • Log full traceback            │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Can Retry?                       │
│ retry_count < max_retries        │
└──────┬──────────────┬────────────┘
       │              │
    YES│              │NO
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────────┐
│ Retry:      │  │ Give Up:         │
│ _retry_count│  │ • Add error msg  │
│ += 1        │  │ • Set status     │
│ Recursive   │  │ • Log error      │
│ __call__()  │  │ • Return state   │
└─────────────┘  └──────────────────┘
```

## Advanced: StatefulAgent

```
                StatefulAgent (extends BaseAgent)
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Execution History          Intermediate Results
         │                               │
    ┌────▼────────────────┐    ┌────────▼──────┐
    │ _execution_history  │    │ _current_     │
    │ [                   │    │ result        │
    │   {                 │    │               │
    │     timestamp,      │    │ Accessible    │
    │     result,         │    │ via:          │
    │     metrics         │    │ get_last_     │
    │   },                │    │ result()      │
    │   {...},            │    │               │
    │   ...               │    └───────────────┘
    │ ]                   │
    │                     │
    │ Accessible via:     │
    │ get_history()       │
    └─────────────────────┘
```

## Advanced: ComposableAgent

```
           ComposableAgent (extends BaseAgent)
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Sub-agents Dictionary        Execution Method
         │                               │
    ┌────▼──────────────────┐  ┌────────▼──────────┐
    │ _sub_agents: {         │  │ execute():        │
    │   "planner": PlannerAg │  │  • Get sub-agent  │
    │   "reviewer": ReviewerA│  │  • Execute it     │
    │   "decision": Decision │  │  • Pass state     │
    │   ...                  │  │  • Collect result │
    │ }                      │  │  • Repeat...      │
    │                        │  │                   │
    │ Methods:              │  └───────────────────┘
    │ • add_sub_agent()     │
    │ • execute_sub_agent() │
    │ • get_sub_agents()    │
    └────────────────────────┘
```

## Integration with LangGraph

```
┌─────────────────────────────────────┐
│    LangGraph StateGraph             │
├─────────────────────────────────────┤
│                                     │
│  graph.add_node("planner", ├─ PlannerAgent instance
│                            │  (callable via __call__)
│  graph.add_node("implement",├─ ImplementerAgent
│                             │
│  graph.add_node("review",   ├─ ReviewerAgent
│                             │
│  graph.add_node("decision", ├─ DecisionAgent
│                             │
│  graph.add_node("report",   ├─ ReporterAgent
│                             │
│  graph.add_edge(...)  [routing logic]
│                                     │
│  graph.compile()                    │
│         │                           │
│         ▼                           │
│  Graph execution calls __call__()   │
│  on each agent instance             │
└─────────────────────────────────────┘
```

## Summary Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    BASE AGENT ARCHITECTURE                    │
│                                                                │
│  BaseAgent                 ┌─ Concrete Agents ─────────────┐  │
│  ├─ execute()              │ ├─ PlannerAgent               │  │
│  ├─ validate()             │ ├─ ImplementerAgent           │  │
│  ├─ retry()                │ ├─ ReviewerAgent              │  │
│  ├─ record_metrics()       │ ├─ DecisionAgent              │  │
│  └─ __call__()             │ └─ ReporterAgent              │  │
│                            └──────────────────────────────┘  │
│                                                                │
│  Advanced Extensions       ┌─ Utility Classes ──────────────┐  │
│  ├─ StatefulAgent          │ ├─ ExecutionMetrics           │  │
│  └─ ComposableAgent        │ └─ (dataclass)                │  │
│                            └──────────────────────────────┘  │
│                                                                │
│  Features                                                     │
│  ├─ Unified interface for all agents                         │
│  ├─ Automatic lifecycle management                           │
│  ├─ Built-in error handling & retry                          │
│  ├─ Metrics collection                                       │
│  ├─ Result validation                                        │
│  ├─ Full backward compatibility                              │
│  └─ Easy extension via inheritance                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

See [BASE_AGENT_GUIDE.md](BASE_AGENT_GUIDE.md) for detailed documentation.
