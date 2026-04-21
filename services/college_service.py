# services/college_service.py

from data.college_data import (
    COLLEGE_KEYWORDS,
    COLLEGE_DATABASE,
    get_college_answer as _get_answer,
    get_college_context as _get_context
)


def get_college_answer(message: str, lang: str = "en"):
    q = (message or "").lower().strip()

    meta = COLLEGE_DATABASE.get("metadata", {})

    # 🎯 BASIC INFO
    if any(k in q for k in ["college name", "name of the college", "కళాశాల పేరు"]):
        return meta.get("college_name_te") if lang == "te" else meta.get("college_name_en")

    if any(k in q for k in ["location", "address", "ఎక్కడ ఉంది"]):
        return meta.get("location")

    if "about" in q:
        return meta.get("about")

    if "contact" in q or "phone" in q:
        return meta.get("contact")

    if "timing" in q or "working hours" in q:
        return meta.get("timings")

    if "naac" in q or "grade" in q:
        return meta.get("naac")

    # 🎯 MAIN DATA FETCH
    result = _get_answer(message, lang)

    if result is None:
        return None

    # 🎯 SMART FILTERING
    if isinstance(result, dict):

        # Principal
        if "principal" in q:
            if "principal" in result:
                return str(result["principal"])

        # HOD
        if "hod" in q or "head" in q:
            if "hod" in result:
                return str(result["hod"])

        # Courses
        if "course" in q:
            if isinstance(result, list):
                return ", ".join(map(str, result))

        # Fees
        if "fee" in q:
            if "fees" in result:
                return str(result["fees"])

        # Scholarship
        if "scholarship" in q:
            if "scholarship" in result:
                return str(result["scholarship"])

        # Hostel
        if "hostel" in q:
            if "hostel" in result:
                return str(result["hostel"])

        # Library
        if "library" in q:
            if "library" in result:
                return str(result["library"])

        # Placement
        if "placement" in q:
            if "placement" in result:
                return str(result["placement"])

        # Facilities
        if "facility" in q:
            if "facilities" in result:
                if isinstance(result["facilities"], list):
                    return ", ".join(result["facilities"])
                return str(result["facilities"])

        # Departments
        if "department" in q:
            if isinstance(result, dict):
                return ", ".join(result.keys())

        # Faculty
        if "faculty" in q or "staff" in q:
            faculty = result.get("faculty")
            if isinstance(faculty, list):
                return ", ".join(
                    f.get("name", "") for f in faculty if isinstance(f, dict)
                )

        # Exams
        if "exam" in q:
            if "exams" in result:
                return str(result["exams"])

        # Extracurricular
        if "extra" in q or "activity" in q:
            if "extracurricular" in result:
                return str(result["extracurricular"])

        # Transport
        if "transport" in q or "bus" in q:
            if "transport" in result:
                return str(result["transport"])

        # Internship
        if "internship" in q:
            if "internship" in result:
                return str(result["internship"])

        # Admission
        if "admission" in q:
            if "admission" in result:
                return str(result["admission"])

        # 👉 FINAL CLEAN FALLBACK (NO JSON DUMP)
        values = []
        for v in result.values():
            if isinstance(v, list):
                values.extend(map(str, v))
            elif isinstance(v, dict):
                continue
            elif v:
                values.append(str(v))
        return ", ".join(values)

    # LIST
    if isinstance(result, list):
        return ", ".join(map(str, result))

    return str(result)


def get_college_context():
    return _get_context()


__all__ = ["COLLEGE_KEYWORDS", "get_college_answer", "get_college_context"]