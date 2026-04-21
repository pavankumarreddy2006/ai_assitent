# core/router.py
import logging
from flask import request, jsonify

from services.college_service import get_college_answer, get_college_context, COLLEGE_KEYWORDS
from services.weather_service import get_weather
from services.search_service import search_duckduckgo, format_search_results
from services.news_service import fetch_news
from services.llm_service import query_ai
from responder import (
    format_college_response,
    format_weather_response,
    format_news_response,
    format_search_response,
    format_general_response,
    format_error_response
)

logger = logging.getLogger(__name__)

# Media paths (loaded from config or fallback)
IMAGE_PATHS = ["/static/media/1.png", "/static/media/2.png"]
VIDEO_PATH = "/static/media/college.mp4"

try:
    from config.config import IMAGE_PATHS as CONFIG_IMAGES, VIDEO_PATH as CONFIG_VIDEO
    IMAGE_PATHS = CONFIG_IMAGES
    VIDEO_PATH = CONFIG_VIDEO
except ImportError:
    logger.warning("Could not load media paths from config - using defaults")

def detect_language(text: str) -> str:
    """Simple but reliable language detection (English / Telugu)"""
    if not text or not isinstance(text, str):
        return "en"
    
    # Telugu Unicode range
    telugu_count = sum(1 for char in text if '\u0C00' <= char <= '\u0C7F')
    total_chars = max(len(text.replace(" ", "")), 1)
    
    if telugu_count / total_chars > 0.12:
        return "te"
    
    # Common Roman Telugu words
    roman_telugu = {"nenu", "meeru", "nuvvu", "cheppu", "chepandi", "gurunchi", 
                   "entha", "ela", "emiti", "kavali", "chupinchu", "aadinchu", 
                   "admission", "fee", "fees", "course", "courses"}
    words = set(text.lower().split())
    
    if words & roman_telugu:
        return "te"
    
    return "en"


def classify_intent(user_message: str):
    """Simple keyword-based intent classification"""
    msg = user_message.lower().strip()
    
    if any(k in msg for k in COLLEGE_KEYWORDS):
        return "college"
    if any(word in msg for word in ["weather", "climate", "temperature", "rain", "వాతావరణం"]):
        return "weather"
    if any(word in msg for word in ["news", "latest", "update", "today", "వార్తలు"]):
        return "news"
    if any(word in msg for word in ["search", "find", "what is", "who is", "explain"]):
        return "search"
    return "general"


def handle_chat_request(request):
    """FIXED: Accepts Flask request object - main chat handler"""
    try:
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        history = data.get("history", [])

        if not user_message:
            return jsonify({"reply": "Please type a message."}), 400

        lang = detect_language(user_message)
        msg_lower = user_message.lower()

        # ====================== MEDIA INTENTS (HIGHEST PRIORITY) ======================
        if any(phrase in msg_lower for phrase in [
            "video", "play video", "campus video", "college video", 
            "వీడియో", "వీడియో చూపించు", "ప్లే వీడియో"
        ]):
            return jsonify({
                "reply": "Here is the college promotional video!" if lang == "en" else "మీ కోసం కాలేజీ వీడియో ఇక్కడ ఉంది!",
                "show_video": True,
                "video_url": VIDEO_PATH,
                "show_images": False,
                "images": [],
                "source": "College Media",
                "language": lang
            })

        if any(phrase in msg_lower for phrase in [
            "photo", "photos", "image", "images", "picture", "pictures", "gallery",
            "ఫోటో", "ఫోటోలు", "చిత్రాలు", "క్యాంపస్ ఫోటోలు"
        ]):
            return jsonify({
                "reply": "Here are some beautiful images of our college!" if lang == "en" else "మా కాలేజీ అందమైన ఫోటోలు ఇక్కడ ఉన్నాయి!",
                "show_images": True,
                "images": IMAGE_PATHS,
                "show_video": False,
                "video_url": "",
                "source": "College Media",
                "language": lang
            })

        # ====================== COLLEGE QUERIES ======================
        college_reply = get_college_answer(user_message, lang=lang)
        if college_reply:
            return jsonify(format_college_response(college_reply, source="College Database"))

        # ====================== OTHER INTENTS ======================
        intent = classify_intent(user_message)

        if intent == "weather":
            # Simple city extraction (fallback to Kakinada)
            city = "Kakinada"
            words = user_message.split()
            if len(words) > 2:
                potential_city = words[-1].strip("?.!,")
                if len(potential_city) > 2:
                    city = potential_city
            weather_data = get_weather(city, lang=lang)
            return jsonify(format_weather_response(weather_data, city, lang))

        elif intent == "news":
            articles = fetch_news(user_message)
            return jsonify(format_news_response(articles, lang))

        elif intent == "search":
            search_results = search_duckduckgo(user_message)
            search_text = format_search_results(search_results)
            return jsonify(format_search_response(search_text))

        # ====================== GENERAL AI FALLBACK ======================
        else:
            try:
                ai_reply = query_ai(
                    prompt=user_message,
                    history=history,
                    lang=lang
                )
                return jsonify(format_general_response(ai_reply))
            except Exception as ai_err:
                logger.error(f"AI service failed: {ai_err}")
                return jsonify(format_error_response(
                    "I'm having trouble connecting to my knowledge base right now. "
                    "Please ask me about college courses, fees, weather in Kakinada, or latest news."
                ))

    except Exception as e:
        logger.error(f"Chat route error: {e}", exc_info=True)
        return jsonify(format_error_response()), 500