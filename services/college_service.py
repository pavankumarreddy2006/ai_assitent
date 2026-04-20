from data.college_data import COLLEGE_DATABASE, COLLEGE_CONTEXT

def get_college_answer(query: str, lang: str = "en") -> str | None:
    try:
        q = query.lower().strip()
        for section in COLLEGE_DATABASE["sections"].values():
            keywords = section.get(f"keywords_{lang}", section.get("keywords_en", []))
            if any(kw.lower() in q for kw in keywords):
                data = section["data"].get(lang, section["data"].get("en", {}))
                if isinstance(data, dict):
                    for v in data.values():
                        if v:
                            if isinstance(v, list):
                                return ", ".join(map(str, v))
                            return str(v)
                if isinstance(data, str):
                    return data
        return None
    except Exception as e:
        print(f"College service error: {e}")
        return None

def get_college_context_prompt():
    return COLLEGE_CONTEXT

def get_college_summary():
    return {
        "name": COLLEGE_DATABASE["metadata"]["college_name_en"],
        "location": COLLEGE_DATABASE["metadata"]["location"],
        "contact": "0884-2384382 / 0884-2384381",
        "email": "idealcolleges@gmail.com",
        "summary": "Ideal College of Arts and Sciences is a NAAC A Grade institution in Kakinada."
    }
    