import requests
from config.config import GNEWS_API, NEWS_API_KEY


def fetch_news(query: str | None = None) -> list[dict]:
    """
    Fetch news articles. Tries GNews first, falls back to NewsAPI.
    Returns list of articles with title, description, url, source, published_at.
    """
    search_query = query or "education India"

    if GNEWS_API:
        articles = _fetch_gnews(search_query)
        if articles:
            return articles

    if NEWS_API_KEY:
        articles = _fetch_newsapi(search_query)
        if articles:
            return articles

    return []


def _fetch_gnews(query: str) -> list[dict]:
    try:
        response = requests.get(
            "https://gnews.io/api/v4/search",
            params={
                "q": query,
                "lang": "en",
                "max": 10,
                "apikey": GNEWS_API
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description"),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "published_at": a.get("publishedAt", "")
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        print(f"[GNews Error] {e}")
        return []


def _fetch_newsapi(query: str) -> list[dict]:
    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": NEWS_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description"),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "published_at": a.get("publishedAt", "")
            }
            for a in data.get("articles", [])
        ]
    except Exception as e:
        print(f"[NewsAPI Error] {e}")
        return []
