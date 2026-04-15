"""
router.py — Decides where each request goes and orchestrates the response.

Intent flow:
  college  → college_service (smart DB lookup) → llm_service (AI with full college context)
  weather  → weather_service
  news     → news_service
  search   → search_service → llm_service (summarize results)
  general  → llm_service (Groq → OpenRouter → search fallback)
"""

from core.intent import classify_intent, extract_city
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
    """
    Main routing function.
    Returns a response dict: reply, intent, source, show_video, video_url
    """
    if conversation_history is None:
        conversation_history = []

    intent = classify_intent(message)

    try:
        if intent == "college":
            return _handle_college(message, conversation_history)
        elif intent == "weather":
            return _handle_weather(message)
        elif intent == "news":
            return _handle_news(message)
        elif intent == "search":
            return _handle_search(message, conversation_history)
        else:
            return _handle_general(message, conversation_history)

    except Exception as e:
        print(f"[Router Error] {e}")
        return format_error_response()


# ──────────────────────────────────────────────────────────────
# HANDLERS
# ──────────────────────────────────────────────────────────────

def _handle_college(message: str, history: list[dict]) -> dict:
    """
    Try direct DB lookup first.
    If no match, send the FULL college context to AI so it can answer precisely.
    """

    # Step 1: Smart keyword lookup from college_data.py
    result = get_college_answer(message)
    if result:
        return format_college_response(result, "College Database")

    # Step 2: AI with full college context (no guessing)
    try:
        college_context = get_college_context_prompt()

        system_prompt = (
            "You are the official AI assistant for Ideal College of Arts and Sciences, "
            "located at Vidyuth Nagar, Kakinada, Andhra Pradesh.\n\n"
            "Use ONLY the following college information to answer. "
            "Give a clear, direct, and helpful answer. "
            "If the answer is not in the data, say: "
            "'I don't have that specific information. Please contact the college at "
            "0884-2384382 or email idealcolleges@gmail.com.'\n\n"
            "If the user writes in Telugu, respond in Telugu.\n\n"
            f"COLLEGE INFORMATION:\n{college_context}"
        )

        answer = query_groq(message, history, system_prompt)
        return format_college_response(answer, "AI + College Data")

    except Exception:
        try:
            # OpenRouter fallback
            college_context = get_college_context_prompt()
            system_prompt = (
                "You are the AI assistant for Ideal College of Arts and Sciences, Kakinada. "
                "Answer using only the college data provided. "
                "If the user writes in Telugu, respond in Telugu.\n\n"
                f"COLLEGE INFORMATION:\n{college_context}"
            )
            answer = query_openrouter(message, history, system_prompt)
            return format_college_response(answer, "AI + College Data")

        except Exception:
            return format_college_response(
                "I don't have specific information about that. "
                "Please contact the college at 0884-2384382 or email idealcolleges@gmail.com.",
                "College Database"
            )


def _handle_weather(message: str) -> dict:
    city = extract_city(message) or "Kakinada"
    weather_data = get_weather(city)
    return format_weather_response(weather_data, city)


def _handle_news(message: str) -> dict:
    import re
    raw_query = re.sub(
        r"news|latest|headlines|breaking|today", "", message, flags=re.IGNORECASE
    ).strip()
    articles = fetch_news(raw_query or "education India")
    return format_news_response(articles)


def _handle_search(message: str, history: list[dict]) -> dict:
    results = search_duckduckgo(message)
    formatted = format_search_results(results)

    try:
        prompt = (
            f"Answer this question directly and concisely: \"{message}\"\n\n"
            f"Context from web search:\n{formatted}"
        )
        answer = query_groq(prompt, history)
        return format_search_response(answer, "Internet Search + AI")
    except Exception:
        try:
            answer = query_openrouter(
                f"Answer directly: \"{message}\"\n\nContext:\n{formatted}", history
            )
            return format_search_response(answer, "Internet Search + AI")
        except Exception:
            return format_search_response(formatted, "Internet Search")


def _handle_general(message: str, history: list[dict]) -> dict:
    try:
        answer = query_groq(message, history)
        return format_general_response(answer, "Groq AI")
    except Exception:
        try:
            answer = query_openrouter(message, history)
            return format_general_response(answer, "OpenRouter AI")
        except Exception:
            results = search_duckduckgo(message)
            return format_general_response(format_search_results(results), "Internet Search")
