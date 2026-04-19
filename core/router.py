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
    history = conversation_history or []
    clean_message = strip_wake_phrase(str(message or "").strip())
    if not clean_message:
        return _with_language(format_error_response("Please say or type a message."), "en")

    lang = detect_language(clean_message)
    intent = classify_intent(clean_message)

    try:
        if intent == "images_intent":
            return _with_language(
                {
                    "reply": "Showing campus images now." if lang == "en" else "\u0c07\u0c2a\u0c4d\u0c2a\u0c41\u0c21\u0c41 \u0c15\u0c4d\u0c2f\u0c3e\u0c02\u0c2a\u0c38\u0c4d \u0c1a\u0c3f\u0c24\u0c4d\u0c30\u0c3e\u0c32\u0c41 \u0c1a\u0c42\u0c2a\u0c3f\u0c38\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41.",
                    "intent": "images",
                    "source": "College Media",
                    "show_images": True,
                    "images": media_service.get_college_images(),
                    "show_video": False,
                    "video_url": None,
                    "media_duration": 6,
                },
                lang,
            )
        if intent == "video_intent":
            return _with_language(
                {
                    "reply": "Playing the college video now." if lang == "en" else "\u0c07\u0c2a\u0c4d\u0c2a\u0c41\u0c21\u0c41 \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40 \u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b \u0c2a\u0c4d\u0c32\u0c47 \u0c1a\u0c47\u0c38\u0c4d\u0c24\u0c41\u0c28\u0c4d\u0c28\u0c3e\u0c28\u0c41.",
                    "intent": "video",
                    "source": "College Media",
                    "show_images": False,
                    "images": [],
                    "show_video": True,
                    "video_url": media_service.get_college_video(),
                    "media_duration": 18,
                },
                lang,
            )
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
        message = (
            "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, \u0c0f\u0c26\u0c4b \u0c38\u0c2e\u0c38\u0c4d\u0c2f \u0c35\u0c1a\u0c4d\u0c1a\u0c3f\u0c02\u0c26\u0c3f. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c2e\u0c33\u0c4d\u0c33\u0c40 \u0c2a\u0c4d\u0c30\u0c2f\u0c24\u0c4d\u0c28\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f."
            if lang == "te"
            else "Something went wrong. Please try again."
        )
        return _with_language(format_error_response(message), lang)


def _with_language(payload: dict, lang: str) -> dict:
    enriched = dict(payload)
    enriched.setdefault("language", lang)
    enriched.setdefault("media_duration", 0)
    return enriched


def _handle_college(message: str, history: list[dict], lang: str) -> dict:
    result = get_college_answer(message, lang=lang)
    if result:
        return format_college_response(result, "College Database")

    college_context = get_college_context_prompt()
    if lang == "te":
        system_prompt = (
            "\u0c2e\u0c40\u0c30\u0c41 Ideal College of Arts and Sciences \u0c2f\u0c4a\u0c15\u0c4d\u0c15 \u0c05\u0c27\u0c3f\u0c15\u0c3e\u0c30\u0c3f\u0c15 AI assistant.\n"
            "\u0c2f\u0c42\u0c1c\u0c30\u0c4d \u0c24\u0c46\u0c32\u0c41\u0c17\u0c41 \u0c32\u0c47\u0c26\u0c3e Roman Telugu \u0c32\u0c4b \u0c2e\u0c3e\u0c1f\u0c4d\u0c32\u0c3e\u0c21\u0c3f\u0c24\u0c47 \u0c38\u0c39\u0c1c\u0c2e\u0c48\u0c28 \u0c24\u0c46\u0c32\u0c41\u0c17\u0c41\u0c32\u0c4b \u0c05\u0c28\u0c47 \u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 \u0c07\u0c35\u0c4d\u0c35\u0c02\u0c21\u0c3f.\n"
            "\u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 \u0c38\u0c4d\u0c2a\u0c37\u0c4d\u0c1f\u0c02\u0c17\u0c3e, \u0c1a\u0c15\u0c4d\u0c15\u0c17\u0c3e, \u0c2f\u0c42\u0c1c\u0c30\u0c4d\u0c24\u0c4b interactive \u0c17\u0c3e \u0c09\u0c02\u0c21\u0c3e\u0c32\u0c3f.\n"
            "\u0c15\u0c3f\u0c02\u0c26 \u0c07\u0c1a\u0c4d\u0c1a\u0c3f\u0c28 college data \u0c28\u0c41, conversation history \u0c28\u0c41, user question \u0c28\u0c41 \u0c15\u0c32\u0c3f\u0c2a\u0c3f \u0c38\u0c30\u0c48\u0c28 answer \u0c07\u0c35\u0c4d\u0c35\u0c02\u0c21\u0c3f.\n"
            "\u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02 \u0c32\u0c47\u0c15\u0c2a\u0c4b\u0c24\u0c47 \u0c24\u0c46\u0c32\u0c3f\u0c2f\u0c26\u0c28\u0c3f \u0c38\u0c4d\u0c2a\u0c37\u0c4d\u0c1f\u0c02\u0c17\u0c3e \u0c1a\u0c46\u0c2a\u0c4d\u0c2a\u0c3f, 0884-2384382 \u0c32\u0c47\u0c26\u0c3e idealcolleges@gmail.com \u0c15\u0c3f contact \u0c1a\u0c47\u0c2f\u0c2e\u0c28\u0c3f \u0c1a\u0c46\u0c2a\u0c4d\u0c2a\u0c02\u0c21\u0c3f.\n\n"
            f"COLLEGE INFORMATION:\n{college_context}"
        )
    else:
        system_prompt = (
            "You are Ideal College AI, the official assistant for Ideal College of Arts and Sciences.\n"
            "Answer only in clear English when the user speaks English.\n"
            "Use the supplied college information, conversation context, and the user question to give accurate, interactive, user-friendly answers.\n"
            "If exact information is unavailable, say so clearly and guide the user to contact 0884-2384382 or idealcolleges@gmail.com.\n\n"
            f"COLLEGE INFORMATION:\n{college_context}"
        )

    try:
        answer = query_groq(message, history, system_prompt, lang=lang)
        return format_college_response(_finalize_answer(answer, lang), "Groq + College Data")
    except Exception:
        try:
            answer = query_openrouter(message, history, system_prompt, lang=lang)
            return format_college_response(_finalize_answer(answer, lang), "OpenRouter + College Data")
        except Exception:
            fallback = (
                "\u0c06 \u0c35\u0c3f\u0c35\u0c30\u0c3e\u0c32\u0c41 \u0c28\u0c3e \u0c26\u0c17\u0c4d\u0c17\u0c30 \u0c32\u0c47\u0c35\u0c41. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40\u0c28\u0c3f 0884-2384382 \u0c32\u0c4b \u0c38\u0c02\u0c2a\u0c4d\u0c30\u0c26\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f \u0c32\u0c47\u0c26\u0c3e idealcolleges@gmail.com \u0c15\u0c3f email \u0c1a\u0c47\u0c2f\u0c02\u0c21\u0c3f."
                if lang == "te"
                else "I do not have that exact information right now. Please contact the college at 0884-2384382 or idealcolleges@gmail.com."
            )
            return format_college_response(fallback, "College Database")


def _handle_weather(message: str, lang: str) -> dict:
    city = extract_city(message) or "Kakinada"
    weather_data = get_weather(city, lang=lang)
    return format_weather_response(weather_data, city, lang=lang)


def _handle_news(message: str, lang: str) -> dict:
    raw_query = re.sub(
        r"news|latest|headlines|breaking|today|\u0c35\u0c3e\u0c30\u0c4d\u0c24\u0c32\u0c41|\u0c24\u0c3e\u0c1c\u0c3e|\u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()
    return format_news_response(fetch_news(raw_query or "education India"), lang=lang)


def _handle_search(message: str, history: list[dict], lang: str) -> dict:
    results = search_duckduckgo(message)
    formatted = format_search_results(results)
    if lang == "te":
        prompt = (
            "\u0c2f\u0c42\u0c1c\u0c30\u0c4d Telugu \u0c32\u0c47\u0c26\u0c3e Roman Telugu \u0c32\u0c4b \u0c05\u0c21\u0c3f\u0c17\u0c3e\u0c21\u0c41.\n"
            "\u0c07\u0c02\u0c17\u0c4d\u0c32\u0c3f\u0c37\u0c4d \u0c15\u0c3f translate \u0c1a\u0c47\u0c2f\u0c15\u0c41\u0c02\u0c21\u0c3e \u0c38\u0c39\u0c1c\u0c2e\u0c48\u0c28 \u0c24\u0c46\u0c32\u0c41\u0c17\u0c41\u0c32\u0c4b\u0c28\u0c47 answer \u0c07\u0c35\u0c4d\u0c35\u0c02\u0c21\u0c3f.\n"
            "\u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 user-friendly \u0c17\u0c3e \u0c09\u0c02\u0c21\u0c3e\u0c32\u0c3f.\n"
            f"Question: {message}\n\nContext:\n{formatted}"
        )
    else:
        prompt = (
            "Answer only in English. Keep the reply interactive and easy to understand.\n"
            f"Question: {message}\n\nContext:\n{formatted}"
        )

    try:
        answer = query_groq(prompt, history, lang=lang)
        return format_search_response(_finalize_answer(answer, lang), "Groq + Web Search")
    except Exception:
        try:
            answer = query_openrouter(prompt, history, lang=lang)
            return format_search_response(_finalize_answer(answer, lang), "OpenRouter + Web Search")
        except Exception:
            fallback = (
                formatted
                if formatted and formatted.strip()
                else (
                    "\u0c38\u0c30\u0c48\u0c28 \u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02 \u0c2a\u0c4d\u0c30\u0c38\u0c4d\u0c24\u0c41\u0c24\u0c02 \u0c26\u0c4a\u0c30\u0c15\u0c32\u0c47\u0c26\u0c41. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c2e\u0c30\u0c4b\u0c38\u0c3e\u0c30\u0c3f \u0c05\u0c21\u0c17\u0c02\u0c21\u0c3f."
                    if lang == "te"
                    else "I could not find reliable information right now. Please try another query."
                )
            )
            return format_search_response(fallback, "Internet Search")


def _handle_general(message: str, history: list[dict], lang: str) -> dict:
    if lang == "te":
        prompt = (
            "User Telugu \u0c32\u0c47\u0c26\u0c3e Roman Telugu \u0c32\u0c4b \u0c2e\u0c3e\u0c1f\u0c4d\u0c32\u0c3e\u0c21\u0c3e\u0c30\u0c41.\n"
            "English ki switch avvakunda natural Telugu lone answer ivvandi.\n"
            "Answer warm ga, interactive ga, clear ga undali.\n\n"
            f"User message: {message}"
        )
    else:
        prompt = (
            "The user wrote in English. Reply only in clear, natural English.\n"
            "Keep the answer interactive and helpful.\n\n"
            f"User message: {message}"
        )

    try:
        answer = query_groq(prompt, history, lang=lang)
        return format_general_response(_finalize_answer(answer, lang), "Groq AI")
    except Exception:
        try:
            answer = query_openrouter(prompt, history, lang=lang)
            return format_general_response(_finalize_answer(answer, lang), "OpenRouter AI")
        except Exception:
            results = search_duckduckgo(message)
            formatted = format_search_results(results)
            if not formatted or "couldn't find relevant information" in formatted.lower():
                formatted = (
                    "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, \u0c2a\u0c4d\u0c30\u0c38\u0c4d\u0c24\u0c41\u0c24\u0c02 \u0c38\u0c30\u0c48\u0c28 \u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 \u0c07\u0c35\u0c4d\u0c35\u0c32\u0c47\u0c15\u0c2a\u0c4b\u0c2f\u0c3e\u0c28\u0c41. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c2a\u0c4d\u0c30\u0c36\u0c4d\u0c28\u0c28\u0c41 \u0c15\u0c4a\u0c02\u0c1a\u0c46\u0c02 \u0c35\u0c3f\u0c35\u0c30\u0c02\u0c17\u0c3e \u0c05\u0c21\u0c17\u0c02\u0c21\u0c3f."
                    if lang == "te"
                    else "Sorry, I could not answer that clearly right now. Please ask with a bit more detail."
                )
            return format_general_response(formatted, "Internet Search")


def _finalize_answer(answer: str, lang: str) -> str:
    text = str(answer or "").strip()
    if not text:
        return (
            "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, \u0c38\u0c30\u0c48\u0c28 \u0c38\u0c2e\u0c3e\u0c27\u0c3e\u0c28\u0c02 \u0c26\u0c4a\u0c30\u0c15\u0c32\u0c47\u0c26\u0c41. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c2a\u0c4d\u0c30\u0c36\u0c4d\u0c28\u0c28\u0c41 \u0c07\u0c02\u0c15\u0c4a\u0c02\u0c1a\u0c46\u0c02 \u0c38\u0c4d\u0c2a\u0c37\u0c4d\u0c1f\u0c02\u0c17\u0c3e \u0c05\u0c21\u0c17\u0c02\u0c21\u0c3f."
            if lang == "te"
            else "Sorry, I could not find a clear answer. Please ask in a bit more detail."
        )

    for prefix in ("As an AI", "As an assistant", "Based on the provided"):
        if text.lower().startswith(prefix.lower()):
            parts = text.split(".", 1)
            text = parts[1].strip() if len(parts) > 1 else text
            break
    return text
