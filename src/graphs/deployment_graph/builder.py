"""
Deployment Graph Builder
Constructs the LangGraph workflow for K8s deployment generation
"""

from langgraph.graph import StateGraph, END
from src.state.schemas import AgentState
from src.agents.planner.planner import planner_node
from src.agents.implementer.implementer import implement_node
from src.agents.reviewer.reviewer import review_node
from src.agents.decision.decision import decision_node
from src.agents.reporting.reporter import report_node


def route_decision(state: AgentState):
    """
    Router function: Determines next step based on decision

    - "approve" -> report (end)
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


def retry_wrapper_implement(state: AgentState):
    """Wrapper for implement node with retry counter"""
    state["retries"] = state.get("retries", 0) + 1
    result = implement_node(state)
    result["retries"] = state["retries"]
    return result


def build_deployment_graph():
    """Build the LangGraph workflow for K8s deployment"""

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

    graph = workflow.compile()
    return graph
