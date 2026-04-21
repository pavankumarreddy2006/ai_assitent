# services/college_service.py

from data.college_data import (
    COLLEGE_KEYWORDS,
    COLLEGE_DATABASE,
    get_college_answer as _get_answer,
    get_college_context as _get_context
)


def get_college_answer(message: str, lang: str = "en"):
    q = (message or "").lower().strip()

    # College Name
    if any(k in q for k in [
        "name of the college", "college name", "what is college name",
        "కళాశాల పేరు", "college ka naam"
    ]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("college_name_te") if lang == "te" else meta.get("college_name_en")

    # Location
    if any(k in q for k in [
        "where is college", "college location", "college address",
        "చిరునామా", "ఎక్కడ ఉంది"
    ]):
        meta = COLLEGE_DATABASE.get("metadata", {})
        return meta.get("location")

    # 🔥 MAIN FIX HERE
    result = _get_answer(message, lang)

    # ✅ convert everything to string
    if isinstance(result, dict):
        values = []
        for v in result.values():
            if isinstance(v, list):
                values.extend(map(str, v))
            elif v:
                values.append(str(v))
        return ", ".join(values)

    if isinstance(result, list):
        return ", ".join(map(str, result))

    if result is None:
        return None

    return str(result)


def get_college_context():
    return _get_context()


__all__ = ["COLLEGE_KEYWORDS", "get_college_answer", "get_college_context"]