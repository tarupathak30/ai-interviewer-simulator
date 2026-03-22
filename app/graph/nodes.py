from langchain_groq import ChatGroq
from .state import InterviewState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.utils.prompt_loader import load_prompt
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2
)


def generate_question(difficulty: str, used_topics: list) -> dict:
    """Ask LLM to generate a fresh coding question with topic metadata."""
    used_str = ", ".join(used_topics) if used_topics else "none"

    response = llm.invoke([
        SystemMessage(content="""You are a technical interviewer. Generate a coding interview question.
Respond ONLY with valid JSON in this exact format, no markdown, no extra text:
{
  "question": "Write a function that...",
  "topic": "Hash Maps",
  "subtopic": "Duplicate Detection",
  "hint_1": "Think about what data structure gives O(1) lookup...",
  "hint_2": "A set can track what you have already seen...",
  "hint_3": "Iterate once, check membership, add to seen set..."
}"""),
        HumanMessage(content=f"Difficulty: {difficulty}\nAlready covered topics: {used_str}\nGenerate a NEW question on a DIFFERENT topic. Must be a function implementation task.")
    ])

    try:
        content = response.content.strip()
        # Strip markdown fences if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except Exception as e:
        print(f"[generate_question] JSON parse failed: {e}, raw: {response.content[:200]}")
        return {
            "question": "Write a function that finds all duplicates in a list.",
            "topic": "Hash Maps",
            "subtopic": "Duplicate Detection",
            "hint_1": "Think about tracking seen elements.",
            "hint_2": "A set gives O(1) lookup.",
            "hint_3": "Iterate once and check membership.",
        }


def _next_difficulty(current: str, score: int) -> str:
    if score >= 80:
        if current == "easy":   return "medium"
        if current == "medium": return "hard"
        return "hard"
    elif score <= 50:
        if current == "hard":   return "medium"
        if current == "medium": return "easy"
        return "easy"
    return current


def start_interview(state: InterviewState) -> dict:
    difficulty     = state.get("difficulty") or "medium"
    used_topics    = state.get("used_topics") or []
    scores_history = state.get("scores_history") or []

    q = generate_question(difficulty, used_topics)

    return {
        "question":       q["question"],
        "topic":          q["topic"],
        "subtopic":       q["subtopic"],
        "hint_1":         q["hint_1"],
        "hint_2":         q["hint_2"],
        "hint_3":         q["hint_3"],
        "difficulty":     difficulty,
        "round":          1,
        "scores_history": scores_history,
        "used_topics":    used_topics,
        "messages":       [],   # start clean
        "hints_used":     0,
        "done":           False,
    }


def give_hint(state: InterviewState) -> dict:
    """Progressive hints — uses pre-generated hints, no extra LLM call."""
    hints_used = state.get("hints_used", 0)

    if hints_used == 0:
        hint_text = state.get("hint_1") or "Think about the problem carefully."
    elif hints_used == 1:
        hint_text = state.get("hint_2") or "Consider what data structures could help."
    else:
        hint_text = state.get("hint_3") or "Try iterating once and tracking state."

    return {
        "hints_used": hints_used + 1,
        "messages":   [AIMessage(content=hint_text)]
    }

def evaluate_code(state: InterviewState) -> dict:
    base_prompt = load_prompt("interviewer")
    question   = state.get("question", "")
    hints_used = state.get("hints_used", 0)

    system_prompt = (
        f"{base_prompt}\n\n"
        f"CURRENT QUESTION TO EVALUATE AGAINST: {question}\n"
        f"Hints used by candidate: {hints_used}\n\n"
        f"CRITICAL: Evaluate ONLY against the question above. Ignore everything else."
    )

    # Completely fresh — no state messages used at all
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Candidate's code:\n{state['code']}")
    ])

    try:
        data = json.loads(response.content)
    except Exception:
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        try:
            data = json.loads(content.strip())
        except Exception:
            data = {"score": 50, "feedback": response.content}

    score = data.get("score", 50)
    scores_history = list(state.get("scores_history") or [])
    scores_history.append(score)
    next_difficulty = _next_difficulty(state.get("difficulty") or "medium", score)

    return {
        "score":          score,
        "feedback":       data.get("feedback", ""),
        "done":           True,
        "scores_history": scores_history,
        "difficulty":     next_difficulty,
        "messages":       [],
    }



def ask_followup(state: InterviewState) -> dict:
    question  = state.get("question", "")
    code      = state.get("code", "")
    score     = state.get("score", 0)
    round_num = state.get("round", 1)
    difficulty = state.get("difficulty", "medium")

    response = llm.invoke([
        SystemMessage(content=(
            "You are a technical interviewer. Based on the candidate's solution to the specific question below, "
            "ask ONE short follow-up question about complexity, edge cases, or optimization. "
            "Be conversational, max 2 sentences. Stay strictly on topic."
        )),
        HumanMessage(content=(
            f"Question: {question}\n"
            f"Code:\n{code}\n"
            f"Score: {score}\n"
            f"Difficulty: {difficulty}\n"
            f"Round: {round_num}"
        ))
    ])

    return {
        "followup": response.content,
        "messages": [],   # wipe after followup too
    }


