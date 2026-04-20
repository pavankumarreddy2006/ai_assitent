import os
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Load API keys from environment variables
GNEWS_API = os.getenv("GNEWS_API")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_DATA_API = os.getenv("NEWS_DATA_API")


def fetch_gnews(query: str) -> List[Dict[str, Any]]:
    """Fetch news from GNews.io"""
    if not GNEWS_API:
        return []

    try:
        url = f"https://gnews.io/api/v4/search?q={requests.utils.quote(query)}&lang=en&max=10&apikey={GNEWS_API}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        articles = data.get("articles", [])

        return [
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", "")
            }
            for article in articles if article.get("title")
        ]
    except Exception as e:
        logger.warning(f"GNews API failed for query '{query}': {e}")
        return []


def fetch_newsdata(query: str) -> List[Dict[str, Any]]:
    """Fetch news from NewsData.io"""
    if not NEWS_DATA_API:
        return []

    try:
        url = f"https://newsdata.io/api/1/news?q={requests.utils.quote(query)}&language=en&apikey={NEWS_DATA_API}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        results = data.get("results", [])

        return [
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("link", ""),
                "source": article.get("source_id", "Unknown"),
                "published_at": article.get("pubDate", "")
            }
            for article in results[:10] if article.get("title")
        ]
    except Exception as e:
        logger.warning(f"NewsData API failed for query '{query}': {e}")
        return []


def fetch_newsapi(query: str) -> List[Dict[str, Any]]:
    """Fetch news from NewsAPI.org"""
    if not NEWS_API_KEY:
        return []

    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={requests.utils.quote(query)}&"
            f"sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()
        articles = data.get("articles", [])

        return [
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", "")
            }
            for article in articles if article.get("title")
        ]
    except Exception as e:
        logger.warning(f"NewsAPI.org failed for query '{query}': {e}")
        return []


def fetch_news(query: str = "latest India education news") -> List[Dict[str, Any]]:
    """
    Main function to fetch news with fallback between multiple providers.
    Tries GNews → NewsData → NewsAPI in order.
    Returns list of articles from the first successful provider.
    """
    if not query or not isinstance(query, str):
        query = "latest India education news"
    else:
        query = query.strip()

    providers = [
        ("gnews", fetch_gnews),
        ("newsdata", fetch_newsdata),
        ("newsapi", fetch_newsapi),
    ]

    for name, fetch_func in providers:
        try:
            articles = fetch_func(query)
            if articles and len(articles) > 0:
                logger.info(f"News successfully fetched from {name} for query: {query}")
                return articles
        except Exception as e:
            logger.warning(f"{name} provider failed for query '{query}': {e}")

    logger.warning(f"All news providers failed for query: {query}")
    return []


# Optional helper function to format news for AI prompts
def format_news_for_ai(articles: List[Dict[str, Any]], max_items: int = 5) -> str:
    """Format news articles into a readable string for AI system prompt"""
    if not articles:
        return "No recent news available at the moment."

    formatted = []
    for article in articles[:max_items]:
        title = article.get("title", "").strip()
        source = article.get("source", "Unknown")
        published = article.get("published_at", "")[:10]  # YYYY-MM-DD
        desc = article.get("description", "") or ""

        line = f"• {title}"
        if source and source != "Unknown":
            line += f" (Source: {source})"
        if published:
            line += f" - {published}"
        if desc:
            line += f"\n  {desc[:150]}{'...' if len(desc) > 150 else ''}"

        formatted.append(line)

    return "Latest News:\n" + "\n\n".join(formatted)