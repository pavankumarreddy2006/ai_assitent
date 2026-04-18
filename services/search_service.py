import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("college-ai.search")


def search_duckduckgo(query: str) -> list[dict]:
    """Scrape DuckDuckGo HTML results"""
    try:
        url = "https://html.duckduckgo.com/html/"
        response = requests.post(
            url,
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.select(".result")[:5]:
            title_tag = result.select_one(".result__title")
            link_tag = result.select_one(".result__url")
            snippet_tag = result.select_one(".result__snippet")
            if title_tag and link_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                    "url": link_tag.get("href")
                })
        return results
    except Exception as e:
        logger.exception("Search error: %s", e)
        return []


def format_search_results(results: list[dict]) -> str:
    """Convert search results into readable text"""
    if not results:
        return "I couldn't find relevant information."
    output = []
    for i, r in enumerate(results[:5], 1):
        snippet = r.get("snippet", "")
        output.append(f"{i}. {snippet}")
    return "\n\n".join(output)


def extract_page_content(url: str) -> str:
    """Extract main text from webpage"""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8
        )
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:5])
        return text.strip()
    except Exception as e:
        logger.exception("Scrape error: %s", e)
        return ""


def smart_search_answer(query: str) -> str:
    """Combine search + scraping for better answers"""
    results = search_duckduckgo(query)
    if not results:
        return "I couldn't find useful information."
    final_answer = ""
    for r in results[:3]:
        content = extract_page_content(r["url"])
        if content:
            final_answer += content + "\n\n"
    if not final_answer:
        return format_search_results(results)
    return final_answer[:1500]
