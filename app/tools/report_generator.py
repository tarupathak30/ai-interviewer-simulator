from datetime import datetime


def generate_report(
    session_id: str,
    question: str,
    code: str,
    scores_history: list,
    hints_used: int,
    difficulty: str,
    complexity: dict,
    quality: dict,
    feedback: str,
    followup: str,
    run_result: dict,
    language: str = "python",
) -> dict:
    """Generate a full session report for a candidate."""

    final_score = scores_history[-1] if scores_history else 0
    avg_score = round(sum(scores_history) / len(scores_history), 1) if scores_history else 0

    performance_label = _performance_label(final_score)
    hire_recommendation = _hire_recommendation(
        final_score, hints_used, quality.get("quality_score", 0)
    )

    return {
        "report": {
            "meta": {
                "session_id":   session_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "language":     language,
                "difficulty":   difficulty,
                "rounds":       len(scores_history),
            },
            "problem": {
                "question": question,
                "code_submitted": code,
            },
            "performance": {
                "final_score":       final_score,
                "average_score":     avg_score,
                "scores_history":    scores_history,
                "performance_label": performance_label,
                "hints_used":        hints_used,
                "hint_penalty":      _hint_penalty(hints_used),
                "adjusted_score":    max(0, final_score - _hint_penalty(hints_used)),
            },
            "code_analysis": {
                "complexity": {
                    "time":      complexity.get("time_complexity", "N/A"),
                    "space":     complexity.get("space_complexity", "N/A"),
                    "reasoning": complexity.get("reasoning", ""),
                },
                "quality": {
                    "score":          quality.get("quality_score", 0),
                    "pep8_violations": quality.get("pep8_violations", 0),
                    "has_docstrings": quality.get("has_docstrings", False),
                    "naming_issues":  quality.get("naming_issues", []),
                    "issues":         quality.get("issues", []),
                    "suggestions":    quality.get("suggestions", []),
                },
                "execution": {
                    "success": run_result.get("success", False),
                    "output":  run_result.get("output", ""),
                    "error":   run_result.get("error", ""),
                },
            },
            "interviewer_notes": {
                "feedback":           feedback,
                "followup_question":  followup,
            },
            "verdict": {
                "hire_recommendation": hire_recommendation,
                "strengths":          _strengths(final_score, hints_used, complexity, quality, run_result),
                "improvements":       _improvements(hints_used, complexity, quality, run_result),
                "summary":            _summary(session_id, final_score, difficulty, hints_used, performance_label, hire_recommendation),
            }
        }
    }


def _performance_label(score: int) -> str:
    if score >= 90: return "Excellent"
    if score >= 75: return "Good"
    if score >= 60: return "Average"
    if score >= 40: return "Below Average"
    return "Poor"


def _hint_penalty(hints_used: int) -> int:
    # -3 points per hint used
    return hints_used * 3


def _hire_recommendation(score: int, hints_used: int, quality_score: int) -> str:
    adjusted = score - _hint_penalty(hints_used)
    combined = (adjusted * 0.7) + (quality_score * 0.3)
    if combined >= 80: return "Strong Hire"
    if combined >= 65: return "Hire"
    if combined >= 50: return "Maybe"
    return "No Hire"


def _strengths(score, hints_used, complexity, quality, run_result) -> list:
    strengths = []
    if score >= 80:
        strengths.append("Strong problem-solving ability")
    if hints_used == 0:
        strengths.append("Solved independently without hints")
    if complexity.get("time_complexity") in ("O(n)", "O(log n)", "O(1)", "O(n log n)"):
        strengths.append(f"Efficient algorithm — {complexity.get('time_complexity')} time complexity")
    if quality.get("pep8_violations", 1) == 0:
        strengths.append("Clean code with no PEP 8 violations")
    if quality.get("has_docstrings"):
        strengths.append("Well-documented code with docstrings")
    if run_result.get("success"):
        strengths.append("Code runs correctly and produces expected output")
    return strengths or ["Attempted the problem"]


def _improvements(hints_used, complexity, quality, run_result) -> list:
    improvements = []
    if hints_used > 2:
        improvements.append(f"Needed {hints_used} hints — work on independent problem solving")
    if complexity.get("time_complexity") in ("O(n²)", "O(n³)", "O(2^n)"):
        improvements.append(f"Optimize time complexity — currently {complexity.get('time_complexity')}")
    if not quality.get("has_docstrings"):
        improvements.append("Add docstrings to document functions")
    if quality.get("pep8_violations", 0) > 3:
        improvements.append(f"{quality.get('pep8_violations')} PEP 8 violations — improve code style")
    if not run_result.get("success"):
        improvements.append("Code did not run successfully — fix runtime errors")
    return improvements or ["No major improvements needed"]


def _summary(session_id, score, difficulty, hints_used, label, recommendation) -> str:
    return (
        f"Candidate (session: {session_id}) attempted a {difficulty}-level problem "
        f"and scored {score}/100 ({label}). "
        f"They used {hints_used} hint(s) during the session. "
        f"Overall verdict: {recommendation}."
    )