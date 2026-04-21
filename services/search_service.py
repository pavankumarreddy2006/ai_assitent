# services/search_service.py
import re
import requests
from typing import List, Dict


def search_duckduckgo(query: str) -> List[Dict[str, str]]:
    if not query:
        return []
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            headers={"User-Agent": "Mozilla/5.0"},
            data={"q": query},
            timeout=12,
        )
        if resp.status_code != 200:
            return []

        html = resp.text
        link_matches = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE)
        snippet_matches = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.IGNORECASE)

        results = []
        for i, (url, title) in enumerate(link_matches[:5]):
            title_clean = re.sub("<.*?>", "", title).strip()
            snippet = snippet_matches[i].strip() if i < len(snippet_matches) else ""
            results.append({"title": title_clean, "snippet": snippet, "url": url})
        return results
    except Exception:
        return []


def search_and_format(query: str, lang: str = "en") -> str:
    results = search_duckduckgo(query)
    if not results:
        return "No web results found." if lang == "en" else "వెబ్ ఫలితాలు దొరకలేదు."

    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"{i}. {r.get('title')} - {r.get('snippet')}")
    return "\n".join(lines)