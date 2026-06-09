# Visual Architecture Diagrams

## 1. Complete Agent Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER TASK INPUT                             │
│  "Create K8s deployment for Flask app with 3 replicas..."      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ╔═════════════════╗
                    ║  PLANNER AGENT  ║
                    ║ Using Groq LLM  ║
                    ╚════════┬════════╝
                             │
        ┌────────────────────┴────────────────────┐
        │ Analyzes Requirements                  │
        │ Creates Strategy                       │
        │ Generates Config Schema                │
        │ (app_name, image, replicas, port...)  │
        └────────────────────┬────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  State Updated  │
                    │  - plan: str    │
                    │  - config: Dict │
                    └────────┬────────┘
                             │
                             ▼
                    ╔═════════════════╗
                    ║ IMPLEMENT AGENT ║
                    ║  K8s Generator  ║
                    ╚════════┬════════╝
                             │
        ┌────────────────────┴────────────────────┐
        │ Validates Configuration                │
        │ Generates Deployment YAML              │
        │ Generates Service YAML                 │
        │ Generates HPA YAML                     │
        │ Combines with YAML separators          │
        └────────────────────┬────────────────────┘
                             │
                    ┌────────▼──────────┐
                    │   State Updated   │
                    │ - deployment_yaml │
                    └────────┬──────────┘
                             │
                             ▼
                    ╔═════════════════╗
                    ║  REVIEW AGENT   ║
                    ║ Using Groq LLM  ║
                    ╚════════┬════════╝
                             │
        ┌────────────────────┴────────────────────┐
        │ Validates Best Practices               │
        │ Checks Security Considerations         │
        │ Scores Production Readiness (0-10)     │
        │ Identifies Issues & Strengths          │
        │ Provides Recommendations               │
        └────────────────────┬────────────────────┘
                             │
                    ┌────────▼────────────┐
                    │   State Updated     │
                    │ - review: Dict      │
                    │   * score (0-10)    │
                    │   * issues          │
                    │   * strengths       │
                    └────────┬────────────┘
                             │
                             ▼
                    ╔═════════════════╗
                    ║ DECISION AGENT  ║
                    ║ Using Groq LLM  ║
                    ╚════════┬════════╝
                             │
                    ┌────────▼─────────┐
                    │  Evaluate Score  │
                    │  Check Retries   │
                    │  Make Decision   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         Score < 6      6 ≤ Score < 8   Score ≥ 8
         Retries < Max  Retries < Max   OR Max Retries
              │              │              │
              ▼              ▼              ▼
            RETRY         RETRY         APPROVE
         [Loop Back]   [Loop Back]     [Continue]
              │              │              │
              └──────────────┴──────────────┘
                             │
                             ▼
                    ╔═════════════════╗
                    ║  REPORT AGENT   ║
                    ║  File I/O       ║
                    ╚════════┬════════╝
                             │
        ┌────────────────────┴────────────────────┐
        │ Creates Output Directory (timestamp)    │
        │ Saves deployment.yaml                  │
        │ Generates report.json                  │
        │ Creates SUMMARY.txt                    │
        │ Provides Deployment Instructions       │
        └────────────────────┬────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  ✅ FINAL OUTPUT   │
                    │ outputs/[TIME]/    │
                    │ - deployment.yaml  │
                    │ - report.json      │
                    │ - SUMMARY.txt      │
                    └────────────────────┘
```

---

## 2. Retry Loop Mechanism

```
                    START: FIRST ATTEMPT
                            ↓
                    ┌───────────────┐
                    │    PLANNER    │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │  IMPLEMENT    │ Score: 6.5
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │    REVIEW     │ "Missing health checks"
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │   DECISION    │
                    │ Score 6.5 < 8 │
                    │ Retries 0 < 3 │
                    └───────┬───────┘
                            ↓
                    ⚠️ RETRY DECISION
                    Feedback: "Add health probes"
                            │
                            └──────────────────┐
                                               ↓
                            START: SECOND ATTEMPT
                                (with feedback)
                                    ↓
                            ┌───────────────┐
                            │    PLANNER    │
                            │ (Revised)     │
                            └───────┬───────┘
                                    ↓
                            ┌───────────────┐
                            │  IMPLEMENT    │ (Improved)
                            │ + Health Probes
                            └───────┬───────┘
                                    ↓
                            ┌───────────────┐
                            │    REVIEW     │ Score: 8.5
                            │ "Good config"
                            └───────┬───────┘
                                    ↓
                            ┌───────────────┐
                            │   DECISION    │
                            │ Score 8.5 ≥ 8 │
                            └───────┬───────┘
                                    ↓
                            ✅ APPROVE DECISION
                                    │
                                    └──────────────────┐
                                                       ↓
                                        ┌────────────────────┐
                                        │   REPORT AGENT     │
                                        │ (Final Output)     │
                                        └────────────────────┘
```

---

## 3. Decision Tree

```
                         REVIEW SCORE
                             │
            ┌────────────────┬┴┬────────────────┐
            │                │ │                │
         < 5 (Poor)        5-6 (Fair)       7-8 (Good)      ≥ 9 (Excellent)
            │                │ │                │
            ▼                ▼ ▼                ▼             ▼
      MUST CHECK        CONSIDER        GOOD            EXCELLENT
      RETRIES           RETRIES         CONFIG          CONFIG
            │                │ │          │               │
        ┌─────────┐       ┌────┴──────┐   │               │
        │          │       │           │   │               │
    Retries    Retries    │           │   │               │
    < Max      ≥ Max      │           │   │               │
        │          │      │           │   │               │
        ▼          ▼      ▼           ▼   ▼               ▼
      RETRY    REJECT   RETRY      APPROVE          APPROVE
      [Loop]             [Loop]     [Report]         [Report]
                                                     (Immediate)
```

---

## 4. State Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    INITIAL STATE                        │
│  task: "User requirement"                              │
│  plan: ""                                              │
│  deployment_config: {}                                 │
│  deployment_yaml: ""                                   │
│  review: {}                                            │
│  decision: ""                                          │
│  retries: 0                                            │
│  max_retries: 3                                        │
│  errors: []                                            │
└─────────────────────────┬───────────────────────────────┘
                          │
                ┌─────────▼──────────┐
                │  PLANNER NODE      │
                └─────────┬──────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   AFTER PLANNER                         │
│  + plan: "Strategy to deploy Flask..."                │
│  + deployment_config: {                               │
│      app_name: "flask-app",                           │
│      image: "flask:v1.0",                             │
│      replicas: 3,                                     │
│      port: 8080,                                      │
│      ...                                              │
│    }                                                  │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────▼────────────┐
            │  IMPLEMENT NODE          │
            └─────────────┬────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                 AFTER IMPLEMENT                         │
│  + deployment_yaml: "apiVersion: apps/v1               │
│                     kind: Deployment                   │
│                     metadata:                          │
│                       name: flask-app                  │
│                     spec:                              │
│                       replicas: 3                      │
│                       ..."                             │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────▼──────────┐
            │  REVIEW NODE           │
            └─────────────┬──────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   AFTER REVIEW                          │
│  + review: {                                           │
│      score: 8,                                         │
│      issues: ["Missing probes"],                       │
│      strengths: ["Good resource limits"],              │
│      recommendation: "Consider adding..."              │
│    }                                                   │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────▼─────────┐
            │  DECISION NODE        │
            └─────────────┬─────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                 AFTER DECISION                          │
│  + decision: "approve"                                 │
│  + retries: 0                                          │
│  + errors: []                                          │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────▼──────────┐
            │  REPORT NODE           │
            └─────────────┬──────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   FINAL STATE                           │
│  + final_output: "Deployment generation complete..."   │
│  + output_path: "outputs/20250609_143022"              │
│                                                        │
│  Files Created:                                        │
│  ✓ deployment.yaml                                    │
│  ✓ report.json                                        │
│  ✓ SUMMARY.txt                                        │
└────────────────────────────────────────────────────────┘
```

---

## 5. Scoring Scale Visualization

```
┌──────────────────────────────────────────────────────┐
│         REVIEW SCORE SCALE (0-10)                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  10 │ ████████████████ EXCELLENT ✅                │
│      │ Immediate approval, no issues               │
│      │                                              │
│   8 │ ███████████ GOOD ✅                          │
│      │ Minor issues, acceptable                    │
│      │                                              │
│   6 │ █████ ACCEPTABLE ⚠️                          │
│      │ Several improvements needed                 │
│      │                                              │
│   4 │ ██ POOR ❌                                   │
│      │ Major issues, retry required                │
│      │                                              │
│   0 │ CRITICAL ❌                                  │
│      │ Severe issues, deployment risky             │
│      │                                              │
└──────────────────────────────────────────────────────┘

Decision Thresholds:
─────────────────────

Score ≥ 8          → APPROVE immediately
6 ≤ Score < 8      → RETRY with improvements
Score < 6          → RETRY strongly recommended
Max retries + <6   → REJECT
Max retries + ≥6   → FORCE APPROVE
```

---

## 6. File Processing Pipeline

```
┌──────────────────────────────┐
│    INPUT TASK DESCRIPTION    │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  PLANNER PARSES & CREATES STRATEGY       │
│  (Groq LLM Analysis)                    │
└────────────┬──────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  IMPLEMENT GENERATES YAML MANIFESTS      │
│  ┌──────────────────────────────────┐   │
│  │ Deployment Manifest              │   │
│  │ • replicas, ports, resources     │   │
│  │ • liveness/readiness probes      │   │
│  │ • environment variables          │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ Service Manifest                 │   │
│  │ • ClusterIP, port mapping        │   │
│  │ • service discovery              │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ HPA Manifest                     │   │
│  │ • min/max replicas               │   │
│  │ • CPU-based scaling              │   │
│  └──────────────────────────────────┘   │
└────────────┬──────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  REVIEW VALIDATES & SCORES               │
│  (Groq LLM Analysis)                    │
│  • Best practices check                  │
│  • Security validation                   │
│  • Production readiness                  │
│  • Generate score 0-10                   │
└────────────┬──────────────────────────────┘
             │
             ├─────────────┐
             │             │
      Score ≥ 8      Score < 8
             │             │
             │             ▼
             │    ┌──────────────────┐
             │    │ DECISION: RETRY  │
             │    │ [Loop Back]      │
             │    └──────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│  REPORT GENERATES OUTPUT FILES           │
│  Output Directory: outputs/[TIMESTAMP]/  │
│  ┌──────────────────────────────────┐   │
│  │ deployment.yaml                  │   │
│  │ • Ready to deploy with kubectl   │   │
│  │ • Contains all 3 manifests       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ report.json                      │   │
│  │ • Detailed metrics & scores      │   │
│  │ • Issues & recommendations       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │ SUMMARY.txt                      │   │
│  │ • Human-readable overview        │   │
│  │ • Deployment instructions        │   │
│  └──────────────────────────────────┘   │
└────────────┬──────────────────────────────┘
             │
             ▼
      ✅ COMPLETE
 Ready for Deployment
```

---

## 7. LLM Integration Points

```
┌─────────────────────────────────────────────────────────┐
│            GROQ LLM INTEGRATION POINTS                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. PLANNER AGENT                                      │
│     └─ Prompt: Analyze requirements & create strategy │
│     └─ Model: llama-3.3-70b-versatile                │
│     └─ Temp: 0.3 (moderate creativity)               │
│     └─ Max Tokens: 2000                              │
│                                                         │
│  2. REVIEW AGENT                                       │
│     └─ Prompt: Validate best practices & score        │
│     └─ Model: llama-3.3-70b-versatile                │
│     └─ Temp: 0.2 (consistent scoring)                │
│     └─ Max Tokens: 2000                              │
│                                                         │
│  3. DECISION AGENT                                     │
│     └─ Prompt: Evaluate score & make decision         │
│     └─ Model: llama-3.3-70b-versatile                │
│     └─ Temp: 0.1 (deterministic)                     │
│     └─ Max Tokens: 1000                              │
│                                                         │
│  Expected Latency:                                     │
│  ├─ Planner: ~10s                                    │
│  ├─ Review: ~15s                                     │
│  ├─ Decision: ~10s                                   │
│  └─ Total: ~35s                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

These diagrams provide a comprehensive visual reference for understanding the complete K8s deployment agent flow system.
