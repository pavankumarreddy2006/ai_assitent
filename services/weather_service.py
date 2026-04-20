import os
import requests
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# Weather code descriptions (English)
WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}

# Weather code descriptions (Telugu)
WEATHER_CODES_TE: Dict[int, str] = {
    0: "ఆకాశం స్వచ్ఛంగా ఉంది",
    1: "ప్రధానంగా స్వచ్ఛంగా",
    2: "పాక్షికంగా మేఘావృతం",
    3: "పూర్తిగా మేఘావృతం",
    51: "తేలికపాటి జల్లు",
    61: "తేలికపాటి వర్షం",
    63: "మితమైన వర్షం",
    65: "భారీ వర్షం",
    80: "వర్షపు జల్లులు",
    95: "పిడుగుపాటు వర్షం",
}

def get_weather_api(city: str) -> Optional[Dict[str, Any]]:
    """Primary: WeatherAPI.com"""
    if not WEATHER_API_KEY:
        return None

    try:
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={requests.utils.quote(city)}&aqi=no"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None

        data = response.json()
        current = data.get("current", {})
        location = data.get("location", {})

        return {
            "city": location.get("name", city),
            "temperature": current.get("temp_c"),
            "description": current.get("condition", {}).get("text", "Unknown"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_kph")
        }
    except Exception as e:
        logger.warning(f"WeatherAPI.com failed for {city}: {e}")
        return None


def get_openmeteo_weather(city: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Fallback: Open-Meteo API"""
    try:
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(city)}&count=1"
        geo_resp = requests.get(geo_url, timeout=10)
        
        if geo_resp.status_code != 200:
            return None

        geo_data = geo_resp.json()
        results = geo_data.get("results")
        if not results or len(results) == 0:
            return None

        location = results[0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location.get("name", city)

        # Step 2: Get weather data
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        )
        weather_resp = requests.get(weather_url, timeout=10)

        if weather_resp.status_code != 200:
            return None

        weather_data = weather_resp.json()
        current = weather_data.get("current", {})

        code = current.get("weather_code", 0)
        description = WEATHER_CODES_TE.get(code) if lang == "te" else WEATHER_CODES.get(code, "Unknown")

        return {
            "city": name,
            "temperature": current.get("temperature_2m"),
            "description": description,
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m")
        }
    except Exception as e:
        logger.warning(f"Open-Meteo failed for {city}: {e}")
        return None


def get_weather(city: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """
    Main weather function for Flask backend.
    Tries WeatherAPI first, falls back to Open-Meteo.
    """
    if not city or not isinstance(city, str):
        return None

    city = city.strip()

    # Try primary API first
    result = get_weather_api(city)
    if result:
        return result

    # Fallback to Open-Meteo
    return get_openmeteo_weather(city, lang)