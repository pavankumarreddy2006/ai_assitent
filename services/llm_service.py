import requests
from config.config import (
    GROQ_API_KEY, OPEN_ROUTER_API,
    GROQ_MODEL, OPENROUTER_MODEL
)

COLLEGE_SYSTEM_PROMPT = (
    "You are a helpful AI assistant for Ideal College of Arts and Sciences, Kakinada, Andhra Pradesh. "
    "Provide accurate, concise, and friendly responses. "
    "For college questions, be enthusiastic and informative. "
    "For general questions, be knowledgeable and helpful."
)


def _build_messages(
    prompt: str,
    history: list[dict] | None = None,
    system_prompt: str | None = None
) -> list[dict]:
    messages = [{"role": "system", "content": system_prompt or COLLEGE_SYSTEM_PROMPT}]
    if history:
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    return messages


def query_groq(
    prompt: str,
    history: list[dict] | None = None,
    system_prompt: str | None = None
) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")

    messages = _build_messages(prompt, history, system_prompt)

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def query_openrouter(
    prompt: str,
    history: list[dict] | None = None,
    system_prompt: str | None = None
) -> str:
    if not OPEN_ROUTER_API:
        raise ValueError("OPEN_ROUTER_API not configured")

    messages = _build_messages(prompt, history, system_prompt)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPEN_ROUTER_API}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
