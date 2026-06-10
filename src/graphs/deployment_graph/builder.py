"""
Deployment Graph Builder
Constructs the LangGraph workflow for K8s deployment generation with human approval gate
"""

from langgraph.graph import StateGraph, END
from src.state.schemas import AgentState
from src.agents.planner.planner import planner_node
from src.agents.implementer.implementer import implement_node
from src.agents.reviewer.reviewer import review_node
from src.agents.decision.decision import decision_node
from src.agents.approval.approval_agent import human_approval_node
from src.agents.reporting.reporter import report_node


def route_decision(state: AgentState):
    """
    Router function: Determines next step based on decision

    - "approve" -> human_approval (gate check)
    - "retry" -> implement (with retry logic)
    - "reject" -> end with failure
    """
    decision = state.get("decision", "retry").lower()

    if decision == "approve":
        return "human_approval"  # Route to human approval gate
    elif decision == "reject":
        return END
    else:  # retry
        return "implement"


def route_approval(state: AgentState):
    """
    Router function: Determines next step based on human approval
    
    - If no human approval required: proceed to report
    - If approved: proceed to report
    - If rejected: end with failure
    - If pending: can be deferred or rejected
    """
    requires_approval = state.get("requires_human_approval", False)
    approval_status = state.get("human_approval", "pending").lower()
    
    # If approval not required, proceed to report
    if not requires_approval:
        return "report"
    
    # If approved, proceed to report
    if approval_status == "approved":
        return "report"
    
    # If auto-approved, proceed to report
    if approval_status == "auto_approved":
        return "report"
    
    # If pending or rejected, end (cannot proceed without approval)
    # In production, this could queue for later retry
    return END


def retry_wrapper_implement(state: AgentState):
    """Wrapper for implement node with retry counter"""
    state["retries"] = state.get("retries", 0) + 1
    result = implement_node(state)
    result["retries"] = state["retries"]
    return result


def build_deployment_graph():
    """Build the LangGraph workflow for K8s deployment with human approval"""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("implement", retry_wrapper_implement)
    workflow.add_node("review", review_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("human_approval", human_approval_node)  # NEW: Human approval gate
    workflow.add_node("report", report_node)

    # Add edges
    workflow.add_edge("planner", "implement")
    workflow.add_edge("implement", "review")
    workflow.add_edge("review", "decision")

    # Add conditional edge from decision (routes to approval gate or retry)
    workflow.add_conditional_edges(
        "decision",
        route_decision,
        {
            "implement": "implement",
            "human_approval": "human_approval",  # NEW: Route to approval gate
            END: END
        }
    )

    # Add conditional edge from human_approval (routes to report or end)
    workflow.add_conditional_edges(
        "human_approval",
        route_approval,
        {
            "report": "report",
            END: END
        }
    )

    # Report leads to END
    workflow.add_edge("report", END)

    # Set entry point
    workflow.set_entry_point("planner")

    graph = workflow.compile()
    return graph
