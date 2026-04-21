# services/llm_service.py
import os
from typing import List, Dict, Optional

from groq import Groq
from openai import OpenAI

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

SYSTEM_EN = (
    "You are IDEAL AI for Ideal College. "
    "Answer clearly and accurately. Keep responses concise and helpful."
)
SYSTEM_TE = (
    "మీరు ఐడియల్ కాలేజ్ కోసం IDEAL AI. "
    "స్పష్టంగా, సరైన సమాచారంతో, సంక్షిప్తంగా సమాధానం ఇవ్వండి."
)


def _build_messages(prompt: str, history: Optional[List[Dict[str, str]]], lang: str) -> List[Dict[str, str]]:
    sys = SYSTEM_TE if lang == "te" else SYSTEM_EN
    messages = [{"role": "system", "content": sys}]
    for m in (history or [])[-8:]:
        if m.get("role") in {"user", "assistant"} and m.get("content"):
            messages.append({"role": m["role"], "content": str(m["content"])})
    messages.append({"role": "user", "content": prompt})
    return messages


def _query_groq(prompt: str, history: Optional[List[Dict[str, str]]], lang: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY")
    client = Groq(api_key=GROQ_API_KEY)
    res = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=_build_messages(prompt, history, lang),
        temperature=0.6,
        max_tokens=700,
    )
    return (res.choices[0].message.content or "").strip()


def _query_openrouter(prompt: str, history: Optional[List[Dict[str, str]]], lang: str) -> str:
    if not OPEN_ROUTER_API:
        raise RuntimeError("Missing OPEN_ROUTER_API")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPEN_ROUTER_API)
    res = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=_build_messages(prompt, history, lang),
        temperature=0.6,
        max_tokens=700,
    )
    return (res.choices[0].message.content or "").strip()


def query_ai(prompt: str, history: Optional[List[Dict[str, str]]] = None, lang: str = "en") -> str:
    # Never throw to router; always return safe fallback text.
    try:
        return _query_groq(prompt, history, lang)
    except Exception:
        try:
            return _query_openrouter(prompt, history, lang)
        except Exception:
            return (
                "I could not reach AI providers now. Please try again in a moment."
                if lang == "en"
                else "AI సేవలు ఇప్పుడు అందుబాటులో లేవు. కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి."
            )