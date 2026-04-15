# =====================================================
# COLLEGE SERVICE — FINAL IMPROVED VERSION (ERROR-FREE)
# Ideal College of Arts and Sciences, Kakinada
# =====================================================

from data.college_data import college_info_en, college_info_te, COLLEGE_CONTEXT


def get_college_answer(query: str, lang: str = "en") -> str | None:
    """
    Smart keyword matching against college database.
    Supports English + Telugu.
    Multi-strategy matching for best accuracy.
    """

    try:
        if not query:
            return None

        query_clean = query.strip()
        query_lower = query_clean.lower()

        # Normalize words
        query_words = set(
            query_lower.replace("?", "")
                       .replace(".", "")
                       .replace(",", "")
                       .split()
        )

        # Detect Telugu automatically
        if _is_telugu(query_clean):
            lang = "te"

        data = college_info_te if lang == "te" else college_info_en

        # =====================================================
        # ✅ STRATEGY 1: Exact key match
        # =====================================================
        for key, value in data.items():
            if key.lower() in query_lower:
                return value

        # =====================================================
        # ✅ STRATEGY 2: Strong word match (score based)
        # =====================================================
        best_match = None
        best_score = 0.0

        for key, value in data.items():
            key_words = set(key.lower().split())

            if not key_words:
                continue

            common_words = key_words & query_words
            score = len(common_words) / len(key_words)

            if score > best_score and score >= 0.6:
                best_score = score
                best_match = value

        if best_match:
            return best_match

        # =====================================================
        # ✅ STRATEGY 3: Partial match (fallback)
        # =====================================================
        for key, value in data.items():
            key_lower = key.lower()

            for word in query_words:
                if len(word) >= 3 and word in key_lower:
                    return value

        # =====================================================
        # ❌ No match → let AI handle
        # =====================================================
        return None

    except Exception as e:
        print(f"[College Service Error] {e}")
        return None


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def _is_telugu(text: str) -> bool:
    """Return True if text contains Telugu Unicode characters."""
    try:
        return any('\u0C00' <= ch <= '\u0C7F' for ch in text)
    except:
        return False


# =====================================================
# COLLEGE SUMMARY (UI PANEL)
# =====================================================

def get_college_summary() -> dict:
    return {
        "name": "Ideal College of Arts and Sciences",
        "location": "Vidyuth Nagar, Kakinada, Andhra Pradesh",
        "contact": "0884-2384382 / 0884-2384381",
        "email": "idealcolleges@gmail.com",
        "website": "https://idealcollege.edu.in",
        "accreditation": "NAAC A Grade",
        "principal": "Dr. T. Satyanarayana",
        "timings": "9:30 AM – 3:45 PM (Mon–Sat)",

        "courses": [
            "B.Sc Computers",
            "BCA",
            "B.Sc AI",
            "BBA",
            "B.Sc Agriculture",
            "Food Technology",
            "Aqua & Fisheries",
            "MCA",
            "M.Sc Organic Chemistry",
            "M.Sc Food Science"
        ],

        "facilities": [
            "Library",
            "Computer Labs",
            "Science Labs",
            "Hostel",
            "Bus Facility",
            "Wi-Fi",
            "Cafeteria",
            "Playground",
            "CCTV Security",
            "Auditorium",
            "Placements"
        ]
    }


# =====================================================
# ✅ CONTEXT FOR AI (VERY IMPORTANT)
# =====================================================

def get_college_context_prompt() -> str:
    """
    Returns full college data for AI usage.
    Ensures no crash even if data issue happens.
    """
    try:
        return COLLEGE_CONTEXT
    except Exception as e:
        print(f"[Context Error] {e}")
        return "College data not available."