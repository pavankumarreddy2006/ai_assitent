# services/weather_service.py
import os
import re
import requests

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")


def _extract_city(query: str) -> str:
    q = (query or "").strip()
    match = re.search(r"(?:in|at)\s+([a-zA-Z\s]+)", q, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    parts = q.split()
    if parts:
        return parts[-1].strip("?.!,")
    return "Kakinada"


def get_weather_from_query(query: str, lang: str = "en") -> str:
    city = _extract_city(query)
    if not WEATHER_API_KEY:
        return "Weather API key not configured." if lang == "en" else "Weather API key configure చేయలేదు."

    url = "https://api.weatherapi.com/v1/current.json"
    try:
        resp = requests.get(url, params={"key": WEATHER_API_KEY, "q": city, "aqi": "no"}, timeout=12)
        if resp.status_code != 200:
            return "Unable to fetch weather now." if lang == "en" else "ఇప్పుడు వాతావరణం తీసుకురాలేకపోయాను."

        data = resp.json()
        loc = data.get("location", {}).get("name", city)
        cur = data.get("current", {})
        temp = cur.get("temp_c", "N/A")
        desc = cur.get("condition", {}).get("text", "Unknown")
        hum = cur.get("humidity", "N/A")
        wind = cur.get("wind_kph", "N/A")

        if lang == "te":
            return f"{loc} లో ప్రస్తుతం {temp}°C ఉంది, {desc}. Humidity {hum}% మరియు Wind {wind} km/h."
        return f"In {loc}, it is {temp}°C with {desc}. Humidity {hum}% and wind {wind} km/h."
    except Exception:
        return "Weather service unavailable." if lang == "en" else "Weather service ప్రస్తుతం అందుబాటులో లేదు."