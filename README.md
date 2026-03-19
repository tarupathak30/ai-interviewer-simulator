# Automated Technical Screening Engine 

An agentic AI system that conducts live, adaptive coding interviews — evaluating code quality, complexity, and problem-solving ability with human-like insight.

---

## What It Does

Automated Technical Screening Engine acts as a technical interviewer. It asks coding questions, adapts difficulty based on performance, analyzes submitted code in real-time, and generates a full candidate report with a hire recommendation.

---

## Features

- **Adaptive Difficulty** — questions get harder or easier based on your score
- **Real-time Code Execution** — runs code safely in a sandboxed environment
- **Big O Complexity Analysis** — detects time and space complexity automatically
- **PEP 8 + Code Quality** — checks style, naming, docstrings, and violations
- **LLM Evaluation** — scores code and generates detailed feedback via Groq LLM
- **Follow-up Questions** — probes deeper understanding after each submission
- **Session Report** — full candidate report with strengths, improvements, and hire verdict

---

## Tech Stack

| Layer | Tech |
|---|---|
| API | FastAPI + Uvicorn |
| AI Agent | LangGraph + LangChain |
| LLM | Groq |
| Code Execution | Sandboxed subprocess |
| State Management | LangGraph MemorySaver |
| Analysis | AST-based complexity + quality analyzer |

---

## Project Structure
```
interview-simulator/
├── api/
│   ├── main.py              # FastAPI app + middleware
│   └── routes.py            # API endpoints
├── app/
│   ├── graph/
│   │   ├── builder.py       # LangGraph graph definition
│   │   ├── nodes.py         # Interview nodes (start, hint, evaluate, followup)
│   │   ├── edges.py         # Routing logic
│   │   └── state.py         # Interview state schema
│   ├── tools/
│   │   ├── code_runner.py        # Sandboxed code execution
│   │   ├── complexity_analyzer.py # Big O detection via AST
│   │   ├── code_quality.py        # PEP 8 + style analysis
│   │   └── report_generator.py   # Session report generator
│   ├── prompts/
│   │   ├── interviewer.txt   # LLM evaluation prompt
│   │   └── hint.txt          # LLM hint prompt
│   └── utils/
│       └── prompt_loader.py
├── test.py
├── requirements.txt
└── .env
```

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/interview-simulator.git
cd interview-simulator
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Add your GROQ_API_KEY in .env
```

### 5. Run the server
```bash
uvicorn api.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for the Swagger UI.

---

## API Endpoints

### `POST /api/start` — Start interview session
```json
{ "session_id": "optional" }
```
```json
{ "session_id": "abc123", "question": "Find all duplicates in a list.", "difficulty": "medium", "round": 1 }
```

### `POST /api/hint` — Get a progressive hint
```json
{ "session_id": "abc123" }
```

### `POST /api/submit` — Submit code for evaluation
```json
{ "session_id": "abc123", "code": "def find_dupes(arr):\n    ...", "language": "python" }
```
Response includes: score, feedback, followup, complexity, quality, report, next question.