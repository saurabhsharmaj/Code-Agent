def decision_node(state):

    review = state["review"]

    if review["score"] >= 8:
        return {"decision": "approve"}

    return {"decision": "retry"}