# services/search_service.py
import re
import requests
from typing import List, Dict


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#039;", "'", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def search_duckduckgo(query: str) -> List[Dict[str, str]]:
    if not query:
        return []
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            },
            data={"q": query, "kl": "in-en"},
            timeout=15,
        )
        if resp.status_code != 200:
            return []

        html = resp.text
        results = []

        result_blocks = re.findall(
            r'<div[^>]+class="[^"]*result[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            html, re.DOTALL | re.IGNORECASE
        )

        for block in result_blocks[:6]:
            title_m = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL)
            snippet_m = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL)

            title = _clean_html(title_m.group(1)) if title_m else ""
            snippet = _clean_html(snippet_m.group(1)) if snippet_m else ""

            if title and len(title) > 3:
                results.append({"title": title, "snippet": snippet})

        if not results:
            title_matches = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
            snippet_matches = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
            for i, t in enumerate(title_matches[:5]):
                title = _clean_html(t)
                snippet = _clean_html(snippet_matches[i]) if i < len(snippet_matches) else ""
                if title and len(title) > 3:
                    results.append({"title": title, "snippet": snippet})

        return results
    except Exception:
        return []


def search_and_format(query: str, lang: str = "en") -> str:
    results = search_duckduckgo(query)
    if not results:
        return "వెబ్ ఫలితాలు దొరకలేదు." if lang == "te" else "No results found. Please try a different search query."

    lines = []
    for i, r in enumerate(results[:4], 1):
        title = r.get("title", "").strip()
        snippet = r.get("snippet", "").strip()
        if snippet:
            lines.append(f"{i}. **{title}**\n   {snippet}")
        elif title:
            lines.append(f"{i}. {title}")

    return "\n\n".join(lines) if lines else ("No relevant results found." if lang == "en" else "సంబంధిత ఫలితాలు దొరకలేదు.")
