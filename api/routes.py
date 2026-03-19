from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.builder import interview_graph
from app.tools.code_runner import run_code
from app.tools.complexity_analyzer import analyze_complexity
from app.tools.code_quality import analyze_code_quality
from app.graph.nodes import _pick_question
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


# Standalone report endpoint
class ReportRequest(BaseModel):
    session_id: str


def _config(session_id: str):
    return {"configurable": {"thread_id": session_id}}


def _pick_next_question(result: dict) -> dict:
    difficulty = result.get("difficulty", "medium")
    scores_history = result.get("scores_history", [])
    return {
        "difficulty": difficulty,
        "question": _pick_question(difficulty, scores_history),
        "message": {
            "easy":   "Let's try an easier one to build confidence.",
            "medium": "Good work! Here's a similar challenge.",
            "hard":   "Impressive! Ready for a harder problem?",
        }[difficulty]
    }


@router.post("/start")
def start(req: StartRequest):
    sid = req.session_id or str(uuid.uuid4())
    result = interview_graph.invoke({
        "messages":      [],
        "code":          "",
        "language":      "python",
        "hints_used":    0,
        "score":         0,
        "feedback":      "",
        "done":          False,
        "difficulty":    "medium",
        "round":         1,
        "scores_history": [],
        "followup":      "",
    }, _config(sid))
    return {
        "session_id": sid,
        "question":   result["question"],
        "difficulty": result["difficulty"],
        "round":      result["round"],
    }


@router.post("/hint")
def hint(req: HintRequest):
    state = interview_graph.get_state(_config(req.session_id))
    if not state:
        return {"error": "Session not found"}
    result = interview_graph.invoke(
        {"messages": [{"role": "user", "content": "hint"}]},
        _config(req.session_id)
    )
    last = result["messages"][-1].content
    return {"hint": last, "hints_used": result["hints_used"]}





from app.tools.report_generator import generate_report

# Add this to your existing imports at top of routes.py


@router.post("/submit")
def submit(req: SubmitRequest):
    print(">>>> SUBMIT HIT", req)

    run_result  = run_code(req.code, req.language)
    complexity  = analyze_complexity(req.code) if req.language == "python" else {
        "time_complexity": "N/A", "space_complexity": "N/A", "reasoning": "Python only"
    }
    quality     = analyze_code_quality(req.code) if req.language == "python" else {
        "quality_score": 0, "issues": [], "suggestions": []
    }

    result = interview_graph.invoke(
        {
            "code":     req.code,
            "language": req.language,
            "messages": [{"role": "user", "content": f"evaluate: {req.code}"}]
        },
        _config(req.session_id)
    )

    # Generate session report
    report = generate_report(
        session_id    = req.session_id,
        question      = result.get("question", ""),
        code          = req.code,
        scores_history= result.get("scores_history", []),
        hints_used    = result.get("hints_used", 0),
        difficulty    = result.get("difficulty", "medium"),
        complexity    = complexity,
        quality       = quality,
        feedback      = result.get("feedback", ""),
        followup      = result.get("followup", ""),
        run_result    = run_result,
        language      = req.language,
    )

    return {
        "score":          result["score"],
        "feedback":       result["feedback"],
        "followup":       result.get("followup", ""),
        "run":            run_result,
        "complexity":     complexity,
        "quality":        quality,
        "difficulty":     result.get("difficulty", "medium"),
        "round":          result.get("round", 1),
        "scores_history": result.get("scores_history", []),
        "next_question":  _pick_next_question(result),
        **report,   # merges "report": {...} into response
    }



@router.get("/report/{session_id}")
def get_report(session_id: str):
    state = interview_graph.get_state(_config(session_id))
    if not state or not state.values:
        return {"error": "Session not found"}

    s = state.values
    complexity = analyze_complexity(s.get("code", "")) if s.get("language", "python") == "python" else {}
    quality    = analyze_code_quality(s.get("code", ""))  if s.get("language", "python") == "python" else {}

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