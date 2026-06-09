from typing import TypedDict, Optional, Any, Dict

class AgentState(TypedDict):
    """State object passed through agent nodes"""
    task: str  # User requirement/task description
    plan: str  # Planner agent's strategy
    deployment_config: Dict[str, Any]  # K8s deployment configuration
    deployment_yaml: str  # Generated K8s YAML
    review: Dict[str, Any]  # Review agent's feedback
    decision: str  # Decision (approve/retry)
    retries: int  # Current retry count
    max_retries: int  # Maximum retry attempts
    errors: list[str]  # Error tracking
    final_output: Optional[str]  # Final K8s deployment files