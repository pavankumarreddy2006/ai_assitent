# services/college_service.py
"""
College service compatibility layer.

Goals:
- Keep current JSON-style college_data architecture
- Preserve previous imports used across older code:
  - COLLEGE_KEYWORDS
  - get_college_answer
  - get_college_context
"""

from data.college_data import (
    COLLEGE_KEYWORDS,
    get_college_answer as _data_get_college_answer,
    get_college_context as _data_get_college_context,
)


def get_college_answer(message: str, lang: str = "en"):
    """
    Proxy to data.college_data.get_college_answer()
    """
    return _data_get_college_answer(message, lang)


def get_college_context():
    """
    Proxy to data.college_data.get_college_context()
    """
    return _data_get_college_context()


__all__ = [
    "COLLEGE_KEYWORDS",
    "get_college_answer",
    "get_college_context",
]