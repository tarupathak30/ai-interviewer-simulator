from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.builder import interview_graph
from app.tools.code_runner import run_code
from app.tools.complexity_analyzer import analyze_complexity
from app.tools.code_quality import analyze_code_quality
from app.tools.report_generator import generate_report
import uuid

router = APIRouter()


class StartRequest(BaseModel):
    session_id: str = None

class HintRequest(BaseModel):
    session_id: str

class SubmitRequest(BaseModel):
    session_id: str
    code: str
    language: str = "python"


def _config(session_id: str):
    return {"configurable": {"thread_id": session_id}}





@router.post("/start")
def start(req: StartRequest):
    sid = req.session_id or str(uuid.uuid4())
    result = interview_graph.invoke({
        "messages":       [],
        "code":           "",
        "language":       "python",
        "hints_used":     0,
        "score":          0,
        "feedback":       "",
        "done":           False,
        "difficulty":     "medium",
        "round":          1,
        "scores_history": [],
        "followup":       "",
        "topic":          "",
        "subtopic":       "",
        "hint_1":         "",
        "hint_2":         "",
        "hint_3":         "",
        "used_topics":    [],
    }, _config(sid))
    return {
        "session_id": sid,
        "question":   result["question"],
        "topic":      result["topic"],
        "subtopic":   result["subtopic"],
        "difficulty": result["difficulty"],
        "round":      result["round"],
    }


@router.post("/next")
def next_question(req: StartRequest):
    if not req.session_id:
        return {"error": "session_id required"}

    state = interview_graph.get_state(_config(req.session_id))
    if not state or not state.values:
        return {"error": "Session not found"}

    current        = state.values
    difficulty     = current.get("difficulty", "medium")
    scores_history = current.get("scores_history", [])
    current_round  = current.get("round", 1)
    used_topics    = current.get("used_topics", [])

    # Add current topic to used list
    current_topic = current.get("topic", "")
    if current_topic and current_topic not in used_topics:
        used_topics = used_topics + [current_topic]

    # Generate fresh LLM question
    from app.graph.nodes import generate_question
    q = generate_question(difficulty, used_topics)

    interview_graph.update_state(
        _config(req.session_id),
        {
            "question":   q["question"],
            "topic":      q["topic"],
            "subtopic":   q["subtopic"],
            "hint_1":     q["hint_1"],
            "hint_2":     q["hint_2"],
            "hint_3":     q["hint_3"],
            "used_topics": used_topics,
            "code":       "",
            "done":       False,
            "round":      current_round + 1,
            "hints_used": 0,
            "followup":   "",
            "messages":   [],
        }
    )

    return {
        "session_id":     req.session_id,
        "question":       q["question"],
        "topic":          q["topic"],
        "subtopic":       q["subtopic"],
        "difficulty":     difficulty,
        "round":          current_round + 1,
        "scores_history": scores_history,
    }



@router.post("/hint")
def hint(req: HintRequest):
    state = interview_graph.get_state(_config(req.session_id))
    if not state:
        return {"error": "Session not found"}

    # Get current hints_used before invoke
    hints_used_before = state.values.get("hints_used", 0)
    
    # Get pre-generated hints directly from state
    hint_map = {
        0: state.values.get("hint_1", ""),
        1: state.values.get("hint_2", ""),
        2: state.values.get("hint_3", ""),
    }
    hint_text = hint_map.get(hints_used_before) or "No more hints available."

    # Update hints_used in state
    interview_graph.update_state(
        _config(req.session_id),
        {"hints_used": hints_used_before + 1}
    )

    return {
        "hint":       hint_text,
        "hints_used": hints_used_before + 1,
    }


    
@router.post("/submit")
def submit(req: SubmitRequest):
    print(">>>> SUBMIT HIT", req)

    # Read current state before invoke
    state = interview_graph.get_state(_config(req.session_id))
    current_question   = ""
    current_round      = 1

    if state and state.values:
        current_question = state.values.get("question", "")
        current_round    = state.values.get("round", 1)

    print(f">>> EVALUATING against question: {current_question}")

    run_result = run_code(req.code, req.language)
    complexity = analyze_complexity(req.code) if req.language == "python" else {
        "time_complexity": "N/A", "space_complexity": "N/A", "reasoning": "Python only"
    }
    quality = analyze_code_quality(req.code) if req.language == "python" else {
        "quality_score": 0, "issues": [], "suggestions": []
    }

    # ── LangGraph handles evaluate → followup chain ──
    result = interview_graph.invoke(
        {
            "code":     req.code,
            "language": req.language,
            "messages": [],
        },
        _config(req.session_id)
    )

    report = generate_report(
        session_id     = req.session_id,
        question       = current_question,
        code           = req.code,
        scores_history = result.get("scores_history", []),
        hints_used     = result.get("hints_used", 0),
        difficulty     = result.get("difficulty", "medium"),
        complexity     = complexity,
        quality        = quality,
        feedback       = result.get("feedback", ""),
        followup       = result.get("followup", ""),
        run_result     = run_result,
        language       = req.language,
    )

    return {
        "score":          result["score"],
        "feedback":       result["feedback"],
        "followup":       result.get("followup", ""),
        "run":            run_result,
        "complexity":     complexity,
        "quality":        quality,
        "difficulty":     result.get("difficulty", "medium"),
        "round":          current_round,
        "scores_history": result.get("scores_history", []),
        "next_question": {
            "difficulty": result.get("difficulty", "medium"),
            "message": {
                "easy":   "Let's try an easier one to build confidence.",
                "medium": "Good work! Here's a similar challenge.",
                "hard":   "Impressive! Ready for a harder problem?",
            }.get(result.get("difficulty", "medium"), "Ready for the next one?")
        },
        **report,
    }

@router.get("/report/{session_id}")
def get_report(session_id: str):
    state = interview_graph.get_state(_config(session_id))
    if not state or not state.values:
        return {"error": "Session not found"}

    s = state.values
    complexity = analyze_complexity(s.get("code", "")) if s.get("language", "python") == "python" else {}
    quality    = analyze_code_quality(s.get("code", "")) if s.get("language", "python") == "python" else {}

    return generate_report(
        session_id     = session_id,
        question       = s.get("question", ""),
        code           = s.get("code", ""),
        scores_history = s.get("scores_history", []),
        hints_used     = s.get("hints_used", 0),
        difficulty     = s.get("difficulty", "medium"),
        complexity     = complexity,
        quality        = quality,
        feedback       = s.get("feedback", ""),
        followup       = s.get("followup", ""),
        run_result     = {"success": False, "output": "", "error": ""},
        language       = s.get("language", "python"),
    )