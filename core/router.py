import logging
import re
from flask import Blueprint, request, jsonify
from core.intent import classify_intent, detect_language
from services.college_service import get_college_answer
from services.weather_service import get_weather_from_query
from services.news_service import fetch_news, summarize_news
from services.search_service import search_and_format
from services.llm_service import query_ai
from data.media_data import IMAGE_PATHS, VIDEO_PATH

logger = logging.getLogger(__name__)  # Fixed: __name__ instead of name
router = Blueprint("router", __name__)  # Fixed: __name__ instead of name

def purify_reply(text: str, max_lines: int = 4, max_chars: int = 420) -> str:
    if not text:
        return "No data found."
    
    try:
        cleaned = re.sub(r"\s+", " ", str(text)).strip()
        cleaned = cleaned.replace("Here are the latest updates:", "Latest updates:")
        cleaned = cleaned.replace("Top search results:", "Search summary:")
        parts = re.split(r"\s(?=\d+\.)", cleaned)
        
        if len(parts) > 1:
            cleaned = " ".join(parts[:max_lines])
        
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars].rstrip() + "..."
        
        return cleaned
    except Exception as e:
        logger.error(f"Error in purify_reply: {e}")
        return str(text)[:max_chars] if text else "Error formatting response."

@router.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        history = data.get("history") or []
        
        if not user_message:
            return jsonify({"reply": "Please enter a message."}), 400
        
        # Language and intent detection with error handling
        try:
            lang = detect_language(user_message)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            lang = "en"  # Default to English
        
        try:
            intent_data = classify_intent(user_message)
            intent = intent_data.get("intent") if isinstance(intent_data, dict) else "general"
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            intent = "general"
        
        # Handle different intents with proper error handling
        if intent == "images":
            try:
                reply = "Here are campus photos." if lang == "en" else "ఇవి క్యాంపస్ ఫోటోలు."
                return jsonify({
                    "reply": reply,
                    "source": "College Media",
                    "show_images": True,
                    "images": IMAGE_PATHS,
                    "show_video": False,
                    "video_url": ""
                })
            except Exception as e:
                logger.error(f"Images intent failed: {e}")
                return jsonify({
                    "reply": "Sorry, unable to load images." if lang == "en" else "క్షమించండి, ఫోటోలు లోడ్ చేయలేకపోయాము.",
                    "source": "Error",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
        
        if intent == "video":
            try:
                reply = "Here is the full college explanation video." if lang == "en" else "ఇది కాలేజీ పూర్తి వివరాల వీడియో."
                return jsonify({
                    "reply": reply,
                    "source": "College Media",
                    "show_images": False,
                    "images": [],
                    "show_video": True,
                    "video_url": VIDEO_PATH
                })
            except Exception as e:
                logger.error(f"Video intent failed: {e}")
                return jsonify({
                    "reply": "Sorry, unable to load video." if lang == "en" else "క్షమించండి, వీడియో లోడ్ చేయలేకపోయాము.",
                    "source": "Error",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
        
        if intent == "weather":
            try:
                weather_data = get_weather_from_query(user_message, lang=lang)
                reply = purify_reply(weather_data, max_lines=2, max_chars=220)
                return jsonify({
                    "reply": reply,
                    "source": "Weather Service",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
            except Exception as e:
                logger.error(f"Weather intent failed: {e}")
                return jsonify({
                    "reply": "Sorry, unable to fetch weather data." if lang == "en" else "క్షమించండి, వాతావరణ డేటా పొందలేకపోయాము.",
                    "source": "Error",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
        
        if intent == "news":
            try:
                articles, provider = fetch_news(user_message)
                if articles:
                    summary = summarize_news(articles, lang=lang)
                    reply = purify_reply(summary, max_lines=3, max_chars=320)
                else:
                    reply = "No news articles found." if lang == "en" else "వార్తా కథనాలు ఏవీ కనుగొనబడలేదు."
                
                return jsonify({
                    "reply": reply,
                    "source": f"News ({provider})" if articles else "News Service",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
            except Exception as e:
                logger.error(f"News intent failed: {e}")
                return jsonify({
                    "reply": "Sorry, unable to fetch news." if lang == "en" else "క్షమించండి, వార్తలు పొందలేకపోయాము.",
                    "source": "Error",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
        
        if intent == "search":
            try:
                search_result = search_and_format(user_message, lang=lang)
                reply = purify_reply(search_result, max_lines=3, max_chars=320)
                return jsonify({
                    "reply": reply,
                    "source": "Web Search",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
            except Exception as e:
                logger.error(f"Search intent failed: {e}")
                return jsonify({
                    "reply": "Sorry, unable to perform search." if lang == "en" else "క్షమించండి, శోధన చేయలేకపోయాము.",
                    "source": "Error",
                    "show_images": False,
                    "images": [],
                    "show_video": False,
                    "video_url": ""
                })
        
        if intent == "college":
            try:
                local_answer = get_college_answer(user_message, lang=lang)
                if local_answer:
                    return jsonify({
                        "reply": local_answer,
                        "source": "College Data",
                        "show_images": False,
                        "images": [],
                        "show_video": False,
                        "video_url": ""
                    })
            except Exception as e:
                logger.error(f"College intent failed: {e}")
                # Continue to AI if college service fails
        
        # AI fallback for general queries or when college service fails
        try:
            ai_reply = query_ai(prompt=user_message, history=history, lang=lang)
            return jsonify({
                "reply": purify_reply(ai_reply, max_lines=4, max_chars=420),
                "source": "AI Assistant",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": ""
            })
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            return jsonify({
                "reply": "Sorry, I'm having trouble processing your request. Please try again later." if lang == "en" else "క్షమించండి, మీ అభ్యర్థనను ప్రాసెస్ చేయడంలో సమస్య ఉంది. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి.",
                "source": "Error",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": ""
            })
    
    except Exception as exc:
        logger.exception("Chat route failed: %s", exc)
        return jsonify({
            "reply": "Sorry, server error. Please try again.",
            "source": "System",
            "show_images": False,
            "images": [],
            "show_video": False,
            "video_url": ""
        }), 500