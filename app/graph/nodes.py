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
    "easy": "Write a function that reverses a string.",
    "medium": "Write a function that finds all duplicates in a list.",
    "hard": "Write a function that finds the longest substring without repeating characters.",
}

def start_interview(state: InterviewState) -> dict:
    """Pick a question and greet the candidate."""
    question = QUESTIONS["medium"]
    msg = HumanMessage(content=f"Interview started. Question: {question}")
    return {
        "question": question,
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
    return {
        "score": data.get("score", 50),
        "feedback": data.get("feedback", ""),
        "done": True,
        "messages": [response]
    }


def ask_followup(state: InterviewState) -> dict:
    response = llm.invoke([
        SystemMessage(content="You are a technical interviewer. Based on the candidate's solution, ask ONE short follow-up question about complexity, edge cases, or a possible optimization. Be conversational, max 2 sentences."),
        HumanMessage(content=f"Question: {state['question']}\nCode:\n{state['code']}\nScore: {state['score']}")
    ])
    return {
        "followup": response.content,
        "messages": [response]
    }