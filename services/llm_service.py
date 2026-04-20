import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from groq import Groq
import logging

logger = logging.getLogger(__name__)

# ====================== ENVIRONMENT VARIABLES ======================
AI_BASE_URL = os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL")
AI_API_KEY = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API")  # renamed for clarity

# ====================== MODEL CONFIG ======================
GROQ_MODEL = "llama3-8b-8192"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"
REPLIT_MODEL = "gpt-5-mini"

# ====================== SYSTEM PROMPTS (FIXED) ======================
COLLEGE_SYSTEM_PROMPT = """You are the official AI assistant for Ideal College of Arts and Sciences,
located at Vidyuth Nagar, Kakinada, Andhra Pradesh.

LANGUAGE RULE (VERY IMPORTANT):
# If the user writes in Telugu - reply ONLY in Telugu.
# If the user writes in English - reply ONLY in English.
# If the user writes Roman Telugu - reply in Telugu.
# Never switch languages unless the user switches first.

BEHAVIOR:
- Be friendly, helpful, and professional.
- For college questions, give direct and accurate answers.
- For general questions, be concise and informative.
- Always greet warmly if it is the first message.
- Keep answers clear and easy to understand.

COLLEGE CONTACT (use when needed):
- Phone: "0884-2384382" / "0884-2384381"
- Email: idealcolleges@gmail.com
- Website: https://idealcollege.edu.in
- Location: Vidyuth Nagar, Kakinada, Andhra Pradesh"""

TELUGU_SYSTEM_PROMPT = """మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.

భాషా నియమం: వినియోగదారు తెలుగులో మాట్లాడితే తెలుగులోనే సమాధానం ఇవ్వండి.

ప్రవర్తన:
- స్నేహపూర్వకంగా మరియు సహాయకరంగా ఉండండి.
- కాలేజీ సమాచారాన్ని స్పష్టంగా ఇవ్వండి.
- సమాధానాలు సంక్షిప్తంగా ఉండాలి.

కాలేజీ సంప్రదింపు:
- ఫోన్: "0884-2384382" / "0884-2384381"
- ఇమెయిల్: idealcolleges@gmail.com
- వెబ్‌సైట్: https://idealcollege.edu.in
- చిరునామా: విద్యుత్ నగర్, కాకినాడ, ఆంధ్రప్రదేశ్"""

# ====================== HELPER FUNCTIONS ======================
def build_messages(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    lang: str = "en"
) -> List[Dict[str, str]]:
    if history is None:
        history = []

    sys_prompt = system_prompt or (TELUGU_SYSTEM_PROMPT if lang == "te" else COLLEGE_SYSTEM_PROMPT)
    messages: List[Dict[str, str]] = [{"role": "system", "content": sys_prompt}]

    # Keep only last 10 valid messages
    for msg in history[-10:]:
        if msg.get("role") in ("user", "assistant") and str(msg.get("content", "")).strip():
            messages.append({
                "role": msg["role"],
                "content": str(msg["content"]).strip()
            })

    messages.append({"role": "user", "content": prompt})
    return messages


def call_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    use_completion_tokens: bool = False,
    skip_temperature: bool = False,
) -> str:
    client = OpenAI(base_url=base_url.rstrip("/"), api_key=api_key)

    params: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    if use_completion_tokens:
        params["max_completion_tokens"] = 1200
    else:
        params["max_tokens"] = 1200

    if not skip_temperature:
        params["temperature"] = 0.7

    try:
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI-compatible API error: {e}")
        raise


def query_replit_ai(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    lang: str = "en"
) -> str:
    if not AI_BASE_URL or not AI_API_KEY:
        raise ValueError("Replit AI integration not configured")
    messages = build_messages(prompt, history, system_prompt, lang)
    return call_openai_compatible(
        AI_BASE_URL,
        AI_API_KEY,
        REPLIT_MODEL,
        messages,
        use_completion_tokens=True,
        skip_temperature=True,
    )


def query_groq(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    lang: str = "en"
) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")

    messages = build_messages(prompt, history, system_prompt, lang)
    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise


def query_openrouter(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    lang: str = "en"
) -> str:
    if not OPEN_ROUTER_API_KEY:
        raise ValueError("OPEN_ROUTER_API not configured")
    messages = build_messages(prompt, history, system_prompt, lang)
    return call_openai_compatible(
        "https://openrouter.ai/api/v1",
        OPEN_ROUTER_API_KEY,
        OPENROUTER_MODEL,
        messages,
    )


# ====================== MAIN ENTRY POINT ======================
def query_ai(
    prompt: str,
    history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    lang: str = "en"
) -> str:
    if history is None:
        history = []

    # 1. Try Replit AI first (primary)
    if AI_BASE_URL and AI_API_KEY:
        try:
            return query_replit_ai(prompt, history, system_prompt, lang)
        except Exception as err:
            logger.warning(f"Replit AI failed: {err}. Trying Groq...")

    # 2. Try Groq
    if GROQ_API_KEY:
        try:
            return query_groq(prompt, history, system_prompt, lang)
        except Exception as err:
            logger.warning(f"Groq failed: {err}. Trying OpenRouter...")

    # 3. Try OpenRouter as last fallback
    if OPEN_ROUTER_API_KEY:
        try:
            return query_openrouter(prompt, history, system_prompt, lang)
        except Exception as err:
            logger.error(f"All AI providers failed: {err}")
            raise

    raise RuntimeError("No AI providers are configured. Check environment variables.")