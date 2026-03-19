import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"