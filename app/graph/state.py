from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    code: str
    language: str
    hints_used: int
    score: int
    feedback: str
    done: bool
    followup: str
    difficulty: str        # "easy" | "medium" | "hard"
    round: int             # which round we're on (1, 2, 3...)
    scores_history: list   # track scores across rounds