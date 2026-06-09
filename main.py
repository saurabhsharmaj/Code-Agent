
"""
K8s Deployment Generation Agent Flow
Orchestrates multi-agent workflow for generating Kubernetes deployment files using Groq LLM
"""

from asyncio import graph
import os
import sys
from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from IPython.display import Image, display

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.agentstatus import AgentState

# Import agent nodes from hyphenated directories
# Python allows importing from hyphenated names using __import__
planner_module = __import__('planner-agent.planner_node', fromlist=['planner_node'])
implement_module = __import__('implement-agent.implement_node', fromlist=['implement_node'])
review_module = __import__('review-agent.review_node', fromlist=['review_node'])
decision_module = __import__('decision-agent.decision_node', fromlist=['decision_node'])
report_module = __import__('report-agent.report_node', fromlist=['report_node'])

planner_node = planner_module.planner_node
implement_node = implement_module.implement_node
review_node = review_module.review_node
decision_node = decision_module.decision_node
report_node = report_module.report_node

# Load environment variables
load_dotenv()

# Verify Groq API key is set
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def route_decision(state):
    """
    Router function: Determines next step based on decision
    
    - "approve" -> end (go to report)
    - "retry" -> implement (with retry logic)
    - "reject" -> end with failure
    """
    decision = state.get("decision", "retry").lower()
    
    if decision == "approve":
        return "report"
    elif decision == "reject":
        return END
    else:  # retry
        return "implement"


def retry_wrapper_implement(state):
    """Wrapper for implement node with retry counter"""
    state["retries"] = state.get("retries", 0) + 1
    result = implement_node(state)
    result["retries"] = state["retries"]
    return result


def build_graph():
    """Build the LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("implement", retry_wrapper_implement)
    workflow.add_node("review", review_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("report", report_node)
    
    # Add edges
    workflow.add_edge("planner", "implement")
    workflow.add_edge("implement", "review")
    workflow.add_edge("review", "decision")
    
    # Add conditional edge (router)
    workflow.add_conditional_edges(
        "decision",
        route_decision,
        {
            "implement": "implement",
            "report": "report",
            END: END
        }
    )
    
    # Report leads to END
    workflow.add_edge("report", END)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    workflowGraph =workflow.compile()
    # Visualize
    print(workflowGraph.get_graph().draw_ascii())
    print(workflowGraph.get_graph().draw_mermaid())    
    display(Image(graph.get_graph().draw_mermaid_png()))
    return workflowGraph;


def create_initial_state(task: str, max_retries: int = 3) -> AgentState:
    """Create initial state for the workflow"""
    return {
        "task": task,
        "plan": "",
        "deployment_config": {},
        "deployment_yaml": "",
        "review": {},
        "decision": "",
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
    """
    print("\n" + "="*60)
    print("K8s Deployment Generation Agent Flow")
    print("="*60)
    print(f"Task: {task}")
    print(f"Max Retries: {max_retries}")
    print("="*60 + "\n")
    
    try:
        # Build and execute graph
        graph = build_graph()
        initial_state = create_initial_state(task, max_retries)
        
        # Run the workflow
        final_state = graph.invoke(initial_state)
        
        # Display results
        print("\n" + "="*60)
        print("WORKFLOW EXECUTION COMPLETE")
        print("="*60)
        
        print(f"Final Decision: {final_state.get('decision', 'unknown').upper()}")
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
