# Frontend — Agentic Code Interview Engine

React frontend for the Agentic Code Interview Engine. Provides a candidate-facing interview interface and a hiring manager dashboard.

---

## Views

**Interview Tab** — start a session, write code, request hints, submit for evaluation. Shows score, complexity analysis, code quality, execution output, strengths, improvements, and next question.

**Dashboard Tab** — paste a session ID to load a full candidate report with hire recommendation, metrics, and interviewer notes.

---

## Setup

Make sure the backend is running first at `http://127.0.0.1:8000`.
```bash
npm install
npm start
```

Opens at **http://localhost:3000**

---

## Build for Production
```bash
npm run build
```

---

## Stack

- React (Create React App)
- Pure CSS-in-JS styling — no external UI library
- DM Sans + DM Mono fonts
- Dark / Light theme toggle


## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/start` | Start a new interview session |
| POST | `/api/hint` | Get a progressive hint |
| POST | `/api/submit` | Submit code for evaluation |
| POST | `/api/next` | Advance to next question |
| GET | `/api/report/{session_id}` | Get full session report |

---

## Engineering Notes

**LangGraph state bleed** — `add_messages` reducer accumulated messages across rounds, causing the LLM to evaluate code against stale questions from previous rounds. Fixed by replacing the reducer with a plain list and injecting the current question explicitly into the system prompt on every evaluation.

**ASGI JSON middleware** — Swagger UI sends raw unescaped newlines inside JSON string bodies. Built a custom ASGI middleware that intercepts the raw byte stream and parses it character-by-character, escaping control characters before FastAPI's JSON parser runs.

**AST complexity detection** — `set()` and `dict()` constructor calls were not being detected as hash structures since the visitor only caught literal `{...}` syntax. Fixed by adding `visit_Call` handlers for `set()`, `dict()`, `Counter()`, `defaultdict()`, and `OrderedDict()`.