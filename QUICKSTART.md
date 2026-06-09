"""
QUICK START GUIDE - K8s Deployment Agent Flow
==============================================

This document provides step-by-step instructions to run the system.
"""

# SETUP INSTRUCTIONS
# ==================

"""
1. INSTALL DEPENDENCIES

   pip install -r requirements.txt

   This installs:
   - langchain
   - langchain-groq
   - langgraph
   - python-dotenv
   - pyyaml
   - pydantic
   - requests


2. CONFIGURE GROQ API

   Option A: Set environment variable
   ------------------------------------
   export GROQ_API_KEY="gsk_your_actual_key_here"

   Option B: Create .env file
   ---------------------------
   Create file: .env
   Add line: GROQ_API_KEY=gsk_your_actual_key_here

   Get your key from: https://console.groq.com/keys


3. VERIFY SETUP

   python -c "import langchain; import langgraph; print('Setup OK')"


4. RUN THE WORKFLOW

   python main.py

   This will:
   - Execute the full agent flow
   - Generate K8s deployment YAML
   - Save outputs to outputs/[TIMESTAMP]/
   - Display results in console


5. DEPLOY GENERATED MANIFESTS

   kubectl apply -f outputs/[LATEST_TIMESTAMP]/deployment.yaml
"""


# EXAMPLE USAGE IN CODE
# ====================

# Basic Example
# =============

"""
from main import run_k8s_deployment_flow

# Simple K8s deployment request
task = "Create a K8s deployment for a Node.js app with 3 replicas"

# Run the workflow
result = run_k8s_deployment_flow(task)

# Check the result
if result['decision'] == 'approve':
    print("✅ Deployment approved!")
    print(f"Review Score: {result['review']['score']}/10")
else:
    print("❌ Deployment failed")
"""


# Advanced Example
# ================

"""
from main import run_k8s_deployment_flow

# Detailed K8s deployment specification
task = '''
Create Kubernetes deployment with these specifications:
- Application: Python FastAPI service
- Docker Image: mycompany/fastapi-service:v2.1.0
- Replicas: 4
- Port: 9000
- Environment Variables:
  * ENV=production
  * LOG_LEVEL=INFO
  * DATABASE_URL=postgresql://db:5432/myapp
- Resource Limits:
  * CPU: 1000m
  * Memory: 1Gi
- Resource Requests:
  * CPU: 250m
  * Memory: 256Mi
- Namespace: production
- Auto-scaling:
  * Min replicas: 3
  * Max replicas: 15
  * Target CPU: 60%
'''

# Run with custom max retries
result = run_k8s_deployment_flow(task, max_retries=5)

# Access detailed results
print(f"Status: {result['decision']}")
print(f"Retries used: {result['retries']}/{result['max_retries']}")
print(f"Quality score: {result['review']['score']}/10")

if result['review']['issues']:
    print("Issues found:")
    for issue in result['review']['issues']:
        print(f"  - {issue}")

if result['review']['strengths']:
    print("Strengths:")
    for strength in result['review']['strengths']:
        print(f"  ✓ {strength}")

print(f"\\nOutput saved to: {result.get('output_path')}")
"""


# WORKFLOW DECISION TREE
# ======================

"""
User Provides Task
        ↓
   PLANNER AGENT
   (Create plan & config)
        ↓
   IMPLEMENT AGENT
   (Generate YAML)
        ↓
   REVIEW AGENT
   (Score: 0-10)
        ↓
   DECISION AGENT
   (Evaluate score)
        ↓
   ┌───┴─────────────┐
   ↓                 ↓
Score ≥ 8      Score < 8
   ↓                 ↓
APPROVE        RETRY or REJECT
   ↓                 ↓
   └────┬────────────┘
        ↓
   REPORT AGENT
   (Save files)
        ↓
    Output Generated
    ✓ deployment.yaml
    ✓ report.json
    ✓ SUMMARY.txt
"""


# OUTPUT EXAMPLES
# ===============

"""
SUCCESS OUTPUT:
===============

============================================================
K8s Deployment Generation Agent Flow
============================================================
Task: Create a Kubernetes deployment for a Python Flask web application...
Max Retries: 3
============================================================

============================================================
WORKFLOW EXECUTION COMPLETE
============================================================
Final Decision: APPROVE
Retries Used: 0/3
Review Score: 9/10

Deployment Generation Complete!
================================

Output Location: outputs/20250609_143022

Files Generated:
1. deployment.yaml - K8s deployment manifests (Deployment, Service, HPA)
2. report.json - Detailed generation report
3. SUMMARY.txt - Quick summary

Status: APPROVE
Review Score: 9/10

To deploy:
kubectl apply -f outputs/20250609_143022/deployment.yaml

============================================================
"""


# CHECKING RESULTS
# ================

"""
1. View Generated YAML
   cat outputs/[TIMESTAMP]/deployment.yaml

2. View JSON Report
   cat outputs/[TIMESTAMP]/report.json

3. View Summary
   cat outputs/[TIMESTAMP]/SUMMARY.txt

4. Validate YAML Syntax
   kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml --dry-run=client

5. Deploy to Cluster
   kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml

6. Check Deployment Status
   kubectl get deployments
   kubectl get pods
   kubectl describe deployment [app-name]
   kubectl logs deployment/[app-name]
"""


# TROUBLESHOOTING
# ===============

"""
ERROR: GROQ_API_KEY not set
SOLUTION: 
  export GROQ_API_KEY="your_key"
  OR create .env file with: GROQ_API_KEY=your_key

ERROR: ImportError: No module named 'langgraph'
SOLUTION:
  pip install -r requirements.txt

ERROR: JSON parsing errors
SOLUTION:
  - Retry the run (automatic via decision agent)
  - Check that GROQ_API_KEY is valid
  - Try a simpler task description

ERROR: Max retries exceeded
SOLUTION:
  - Check report.json for issues
  - Simplify the task requirements
  - Increase max_retries parameter

ERROR: Validation failed
SOLUTION:
  - Ensure image has a tag (e.g., app:v1.0)
  - Verify replicas > 0
  - Check deployment_config in report.json
"""


# FILE STRUCTURE AFTER RUN
# ========================

"""
Code-Agent/
├── main.py
├── requirements.txt
├── .env (created with GROQ_API_KEY)
├── common/
│   ├── agentstatus.py
│   ├── reviewoutput.py
│   ├── k8s_generator.py
├── planner_agent/
│   └── planner_node.py
├── implement_agent/
│   └── implement_node.py
├── review_agent/
│   └── review_node.py
├── decision_agent/
│   └── decision_node.py
├── report_agent/
│   └── report_node.py
├── outputs/  ← Generated here
│   └── 20250609_143022/  ← Timestamped folder
│       ├── deployment.yaml
│       ├── report.json
│       └── SUMMARY.txt
├── README.md
└── ARCHITECTURE.md
"""


# PERFORMANCE EXPECTATIONS
# ==========================

"""
Typical Execution Timeline:
├─ Planner Agent:    ~10 seconds (Groq LLM call)
├─ Implement Agent:  ~5 seconds (YAML generation)
├─ Review Agent:     ~15 seconds (Groq LLM call)
├─ Decision Agent:   ~10 seconds (Groq LLM call)
├─ Report Agent:     ~5 seconds (file I/O)
└─ TOTAL:            ~45 seconds (first run)

With retry: Add 45 seconds per retry

Main bottleneck: LLM inference time from Groq API
Network latency: Can add 5-10 seconds per call
"""


# NEXT STEPS
# ==========

"""
1. ✅ Install dependencies
2. ✅ Set GROQ_API_KEY
3. ✅ Run: python main.py
4. ✅ Check outputs/[TIMESTAMP]/
5. ✅ Review deployment.yaml
6. ✅ Deploy: kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml
7. ✅ Monitor: kubectl get pods, kubectl logs

For more details, see:
- README.md for overview
- ARCHITECTURE.md for technical details
- main.py for orchestration logic
"""
