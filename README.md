# 🚀 AI Interview Simulator

An AI-powered backend system that evaluates coding responses, provides structured feedback, and simulates real interview scenarios.

## 🧠 Overview

This project simulates a technical interview environment where users submit code solutions and receive:

- ✅ Automated evaluation
- 📊 Score-based feedback
- 💬 Constructive suggestions
- 🔁 Follow-up questions (just like real interviews)

Built to mimic real-world coding interviews using modern LLM-powered workflows.

---

## ⚙️ Features

- 🧪 Code execution and validation
- 📈 Scoring system for responses
- 💡 Feedback generation (strengths + improvements)
- ❓ Dynamic follow-up questions
- 🔄 API-based architecture for easy integration

---

## 🏗️ Tech Stack

- **Backend:** FastAPI
- **LLMs / NLP:** OpenAI / LangChain / LangGraph
- **Execution Engine:** Python sandboxing
- **Environment:** Uvicorn

---


---

## 🚀 Getting Started

### 1. Clone the repo

git clone https://github.com/your-username/interview-simulator.git
cd interview-simulator


### 2. Create Virtual Environment 
python -m venv venv
venv\Scripts\activate   # Windows


### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the server
uvicorn api.main:app --reload


Server runs at:
👉 http://127.0.0.1:8000