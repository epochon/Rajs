"""Configuration for The Rational Decision Engine. Only Groq and DeepSeek."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# groq | deepseek — default to groq if key set, else deepseek
LLM_PROVIDER = (os.environ.get("LLM_PROVIDER", "") or "groq").lower().strip()
if LLM_PROVIDER not in ("groq", "deepseek"):
    LLM_PROVIDER = "groq" if GROQ_API_KEY else "deepseek"

COMBINED_DEBATE = os.environ.get("COMBINED_DEBATE", "").lower() in ("1", "true", "yes")
LITE_MODE = os.environ.get("LITE_MODE", "").lower() in ("1", "true", "yes")
