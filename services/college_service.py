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

        query_words = set(
            query_lower.replace("?", "")
                       .replace(".", "")
                       .replace(",", "")
                       .split()
        )

        if _is_telugu(query_clean):
            lang = "te"

        data = college_info_te if lang == "te" else college_info_en

        # Prefer the LONGEST matching key (more specific wins over shorter match)
        exact_matches = [
            (key, value) for key, value in data.items()
            if key.lower() in query_lower
        ]
        if exact_matches:
            best_key, best_val = max(exact_matches, key=lambda x: len(x[0]))
            return best_val

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

        for key, value in data.items():
            key_lower = key.lower()
            for word in query_words:
                if len(word) >= 3 and word in key_lower:
                    return value

        return None

    except Exception as e:
        print(f"[College Service Error] {e}")
        return None


def _is_telugu(text: str) -> bool:
    try:
        return any('\u0C00' <= ch <= '\u0C7F' for ch in text)
    except Exception:
        return False

from data.college_data import college_info_en, college_info_te

def get_college_summary() -> dict:
    return {
        "name": "Ideal College of Arts and Sciences",
        "location": "Vidyuth Nagar, Kakinada, Andhra Pradesh",
        "contact": "0884-2384382 / 0884-2384381",
        "email": "idealcolleges@gmail.com",
        "website": "https://idealcollege.edu.in",
        "accreditation": "NAAC A Grade",
        "principal": "Dr. T. Satyanarayana",
        "timings": "9:30 AM - 3:45 PM (Mon-Sat)",
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


def get_college_context_prompt() -> str:
    try:
        return COLLEGE_CONTEXT
    except Exception as e:
        print(f"[Context Error] {e}")
        return "College data not available."
