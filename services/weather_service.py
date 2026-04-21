# services/weather_service.py
import os
import re
import requests
from typing import Optional, Dict, Any

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")


def _extract_city(query: str) -> str:
    q = (query or "").strip()

    # "weather in Hyderabad", "temperature at Kakinada"
    m = re.search(r"(?:in|at)\s+([a-zA-Z\s]+)", q, re.IGNORECASE)
    if m:
        return m.group(1).strip("?.!, ")

    # Telugu fallback words
    m2 = re.search(r"(?:లో|కి)\s*([a-zA-Z\u0C00-\u0C7F\s]+)", q)
    if m2:
        return m2.group(1).strip("?.!, ")

    # Last token fallback
    parts = q.split()
    if parts:
        return parts[-1].strip("?.!,")
    return "Kakinada"


def _weatherapi(city: str) -> Optional[Dict[str, Any]]:
    if not WEATHER_API_KEY:
        return None
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        resp = requests.get(url, params={"key": WEATHER_API_KEY, "q": city, "aqi": "no"}, timeout=12)
        if resp.status_code != 200:
            return None

        data = resp.json()
        cur = data.get("current", {})
        loc = data.get("location", {})
        return {
            "city": loc.get("name", city),
            "temp": cur.get("temp_c", "N/A"),
            "desc": cur.get("condition", {}).get("text", "Unknown"),
            "humidity": cur.get("humidity", "N/A"),
            "wind": cur.get("wind_kph", "N/A"),
            "provider": "WeatherAPI",
        }
    except Exception:
        return None


def _open_meteo(city: str) -> Optional[Dict[str, Any]]:
    # Free fallback (no key)
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        )
        if geo.status_code != 200:
            return None
        results = geo.json().get("results") or []
        if not results:
            return None

        lat = results[0]["latitude"]
        lon = results[0]["longitude"]
        name = results[0].get("name", city)

        w = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            },
            timeout=10,
        )
        if w.status_code != 200:
            return None

        current = w.json().get("current", {})
        code = current.get("weather_code", -1)

        code_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Fog", 51: "Drizzle", 61: "Rain", 63: "Rain", 65: "Heavy rain",
            80: "Rain showers", 95: "Thunderstorm",
        }

        return {
            "city": name,
            "temp": current.get("temperature_2m", "N/A"),
            "desc": code_map.get(code, "Unknown"),
            "humidity": current.get("relative_humidity_2m", "N/A"),
            "wind": current.get("wind_speed_10m", "N/A"),
            "provider": "Open-Meteo",
        }
    except Exception:
        return None


def get_weather_from_query(query: str, lang: str = "en") -> str:
    city = _extract_city(query)

    data = _weatherapi(city) or _open_meteo(city)
    if not data:
        return "Unable to fetch weather now." if lang == "en" else "ఇప్పుడు వాతావరణ వివరాలు తీసుకురాలేకపోయాను."

    if lang == "te":
        return (
            f"{data['city']} లో ప్రస్తుతం {data['temp']}°C ఉంది, {data['desc']}. "
            f"Humidity {data['humidity']}% మరియు Wind {data['wind']} km/h. "
            f"(Source: {data['provider']})"
        )

    return (
        f"In {data['city']}, it is {data['temp']}°C with {data['desc']}. "
        f"Humidity {data['humidity']}% and wind {data['wind']} km/h. "
        f"(Source: {data['provider']})"
    )