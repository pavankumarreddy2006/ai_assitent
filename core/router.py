# core/router.py

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

logger = logging.getLogger(**name**)
router = Blueprint("router", **name**)

# ✅ ONLY ADDITION (no logic change)

def purify_reply(text: str, max_lines: int = 4, max_chars: int = 420) -> str:
if not text:
return "No data found."

```
cleaned = re.sub(r"\s+", " ", str(text)).strip()
cleaned = cleaned.replace("Here are the latest updates:", "Latest updates:")
cleaned = cleaned.replace("Top search results:", "Search summary:")

parts = re.split(r"\s(?=\d+\.)", cleaned)

if len(parts) > 1:
    cleaned = " ".join(parts[:max_lines])

if len(cleaned) > max_chars:
    cleaned = cleaned[:max_chars].rstrip() + "..."

return cleaned
```

@router.route("/api/chat", methods=["POST"])
def api_chat():
try:
data = request.get_json(silent=True) or {}
user_message = (data.get("message") or "").strip()
history = data.get("history") or []

```
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
        reply = purify_reply(
            get_weather_from_query(user_message, lang=lang),
            max_lines=2,
            max_chars=220
        )
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
        reply = purify_reply(
            summarize_news(articles, lang=lang),
            max_lines=3,
            max_chars=320
        )
        return jsonify({
            "reply": reply,
            "source": f"News ({provider})",
            "show_images": False,
            "images": [],
            "show_video": False,
            "video_url": ""
        })

    if intent == "search":
        reply = purify_reply(
            search_and_format(user_message, lang=lang),
            max_lines=3,
            max_chars=320
        )
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
        "reply": purify_reply(ai_reply, max_lines=4, max_chars=420),
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
```
