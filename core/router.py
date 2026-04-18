# router.py - Routes each request to the correct handler.
#
# Intent flow:
#   college  -> college_service (smart DB lookup) -> llm with full college context
#   weather  -> weather_service
#   news     -> news_service
#   search   -> search_service -> llm summarize
#   images   -> media_service (returns image paths)
#   video    -> media_service (returns video url)
#   general  -> llm (Groq -> OpenRouter -> search fallback)
#
# Language:
#   - detect_language() auto-detects Telugu vs English
#   - All handlers pass lang to LLM so responses match user's language

from core.intent import classify_intent, extract_city, detect_language
from core.responder import (
    format_college_response,
    format_weather_response,
    format_news_response,
    format_search_response,
    format_general_response,
    format_error_response,
)
from services.college_service import get_college_answer, get_college_context_prompt
from services.llm_service import query_groq, query_openrouter
from services.search_service import search_duckduckgo, format_search_results
from services.news_service import fetch_news
from services.weather_service import get_weather
import services.media_service as media_service

def route_message(message: str, conversation_history: list[dict] | None = None) -> dict:
    if conversation_history is None:
        conversation_history = []

    lang = detect_language(message)
    intent = classify_intent(message)

    try:
        if intent == "images_intent":
            return {
                "reply": "Showing campus images",
                "show_images": True,
                "images": media_service.get_college_images(),
                "show_video": False
            }
        elif intent == "video_intent":
            return {
                "reply": "Playing college video",
                "show_video": True,
                "video_url": media_service.get_college_video(),
                "show_images": False
            }
        elif intent == "college":
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


from core.intent import classify_intent, extract_city, detect_language
from core.responder import (
    format_college_response,
    format_weather_response,
    format_news_response,
    format_search_response,
    format_general_response,
    format_error_response,
)
from services.college_service import get_college_answer, get_college_context_prompt
from services.llm_service import query_groq, query_openrouter
from services.search_service import search_duckduckgo, format_search_results
from services.news_service import fetch_news
from services.weather_service import get_weather


def route_message(message: str, conversation_history: list[dict] | None = None) -> dict:
    if conversation_history is None:
        conversation_history = []

    lang = detect_language(message)
    intent = classify_intent(message)

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


def _handle_college(message: str, history: list[dict], lang: str) -> dict:
    result = get_college_answer(message, lang=lang)
    if result:
        return format_college_response(result, "College Database")

    college_context = get_college_context_prompt()

    if lang == "te":
        system_prompt = (
            "మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.\n\n"
            "కింది కాలేజీ సమాచారం మాత్రమే ఉపయోగించి తెలుగులో సమాధానం ఇవ్వండి.\n"
            "సమాచారం లేకపోతే: 'ఆ వివరాలు నా దగ్గర లేవు. దయచేసి కాలేజీని 0884-2384382 లో సంప్రదించండి.'\n\n"
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


def _handle_weather(message: str, lang: str) -> dict:
    city = extract_city(message) or "Kakinada"
    weather_data = get_weather(city, lang=lang)
    return format_weather_response(weather_data, city, lang=lang)


def _handle_news(message: str, lang: str) -> dict:
    import re
    raw_query = re.sub(
        r"news|latest|headlines|breaking|today|వార్తలు|తాజా|సమాచారం",
        "", message, flags=re.IGNORECASE
    ).strip()

    articles = fetch_news(raw_query or "education India")
    return format_news_response(articles, lang=lang)


def _handle_search(message: str, history: list[dict], lang: str) -> dict:
    results = search_duckduckgo(message)
    formatted = format_search_results(results)

    if lang == "te":
        prompt = (
            "వినియోగదారు తెలుగు లేదా Roman Telugu లో అడిగారు. "
            "ముందుగా English కి translate చేయకుండా తెలుగులోనే సహజంగా సమాధానం ఇవ్వండి.\n"
            f"ప్రశ్న: \"{message}\"\n\nవెబ్ సమాచారం:\n{formatted}"
        )
    else:
        prompt = f"Answer this question in English only. Do not switch to Telugu. Question: \"{message}\"\n\nContext:\n{formatted}"

    try:
        answer = query_groq(prompt, history, lang=lang)
        return format_search_response(answer, "Internet Search + AI")
    except Exception:
        try:
            answer = query_openrouter(prompt, history, lang=lang)
            return format_search_response(answer, "Internet Search + AI")
        except Exception:
            return format_search_response(formatted, "Internet Search")


def _handle_general(message: str, history: list[dict], lang: str) -> dict:
    if lang == "te":
        prompt = (
            "User Telugu/Roman Telugu lo matladaru. English ki translate cheyyakunda "
            "Telugu lone natural ga answer ivvandi.\n\n"
            f"User message: {message}"
        )
    else:
        prompt = (
            "The user wrote in English. Reply only in English. "
            "Do not switch to Telugu unless the user switches language.\n\n"
            f"User message: {message}"
        )
    try:
        answer = query_groq(prompt, history, lang=lang)
        return format_general_response(answer, "Groq AI")
    except Exception:
        try:
            answer = query_openrouter(prompt, history, lang=lang)
            return format_general_response(answer, "OpenRouter AI")
        except Exception:
            results = search_duckduckgo(message)
            return format_general_response(format_search_results(results), "Internet Search")
