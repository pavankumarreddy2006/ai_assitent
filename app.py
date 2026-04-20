import os
import json
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from college_service import get_college_answer, get_college_context, COLLEGE_KEYWORDS

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── ENV ──────────────────────────────────────────────────────
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
GNEWS_API       = os.getenv("GNEWS_API", "")
NEWS_API_KEY    = os.getenv("NEWS_API_KEY", "")
NEWS_DATA_API   = os.getenv("NEWS_DATA_API", "")

GROQ_MODEL        = "llama3-8b-8192"
OPENROUTER_MODEL  = "openai/gpt-3.5-turbo"

COLLEGE_SYSTEM_PROMPT = """You are the official AI assistant for Ideal College of Arts and Sciences,
located at Vidyuth Nagar, Kakinada, Andhra Pradesh.

LANGUAGE RULE:
- If the user writes in Telugu → reply ONLY in Telugu.
- If the user writes in English → reply ONLY in English.

BEHAVIOR:
- Be friendly, helpful, and professional.
- For college questions, give direct and accurate answers.
- Keep answers clear and concise.

COLLEGE CONTACT:
- Phone: 0884-2384382 / 0884-2384381
- Email: idealcolleges@gmail.com
- Website: https://idealcollege.edu.in
- Location: Vidyuth Nagar, Kakinada, Andhra Pradesh"""

TELUGU_SYSTEM_PROMPT = """మీరు ఐడియల్ కాలేజ్ ఆఫ్ ఆర్ట్స్ అండ్ సైన్సెస్, కాకినాడ యొక్క అధికారిక AI అసిస్టెంట్.
భాషా నియమం: తెలుగులో మాట్లాడితే తెలుగులోనే సమాధానం ఇవ్వండి.
కాలేజీ సంప్రదింపు: ఫోన్: 0884-2384382, ఇమెయిల్: idealcolleges@gmail.com"""

IMAGE_PATHS = ["/static/media/1.png", "/static/media/2.png"]
VIDEO_PATH  = "/static/media/college.mp4"

ROMAN_TELUGU = {"nenu","meeru","nuvvu","enti","emiti","ela","enduku","undi","kavali","chesi","gurunchi"}
WEATHER_KW   = ["weather","temperature","rain","sunny","cloudy","forecast","humidity","wind","climate"]
NEWS_KW      = ["news","headlines","latest","breaking","current affairs","trending","update"]
SEARCH_KW    = ["search","find","what is","who is","where is","how to","define","explain","tell me about"]
IMAGE_KW     = ["college photos","campus photos","show photos","show images","college images","campus images",
                "ఫోటోలు","చిత్రాలు","కాలేజీ ఫోటో"]
VIDEO_KW     = ["college video","campus video","play video","show video","watch video","full details",
                "కాలేజీ వీడియో","వీడియో"]
COLLEGE_HINTS= {"admission","course","fee","principal","hostel","library","placement","college","campus",
                "scholarship","timings","contact","courses","fees","placements"}


# ── LANGUAGE DETECTION ───────────────────────────────────────
def detect_language(text: str) -> str:
    telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
    total = max(len(text.replace(" ", "")), 1)
    if telugu_chars / total > 0.15:
        return "te"
    words = [w.lower() for w in text.split() if w.isalpha()]
    if sum(1 for w in words if w in ROMAN_TELUGU) >= 2:
        return "te"
    return "en"


# ── INTENT CLASSIFICATION ────────────────────────────────────
def classify_intent(message: str) -> str:
    msg = message.lower().strip()
    if any(p in msg for p in VIDEO_KW):  return "video_intent"
    if any(p in msg for p in IMAGE_KW):  return "images_intent"
    words = set(msg.split())
    if words & COLLEGE_HINTS:            return "college"
    if any(kw in msg for kw in COLLEGE_KEYWORDS): return "college"
    if any(kw in msg for kw in WEATHER_KW):       return "weather"
    if any(kw in msg for kw in NEWS_KW):           return "news"
    if any(kw in msg for kw in SEARCH_KW):         return "search"
    if "?" in msg:                                  return "search"
    return "general"


def extract_city(message: str) -> str:
    import re
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


# ── WEATHER ──────────────────────────────────────────────────
WEATHER_CODES = {
    0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
    45:"Foggy",51:"Light drizzle",61:"Slight rain",63:"Moderate rain",
    65:"Heavy rain",80:"Rain showers",95:"Thunderstorm"
}

def get_weather(city: str, lang: str = "en") -> dict | None:
    try:
        if WEATHER_API_KEY:
            r = requests.get(
                f"https://api.weatherapi.com/v1/current.json",
                params={"key": WEATHER_API_KEY, "q": city, "aqi": "no"},
                timeout=10
            )
            if r.ok:
                d = r.json()
                return {
                    "city": d["location"]["name"],
                    "temperature": d["current"]["temp_c"],
                    "description": d["current"]["condition"]["text"],
                    "humidity": d["current"]["humidity"],
                    "wind_speed": d["current"]["wind_kph"],
                }
        # fallback: Open-Meteo
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}, timeout=10
        ).json()
        results = geo.get("results", [])
        if not results:
            return None
        lat, lon, name = results[0]["latitude"], results[0]["longitude"], results[0]["name"]
        w = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"},
            timeout=10
        ).json()
        cur = w["current"]
        return {
            "city": name,
            "temperature": cur["temperature_2m"],
            "description": WEATHER_CODES.get(cur.get("weather_code", 0), "Unknown"),
            "humidity": cur["relative_humidity_2m"],
            "wind_speed": cur["wind_speed_10m"],
        }
    except Exception:
        return None


# ── NEWS ─────────────────────────────────────────────────────
def fetch_news(query: str = "India education college news") -> list[dict]:
    if GNEWS_API:
        try:
            r = requests.get(
                "https://gnews.io/api/v4/search",
                params={"q": query, "lang": "en", "max": 10, "apikey": GNEWS_API},
                timeout=10
            )
            if r.ok:
                arts = r.json().get("articles", [])
                if arts:
                    return [{"title": a["title"], "source": a.get("source", {}).get("name", "")} for a in arts[:5]]
        except Exception:
            pass

    if NEWS_DATA_API:
        try:
            r = requests.get(
                "https://newsdata.io/api/1/news",
                params={"q": query, "language": "en", "apikey": NEWS_DATA_API},
                timeout=10
            )
            if r.ok:
                arts = r.json().get("results", [])
                if arts:
                    return [{"title": a["title"], "source": a.get("source_id", "")} for a in arts[:5]]
        except Exception:
            pass

    if NEWS_API_KEY:
        try:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": query, "sortBy": "publishedAt", "pageSize": 10, "apiKey": NEWS_API_KEY},
                timeout=10
            )
            if r.ok:
                arts = r.json().get("articles", [])
                if arts:
                    return [{"title": a["title"], "source": a.get("source", {}).get("name", "")} for a in arts[:5]]
        except Exception:
            pass

    return []


# ── DUCKDUCKGO SEARCH ─────────────────────────────────────────
def search_duckduckgo(query: str) -> list[dict]:
    try:
        import re
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if not r.ok:
            return []
        html = r.text
        titles   = re.findall(r'class="result__a"[^>]*>([^<]+)<', html)
        snippets = re.findall(r'class="result__snippet"[^>]*>([^<]+)<', html)
        return [{"title": t.strip(), "snippet": snippets[i].strip() if i < len(snippets) else ""}
                for i, t in enumerate(titles[:5])]
    except Exception:
        return []


# ── AI QUERY ─────────────────────────────────────────────────
def call_openai_compatible(base_url: str, api_key: str, model: str,
                            messages: list, max_tokens: int = 1200,
                            temperature: float | None = 0.7) -> str:
    body = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        body["temperature"] = temperature
    r = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body, timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def build_messages(prompt: str, history: list, system_prompt: str) -> list:
    msgs = [{"role": "system", "content": system_prompt}]
    for m in history[-10:]:
        if m.get("role") in ("user", "assistant") and m.get("content", "").strip():
            msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": prompt})
    return msgs


def query_ai(prompt: str, history: list = None, system_prompt: str = None, lang: str = "en") -> str:
    history = history or []
    sys_prompt = system_prompt or (TELUGU_SYSTEM_PROMPT if lang == "te" else COLLEGE_SYSTEM_PROMPT)
    messages = build_messages(prompt, history, sys_prompt)

    if GROQ_API_KEY:
        try:
            return call_openai_compatible("https://api.groq.com/openai/v1", GROQ_API_KEY, GROQ_MODEL, messages)
        except Exception:
            pass

    if OPEN_ROUTER_API:
        try:
            return call_openai_compatible("https://openrouter.ai/api/v1", OPEN_ROUTER_API, OPENROUTER_MODEL, messages)
        except Exception:
            pass

    return ("క్షమించండి, AI సేవ అందుబాటులో లేదు." if lang == "te"
            else "Sorry, AI service is temporarily unavailable. Please try again.")


# ── ROUTES ───────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/media/<path:filename>")
def serve_media(filename):
    return send_from_directory("static/media", filename)


@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message is required"}), 400

    lang   = detect_language(message)
    intent = classify_intent(message)

    defaults = {"show_images": False, "images": [], "show_video": False, "video_url": None}

    # Images
    if intent == "images_intent":
        return jsonify({
            "reply": "ఇప్పుడు క్యాంపస్ చిత్రాలు చూపిస్తున్నాను." if lang == "te"
                     else "Here are the campus images for you.",
            "intent": "images", "source": "Media Service", "language": lang,
            "show_images": True, "images": IMAGE_PATHS, "show_video": False, "video_url": None
        })

    # Video
    if intent == "video_intent":
        return jsonify({
            "reply": "కాలేజీ వీడియో ప్లే చేస్తున్నాను." if lang == "te"
                     else "Playing the college promotional video.",
            "intent": "video", "source": "Media Service", "language": lang,
            "show_images": False, "images": [], "show_video": True, "video_url": VIDEO_PATH
        })

    # College DB
    if intent == "college":
        local = get_college_answer(message, lang)
        if local:
            return jsonify({"reply": local, "intent": "college",
                            "source": "College Database", "language": lang, **defaults})
        ctx = get_college_context()
        sys = (TELUGU_SYSTEM_PROMPT if lang == "te" else COLLEGE_SYSTEM_PROMPT) + f"\n\nCOLLEGE INFO:\n{ctx}"
        reply = query_ai(message, history, sys, lang)
        return jsonify({"reply": reply, "intent": "college",
                        "source": "AI + College Database", "language": lang, **defaults})

    # Weather
    if intent == "weather":
        city = extract_city(message)
        wd = get_weather(city, lang)
        if wd:
            reply = (f"{wd['city']}లో వాతావరణం: {wd['description']}, "
                     f"ఉష్ణోగ్రత: {wd['temperature']}°C, తేమ: {wd['humidity']}%, "
                     f"గాలి: {wd['wind_speed']} km/h."
                     if lang == "te"
                     else f"Weather in {wd['city']}: {wd['description']}, "
                          f"Temperature: {wd['temperature']}°C, Humidity: {wd['humidity']}%, "
                          f"Wind: {wd['wind_speed']} km/h.")
        else:
            reply = (f"'{city}' వాతావరణ సమాచారం దొరకలేదు." if lang == "te"
                     else f"Couldn't find weather data for '{city}'.")
        return jsonify({"reply": reply, "intent": "weather",
                        "source": "Weather API", "language": lang, **defaults})

    # News
    if intent == "news":
        articles = fetch_news()
        if articles:
            header = "తాజా వార్తలు:\n" if lang == "te" else "Here are the latest headlines:\n"
            lines = [f"{i+1}. {a['title']} — {a['source']}" for i, a in enumerate(articles)]
            reply = header + "\n".join(lines)
        else:
            reply = ("వార్తలు తీసుకోలేకపోయాము." if lang == "te"
                     else "Couldn't fetch news right now. Please try again.")
        return jsonify({"reply": reply, "intent": "news",
                        "source": "News API", "language": lang, **defaults})

    # Search / General
    results = search_duckduckgo(message)
    if results:
        ctx = "\n".join(f"{i+1}. {r['snippet'] or r['title']}" for i, r in enumerate(results))
        prompt = f'Answer: "{message}"\n\nWeb results:\n{ctx}\n\nGive a clear, direct answer.'
        source = "Web + AI"
    else:
        prompt = message
        source = "AI"

    reply = query_ai(prompt, history, None, lang)
    return jsonify({"reply": reply, "intent": intent,
                    "source": source, "language": lang, **defaults})


@app.route("/api/news")
def api_news():
    return jsonify(fetch_news())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)