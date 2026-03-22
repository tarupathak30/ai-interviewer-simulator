from .state import InterviewState

def route_entry(state: InterviewState) -> str:
    """Top-level router — decides if we need to start or continue."""
    messages = state.get("messages") or []
    code     = state.get("code", "")
    question = state.get("question", "")

    # No question yet — fresh session, run start
    if not question:
        return "start"

    # Has a hint request
    if messages and hasattr(messages[-1], 'content') and "hint" in messages[-1].content.lower():
        return "give_hint"

    # Has code to evaluate
    if code:
        return "evaluate"

    return "wait"


def route_candidate_action(state: InterviewState) -> str:
    """After start node — always wait for candidate."""
    return "wait"

