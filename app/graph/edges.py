from .state import InterviewState

def route_candidate_action(state: InterviewState) -> str:
    """
    Decide what to do next based on the last user message.
    In a real app this reads from the API request type.
    """
    last = state["messages"][-1].content.lower()
    
    if "hint" in last:
        return "give_hint"
    if state.get("code"):
        return "evaluate"
    return "wait"   # waiting for candidate to submit code