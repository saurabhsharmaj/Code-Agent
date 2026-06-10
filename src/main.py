"""
K8s Deployment Generation Agent Flow
Orchestrates multi-agent workflow for generating Kubernetes deployment files using Groq LLM

Refactored structure:
- src/agents/: Individual agent implementations
- src/state/: State management and schemas
- src/tools/kubernetes/: Kubernetes utilities
- src/graphs/deployment_graph/: Workflow graph construction
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

# Add parent directory to path for imports
# This allows importing src.* modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state.schemas import AgentState
from src.graphs.deployment_graph.builder import build_deployment_graph

# Verify Groq API key is set
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable not set")


def create_initial_state(task: str, max_retries: int = 3) -> AgentState:
    """Create initial state for the workflow"""
    return {
        "task": task,
        "plan": "",
        "deployment_config": {},
        "deployment_yaml": "",
        "review": {},
        "decision": "",
        "risk_score": 0,
        "requires_human_approval": False,
        "human_approval": None,
        "human_notes": None,
        "retries": 0,
        "max_retries": max_retries,
        "errors": [],
        "final_output": None
    }


def run_k8s_deployment_flow(task: str, max_retries: int = 3):
    """
    Execute the K8s deployment generation workflow

    Args:
        task: User requirement/description for K8s deployment
        max_retries: Maximum retry attempts (default: 3)

    Returns:
        Final workflow state
    """
    print("\n" + "="*60)
    print("K8s Deployment Generation Agent Flow")
    print("="*60)
    print(f"Task: {task}")
    print(f"Max Retries: {max_retries}")
    print("="*60 + "\n")

    try:
        # Build and execute graph
        graph = build_deployment_graph()
        initial_state = create_initial_state(task, max_retries)

        # Run the workflow
        final_state = graph.invoke(initial_state)

        # Display results
        print("\n" + "="*60)
        print("WORKFLOW EXECUTION COMPLETE")
        print("="*60)

        print(f"Final Decision: {final_state.get('decision', 'unknown').upper()}")
        print(f"Risk Score: {final_state.get('risk_score', 0)}/10")
        print(f"Requires Human Approval: {'Yes' if final_state.get('requires_human_approval') else 'No'}")
        
        if final_state.get('human_approval'):
            print(f"Human Approval Status: {final_state.get('human_approval', 'unknown').upper()}")
        if final_state.get('human_notes'):
            print(f"Human Notes: {final_state.get('human_notes')}")
            
        print(f"Retries Used: {final_state.get('retries', 0)}/{max_retries}")
        print(f"Review Score: {final_state.get('review', {}).get('score', 'N/A')}/10")

        if final_state.get("errors"):
            print(f"Errors: {len(final_state['errors'])}")
            for error in final_state["errors"]:
                print(f"  - {error}")

        if final_state.get("final_output"):
            print("\n" + final_state["final_output"])

        print("="*60 + "\n")

        return final_state

    except Exception as e:
        print(f"Error in workflow execution: {str(e)}")
        raise


if __name__ == "__main__":
    # Example task
    task = """
    Create a Kubernetes deployment for a Python Flask web application with:
    - Docker image: "myapp:v1.0"
    - 3 replicas for high availability
    - Port 8080
    - CPU requests: 100m, limits: 500m
    - Memory requests: 128Mi, limits: 512Mi
    - Environment variables: DEBUG=false, LOG_LEVEL=info
    - Auto-scaling: min 2, max 10 replicas based on 70% CPU utilization
    - Include liveness and readiness probes
    - Namespace: production
    """

    run_k8s_deployment_flow(task, max_retries=3)
