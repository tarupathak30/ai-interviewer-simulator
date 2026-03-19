from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import InterviewState
from .nodes import start_interview, give_hint, evaluate_code, ask_followup  # add ask_followup
from .edges import route_candidate_action

def build_graph():
    g = StateGraph(InterviewState)

    g.add_node("start",     start_interview)
    g.add_node("give_hint", give_hint)
    g.add_node("evaluate",  evaluate_code)
    g.add_node("followup",  ask_followup)    # add node BEFORE edges

    g.set_entry_point("start")

    g.add_conditional_edges("start", route_candidate_action, {
        "give_hint": "give_hint",
        "evaluate":  "evaluate",
        "wait":      END,
    })

    g.add_edge("give_hint", END)
    g.add_edge("evaluate",  "followup")
    g.add_edge("followup",  END)

    return g.compile(checkpointer=MemorySaver())

interview_graph = build_graph()