from typing import TypedDict

class InterviewState(TypedDict):
    messages:       list          # ← plain list, no add_messages reducer
    question:       str
    topic:          str
    subtopic:       str
    hint_1:         str
    hint_2:         str
    hint_3:         str
    used_topics:    list
    code:           str
    language:       str
    hints_used:     int
    score:          int
    feedback:       str
    done:           bool
    followup:       str
    difficulty:     str
    round:          int
    scores_history: list