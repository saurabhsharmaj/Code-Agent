"""
Routing logic for agent flow decision-making
"""


def router(state):
    """
    Route decision based on agent state
    Determines whether to retry or proceed to report
    """
    decision = state.get("decision", "retry").lower()
    
    if decision == "approve":
        return "report"
    
    return "implement"


def handle_retry_logic(state):
    """
    Handle retry logic - increments retry counter
    Called when looping back to implement after failed review
    """
    max_retries = state.get("max_retries", 3)
    current_retries = state.get("retries", 0)
    
    if current_retries >= max_retries:
        return False  # No more retries allowed
    
    return True  # Can retry


def get_suggested_improvements(review_data):
    """
    Extract suggested improvements from review
    """
    return review_data.get("recommendation", "")
