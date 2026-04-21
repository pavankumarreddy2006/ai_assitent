# services/college_service.py
from data.college_data import COLLEGE_KEYWORDS, COLLEGE_DATABASE, get_college_answer as _get_answer, get_college_context as _get_context


def get_college_answer(message: str, lang: str = "en"):
    q = (message or "").lower().strip()

    if any(k in q for k in ["name of the college", "college name", "what is college name", "కళాశాల పేరు", "college ka naam"]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("college_name_te") if lang == "te" else meta.get("college_name_en")

    if any(k in q for k in ["where is college", "college location", "college address", "చిరునామా", "ఎక్కడ ఉంది"]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("location")

    return _get_answer(message, lang)


def get_college_context():
    return _get_context()


__all__ = ["COLLEGE_KEYWORDS", "get_college_answer", "get_college_context"]
