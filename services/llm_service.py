import requests
from config.config import (
    GROQ_API_KEY, OPEN_ROUTER_API,
    GROQ_MODEL, OPENROUTER_MODEL
)

# =====================================================
# BILINGUAL SYSTEM PROMPT (Telugu + English)
# =====================================================
COLLEGE_SYSTEM_PROMPT = """You are the official AI assistant for Ideal College of Arts and Sciences, 
located at Vidyuth Nagar, Kakinada, Andhra Pradesh.

LANGUAGE RULE (VERY IMPORTANT):
- If the user writes in Telugu → you MUST reply in Telugu only.
- If the user writes in English → you MUST reply in English only.
- If the user mixes both → reply in the dominant language used.
- Never switch languages unless the user switches first.

BEHAVIOR:
- Be friendly, helpful, and professional.
- For college questions, give direct and accurate answers.
- For general questions, be concise and informative.
- Always greet warmly if it is the first message.
- Keep answers clear and easy to understand.

COLLEGE CONTACT (use when needed):
- Phone: 0884-2384382 / 0884-2384381
- Email: idealcolleges@gmail.com
- Website: https://idealcollege.edu.in
- Location: Vidyuth Nagar, Kakinada, Andhra Pradesh
"""

# =====================================================
# TELUGU-SPECIFIC SYSTEM PROMPT
# =====================================================
TELUGU_SYSTEM_PROMPT = """మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.

భాషా నియమం (చాలా ముఖ్యమైనది):
- వినియోగదారు తెలుగులో మాట్లాడితే → తెలుగులో మాత్రమే సమాధానం ఇవ్వండి.
- వినియోగదారు ఇంగ్లీష్‌లో మాట్లాడితే → ఇంగ్లీష్‌లో సమాధానం ఇవ్వండి.

ప్రవర్తన:
- స్నేహపూర్వకంగా మరియు సహాయకరంగా ఉండండి.
- కాలేజీ సమాచారాన్ని స్పష్టంగా మరియు నేరుగా ఇవ్వండి.
- సమాధానాలు సంక్షిప్తంగా మరియు అర్థమయ్యేలా ఉండాలి.

కాలేజీ సంప్రదింపు:
- ఫోన్: 0884-2384382 / 0884-2384381
- ఇమెయిల్: idealcolleges@gmail.com
- వెబ్‌సైట్: https://idealcollege.edu.in
- చిరునామా: విద్యుత్ నగర్, కాకినాడ, ఆంధ్రప్రదేశ్
"""


def _build_messages(
    prompt: str,
    history: list[dict] | None = None,
    system_prompt: str | None = None,
    lang: str = "en"
) -> list[dict]:
    """Build message list for LLM API call."""

    # Choose default system prompt based on detected language
    if system_prompt is None:
        if lang == "te":
            system_prompt = TELUGU_SYSTEM_PROMPT
        else:
            system_prompt = COLLEGE_SYSTEM_PROMPT

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})
    return messages


def query_groq(
    prompt: str,
    history: list[dict] | None = None,
    system_prompt: str | None = None,
    lang: str = "en"
) -> str:
    """Query Groq API (Llama model). Returns AI response string."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")

    messages = _build_messages(prompt, history, system_prompt, lang)

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
    system_prompt: str | None = None,
    lang: str = "en"
) -> str:
    """Query OpenRouter API (fallback). Returns AI response string."""
    if not OPEN_ROUTER_API:
        raise ValueError("OPEN_ROUTER_API not configured")

    messages = _build_messages(prompt, history, system_prompt, lang)

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
