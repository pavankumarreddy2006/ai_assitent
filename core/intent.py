import re
from data.college_data import COLLEGE_KEYWORDS

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


def detect_language(text: str) -> str:
    telugu_chars = sum(1 for ch in text if '\u0C00' <= ch <= '\u0C7F')
    total_chars = max(len(text.replace(" ", "")), 1)
    ratio = telugu_chars / total_chars
    return "te" if ratio > 0.15 else "en"


def classify_intent(message: str) -> str:
    msg = message.lower().strip()

    if any(kw in msg for kw in COLLEGE_KEYWORDS):
        return "college"
    if any(kw in message for kw in COLLEGE_KEYWORDS_TE):
        return "college"

    if any(kw in msg for kw in WEATHER_KEYWORDS):
        return "weather"
    if any(kw in message for kw in WEATHER_KEYWORDS_TE):
        return "weather"

    if any(kw in msg for kw in NEWS_KEYWORDS):
        return "news"
    if any(kw in message for kw in NEWS_KEYWORDS_TE):
        return "news"

    if any(kw in msg for kw in SEARCH_KEYWORDS):
        return "search"
    if any(kw in message for kw in SEARCH_KEYWORDS_TE):
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
