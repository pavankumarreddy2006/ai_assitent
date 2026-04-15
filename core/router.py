"""
router.py — Routes each request to the correct handler.

Intent flow:
  college  → college_service (smart DB lookup) → llm with full college context
  weather  → weather_service
  news     → news_service
  search   → search_service → llm summarize
  general  → llm (Groq → OpenRouter → search fallback)

Language:
  - detect_language() auto-detects Telugu vs English
  - All handlers pass lang to LLM so responses match user's language
"""

from core.intent import classify_intent, extract_city, detect_language
from core.responder import (
    format_college_response,
    format_weather_response,
    format_news_response,
    format_search_response,
    format_general_response,
    format_error_response,
)
from services.college_service import (
    get_college_answer,
    get_college_context_prompt,
)
from services.llm_service import query_groq, query_openrouter
from services.search_service import search_duckduckgo, format_search_results
from services.news_service import fetch_news
from services.weather_service import get_weather


def route_message(message: str, conversation_history: list[dict] | None = None) -> dict:
    if conversation_history is None:
        conversation_history = []

    lang   = detect_language(message)   # "te" or "en"
    intent = classify_intent(message)   # "college" | "weather" | "news" | "search" | "general"

    try:
        if intent == "college":
            return _handle_college(message, conversation_history, lang)
        elif intent == "weather":
            return _handle_weather(message, lang)
        elif intent == "news":
            return _handle_news(message, lang)
        elif intent == "search":
            return _handle_search(message, conversation_history, lang)
        else:
            return _handle_general(message, conversation_history, lang)
    except Exception as e:
        print(f"[Router Error] {e}")
        return format_error_response()


# ── COLLEGE ────────────────────────────────────────────────────

def _handle_college(message: str, history: list[dict], lang: str) -> dict:
    # Step 1: Direct keyword match from college_data.py
    result = get_college_answer(message, lang=lang)
    if result:
        return format_college_response(result, "College Database")

    # Step 2: AI with full college context
    college_context = get_college_context_prompt()

    if lang == "te":
        system_prompt = (
            "మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.\n\n"
            "కింది కాలేజీ సమాచారం మాత్రమే ఉపయోగించి తెలుగులో సమాధానం ఇవ్వండి.\n"
            "సమాచారం లేకపోతే ఇలా చెప్పండి: "
            "'ఆ వివరాలు నా దగ్గర లేవు. దయచేసి కాలేజీని 0884-2384382 లో సంప్రదించండి.'\n\n"
            f"కాలేజీ సమాచారం:\n{college_context}"
        )
    else:
        system_prompt = (
            "You are the official AI assistant for Ideal College of Arts and Sciences, "
            "Vidyuth Nagar, Kakinada, Andhra Pradesh.\n\n"
            "Use ONLY the following college data to answer in English. "
            "Be direct, clear, and helpful. "
            "If information is not available, say: "
            "'I don't have that specific information. "
            "Please contact the college at 0884-2384382 or email idealcolleges@gmail.com.'\n\n"
            f"COLLEGE INFORMATION:\n{college_context}"
        )

    try:
        answer = query_groq(message, history, system_prompt, lang=lang)
        return format_college_response(answer, "AI + College Data")
    except Exception:
        try:
            answer = query_openrouter(message, history, system_prompt, lang=lang)
            return format_college_response(answer, "AI + College Data")
        except Exception:
            if lang == "te":
                return format_college_response(
                    "ఆ వివరాలు నా దగ్గర లేవు. దయచేసి కాలేజీని 0884-2384382 లో సంప్రదించండి "
                    "లేదా idealcolleges@gmail.com కి ఇమెయిల్ చేయండి.",
                    "College Database"
                )
            else:
                return format_college_response(
                    "I don't have specific information about that. "
                    "Please contact the college at 0884-2384382 or email idealcolleges@gmail.com.",
                    "College Database"
                )


# ── WEATHER ───────────────────────────────────────────────────

def _handle_weather(message: str, lang: str) -> dict:
    city         = extract_city(message) or "Kakinada"
    weather_data = get_weather(city)

    if weather_data and lang == "te":
        reply = (
            f"{weather_data['city']}లో వాతావరణం: {weather_data['description']}, "
            f"ఉష్ణోగ్రత: {weather_data['temperature']}°C, "
            f"తేమ: {weather_data['humidity']}%, "
            f"గాలి వేగం: {weather_data['wind_speed']} km/h."
        )
        return {"reply": reply, "intent": "weather", "source": "Open-Meteo", "show_video": False, "video_url": None}

    if not weather_data and lang == "te":
        return {"reply": f"'{city}' వాతావరణ సమాచారం దొరకలేదు.", "intent": "weather", "source": "Weather Service", "show_video": False, "video_url": None}

    return format_weather_response(weather_data, city)


# ── NEWS ──────────────────────────────────────────────────────

def _handle_news(message: str, lang: str) -> dict:
    import re
    raw_query = re.sub(
        r"news|latest|headlines|breaking|today|వార్తలు|తాజా|సమాచారం",
        "", message, flags=re.IGNORECASE
    ).strip()

    articles = fetch_news(raw_query or "education India")

    if lang == "te":
        if articles:
            lines = ["తాజా విషయాలు:\n"]
            for i, a in enumerate(articles[:5], 1):
                lines.append(f"{i}. {a['title']} — {a['source']}")
            reply = "\n".join(lines)
        else:
            reply = "ప్రస్తుతం వార్తలు తీసుకోలేకపోయాము. తర్వాత మళ్ళీ ప్రయత్నించండి."
        return {"reply": reply, "intent": "news", "source": "News API", "show_video": False, "video_url": None}

    return format_news_response(articles)


# ── SEARCH ────────────────────────────────────────────────────

def _handle_search(message: str, history: list[dict], lang: str) -> dict:
    results   = search_duckduckgo(message)
    formatted = format_search_results(results)

    if lang == "te":
        prompt = f"ఈ ప్రశ్నకు తెలుగులో స్పష్టంగా సమాధానం ఇవ్వండి: \"{message}\"\n\nవెబ్ సమాచారం:\n{formatted}"
    else:
        prompt = f"Answer this question directly and concisely: \"{message}\"\n\nContext:\n{formatted}"

    try:
        answer = query_groq(prompt, history, lang=lang)
        return format_search_response(answer, "Internet Search + AI")
    except Exception:
        try:
            answer = query_openrouter(prompt, history, lang=lang)
            return format_search_response(answer, "Internet Search + AI")
        except Exception:
            return format_search_response(formatted, "Internet Search")


# ── GENERAL ───────────────────────────────────────────────────

def _handle_general(message: str, history: list[dict], lang: str) -> dict:
    try:
        answer = query_groq(message, history, lang=lang)
        return format_general_response(answer, "Groq AI")
    except Exception:
        try:
            answer = query_openrouter(message, history, lang=lang)
            return format_general_response(answer, "OpenRouter AI")
        except Exception:
            results = search_duckduckgo(message)
            return format_general_response(format_search_results(results), "Internet Search")