# core/intent.py
import re
from typing import Dict

COLLEGE_KEYWORDS = [
    "college", "name of the college", "about college", "course", "courses", "fee", "fees",
    "admission", "hostel", "principal", "contact", "facility", "facilities", "campus", "ideal",
    "timings", "naac", "placements", "library"
]

WEATHER_KEYWORDS = [
    "weather", "temperature", "climate", "rain", "forecast", "humidity", "wind",
    "వాతావరణం", "ఉష్ణోగ్రత", "వర్షం"
]

NEWS_KEYWORDS = ["news", "latest", "update", "today", "headlines", "వార్తలు"]
SEARCH_KEYWORDS = ["search", "find", "what is", "who is", "tell me about", "internet", "web"]
IMAGE_KEYWORDS = ["image", "images", "photo", "photos", "campus", "campus photos", "gallery", "ఫోటోలు", "చిత్రాలు"]
VIDEO_KEYWORDS = ["video", "full details", "full explanation", "explain college", "college video", "వీడియో", "పూర్తి వివరాలు"]


def detect_language(text: str) -> str:
    if not text:
        return "en"

    telugu_chars = sum(1 for ch in text if "\u0C00" <= ch <= "\u0C7F")
    total = max(len(text.replace(" ", "")), 1)
    if telugu_chars / total > 0.1:
        return "te"

    roman_telugu = {"nenu", "meeru", "kavali", "cheppu", "fees", "admission", "course", "college"}
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    if words & roman_telugu:
        return "te"

    return "en"


def classify_intent(message: str) -> Dict[str, str]:
    msg = (message or "").lower().strip()

    if any(k in msg for k in IMAGE_KEYWORDS):
        return {"intent": "images"}
    if any(k in msg for k in VIDEO_KEYWORDS):
        return {"intent": "video"}
    if any(k in msg for k in WEATHER_KEYWORDS):
        return {"intent": "weather"}
    if any(k in msg for k in NEWS_KEYWORDS):
        return {"intent": "news"}
    if any(k in msg for k in SEARCH_KEYWORDS):
        return {"intent": "search"}
    if any(k in msg for k in COLLEGE_KEYWORDS):
        return {"intent": "college"}

    return {"intent": "general"}