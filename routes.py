
def router(state):

    if state["decision"] == "approve":
        return "report"

    return "implement"
