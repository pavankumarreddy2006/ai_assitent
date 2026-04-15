import re
from data.college_data import COLLEGE_KEYWORDS

# =====================================================
# ENGLISH KEYWORDS
# =====================================================
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

# =====================================================
# TELUGU KEYWORDS
# =====================================================
WEATHER_KEYWORDS_TE = [
    "వాతావరణం", "ఉష్ణోగ్రత", "వర్షం", "వర్షపాతం", "ఎండ", "మేఘం",
    "గాలి", "వాతావరణ సమాచారం", "చలి", "తుఫాను", "ఆబ్కారీ",
    "వాన", "ఆకాశం"
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
    "ఐడియల్", "కాకినాడ", "విద్యుత్ నగర్", "ప్రిన్సిపాల్"
]


# =====================================================
# LANGUAGE DETECTION
# =====================================================
def detect_language(text: str) -> str:
    """
    Returns 'te' if the message is primarily Telugu, else 'en'.
    Telugu Unicode range: U+0C00 to U+0C7F
    """
    telugu_chars = sum(1 for ch in text if '\u0C00' <= ch <= '\u0C7F')
    total_chars  = max(len(text.replace(" ", "")), 1)
    ratio = telugu_chars / total_chars
    return "te" if ratio > 0.15 else "en"


# =====================================================
# INTENT CLASSIFICATION
# =====================================================
def classify_intent(message: str) -> str:
    """
    Classifies user intent as: college | weather | news | search | general

    Works for both English and Telugu messages.
    """
    msg = message.lower().strip()

    # ── College ────────────────────────────────────────────────
    # Check English college keywords (from college_data.py)
    if any(kw in msg for kw in COLLEGE_KEYWORDS):
        return "college"

    # Check Telugu college keywords
    if any(kw in message for kw in COLLEGE_KEYWORDS_TE):
        return "college"

    # ── Weather ────────────────────────────────────────────────
    if any(kw in msg for kw in WEATHER_KEYWORDS):
        return "weather"

    if any(kw in message for kw in WEATHER_KEYWORDS_TE):
        return "weather"

    # ── News ──────────────────────────────────────────────────
    if any(kw in msg for kw in NEWS_KEYWORDS):
        return "news"

    if any(kw in message for kw in NEWS_KEYWORDS_TE):
        return "news"

    # ── Search ────────────────────────────────────────────────
    if any(kw in msg for kw in SEARCH_KEYWORDS):
        return "search"

    if any(kw in message for kw in SEARCH_KEYWORDS_TE):
        return "search"

    return "general"


# =====================================================
# CITY EXTRACTION (for weather)
# =====================================================
def extract_city(message: str) -> str | None:
    """
    Extract city name from a weather query.
    Returns the city name or None.
    """
    patterns = [
        r"weather (?:in|at|for|of) ([a-zA-Z\s]+)",
        r"(?:in|at|for|of) ([a-zA-Z\s]+) weather",
        r"temperature (?:in|at|of) ([a-zA-Z\s]+)",
        r"how(?:'s| is) (?:the )?weather (?:in|at) ([a-zA-Z\s]+)",
        r"climate (?:in|at|of) ([a-zA-Z\s]+)",
        # Telugu patterns (transliterated city names)
        r"([a-zA-Z\s]+)\s+(?:వాతావరణం|వర్షం|ఉష్ణోగ్రత)",
        r"(?:వాతావరణం|వర్షం)\s+([a-zA-Z\s]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            city = match.group(1).strip().split("?")[0].strip()
            if city:
                return city

    return None
