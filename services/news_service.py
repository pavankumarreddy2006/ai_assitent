# services/news_service.py
import os
import requests
from typing import List, Dict, Tuple

GNEWS_API = os.getenv("GNEWS_API", "")
NEWS_DATA_API = os.getenv("NEWS_DATA_API", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")


def _from_gnews(query: str) -> List[Dict]:
    if not GNEWS_API:
        return []
    url = "https://gnews.io/api/v4/search"
    r = requests.get(url, params={"q": query, "lang": "en", "max": 10, "apikey": GNEWS_API}, timeout=12)
    if r.status_code != 200:
        return []
    return [{
        "title": a.get("title", ""),
        "source": a.get("source", {}).get("name", "GNews"),
    } for a in r.json().get("articles", []) if a.get("title")]


def _from_newsdata(query: str) -> List[Dict]:
    if not NEWS_DATA_API:
        return []
    url = "https://newsdata.io/api/1/news"
    r = requests.get(url, params={"q": query, "language": "en", "apikey": NEWS_DATA_API}, timeout=12)
    if r.status_code != 200:
        return []
    return [{
        "title": a.get("title", ""),
        "source": a.get("source_id", "NewsData"),
    } for a in r.json().get("results", []) if a.get("title")][:10]


def _from_newsapi(query: str) -> List[Dict]:
    if not NEWS_API_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    r = requests.get(url, params={"q": query, "sortBy": "publishedAt", "pageSize": 10, "apiKey": NEWS_API_KEY}, timeout=12)
    if r.status_code != 200:
        return []
    return [{
        "title": a.get("title", ""),
        "source": a.get("source", {}).get("name", "NewsAPI"),
    } for a in r.json().get("articles", []) if a.get("title")]


def fetch_news(query: str = "latest india education news") -> Tuple[List[Dict], str]:
    q = (query or "").strip() or "latest india education news"

    data = _from_gnews(q)
    if data:
        return data, "GNEWS"

    data = _from_newsdata(q)
    if data:
        return data, "NEWSDATA"

    data = _from_newsapi(q)
    if data:
        return data, "NEWSAPI"

    return [], "NONE"


def summarize_news(articles: List[Dict], lang: str = "en") -> str:
    if not articles:
        return "No news available now." if lang == "en" else "ఇప్పుడు వార్తలు అందుబాటులో లేవు."

    lines = []
    for idx, a in enumerate(articles[:5], start=1):
        lines.append(f"{idx}. {a.get('title')} (Source: {a.get('source')})")

    if lang == "te":
        return "తాజా అప్డేట్స్:\n" + "\n".join(lines)
    return "Latest updates:\n" + "\n".join(lines)