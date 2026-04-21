# core/router.py
import logging
from flask import Blueprint, request, jsonify

from core.intent import classify_intent, detect_language
from services.college_service import get_college_answer
from services.weather_service import get_weather_from_query
from services.news_service import fetch_news, summarize_news
from services.search_service import search_and_format
from services.llm_service import query_ai
from data.media_data import IMAGE_PATHS, VIDEO_PATH

logger = logging.getLogger(__name__)
router = Blueprint("router", __name__)


@router.route("/api/chat", methods=["POST"])
def api_chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        history = data.get("history") or []

        if not user_message:
            return jsonify({"reply": "Please enter a message."}), 400

        lang = detect_language(user_message)
        intent = classify_intent(user_message).get("intent")

        if intent == "images":
            reply = "Here are campus photos." if lang == "en" else "ఇవి క్యాంపస్ ఫోటోలు."
            return jsonify({
                "reply": reply,
                "source": "College Media",
                "show_images": True,
                "images": IMAGE_PATHS,
                "show_video": False,
                "video_url": ""
            })

        if intent == "video":
            reply = "Here is the full college explanation video." if lang == "en" else "ఇది కాలేజీ పూర్తి వివరాల వీడియో."
            return jsonify({
                "reply": reply,
                "source": "College Media",
                "show_images": False,
                "images": [],
                "show_video": True,
                "video_url": VIDEO_PATH
            })

        if intent == "weather":
            reply = get_weather_from_query(user_message, lang=lang)
            return jsonify({
                "reply": reply,
                "source": "Weather Service",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": ""
            })

        if intent == "news":
            articles, provider = fetch_news(user_message)
            reply = summarize_news(articles, lang=lang)
            return jsonify({
                "reply": reply,
                "source": f"News ({provider})",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": ""
            })

        if intent == "search":
            reply = search_and_format(user_message, lang=lang)
            return jsonify({
                "reply": reply,
                "source": "Web Search",
                "show_images": False,
                "images": [],
                "show_video": False,
                "video_url": ""
            })

        if intent == "college":
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

        ai_reply = query_ai(prompt=user_message, history=history, lang=lang)
        return jsonify({
            "reply": ai_reply,
            "source": "AI Assistant",
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