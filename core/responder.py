def format_college_response(answer: str, source: str = "College Database") -> dict:
    return {
        "reply": answer,
        "intent": "college",
        "source": source,
        "show_video": True,
        "video_url": None
    }


def format_weather_response(weather_data: dict | None, city: str, lang: str = "en") -> dict:
    if weather_data:
        if lang == "te":
            reply = (
                f"{weather_data['city']}లో వాతావరణం: {weather_data['description']}, "
                f"ఉష్ణోగ్రత: {weather_data['temperature']}°C, "
                f"తేమ: {weather_data['humidity']}%, "
                f"గాలి వేగం: {weather_data['wind_speed']} km/h."
            )
        else:
            reply = (
                f"Weather in {weather_data['city']}: {weather_data['description']}, "
                f"Temperature: {weather_data['temperature']}°C, "
                f"Humidity: {weather_data['humidity']}%, "
                f"Wind: {weather_data['wind_speed']} km/h."
            )
        source = "Open-Meteo Weather API"
    else:
        if lang == "te":
            reply = f"'{city}' వాతావరణ సమాచారం దొరకలేదు. నగరం పేరు తనిఖీ చేయండి."
        else:
            reply = f"I couldn't find weather data for '{city}'. Please check the city name."
        source = "Weather Service"

    return {
        "reply": reply,
        "intent": "weather",
        "source": source,
        "show_video": False,
        "video_url": None
    }


def format_news_response(articles: list, lang: str = "en") -> dict:
    if articles:
        if lang == "te":
            lines = ["తాజా వార్తలు:\n"]
            for i, article in enumerate(articles[:5], 1):
                lines.append(f"{i}. {article['title']} — {article['source']}")
        else:
            lines = ["Here are the latest headlines:\n"]
            for i, article in enumerate(articles[:5], 1):
                lines.append(f"{i}. {article['title']} — {article['source']}")
        reply = "\n".join(lines)
        source = "News API"
    else:
        if lang == "te":
            reply = "ప్రస్తుతం వార్తలు తీసుకోలేకపోయాము. తర్వాత మళ్ళీ ప్రయత్నించండి."
        else:
            reply = "I couldn't fetch the latest news right now. Please try again later."
        source = "News Service"

    return {
        "reply": reply,
        "intent": "news",
        "source": source,
        "show_video": False,
        "video_url": None
    }


def format_search_response(answer: str, source: str = "Live Web (DuckDuckGo)") -> dict:
    return {
        "reply": answer,
        "intent": "search",
        "source": source,
        "show_video": False,
        "video_url": None
    }


def format_general_response(answer: str, source: str = "Groq AI") -> dict:
    return {
        "reply": answer,
        "intent": "general",
        "source": source,
        "show_video": False,
        "video_url": None
    }


def format_error_response(message: str = "Something went wrong. Please try again.") -> dict:
    return {
        "reply": message,
        "intent": "general",
        "source": "Error",
        "show_video": False,
        "video_url": None
    }
