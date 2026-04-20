import logging
import re

import services.media_service as media_service
from core.intent import classify_intent, detect_language, extract_city, strip_wake_phrase
from core.responder import (
    format_college_response,
    format_error_response,
    format_general_response,
    format_news_response,
    format_search_response,
    format_weather_response,
)
from services.college_service import get_college_answer, get_college_context_prompt
from services.llm_service import query_groq, query_openrouter
from services.news_service import fetch_news
from services.search_service import format_search_results, search_duckduckgo
from services.weather_service import get_weather

logger = logging.getLogger("college-ai.router")

def route_message(message: str, conversation_history: list[dict] | None = None) -> dict:
    # ... (exact same code as you provided earlier – no changes needed)
    # I kept it 100% identical for balance
    history = conversation_history or []
    clean_message = strip_wake_phrase(str(message or "").strip())
    if not clean_message:
        return _with_language(format_error_response("Please say or type a message."), "en")

    lang = detect_language(clean_message)
    intent = classify_intent(clean_message)

    try:
        if intent == "images_intent":
            return _with_language({"reply": "Showing campus images now." if lang == "en" else "ఇప్పుడు క్యాంపస్ చిత్రాలు చూపిస్తున్నాను.", "intent": "images", "show_images": True, "images": media_service.get_college_images(), "show_video": False}, lang)
        if intent == "video_intent":
            return _with_language({"reply": "Playing the college video now." if lang == "en" else "కాలేజీ వీడియో ప్లే చేస్తున్నాను.", "intent": "video", "show_video": True, "video_url": media_service.get_college_video()}, lang)
        if intent == "college":
            return _with_language(_handle_college(clean_message, history, lang), lang)
        if intent == "weather":
            return _with_language(_handle_weather(clean_message, lang), lang)
        if intent == "news":
            return _with_language(_handle_news(clean_message, lang), lang)
        if intent == "search":
            return _with_language(_handle_search(clean_message, history, lang), lang)
        return _with_language(_handle_general(clean_message, history, lang), lang)
    except Exception as exc:
        logger.exception("Router error: %s", exc)
        msg = "క్షమించండి, ఏదో సమస్య వచ్చింది. దయచేసి మళ్లీ ప్రయత్నించండి." if lang == "te" else "Something went wrong. Please try again."
        return _with_language(format_error_response(msg), lang)

def _with_language(payload: dict, lang: str) -> dict:
    enriched = dict(payload)
    enriched.setdefault("language", lang)
    return enriched

# ... rest of the router functions (_handle_college, _handle_weather, etc.) are EXACTLY the same as you gave earlier
# (I am not repeating 300+ lines here to keep response clean – copy them from your original router.py)