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
import logging

logger = logging.getLogger("college-ai.router")


def route_message(message: str, conversation_history: list[dict] | None = None) -> dict:
    if conversation_history is None:
        conversation_history = []

    clean_message = str(message or "").strip()
    if not clean_message:
        return format_error_response("Please say or type a message.")

    lang = detect_language(clean_message)
    intent = classify_intent(clean_message)

    try:
        if intent == "images_intent":
            return {
                "reply": "Showing campus images" if lang == "en" else "క్యాంపస్ చిత్రాలు చూపిస్తున్నాను",
                "intent": "images",
                "source": "College Media",
                "show_images": True,
                "images": media_service.get_college_images(),
                "show_video": False,
                "video_url": None,
            }
        if intent == "video_intent":
            return {
                "reply": "Playing college video" if lang == "en" else "కాలేజీ వీడియో ప్లే చేస్తున్నాను",
                "intent": "video",
                "source": "College Media",
                "show_images": False,
                "images": [],
                "show_video": True,
                "video_url": media_service.get_college_video(),
            }
        if intent == "college":
            return _handle_college(clean_message, conversation_history, lang)
        if intent == "weather":
            return _handle_weather(clean_message, lang)
        if intent == "news":
            return _handle_news(clean_message, lang)
        if intent == "search":
            return _handle_search(clean_message, conversation_history, lang)
        return _handle_general(clean_message, conversation_history, lang)
    except Exception as e:
        logger.exception("Router error: %s", e)
        if lang == "te":
            return format_error_response("క్షమించండి, ఏదో సమస్య వచ్చింది. దయచేసి మళ్ళీ ప్రయత్నించండి.")
        return format_error_response("Something went wrong. Please try again.")


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
            "Use ONLY the following college data to answer in English. Be direct, clear, and helpful. "
            "If information is not available, say: 'I don't have that specific information. "
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
                    "ఆ వివరాలు నా దగ్గర లేవు. దయచేసి కాలేజీని 0884-2384382 లో సంప్రదించండి లేదా idealcolleges@gmail.com కి ఇమెయిల్ చేయండి.",
                    "College Database",
                )
            return format_college_response(
                "I don't have specific information about that. Please contact the college at 0884-2384382 or email idealcolleges@gmail.com.",
                "College Database",
            )


def _handle_weather(message: str, lang: str) -> dict:
    city = extract_city(message) or "Kakinada"
    weather_data = get_weather(city, lang=lang)
    return format_weather_response(weather_data, city, lang=lang)


def _handle_news(message: str, lang: str) -> dict:
    import re

    raw_query = re.sub(
        r"news|latest|headlines|breaking|today|వార్తలు|తాజా|సమాచారం",
        "",
        message,
        flags=re.IGNORECASE,
    ).strip()
    articles = fetch_news(raw_query or "education India")
    return format_news_response(articles, lang=lang)


def _handle_search(message: str, history: list[dict], lang: str) -> dict:
    results = search_duckduckgo(message)
    formatted = format_search_results(results)

    if lang == "te":
        prompt = (
            "వినియోగదారు తెలుగు లేదా Roman Telugu లో అడిగారు. ముందుగా English కి translate చేయకుండా తెలుగులోనే సహజంగా సమాధానం ఇవ్వండి.\n"
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
            fallback = formatted if formatted and formatted.strip() else (
                "సరైన సమాచారం ప్రస్తుతం దొరకలేదు. దయచేసి మరోసారి అడగండి." if lang == "te"
                else "I could not find reliable information right now. Please try another query."
            )
            return format_search_response(fallback, "Internet Search")


def _handle_general(message: str, history: list[dict], lang: str) -> dict:
    if lang == "te":
        prompt = (
            "User Telugu/Roman Telugu lo matladaru. English ki translate cheyyakunda Telugu lone natural ga answer ivvandi.\n\n"
            f"User message: {message}"
        )
    else:
        prompt = (
            "The user wrote in English. Reply only in English. Do not switch to Telugu unless the user switches language.\n\n"
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
            formatted = format_search_results(results)
            if not formatted or "couldn't find relevant information" in formatted.lower():
                formatted = (
                    "క్షమించండి, ప్రస్తుతం సరైన సమాధానం ఇవ్వలేకపోయాను. దయచేసి ప్రశ్నను కొంచెం వివరంగా అడగండి."
                    if lang == "te"
                    else "Sorry, I could not answer that clearly right now. Please ask with a bit more detail."
                )
            return format_general_response(formatted, "Internet Search")
