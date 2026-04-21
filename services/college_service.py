# services/college_service.py
from data.college_data import FAQS, KEYWORDS


def get_college_answer(message: str, lang: str = "en"):
    msg = (message or "").lower()

    for key, kws in KEYWORDS.items():
        if any(kw in msg for kw in kws):
            val = FAQS.get(key, {})
            return val.get(lang) or val.get("en")
    return None