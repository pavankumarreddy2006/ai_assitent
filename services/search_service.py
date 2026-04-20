import os
import re
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def search_duckduckgo(query: str) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo HTML version and return up to 5 results.
    Returns list of dictionaries: [{"title": , "snippet": , "url": }]
    """
    if not query or not isinstance(query, str):
        return []

    query = query.strip()
    results: List[Dict[str, str]] = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"q": query}

        response = requests.post(
            "https://html.duckduckgo.com/html/",
            headers=headers,
            data=data,
            timeout=10
        )

        if response.status_code != 200:
            logger.warning(f"DuckDuckGo search returned status {response.status_code}")
            return []

        html = response.text

        # Extract result links (title + url)
        result_pattern = r'<a[^>]+class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>'
        result_matches = re.findall(result_pattern, html, re.IGNORECASE)

        # Extract snippets
        snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]*)<\/a>'
        snippet_matches = re.findall(snippet_pattern, html, re.IGNORECASE)

        # Combine results
        for i, (url, title) in enumerate(result_matches):
            if len(results) >= 5:
                break

            snippet = snippet_matches[i].strip() if i < len(snippet_matches) else ""

            results.append({
                "title": title.strip(),
                "snippet": snippet,
                "url": url
            })

        return results

    except requests.exceptions.RequestException as e:
        logger.warning(f"DuckDuckGo search request failed for '{query}': {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in DuckDuckGo search for '{query}': {e}")
        return []


def format_search_results(results: List[Dict[str, str]]) -> str:
    """
    Format search results into a readable string for AI prompt or response.
    """
    if not results:
        return "I couldn't find any relevant information from the web."

    formatted = []
    for i, result in enumerate(results[:5], 1):
        text = result.get("snippet") or result.get("title") or "No description available"
        formatted.append(f"{i}. {text.strip()}")

    return "\n\n".join(formatted)


# Optional: Combined helper function
def search_and_format(query: str) -> str:
    """Convenience function: Search and return formatted string"""
    results = search_duckduckgo(query)
    return format_search_results(results)