# services/college_service.py
"""
Compatibility + enhancement layer for college data access.
"""

from data.college_data import (
    COLLEGE_KEYWORDS,
    COLLEGE_DATABASE,
    get_college_answer as _data_get_college_answer,
    get_college_context as _data_get_college_context,
)


def get_college_answer(message: str, lang: str = "en"):
    q = (message or "").lower().strip()

    # Handle common direct metadata questions first
    if any(k in q for k in ["name of the college", "college name", "what is college name", "కళాశాల పేరు"]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("college_name_te") if lang == "te" else meta.get("college_name_en")

    if any(k in q for k in ["where is college", "college location", "address", "చిరునామా", "ఎక్కడ ఉంది"]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("location")

    # Fallback to existing JSON section matcher
    return _data_get_college_answer(message, lang)


def get_college_context():
    return _data_get_college_context()


__all__ = [
    "COLLEGE_KEYWORDS",
    "get_college_answer",
    "get_college_context",
]