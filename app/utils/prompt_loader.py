from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    with open(BASE_PATH / f"{name}.txt", "r", encoding="utf-8") as f:
        return f.read()


def format_prompt(template: str, **kwargs):
    return template.format(**kwargs)