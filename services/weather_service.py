import requests
from config.config import WEATHER_API_KEY

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}

WEATHER_CODES_TE = {
    0: "ఆకాశం స్వచ్ఛంగా ఉంది", 1: "ప్రధానంగా స్వచ్ఛంగా", 2: "పాక్షికంగా మేఘావృతం", 3: "పూర్తిగా మేఘావృతం",
    45: "మంచు పొర", 48: "మంచు పొర",
    51: "తేలికపాటి జల్లు", 53: "మితమైన జల్లు", 55: "దట్టమైన జల్లు",
    61: "తేలికపాటి వర్షం", 63: "మితమైన వర్షం", 65: "భారీ వర్షం",
    80: "వర్షపు జల్లులు", 81: "మితమైన వర్షపు జల్లులు", 82: "భారీ వర్షపు జల్లులు",
    95: "పిడుగుపాటు వర్షం", 96: "వడగళ్ళతో పిడుగుపాటు", 99: "తీవ్రమైన పిడుగుపాటు",
}


def get_weather(city: str, lang: str = "en") -> dict | None:
    """
    Get current weather for any city using Open-Meteo (free, no API key).
    Returns dict with city, temperature, description, humidity, wind_speed or None.
    """
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        results = geo_data.get("results")
        if not results:
            return None

        loc = results[0]
        lat, lon, name = loc["latitude"], loc["longitude"], loc["name"]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            },
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current", {})
        code = current.get("weather_code", 0)

        description = WEATHER_CODES_TE.get(code, "తెలియదు") if lang == "te" else WEATHER_CODES.get(code, "Unknown")

        return {
            "city": name,
            "temperature": current.get("temperature_2m", 0),
            "description": description,
            "humidity": current.get("relative_humidity_2m", 0),
            "wind_speed": current.get("wind_speed_10m", 0),
        }

    except Exception as e:
        print(f"[Weather Error] {e}")
        return None
