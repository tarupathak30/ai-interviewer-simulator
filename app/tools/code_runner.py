import subprocess
import tempfile
import os

import sys



def run_code(code: str, language: str = "python") -> dict:
    """
    Run code in a subprocess with a timeout.
    Returns stdout, stderr, and whether it succeeded.
    """
    if language != "python":
        return {"output": "", "error": "Only Python supported right now.", "success": False}

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],  # uses whatever python is running this app
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "output": result.stdout,
            "error": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time limit exceeded (5s).", "success": False}
    finally:
        os.unlink(tmp_path)