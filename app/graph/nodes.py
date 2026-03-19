from langchain_groq import ChatGroq
from .state import InterviewState
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.prompt_loader import load_prompt
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2
)

QUESTIONS = {
    "easy": [
        "Write a function that reverses a string.",
        "Write a function that checks if a number is prime.",
        "Write a function that returns the factorial of a number.",
    ],
    "medium": [
        "Write a function that finds all duplicates in a list.",
        "Write a function that checks if a string is a valid palindrome.",
        "Write a function that finds the two numbers in a list that sum to a target.",
    ],
    "hard": [
        "Write a function that finds the longest substring without repeating characters.",
        "Write a function to serialize and deserialize a binary tree.",
        "Implement an LRU cache with O(1) get and put operations.",
    ],
}


def _next_difficulty(current: str, score: int) -> str:
    """Adapt difficulty based on score."""
    if score >= 80:
        # Did well → go harder
        if current == "easy":   return "medium"
        if current == "medium": return "hard"
        return "hard"
    elif score <= 50:
        # Struggled → go easier
        if current == "hard":   return "medium"
        if current == "medium": return "easy"
        return "easy"
    else:
        # Average → stay same
        return current


def _pick_question(difficulty: str, scores_history: list) -> str:
    """Pick a question not already used this session."""
    used_count = len(scores_history)
    questions = QUESTIONS[difficulty]
    # cycle through questions to avoid repeats
    return questions[used_count % len(questions)]


def start_interview(state: InterviewState) -> dict:
    """Pick initial medium question and greet the candidate."""
    difficulty = state.get("difficulty") or "medium"
    scores_history = state.get("scores_history") or []
    question = _pick_question(difficulty, scores_history)

    msg = HumanMessage(content=f"Interview started. Question: {question}")
    return {
        "question": question,
        "difficulty": difficulty,
        "round": 1,
        "scores_history": scores_history,
        "messages": [msg],
        "hints_used": 0,
        "done": False,
    }


def give_hint(state: InterviewState) -> dict:
    base_prompt = load_prompt("hint")
    prompt = f"{base_prompt}\n\nQuestion: {state['question']}\nHints already given: {state['hints_used']}"
    response = llm.invoke([SystemMessage(content=prompt)])
    return {
        "hints_used": state["hints_used"] + 1,
        "messages": [response]
    }


def evaluate_code(state: InterviewState) -> dict:
    base_prompt = load_prompt("interviewer")
    system_prompt = f"{base_prompt}\n\nQuestion: {state['question']}\nHints used: {state['hints_used']}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Candidate's code:\n{state['code']}")
    ])
    data = json.loads(response.content)
    score = data.get("score", 50)

    # Update scores history
    scores_history = list(state.get("scores_history") or [])
    scores_history.append(score)

    # Adapt difficulty for next round
    current_difficulty = state.get("difficulty") or "medium"
    next_difficulty = _next_difficulty(current_difficulty, score)

    return {
        "score": score,
        "feedback": data.get("feedback", ""),
        "done": True,
        "scores_history": scores_history,
        "difficulty": next_difficulty,   # updated for next round
        "messages": [response]
    }


def ask_followup(state: InterviewState) -> dict:
    difficulty = state.get("difficulty", "medium")
    round_num = state.get("round", 1)

    response = llm.invoke([
        SystemMessage(content=(
            "You are a technical interviewer. Based on the candidate's solution, "
            "ask ONE short follow-up question about complexity, edge cases, or optimization. "
            "Be conversational, max 2 sentences."
        )),
        HumanMessage(content=(
            f"Question: {state['question']}\n"
            f"Code:\n{state['code']}\n"
            f"Score: {state['score']}\n"
            f"Current difficulty: {difficulty}\n"
            f"Round: {round_num}"
        ))
    ])
    return {
        "followup": response.content,
        "round": round_num + 1,
        "messages": [response]
    }