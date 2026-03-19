from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class InterviewState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str          # current coding question
    code: str              # candidate's latest code submission
    language: str          # python / javascript
    hints_used: int        # how many hints they've asked for
    score: int             # 0-100
    feedback: str          # final written feedback
    done: bool
    followup: str          # follow-up question asked after evaluation