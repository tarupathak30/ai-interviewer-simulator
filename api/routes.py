from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.graph.builder import interview_graph
from app.tools.code_runner import run_code
import uuid
import json

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
        "messages": [], "code": "", "language": "python",
        "hints_used": 0, "score": 0, "feedback": "", "done": False
    }, _config(sid))
    return {"session_id": sid, "question": result["question"]}

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

# Swagger UI schema model (for docs only)
class SubmitRequest(BaseModel):
    session_id: str
    code: str
    language: str = "python"

@router.post("/submit")
def submit(req: SubmitRequest):
    print(">>>> SUBMIT HIT", req)
    run_result = run_code(req.code, req.language)
    result = interview_graph.invoke(
        {
            "code": req.code,
            "language": req.language,
            "messages": [{"role": "user", "content": f"evaluate: {req.code}"}]
        },
        _config(req.session_id)
    )
    return {
        "score":    result["score"],
        "feedback": result["feedback"],
        "followup": result.get("followup", ""),
        "run":      run_result,
    }