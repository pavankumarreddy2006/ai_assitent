import re

from data.college_data import COLLEGE_KEYWORDS

IMAGE_INTENT_PHRASES = [
    "college photos",
    "college images",
    "college pictures",
    "college gallery",
    "campus photos",
    "campus images",
    "campus pictures",
    "campus gallery",
    "show college photos",
    "show campus photos",
    "show photos",
    "show images",
    "campus tour",
    "virtual tour",
    "\u0c2b\u0c4b\u0c1f\u0c4b\u0c32\u0c41 \u0c1a\u0c42\u0c2a\u0c3f\u0c02\u0c1a\u0c41",
    "\u0c1a\u0c3f\u0c24\u0c4d\u0c30\u0c3e\u0c32\u0c41 \u0c1a\u0c42\u0c2a\u0c3f\u0c02\u0c1a\u0c41",
    "\u0c15\u0c4d\u0c2f\u0c3e\u0c02\u0c2a\u0c38\u0c4d \u0c2b\u0c4b\u0c1f\u0c4b",
    "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40 \u0c2b\u0c4b\u0c1f\u0c4b",
    "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40 \u0c1a\u0c3f\u0c24\u0c4d\u0c30\u0c3e\u0c32\u0c41",
    "\u0c15\u0c4d\u0c2f\u0c3e\u0c02\u0c2a\u0c38\u0c4d \u0c1a\u0c3f\u0c24\u0c4d\u0c30\u0c3e\u0c32\u0c41",
]

VIDEO_INTENT_PHRASES = [
    "college video",
    "campus video",
    "promotional video",
    "promo video",
    "ideal college video",
    "play college video",
    "show college video",
    "watch college video",
    "play video",
    "show video",
    "watch video",
    "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40 \u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b",
    "\u0c15\u0c4d\u0c2f\u0c3e\u0c02\u0c2a\u0c38\u0c4d \u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b",
    "\u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b \u0c2a\u0c4d\u0c32\u0c47",
    "\u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b \u0c1a\u0c42\u0c2a\u0c3f\u0c02\u0c1a\u0c41",
]

WAKE_PHRASES = [
    "hello ideal college ai",
    "hello ideal ai",
    "hi ideal college ai",
    "ideal college ai",
    "hello jarvis",
    "hi jarvis",
    "jarvis",
    "\u0c39\u0c32\u0c4b \u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c4d \u0c0f\u0c10",
    "\u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d \u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c4d \u0c0f\u0c10",
]

ROMAN_TELUGU_WORDS = {
    "nenu",
    "meeru",
    "nuvvu",
    "adigina",
    "adigithe",
    "matladithe",
    "matladu",
    "matladutunnanu",
    "telugu",
    "cheppu",
    "chepandi",
    "cheppandi",
    "ivvu",
    "ivvandi",
    "enti",
    "emiti",
    "ela",
    "enduku",
    "ekkada",
    "evaru",
    "undi",
    "unnayi",
    "kavali",
    "chesi",
    "cheyyi",
    "cheyyandi",
    "theliyali",
    "gurunchi",
    "varthalu",
    "vartalu",
    "tajaga",
    "vathavaranam",
    "vaatavaranam",
    "varsham",
    "courseulu",
    "chupinchu",
    "aadinchu",
}

WEATHER_KEYWORDS = [
    "weather",
    "temperature",
    "rain",
    "sunny",
    "cloudy",
    "forecast",
    "humidity",
    "wind",
    "climate",
    "hot",
    "cold",
    "storm",
    "drizzle",
    "thunderstorm",
    "heatwave",
    "rainfall",
]

NEWS_KEYWORDS = [
    "news",
    "headlines",
    "latest",
    "breaking",
    "current affairs",
    "trending",
    "update",
    "report",
    "article",
    "today's news",
]

SEARCH_KEYWORDS = [
    "search",
    "find",
    "look up",
    "what is",
    "who is",
    "where is",
    "how to",
    "define",
    "meaning of",
    "explain",
    "tell me about",
    "information about",
    "details about",
]

COLLEGE_HINTS_EN = {
    "admission",
    "admissions",
    "course",
    "courses",
    "fee",
    "fees",
    "principal",
    "hostel",
    "library",
    "placement",
    "placements",
    "college",
    "campus",
    "timings",
    "contact",
    "scholarship",
}

WEATHER_KEYWORDS_TE = [
    "\u0c35\u0c3e\u0c24\u0c3e\u0c35\u0c30\u0c23\u0c02",
    "\u0c09\u0c37\u0c4d\u0c23\u0c4b\u0c17\u0c4d\u0c30\u0c24",
    "\u0c35\u0c30\u0c4d\u0c37\u0c02",
    "\u0c35\u0c30\u0c4d\u0c37\u0c2a\u0c3e\u0c24\u0c02",
    "\u0c0e\u0c02\u0c21",
    "\u0c2e\u0c47\u0c18\u0c02",
    "\u0c17\u0c3e\u0c32\u0c3f",
    "\u0c35\u0c3e\u0c24\u0c3e\u0c35\u0c30\u0c23 \u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02",
    "\u0c1a\u0c32\u0c3f",
    "\u0c24\u0c41\u0c2b\u0c3e\u0c28\u0c41",
    "\u0c35\u0c3e\u0c28",
    "\u0c06\u0c15\u0c3e\u0c36\u0c02",
]

NEWS_KEYWORDS_TE = [
    "\u0c35\u0c3e\u0c30\u0c4d\u0c24\u0c32\u0c41",
    "\u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02",
    "\u0c24\u0c3e\u0c1c\u0c3e \u0c35\u0c3e\u0c30\u0c4d\u0c24\u0c32\u0c41",
    "\u0c2c\u0c4d\u0c30\u0c47\u0c15\u0c3f\u0c02\u0c17\u0c4d",
    "\u0c2e\u0c41\u0c16\u0c4d\u0c2f\u0c2e\u0c48\u0c28 \u0c35\u0c3e\u0c30\u0c4d\u0c24\u0c32\u0c41",
    "\u0c28\u0c47\u0c1f\u0c3f \u0c35\u0c3e\u0c30\u0c4d\u0c24\u0c32\u0c41",
    "\u0c05\u0c2a\u0c4d\u0c21\u0c47\u0c1f\u0c4d",
    "\u0c39\u0c46\u0c21\u0c4d\u0c32\u0c48\u0c28\u0c4d\u0c38\u0c4d",
]

SEARCH_KEYWORDS_TE = [
    "\u0c35\u0c46\u0c24\u0c15\u0c41",
    "\u0c1a\u0c46\u0c2a\u0c4d\u0c2a\u0c41",
    "\u0c0f\u0c2e\u0c3f\u0c1f\u0c3f",
    "\u0c0e\u0c35\u0c30\u0c41",
    "\u0c0e\u0c15\u0c4d\u0c15\u0c21",
    "\u0c0e\u0c32\u0c3e",
    "\u0c05\u0c30\u0c4d\u0c25\u0c02",
    "\u0c35\u0c3f\u0c35\u0c30\u0c23",
    "\u0c35\u0c3f\u0c35\u0c30\u0c3e\u0c32\u0c41",
    "\u0c17\u0c41\u0c30\u0c3f\u0c02\u0c1a\u0c3f \u0c1a\u0c46\u0c2a\u0c4d\u0c2a\u0c41",
    "\u0c38\u0c2e\u0c3e\u0c1a\u0c3e\u0c30\u0c02 \u0c07\u0c35\u0c4d\u0c35\u0c41",
    "\u0c24\u0c46\u0c32\u0c41\u0c38\u0c41\u0c15\u0c4b\u0c35\u0c3e\u0c32\u0c3f",
]

COLLEGE_KEYWORDS_TE = [
    "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40",
    "\u0c15\u0c4b\u0c30\u0c4d\u0c38\u0c41",
    "\u0c15\u0c4b\u0c30\u0c4d\u0c38\u0c41\u0c32\u0c41",
    "\u0c2b\u0c40\u0c1c\u0c41",
    "\u0c2a\u0c4d\u0c30\u0c3f\u0c28\u0c4d\u0c38\u0c3f\u0c2a\u0c32\u0c4d",
    "\u0c39\u0c3e\u0c38\u0c4d\u0c1f\u0c32\u0c4d",
    "\u0c32\u0c48\u0c2c\u0c4d\u0c30\u0c30\u0c40",
    "\u0c05\u0c21\u0c4d\u0c2e\u0c3f\u0c37\u0c28\u0c4d",
    "\u0c2a\u0c4d\u0c32\u0c47\u0c38\u0c4d\u0c2e\u0c46\u0c02\u0c1f\u0c4d",
    "\u0c2a\u0c30\u0c40\u0c15\u0c4d\u0c37",
    "\u0c39\u0c3e\u0c1c\u0c30\u0c41",
    "\u0c38\u0c4d\u0c15\u0c3e\u0c32\u0c30\u0c4d\u0c37\u0c3f\u0c2a\u0c4d",
    "\u0c09\u0c26\u0c4d\u0c2f\u0c4b\u0c17\u0c02",
    "\u0c2b\u0c4d\u0c2f\u0c3e\u0c15\u0c32\u0c4d\u0c1f\u0c40",
    "\u0c05\u0c27\u0c4d\u0c2f\u0c3e\u0c2a\u0c15\u0c41\u0c32\u0c41",
    "\u0c38\u0c26\u0c41\u0c2a\u0c3e\u0c2f\u0c3e\u0c32\u0c41",
    "\u0c2c\u0c38\u0c4d\u0c38\u0c41",
    "\u0c39\u0c3e\u0c38\u0c4d\u0c1f\u0c32\u0c4d \u0c2b\u0c40\u0c1c\u0c41",
    "\u0c35\u0c4d\u0c2f\u0c35\u0c38\u0c3e\u0c2f\u0c02",
    "\u0c2c\u0c40\u0c38\u0c40\u0c0f",
    "\u0c2c\u0c40\u0c2c\u0c40\u0c0f",
    "\u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d",
    "\u0c15\u0c3e\u0c15\u0c3f\u0c28\u0c3e\u0c21",
    "\u0c35\u0c3f\u0c26\u0c4d\u0c2f\u0c41\u0c24\u0c4d \u0c28\u0c17\u0c30\u0c4d",
    "\u0c2a\u0c4d\u0c30\u0c3f\u0c28\u0c4d\u0c38\u0c3f\u0c2a\u0c3e\u0c32\u0c4d",
    "\u0c2c\u0c40\u0c0e\u0c38\u0c4d\u0c38\u0c40",
    "\u0c0e\u0c02\u0c38\u0c40\u0c0f",
    "\u0c21\u0c48\u0c30\u0c46\u0c15\u0c4d\u0c1f\u0c30\u0c4d",
    "\u0c38\u0c2e\u0c2f\u0c02",
    "\u0c06\u0c2b\u0c40\u0c38\u0c4d",
]

WEATHER_KEYWORDS_ROMAN_TE = [
    "vathavaranam",
    "vaatavaranam",
    "weather cheppu",
    "varsham",
    "ushnograta",
    "enda",
    "chali",
    "vaana",
    "gali",
]

NEWS_KEYWORDS_ROMAN_TE = [
    "vartalu",
    "varthalu",
    "tajaga",
    "latest news cheppu",
    "news cheppu",
    "breaking vartalu",
]

SEARCH_KEYWORDS_ROMAN_TE = [
    "cheppu",
    "enti",
    "emiti",
    "evaru",
    "ekkada",
    "ela",
    "gurunchi",
    "theliyali",
    "vivaralu",
    "information ivvu",
]

_SCOPE = ("college", "campus", "ideal", "jarvis", "\u0c15\u0c3e\u0c32\u0c47\u0c1c\u0c40", "\u0c15\u0c4d\u0c2f\u0c3e\u0c02\u0c2a\u0c38\u0c4d", "\u0c10\u0c21\u0c3f\u0c2f\u0c32\u0c4d")
_MEDIA_PIC = ("photo", "photos", "image", "images", "picture", "pictures", "gallery", "\u0c2b\u0c4b\u0c1f\u0c4b", "\u0c1a\u0c3f\u0c24\u0c4d\u0c30")
_MEDIA_VID = ("video", "play", "watch", "\u0c35\u0c40\u0c21\u0c3f\u0c2f\u0c4b")


def _images_intent_from_text(msg: str, raw: str) -> bool:
    return any(p in msg for p in IMAGE_INTENT_PHRASES) or any(p in raw for p in IMAGE_INTENT_PHRASES) or (
        any(s in msg for s in _SCOPE) and any(m in msg or m in raw for m in _MEDIA_PIC)
    )


def _video_intent_from_text(msg: str, raw: str) -> bool:
    return any(p in msg for p in VIDEO_INTENT_PHRASES) or any(p in raw for p in VIDEO_INTENT_PHRASES) or (
        any(s in msg for s in _SCOPE) and any(v in msg or v in raw for v in _MEDIA_VID)
    )


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def strip_wake_phrase(text: str) -> str:
    normalized = normalize_text(text)
    for phrase in sorted(WAKE_PHRASES, key=len, reverse=True):
        if normalized.startswith(phrase):
            remainder = normalized[len(phrase) :].strip(" ,.:;-")
            return remainder
    return normalized


def detect_language(text: str) -> str:
    telugu_chars = sum(1 for ch in text if "\u0c00" <= ch <= "\u0c7f")
    total_chars = max(len(text.replace(" ", "")), 1)
    if telugu_chars / total_chars > 0.15:
        return "te"

    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return "en"

    roman_hits = sum(1 for word in words if word in ROMAN_TELUGU_WORDS)
    if roman_hits >= 2:
        return "te"
    if roman_hits == 1 and any(kw in text.lower() for kw in SEARCH_KEYWORDS_ROMAN_TE + NEWS_KEYWORDS_ROMAN_TE + WEATHER_KEYWORDS_ROMAN_TE):
        return "te"
    return "en"


def classify_intent(message: str) -> str:
    msg = normalize_text(message)
    raw = (message or "").strip()
    msg_words = set(re.findall(r"[a-zA-Z]+", msg))

    if _video_intent_from_text(msg, raw):
        return "video_intent"
    if _images_intent_from_text(msg, raw):
        return "images_intent"
    if any(kw in msg for kw in COLLEGE_HINTS_EN) or msg_words & COLLEGE_HINTS_EN:
        return "college"
    if any(kw in msg for kw in COLLEGE_KEYWORDS):
        return "college"
    if any(kw in message for kw in COLLEGE_KEYWORDS_TE):
        return "college"
    if any(kw in msg for kw in WEATHER_KEYWORDS) or any(kw in message for kw in WEATHER_KEYWORDS_TE) or any(kw in msg for kw in WEATHER_KEYWORDS_ROMAN_TE):
        return "weather"
    if any(kw in msg for kw in NEWS_KEYWORDS) or any(kw in message for kw in NEWS_KEYWORDS_TE) or any(kw in msg for kw in NEWS_KEYWORDS_ROMAN_TE):
        return "news"
    if any(kw in msg for kw in SEARCH_KEYWORDS) or any(kw in message for kw in SEARCH_KEYWORDS_TE) or any(kw in msg for kw in SEARCH_KEYWORDS_ROMAN_TE):
        return "search"
    if "?" in msg:
        return "search"
    return "general"


def detect_intent(message: str) -> str:
    intent = classify_intent(message)
    mapping = {
        "video_intent": "video_intent",
        "images_intent": "images_intent",
        "college": "college_intent",
        "weather": "weather_intent",
        "news": "news_intent",
        "search": "search_intent",
        "general": "unknown_intent",
    }
    return mapping.get(intent, "unknown_intent")


def extract_city(message: str) -> str | None:
    patterns = [
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)(?:\?|$|\.)",
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)\s+weather",
        r"temperature\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"how(?:'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"climate\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"([a-zA-Z][a-zA-Z\s]{1,20}?)\s+(?:lo\s+)?(?:weather|vaatavaranam|vastavam)",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+(?:\u0c35\u0c3e\u0c24\u0c3e\u0c35\u0c30\u0c23\u0c02|\u0c35\u0c30\u0c4d\u0c37\u0c02|\u0c09\u0c37\u0c4d\u0c23\u0c4b\u0c17\u0c4d\u0c30\u0c24)",
        r"(?:\u0c35\u0c3e\u0c24\u0c3e\u0c35\u0c30\u0c23\u0c02|\u0c35\u0c30\u0c4d\u0c37\u0c02)\s+([a-zA-Z][a-zA-Z\s]{1,20})",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+lo\s+weather",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+weather\s+cheppu",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            city = re.sub(r"[?.,!]+$", "", match.group(1).strip()).strip()
            if city and 2 <= len(city) <= 30:
                return city

    for word in message.split():
        cleaned = re.sub(r"[^a-zA-Z]", "", word)
        if len(cleaned) >= 3 and cleaned[0].isupper():
            lower = cleaned.lower()
            if lower not in {
                "weather",
                "what",
                "how",
                "tell",
                "the",
                "for",
                "now",
                "today",
                "check",
                "please",
                "kakinada",
                "show",
                "give",
                "temperature",
                "forecast",
                "update",
                "current",
            }:
                return cleaned
    return None
