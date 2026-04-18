import logging
from datetime import date

import requests

from config.config import GNEWS_API, NEWS_API_KEY, NEWS_DATA_API
from services.llm_service import query_groq, query_openrouter

logger = logging.getLogger("college-ai.news")
_LAST_PRIMARY_RESET = date.today()


def fetch_news(query: str | None = None) -> list[dict]:
    """
    Fetch news articles. Tries GNews first, falls back to NewsAPI.
    Returns list of articles with title, description, url, source, published_at.
    """
    global _LAST_PRIMARY_RESET
    if _LAST_PRIMARY_RESET != date.today():
        _LAST_PRIMARY_RESET = date.today()

    search_query = query or "latest India education"
    providers = [
        ("gnews", _fetch_gnews, bool(GNEWS_API)),
        ("newsdata", _fetch_newsdata, bool(NEWS_DATA_API)),
        ("newsapi", _fetch_newsapi, bool(NEWS_API_KEY)),
    ]

    selected: list[dict] = []
    for provider_name, provider_fn, enabled in providers:
        if not enabled:
            continue
        try:
            selected = provider_fn(search_query)
            if selected:
                logger.info("News fetched from %s", provider_name)
                break
        except Exception:
            logger.exception("News provider failed: %s", provider_name)

    if not selected:
        return []
    return _summarize_news(selected, search_query)


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
        logger.warning("GNews error: %s", e)
        return []


def _fetch_newsdata(query: str) -> list[dict]:
    try:
        response = requests.get(
            "https://newsdata.io/api/1/news",
            params={
                "q": query,
                "language": "en",
                "apikey": NEWS_DATA_API,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return [
            {
                "title": a.get("title", ""),
                "description": a.get("description"),
                "url": a.get("link", ""),
                "source": a.get("source_id", "Unknown"),
                "published_at": a.get("pubDate", ""),
            }
            for a in data.get("results", [])[:10]
            if a.get("title")
        ]
    except Exception as e:
        logger.warning("NewsData error: %s", e)
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
        logger.warning("NewsAPI error: %s", e)
        return []


def _summarize_news(articles: list[dict], query: str) -> list[dict]:
    top = articles[:5]
    bullets = [f"- {a.get('title', '')}" for a in top if a.get("title")]
    if not bullets:
        return top

    prompt = (
        "Summarize these headlines in 1 short sentence for a college assistant user. "
        f"Query: {query}\n\nHeadlines:\n" + "\n".join(bullets)
    )
    summary = None
    try:
        summary = query_groq(prompt, history=[], lang="en")
    except Exception:
        try:
            summary = query_openrouter(prompt, history=[], lang="en")
        except Exception:
            summary = None

    if summary:
        top[0]["summary"] = summary.strip()
    return top
