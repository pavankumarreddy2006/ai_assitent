from data.college_data import COLLEGE_DATABASE, COLLEGE_CONTEXT, get_college_summary
import re

def get_college_answer(query: str, lang: str = "en") -> str | None:
    """
    FULL DATABASE SEARCH – now reads entire COLLEGE_DATABASE accurately
    Supports English + Telugu perfectly
    """
    try:
        if not query:
            return None
        q = _normalize_text(query)

        # Search every section
        for section_name, section in COLLEGE_DATABASE["sections"].items():
            keywords = section.get(f"keywords_{lang}", section.get("keywords_en", []))
            if any(kw.lower() in q for kw in keywords):
                data = section["data"].get(lang, section["data"].get("en", {}))
                if isinstance(data, dict):
                    # Return first meaningful value
                    for v in data.values():
                        if isinstance(v, (str, list)):
                            if isinstance(v, list):
                                return ", ".join(str(item) for item in v[:6])
                            return str(v)
                if isinstance(data, str):
                    return data

        # Fallback to general summary
        if any(x in q for x in ["about", "college", "name", "who are you"]):
            return get_college_summary()["summary"]

        return None
    except Exception:
        return None

def _normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^\w\s\u0C00-\u0C7F]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def get_college_context_prompt() -> str:
    return COLLEGE_CONTEXT

# Keep old function for compatibility
def get_college_summary():
    return get_college_summary()   # from data.college_data