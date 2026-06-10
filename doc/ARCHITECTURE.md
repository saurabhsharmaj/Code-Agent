"""
K8s Deployment Generation Agent Flow - Complete Documentation
=====================================================

ARCHITECTURE OVERVIEW
====================

This project implements a multi-agent workflow using LangGraph and Groq LLM
to intelligently generate Kubernetes deployment files.

AGENT FLOW:
1. PLANNER AGENT -> 2. IMPLEMENT AGENT -> 3. REVIEW AGENT -> 4. DECISION AGENT
                                                                   |
                                                        [Score >= 8 or max retries]
                                                                   |
                                                            5. REPORT AGENT


DETAILED FLOW EXPLANATION
========================

1. PLANNER AGENT (planner_node.py)
   ├─ Input: User task description
   ├─ Process:
   │  ├─ Analyzes requirements using Groq LLM
   │  ├─ Creates deployment strategy
   │  └─ Generates configuration schema
   ├─ Output: 
   │  ├─ Deployment plan (strategy)
   │  └─ Deployment config (app_name, image, replicas, etc.)
   └─ Error Handling: Validates JSON response, provides retry on failure

2. IMPLEMENT AGENT (implement_node.py)
   ├─ Input: Deployment configuration from planner
   ├─ Process:
   │  ├─ Validates configuration using K8sDeploymentGenerator
   │  ├─ Generates Deployment manifest
   │  ├─ Generates Service manifest
   │  └─ Generates HPA (Horizontal Pod Autoscaler) manifest
   ├─ Output: Combined YAML manifests with proper separators
   └─ Retry Counter: Incremented on each loop

3. REVIEW AGENT (review_node.py)
   ├─ Input: Generated K8s YAML manifests
   ├─ Process:
   │  ├─ Reviews for best practices
   │  ├─ Checks security considerations
   │  ├─ Validates resource optimization
   │  ├─ Assesses high availability setup
   │  └─ Evaluates production readiness
   ├─ Output:
   │  ├─ Score (0-10)
   │  ├─ Issues list
   │  ├─ Strengths list
   │  ├─ Improvements list
   │  └─ Recommendation
   └─ Scoring Guide:
       ├─ 9-10: Production ready
       ├─ 7-8: Good, minor issues
       ├─ 5-6: Acceptable, improvements needed
       └─ <5: Major issues, retry recommended

4. DECISION AGENT (decision_node.py)
   ├─ Input: Review score, retry count, max retries
   ├─ Decision Logic:
   │  ├─ Score >= 8: APPROVE
   │  ├─ Score >= 6 && retries < max: RETRY with improvements
   │  ├─ Score < 6 && retries < max: RETRY
   │  └─ Retries maxed out:
   │     ├─ If score >= 6: Force APPROVE
   │     └─ If score < 6: REJECT
   ├─ Output:
   │  ├─ Decision (approve/retry/reject)
   │  ├─ Reasoning
   │  ├─ Suggested fixes
   │  └─ Can retry flag
   └─ Routing:
       ├─ APPROVE → REPORT AGENT
       ├─ RETRY → back to IMPLEMENT AGENT (with incremented counter)
       └─ REJECT → END (workflow fails)

5. REPORT AGENT (report_node.py)
   ├─ Input: Final approved state
   ├─ Process:
   │  ├─ Creates timestamped output directory
   │  ├─ Saves deployment.yaml
   │  ├─ Generates JSON report with metrics
   │  └─ Creates human-readable summary
   ├─ Outputs:
   │  ├─ outputs/TIMESTAMP/deployment.yaml (K8s manifests)
   │  ├─ outputs/TIMESTAMP/report.json (detailed metrics)
   │  └─ outputs/TIMESTAMP/SUMMARY.txt (quick overview)
   └─ Final Output: Instructions for deployment


STATE MANAGEMENT
===============

AgentState (TypedDict) tracks:
├─ task: str (original user requirement)
├─ plan: str (planner's strategy)
├─ deployment_config: Dict (K8s configuration)
├─ deployment_yaml: str (generated YAML)
├─ review: Dict (review feedback and score)
├─ decision: str (approve/retry/reject)
├─ retries: int (current retry count)
├─ max_retries: int (maximum allowed retries)
├─ errors: list[str] (error tracking)
└─ final_output: Optional[str] (completion status)


RETRY MECHANISM
==============

Default: 3 max retries

Flow on Retry:
1. Review Agent scores deployment
2. Decision Agent evaluates score
3. If score < threshold and retries < max:
   └─ Retry counter increments
   └─ Router directs back to IMPLEMENT AGENT
   └─ IMPLEMENT AGENT receives previous feedback
   └─ Cycle repeats

Termination:
- If approval threshold met: Move to REPORT
- If max retries exhausted: 
  ├─ If score >= 6: Approve anyway (with warnings)
  └─ If score < 6: Reject


KUBERNETES MANIFESTS GENERATED
=============================

1. Deployment
   ├─ Configurable replicas
   ├─ Liveness probe (/health endpoint)
   ├─ Readiness probe (/ready endpoint)
   ├─ Resource requests/limits
   ├─ Environment variables
   └─ Image pull policy

2. Service
   ├─ ClusterIP type (configurable)
   ├─ Port mapping
   └─ Service discovery

3. HorizontalPodAutoscaler
   ├─ Min/max replicas
   ├─ CPU-based scaling
   └─ Automatic scaling policy


CONFIGURATION SCHEMA
===================

Deployment config includes:
├─ app_name (string): Application identifier
├─ image (string): Docker image URI with tag
├─ replicas (int): Initial pod replicas
├─ port (int): Container port
├─ namespace (string): K8s namespace
├─ env_vars (dict): Environment variables
├─ resources (dict):
│  ├─ requests: {cpu, memory}
│  └─ limits: {cpu, memory}
└─ considerations (list): Planning notes


ERROR HANDLING
=============

Retry Conditions:
├─ JSON parsing errors: Retry current node
├─ Configuration validation: Retry with new config
├─ LLM response format: Retry LLM call
└─ File I/O errors: Attempt recovery

Max Retry Limits:
├─ Per node: Not limited
├─ Total workflow: Configurable (default: 3)
└─ Escalation: Manual review required


USAGE EXAMPLES
=============

Basic Usage:
```python
from main import run_k8s_deployment_flow

task = "Create K8s deployment for Flask app with 3 replicas on port 8080"
result = run_k8s_deployment_flow(task)
```

With Custom Max Retries:
```python
result = run_k8s_deployment_flow(task, max_retries=5)
```

Access Results:
```python
print(f"Status: {result['decision']}")
print(f"Score: {result['review']['score']}")
print(f"YAML saved: {result['output_path']}")
```


SETUP & INSTALLATION
===================

1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variable:
   export GROQ_API_KEY="your_groq_api_key"
   
   Or create .env file:
   GROQ_API_KEY=your_groq_api_key

3. Run the workflow:
   python main.py

4. Check outputs:
   ls -la outputs/


FILE STRUCTURE
=============

Code-Agent/
├─ main.py (orchestration & entry point)
├─ routes.py (routing logic)
├─ requirements.txt (dependencies)
├─ README.md (documentation)
├─ .env (configuration - GITIGNORED)
├─ .gitignore
├─ common/
│  ├─ agentstatus.py (state definition)
│  ├─ reviewoutput.py (review data model)
│  └─ k8s_generator.py (YAML generation utility)
├─ planner_agent/
│  └─ planner_node.py (planning agent)
├─ implement_agent/
│  └─ implement_node.py (implementation agent)
├─ review_agent/
│  └─ review_node.py (review agent)
├─ decision_agent/
│  └─ decision_node.py (decision agent)
├─ report_agent/
│  └─ report_node.py (report generation)
└─ outputs/
   └─ [TIMESTAMP]/
      ├─ deployment.yaml
      ├─ report.json
      └─ SUMMARY.txt


DEPLOYMENT EXAMPLE OUTPUT
========================

Generated Files:
- deployment.yaml: Contains Deployment, Service, and HPA manifests
- report.json: Detailed generation metrics and review scores
- SUMMARY.txt: Human-readable summary with deployment instructions

Deploy the generated manifest:
kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml

Or deploy with namespace:
kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml -n production


BEST PRACTICES IMPLEMENTED
==========================

1. High Availability
   ├─ Multiple replicas
   ├─ Pod spreading across nodes
   └─ Auto-scaling enabled

2. Health Checks
   ├─ Liveness probes (container restart)
   └─ Readiness probes (traffic routing)

3. Resource Management
   ├─ CPU/Memory requests
   ├─ CPU/Memory limits
   └─ Auto-scaling based on metrics

4. Production Readiness
   ├─ Proper labeling
   ├─ Namespace isolation
   └─ Service discovery

5. Agent Quality
   ├─ Multi-stage review
   ├─ Automatic retry
   └─ Detailed reporting


TROUBLESHOOTING
==============

Issue: GROQ_API_KEY not found
Solution: Set GROQ_API_KEY environment variable or create .env file

Issue: JSON parsing errors in LLM responses
Solution: Nodes automatically retry, check LLM response format in logs

Issue: Max retries exceeded
Solution: Review the report.json for issues, adjust configuration, and rerun

Issue: Validation errors
Solution: Check deployment_config in report.json for invalid values


PERFORMANCE NOTES
================

Typical execution time: 30-60 seconds per run
- Planner: ~10s
- Implement: ~5s
- Review: ~15s
- Decision: ~10s
- Report: ~5s

Bottleneck: Usually LLM inference time
Optimization: Can parallelize non-dependent operations


EXTENSIBILITY
=============

Add Custom Validators:
1. Extend K8sDeploymentGenerator in common/k8s_generator.py
2. Add custom validation methods

Add Additional Manifests:
1. Create new generation methods in K8sDeploymentGenerator
2. Include in implement_node output

Customize Review Criteria:
1. Modify REVIEW_PROMPT in review_node.py
2. Adjust score thresholds in decision_node.py

Custom LLM Models:
1. Change model parameter in ChatGroq initialization
2. Update prompts for new model's capabilities
"""
