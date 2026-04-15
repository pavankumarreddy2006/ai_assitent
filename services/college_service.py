# =====================================================
# FINAL WORKING COLLEGE SERVICE (NO ERROR)
# =====================================================

from data.college_data import college_info_en, college_info_te


def get_college_answer(query: str, lang: str = "en") -> str:
    """
    Returns answer from college database
    """

    try:
        query = query.lower().strip()

        # select language
        data = college_info_te if lang == "te" else college_info_en

        # match keyword
        for key, value in data.items():
            if key.lower() in query:
                return value

        return None

    except Exception as e:
        print(f"[College Error] {e}")
        return None


# ✅ REQUIRED FOR app.py
def get_college_summary():
    return {
        "name": "Ideal College of Arts and Sciences",
        "location": "Kakinada",
        "contact": "0884-2384382",
        "website": "https://idealcollege.edu.in",
        "courses": [
            "BSc Computers", "BCA", "BSc AI",
            "BBA", "Agriculture", "Food Technology"
        ],
        "facilities": [
            "Library", "Labs", "Hostel",
            "Placements", "WiFi", "Transport"
        ]
    }