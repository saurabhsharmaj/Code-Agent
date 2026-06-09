# K8s Deployment Generation Agent Flow

A sophisticated multi-agent AI system using **Groq LLM** and **LangGraph** to intelligently generate, validate, and optimize Kubernetes deployment files.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API Key (get from [Groq Console](https://console.groq.com))

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
export GROQ_API_KEY="your_groq_api_key_here"
# OR create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### Run

```bash
python main.py
```

## 📊 Agent Flow Architecture

```
┌──────────────┐
│   PLANNER    │ → Analyzes requirements, creates strategy
└──────┬───────┘
       ↓
┌──────────────┐
│ IMPLEMENT    │ → Generates K8s manifests (Deployment, Service, HPA)
└──────┬───────┘
       ↓
┌──────────────┐
│   REVIEW     │ → Validates best practices, scores quality (0-10)
└──────┬───────┘
       ↓
┌──────────────┐
│  DECISION    │ → Decides: Approve (score ≥8) or Retry (with feedback)
└──────┬───────┘
       │
   ┌───┴─────────────────┐
   ↓                     ↓
 RETRY          ┌─────────────┐
   ↓            │   REPORT    │ → Generate output & save files
 [LOOP]         └─────────────┘
   ↑                    ↓
   └────────────────────┘
                       ↓
                     [END]
```

## 🎯 Key Features

### Multi-Agent Intelligence
- **Planner Agent**: Strategic deployment planning using Groq LLM
- **Implement Agent**: K8s manifest generation with validation
- **Review Agent**: Quality validation and intelligent scoring
- **Decision Agent**: Automatic retry logic with feedback
- **Report Agent**: Output generation and file management

### Intelligent Retry Logic
- Automatic retry on failed reviews (max 3 retries by default)
- Score-based decision making (0-10 scale)
- Suggested improvements provided on retry
- Progressive improvements through iterations

### Kubernetes Manifests
Generates three integrated manifests:
1. **Deployment** - Pod management with health probes
2. **Service** - Network exposure and discovery
3. **HorizontalPodAutoscaler** - Auto-scaling configuration

### Production-Ready Features
- Liveness & readiness probes
- Resource requests and limits
- Auto-scaling based on CPU metrics
- Environment variable support
- Comprehensive error handling

## 📝 Generated Output

Each workflow generates:
```
outputs/
└── TIMESTAMP/
    ├── deployment.yaml      # K8s manifests (Deployment, Service, HPA)
    ├── report.json          # Detailed metrics and scores
    └── SUMMARY.txt          # Quick reference guide
```

## 💻 Usage Examples

### Basic Usage
```python
from main import run_k8s_deployment_flow

task = """
Create a Kubernetes deployment for a Python Flask web application with:
- Docker image: myapp:v1.0
- 3 replicas
- Port 8080
- Resource limits: 500m CPU, 512Mi memory
"""

result = run_k8s_deployment_flow(task)
print(result['final_output'])
```

### Custom Retry Configuration
```python
result = run_k8s_deployment_flow(task, max_retries=5)
```

### Access Results
```python
print(f"Decision: {result['decision']}")
print(f"Review Score: {result['review']['score']}/10")
print(f"Output Path: {result['output_path']}")
print(f"Retries Used: {result['retries']}")
```

## 🔍 Agent Responsibilities

### Planner Agent
**Input**: User requirement/task  
**Process**: 
- Analyzes deployment needs using Groq LLM
- Creates strategic plan
- Generates configuration schema

**Output**:
- Deployment strategy
- K8s configuration (app_name, image, replicas, resources, etc.)

### Implement Agent
**Input**: Deployment configuration  
**Process**:
- Validates configuration against K8s standards
- Generates Deployment manifest
- Generates Service manifest
- Generates HPA manifest

**Output**: Combined YAML with proper Kubernetes manifest structure

### Review Agent
**Input**: Generated YAML manifests  
**Process**:
- Reviews best practices compliance
- Checks security considerations
- Validates resource optimization
- Assesses production readiness

**Output**:
- Score (0-10)
- Issues identified
- Strengths highlighted
- Improvement recommendations

### Decision Agent
**Input**: Review score, retry count  
**Process**:
- Evaluates quality score
- Considers retry limits
- Applies decision logic

**Decision Logic**:
- Score ≥ 8: **APPROVE** → Report
- Score ≥ 6 & retries < max: **RETRY** with improvements
- Score < 6 & retries < max: **RETRY** 
- Max retries reached:
  - Score ≥ 6: **APPROVE** (with warnings)
  - Score < 6: **REJECT**

### Report Agent
**Input**: Final approved state  
**Process**:
- Creates timestamped output directory
- Saves YAML manifests
- Generates JSON report with metrics
- Creates summary document

**Output**: 
- deployment.yaml
- report.json
- SUMMARY.txt

## 🔧 Configuration

### State Configuration
```python
initial_state = {
    "task": "Your deployment requirement",
    "max_retries": 3,  # Maximum retry attempts
    # ... other fields auto-populated
}
```

### LLM Configuration
Edit in respective agent files (e.g., `planner_node.py`):
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,  # Creativity vs consistency
    max_tokens=2000,
    api_key=os.getenv("GROQ_API_KEY")
)
```

## 📊 Review Score Guide

| Score | Status | Action |
|-------|--------|--------|
| 9-10 | ✅ Excellent | Approve immediately |
| 7-8 | ✅ Good | Minor issues acceptable |
| 5-6 | ⚠️ Fair | Retry with improvements |
| <5 | ❌ Poor | Retry strongly recommended |

## 📂 Project Structure

```
Code-Agent/
├── main.py                      # Orchestration & entry point
├── routes.py                    # Routing logic
├── requirements.txt             # Dependencies
├── ARCHITECTURE.md              # Detailed architecture docs
├── README.md                    # This file
├── .env                         # Configuration (GITIGNORED)
├── .gitignore
│
├── common/
│   ├── agentstatus.py          # State definition (TypedDict)
│   ├── reviewoutput.py         # Review data model
│   └── k8s_generator.py        # K8s YAML generator utility
│
├── planner_agent/
│   └── planner_node.py         # Planner agent implementation
│
├── implement_agent/
│   └── implement_node.py       # Implementation agent
│
├── review_agent/
│   └── review_node.py          # Review agent
│
├── decision_agent/
│   └── decision_node.py        # Decision agent
│
├── report_agent/
│   └── report_node.py          # Report generation
│
└── outputs/
    └── [TIMESTAMP]/
        ├── deployment.yaml
        ├── report.json
        └── SUMMARY.txt
```

## 🚢 Deploying Generated Manifests

```bash
# List available deployments
ls outputs/

# Deploy the latest generated manifest
kubectl apply -f outputs/[LATEST_TIMESTAMP]/deployment.yaml

# Deploy to specific namespace
kubectl apply -f outputs/[TIMESTAMP]/deployment.yaml -n production

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl logs deployment/[app-name]
```

## 🐛 Troubleshooting

### "GROQ_API_KEY environment variable not set"
```bash
export GROQ_API_KEY="your_key"
# OR create .env file
echo "GROQ_API_KEY=your_key" > .env
```

### JSON Parsing Errors
- Check LLM response format in prompts
- Increase `max_tokens` if responses are truncated
- Adjust `temperature` for consistency

### Max Retries Exceeded
- Review `report.json` for identified issues
- Adjust task description for clarity
- Increase `max_retries` parameter

### Validation Failures
- Check `deployment_config` in report.json
- Ensure image includes tag (e.g., `app:v1.0`)
- Verify replicas > 0

## 📈 Performance Notes

Typical execution time: 30-60 seconds
- Planner: ~10s (Groq LLM)
- Implement: ~5s
- Review: ~15s (Groq LLM)
- Decision: ~10s (Groq LLM)
- Report: ~5s

Main bottleneck: LLM inference time via Groq API

## 🔐 Security Notes

- `.env` file is gitignored (don't commit API keys)
- Never share GROQ_API_KEY
- Generated manifests don't contain secrets (add separately via K8s Secrets)
- Review generated YAML for compliance before deployment

## 🛠️ Advanced Usage

### Custom Kubernetes Manifests
Extend `K8sDeploymentGenerator` in `common/k8s_generator.py`:
```python
@staticmethod
def generate_custom_manifest(...):
    # Your custom manifest generation
    return yaml.dump(custom_manifest)
```

### Custom Review Criteria
Update `REVIEW_PROMPT` in `review_agent/review_node.py`

### Different LLM Models
Change model in agent initialization:
```python
llm = ChatGroq(model="mixtral-8x7b-32768")
```

## 📞 Support

For issues or improvements, check:
1. ARCHITECTURE.md for detailed flow documentation
2. Agent node implementations for specific logic
3. Groq documentation for API issues

## 📚 Detailed Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for comprehensive documentation including:
- Detailed agent flow explanation
- State management details
- Retry mechanism explanation
- Configuration schema
- Kubernetes manifests reference
- Extensibility guidelines

## 📄 License

See LICENSE file for details (if applicable).

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Kubernetes Manifests Guide](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [LangChain Documentation](https://python.langchain.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
