import re
from data.college_data import COLLEGE_KEYWORDS

WEATHER_KEYWORDS = [
    "weather", "temperature", "rain", "sunny", "cloudy", "forecast",
    "humidity", "wind", "climate", "hot", "cold", "storm"
]

NEWS_KEYWORDS = [
    "news", "headlines", "latest", "breaking", "current affairs",
    "trending", "update", "report", "article"
]

SEARCH_KEYWORDS = [
    "search", "find", "look up", "what is", "who is", "where is",
    "how to", "define", "meaning of", "explain", "tell me about",
    "information about"
]


def classify_intent(message: str) -> str:
    """
    Returns one of: college | weather | news | search | general
    """
    msg = message.lower().strip()

    if any(kw in msg for kw in COLLEGE_KEYWORDS):
        return "college"

    if any(kw in msg for kw in WEATHER_KEYWORDS):
        return "weather"

    if any(kw in msg for kw in NEWS_KEYWORDS):
        return "news"

    if any(kw in msg for kw in SEARCH_KEYWORDS):
        return "search"

    return "general"


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
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip().split("?")[0].strip()

    return None
