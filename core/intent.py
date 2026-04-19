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
    "ఫోటోలు చూపించు",
    "చిత్రాలు చూపించు",
    "క్యాంపస్ ఫోటో",
    "కాలేజీ ఫోటో",
    "కాలేజీ చిత్రాలు",
    "క్యాంపస్ చిత్రాలు",
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
    "కాలేజీ వీడియో",
    "క్యాంపస్ వీడియో",
    "వీడియో ప్లే",
    "వీడియో చూపించు",
]

_SCOPE = ("college", "campus", "ideal", "కాలేజీ", "క్యాంపస్", "ఐడియల్")
_MEDIA_PIC = ("photo", "photos", "image", "images", "picture", "pictures", "gallery", "ఫోటో", "చిత్ర")
_MEDIA_VID = ("video", "వీడియో")


def _images_intent_from_text(msg: str, raw: str) -> bool:
    if any(p in msg for p in IMAGE_INTENT_PHRASES) or any(p in raw for p in IMAGE_INTENT_PHRASES):
        return True
    if any(s in msg for s in _SCOPE) and any(m in msg or m in raw for m in _MEDIA_PIC):
        return True
    return False


def _video_intent_from_text(msg: str, raw: str) -> bool:
    if any(p in msg for p in VIDEO_INTENT_PHRASES) or any(p in raw for p in VIDEO_INTENT_PHRASES):
        return True
    if any(s in msg for s in _SCOPE) and any(v in msg or v in raw for v in _MEDIA_VID):
        return True
    return False


# Legacy names for detect_intent (unused); keep as supersets for compatibility
IMAGES_KEYWORDS = list(IMAGE_INTENT_PHRASES) + ["photos", "images"]
VIDEO_KEYWORDS = list(VIDEO_INTENT_PHRASES) + ["video"]

def detect_intent(message):
    """
    Detects the type of user intent from the message.

    Returns:
        str: intent name such as "college_intent", "weather_intent", "news_intent", etc.
    """
    text = message.lower().strip()
    # Video intent
    if _video_intent_from_text(text, message.strip()):
        return "video_intent"
    if _images_intent_from_text(text, message.strip()):
        return "images_intent"
    # College intent
    for word in COLLEGE_KEYWORDS:
        if re.search(r"\b" + re.escape(word.lower()) + r"\b", text):
            return "college_intent"
    # Weather intent
    for word in WEATHER_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return "weather_intent"
    # News intent
    for word in NEWS_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return "news_intent"
    # Search intent
    for word in SEARCH_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            return "search_intent"
    # Telugu weather
    for word in WEATHER_KEYWORDS_TE:
        if word in text:
            return "weather_intent"
    # Telugu news
    for word in NEWS_KEYWORDS_TE:
        if word in text:
            return "news_intent"
    # Telugu search
    for word in SEARCH_KEYWORDS_TE:
        if word in text:
            return "search_intent"
    # Telugu college
    for word in COLLEGE_KEYWORDS_TE:
        if word in text:
            return "college_intent"
    # Roman Telugu (fallbacks - basic detection)
    for word in ROMAN_TELUGU_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            # Use search intent as a fallback
            return "search_intent"
    return "unknown_intent"

WEATHER_KEYWORDS = [
    "weather", "temperature", "rain", "sunny", "cloudy", "forecast",
    "humidity", "wind", "climate", "hot", "cold", "storm", "drizzle",
    "thunderstorm", "heatwave", "rainfall"
]

NEWS_KEYWORDS = [
    "news", "headlines", "latest", "breaking", "current affairs",
    "trending", "update", "report", "article", "today's news"
]

SEARCH_KEYWORDS = [
    "search", "find", "look up", "what is", "who is", "where is",
    "how to", "define", "meaning of", "explain", "tell me about",
    "information about", "details about"
]

COLLEGE_HINTS_EN = {
    "admission", "admissions", "course", "courses", "fee", "fees", "principal", "hostel",
    "library", "placement", "placements", "college", "campus", "timings", "contact", "scholarship",
}

WEATHER_KEYWORDS_TE = [
    "వాతావరణం", "ఉష్ణోగ్రత", "వర్షం", "వర్షపాతం", "ఎండ", "మేఘం",
    "గాలి", "వాతావరణ సమాచారం", "చలి", "తుఫాను", "వాన", "ఆకాశం"
]

NEWS_KEYWORDS_TE = [
    "వార్తలు", "సమాచారం", "తాజా వార్తలు", "బ్రేకింగ్", "ముఖ్యమైన వార్తలు",
    "నేటి వార్తలు", "అప్‌డేట్", "హెడ్‌లైన్స్"
]

SEARCH_KEYWORDS_TE = [
    "వెతకు", "చెప్పు", "ఏమిటి", "ఎవరు", "ఎక్కడ", "ఎలా",
    "అర్థం", "వివరణ", "వివరాలు", "గురించి చెప్పు",
    "సమాచారం ఇవ్వు", "తెలుసుకోవాలి"
]

COLLEGE_KEYWORDS_TE = [
    "కాలేజీ", "కోర్సు", "కోర్సులు", "ఫీజు", "ప్రిన్సిపల్",
    "హాస్టల్", "లైబ్రరీ", "అడ్మిషన్", "ప్లేస్‌మెంట్",
    "పరీక్ష", "హాజరు", "స్కాలర్‌షిప్", "ఉద్యోగం",
    "ఫ్యాకల్టీ", "అధ్యాపకులు", "సదుపాయాలు", "బస్సు",
    "హాస్టల్ ఫీజు", "వ్యవసాయం", "బీసీఏ", "బీబీఏ",
    "ఐడియల్", "కాకినాడ", "విద్యుత్ నగర్", "ప్రిన్సిపాల్",
    "బీఎస్సీ", "ఎంసీఏ", "డైరెక్టర్", "సమయం", "ఆఫీస్"
]

ROMAN_TELUGU_WORDS = {
    "nenu", "meeru", "nuvvu", "adigina", "adigithe", "matladithe",
    "matladu", "cheppu", "chepandi", "cheppandi", "ivvu", "ivvandi",
    "enti", "emiti", "ela", "enduku", "ekkada", "evaru", "evarini",
    "telugu", "lo", "ga", "ki", "ni", "undi", "unnayi", "kavali",
    "chesi", "cheyyi", "cheyyandi", "theliyali", "gurunchi",
    "vartalu", "tajaga", "vathavaranam", "vaatavaranam", "varsham",
    "courseulu"
}

WEATHER_KEYWORDS_ROMAN_TE = [
    "vathavaranam", "vaatavaranam", "weather cheppu", "varsham", "ushnograta",
    "enda", "chali", "vaana", "gali"
]

NEWS_KEYWORDS_ROMAN_TE = [
    "vartalu", "tajaga", "latest news cheppu", "news cheppu", "breaking vartalu"
]

SEARCH_KEYWORDS_ROMAN_TE = [
    "cheppu", "enti", "emiti", "evaru", "ekkada", "ela", "gurunchi",
    "theliyali", "vivaralu", "information ivvu"
]


def detect_language(text: str) -> str:
    telugu_chars = sum(1 for ch in text if '\u0C00' <= ch <= '\u0C7F')
    total_chars = max(len(text.replace(" ", "")), 1)
    ratio = telugu_chars / total_chars
    if ratio > 0.15:
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
    msg = message.lower().strip()
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

    if any(kw in msg for kw in WEATHER_KEYWORDS):
        return "weather"
    if any(kw in message for kw in WEATHER_KEYWORDS_TE):
        return "weather"
    if any(kw in msg for kw in WEATHER_KEYWORDS_ROMAN_TE):
        return "weather"

    if any(kw in msg for kw in NEWS_KEYWORDS):
        return "news"
    if any(kw in message for kw in NEWS_KEYWORDS_TE):
        return "news"
    if any(kw in msg for kw in NEWS_KEYWORDS_ROMAN_TE):
        return "news"

    if any(kw in msg for kw in SEARCH_KEYWORDS):
        return "search"
    if any(kw in message for kw in SEARCH_KEYWORDS_TE):
        return "search"
    if any(kw in msg for kw in SEARCH_KEYWORDS_ROMAN_TE):
        return "search"

    if "?" in msg:
        return "search"
    return "general"


def extract_city(message: str) -> str | None:
    patterns = [
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)(?:\?|$|\.)",
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"(?:in|at|for|of)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)\s+weather",
        r"temperature\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"how(?:'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"climate\s+(?:in|at|of)\s+([a-zA-Z][a-zA-Z\s]{1,30})",
        r"([a-zA-Z][a-zA-Z\s]{1,20}?)\s+(?:lo\s+)?(?:weather|vaatavaranam|vastavam)",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+(?:వాతావరణం|వర్షం|ఉష్ణోగ్రత)",
        r"(?:వాతావరణం|వర్షం)\s+([a-zA-Z][a-zA-Z\s]{1,20})",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+lo\s+weather",
        r"([a-zA-Z][a-zA-Z\s]{1,20})\s+weather\s+cheppu",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            city = re.sub(r'[?.,!]+$', '', city).strip()
            if city and 2 <= len(city) <= 30:
                return city

    words = message.split()
    for word in words:
        cleaned = re.sub(r'[^a-zA-Z]', '', word)
        if len(cleaned) >= 3 and cleaned[0].isupper():
            lower = cleaned.lower()
            skip = {
                'weather', 'what', 'how', 'tell', 'the', 'for', 'now',
                'today', 'check', 'please', 'kakinada', 'show', 'give',
                'temperature', 'forecast', 'update', 'current'
            }
            if lower not in skip:
                return cleaned

    return None
