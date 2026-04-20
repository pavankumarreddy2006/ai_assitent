import logging
from flask import Blueprint, request, jsonify

from services.llm_service import query_ai
from services.college_service import get_college_answer, get_college_context, COLLEGE_KEYWORDS
from services.weather_service import get_weather
from services.search_service import search_duckduckgo, format_search_results
from services.news_service import fetch_news

logger = logging.getLogger(__name__)

router = Blueprint('router', __name__)

def classify_intent(user_message: str):
    """Simple keyword-based intent classification"""
    msg = user_message.lower().strip()
    
    if any(k in msg for k in COLLEGE_KEYWORDS):
        return "college"
    if any(word in msg for word in ["weather", "climate", "temperature", "rain"]):
        return "weather"
    if any(word in msg for word in ["news", "latest", "update", "today"]):
        return "news"
    if any(word in msg for word in ["search", "find", "what is", "who is"]):
        return "search"
    return "general"


@router.route("/api/chat", methods=["POST"])
def handle_chat_request():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        if not user_message:
            return jsonify({"reply": "Please type a message."}), 400

        intent = classify_intent(user_message)

        reply = ""
        extra_data = {}

        # === COLLEGE QUERIES ===
        if intent == "college":
            reply = get_college_answer(user_message)
            context = get_college_context(user_message)
            if context:
                extra_data["source"] = "College Database"

        # === WEATHER ===
        elif intent == "weather":
            city = user_message.split()[-1] if len(user_message.split()) > 1 else "Kakinada"
            weather_data = get_weather(city, lang="en")
            if weather_data:
                reply = f"In {weather_data['city']}, it's currently {weather_data['temperature']}°C with {weather_data['description'].lower()}. Humidity: {weather_data['humidity']}%, Wind: {weather_data['wind_speed']} km/h."
            else:
                reply = "Sorry, I couldn't fetch weather information right now."

        # === NEWS ===
        elif intent == "news":
            articles = fetch_news(user_message)
            if articles:
                reply = "Here are the latest updates:\n\n"
                for i, article in enumerate(articles[:5], 1):
                    reply += f"{i}. {article.get('title')}\n   Source: {article.get('source')}\n\n"
            else:
                reply = "No news available at the moment."

        # === GENERAL / AI FALLBACK ===
        else:
            try:
                # Safe AI call with fallback
                ai_reply = query_ai(
                    prompt=user_message,
                    history=history,
                    lang="en"
                )
                reply = ai_reply
            except Exception as ai_err:
                logger.error(f"AI service failed: {ai_err}")
                reply = "I'm having trouble connecting to my knowledge base right now. Please ask me about college courses, fees, weather in Kakinada, or latest news."

        # Always return valid JSON
        return jsonify({
            "reply": reply,
            "source": extra_data.get("source"),
            "show_images": False,
            "show_video": False
        })

    except Exception as e:
        logger.error(f"Chat route error: {e}", exc_info=True)
        return jsonify({
            "reply": "Sorry, something went wrong on our end. Please try again.",
            "error": True
        }), 500