import re
from flask import jsonify, request

# Imports from other services
from config.config import COLLEGE_SYSTEM_PROMPT, TELUGU_SYSTEM_PROMPT, IMAGE_PATHS, VIDEO_PATH
from services.college_service import get_college_answer, get_college_context
from services.llm_service import query_ai
from services.weather_service import get_weather
from services.news_service import fetch_news
from services.search_service import search_duckduckgo

# Constants from old app.py
ROMAN_TELUGU = {"nenu","meeru","nuvvu","enti","emiti","ela","enduku","undi","kavali","chesi","gurunchi"}
WEATHER_KW   = ["weather","temperature","rain","sunny","cloudy","forecast","humidity","wind","climate"]
NEWS_KW      = ["news","headlines","latest","breaking","current affairs","trending","update"]
SEARCH_KW    = ["search","find","what is","who is","where is","how to","define","explain","tell me about"]
IMAGE_KW     = ["college photos","campus photos","show photos","show images","college images","campus images",
                "ఫోటోలు","చిత్రాలు","కాలేజీ ఫోటో"]
VIDEO_KW     = ["college video","campus video","play video","show video","watch video","full details",
                "కాలేజీ వీడియో","వీడియో"]
COLLEGE_HINTS = {"admission","course","fee","principal","hostel","library","placement","college","campus",
                 "scholarship","timings","contact","courses","fees","placements"}

# Media defaults
MEDIA_DEFAULTS = {
    "show_images": False,
    "images": [],
    "show_video": False,
    "video_url": None
}

def detect_language(text: str) -> str:
    telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
    total = max(len(text.replace(" ", "")), 1)
    if telugu_chars / total > 0.15:
        return "te"
    words = [w.lower() for w in text.split() if w.isalpha()]
    if sum(1 for w in words if w in ROMAN_TELUGU) >= 2:
        return "te"
    return "en"

def classify_intent(message: str) -> str:
    msg = message.lower().strip()
    if any(p in msg for p in VIDEO_KW):  return "video_intent"
    if any(p in msg for p in IMAGE_KW):  return "images_intent"
    words = set(msg.split())
    if words & COLLEGE_HINTS:            return "college"
    if any(kw in msg for kw in COLLEGE_KEYWORDS): return "college"   # COLLEGE_KEYWORDS from college_service
    if any(kw in msg for kw in WEATHER_KW):       return "weather"
    if any(kw in msg for kw in NEWS_KW):           return "news"
    if any(kw in msg for kw in SEARCH_KW) or "?" in msg:
        return "search"
    return "general"

def extract_city(message: str) -> str:
    patterns = [
        r'weather\s+(?:in|at|for|of)\s+([A-Za-z][A-Za-z\s]{1,30}?)(?:\?|$|\.)',
        r'temperature\s+(?:in|at|of)\s+([A-Za-z][A-Za-z\s]{1,30})',
        r'how(?:\'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([A-Za-z][A-Za-z\s]{1,30})',
    ]
    for p in patterns:
        m = re.search(p, message, re.IGNORECASE)
        if m:
            city = m.group(1).strip().rstrip("?.,!")
            if 2 <= len(city) <= 30:
                return city
    skip = {"weather","what","how","tell","the","for","now","today","check","please",
            "show","give","temperature","forecast","update","current"}
    for word in message.split():
        w = word.strip("?.,!")
        if w and w[0].isupper() and len(w) >= 3 and w.lower() not in skip:
            return w
    return "Kakinada"

def handle_chat_request(req):
    data = req.get_json(force=True)
    message = (data.get("message") or "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message is required"}), 400

    lang = detect_language(message)
    intent = classify_intent(message)

    defaults = MEDIA_DEFAULTS.copy()

    # Images Intent
    if intent == "images_intent":
        return jsonify({
            "reply": "ఇప్పుడు క్యాంపస్ చిత్రాలు చూపిస్తున్నాను." if lang == "te" else "Here are the campus images for you.",
            "intent": "images",
            "source": "Media Service",
            "language": lang,
            "show_images": True,
            "images": IMAGE_PATHS,
            "show_video": False,
            "video_url": None
        })

    # Video Intent
    if intent == "video_intent":
        return jsonify({
            "reply": "కాలేజీ వీడియో ప్లే చేస్తున్నాను." if lang == "te" else "Playing the college promotional video.",
            "intent": "video",
            "source": "Media Service",
            "language": lang,
            "show_images": False,
            "images": [],
            "show_video": True,
            "video_url": VIDEO_PATH
        })

    # College
    if intent == "college":
        local = get_college_answer(message, lang)
        if local:
            return jsonify({"reply": local, "intent": "college",
                            "source": "College Database", "language": lang, **defaults})
        
        ctx = get_college_context()
        sys_prompt = (TELUGU_SYSTEM_PROMPT if lang == "te" else COLLEGE_SYSTEM_PROMPT) + f"\n\nCOLLEGE INFO:\n{ctx}"
        reply = query_ai(message, history, sys_prompt, lang)
        return jsonify({"reply": reply, "intent": "college",
                        "source": "AI + College Database", "language": lang, **defaults})

    # Weather
    if intent == "weather":
        city = extract_city(message)
        wd = get_weather(city, lang)
        if wd:
            reply = (f"{wd['city']}లో వాతావరణం: {wd['description']}, ఉష్ణోగ్రత: {wd['temperature']}°C, తేమ: {wd['humidity']}%, గాలి: {wd['wind_speed']} km/h." if lang == "te"
                     else f"Weather in {wd['city']}: {wd['description']}, Temperature: {wd['temperature']}°C, Humidity: {wd['humidity']}%, Wind: {wd['wind_speed']} km/h.")
        else:
            reply = f"'{city}' వాతావరణ సమాచారం దొరకలేదు." if lang == "te" else f"Couldn't find weather data for '{city}'."
        return jsonify({"reply": reply, "intent": "weather", "source": "Weather API", "language": lang, **defaults})

    # News
    if intent == "news":
        articles = fetch_news()
        if articles:
            header = "తాజా వార్తలు:\n" if lang == "te" else "Here are the latest headlines:\n"
            lines = [f"{i+1}. {a['title']} — {a['source']}" for i, a in enumerate(articles)]
            reply = header + "\n".join(lines)
        else:
            reply = "వార్తలు తీసుకోలేకపోయాము." if lang == "te" else "Couldn't fetch news right now."
        return jsonify({"reply": reply, "intent": "news", "source": "News API", "language": lang, **defaults})

    # Default Search / General
    results = search_duckduckgo(message)
    if results:
        ctx = "\n".join(f"{i+1}. {r.get('snippet') or r.get('title')}" for i, r in enumerate(results))
        prompt = f'Answer: "{message}"\n\nWeb results:\n{ctx}\n\nGive a clear, direct answer.'
        source = "Web + AI"
    else:
        prompt = message
        source = "AI"

    reply = query_ai(prompt, history, None, lang)
    return jsonify({"reply": reply, "intent": intent, "source": source, "language": lang, **defaults})