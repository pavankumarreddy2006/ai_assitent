# =====================================================
# COLLEGE SERVICE — IMPROVED (SMART MATCHING)
# Ideal College of Arts and Sciences, Kakinada
# =====================================================

from data.college_data import college_info_en, college_info_te, COLLEGE_CONTEXT


def get_college_answer(query: str, lang: str = "en") -> str | None:
    """
    Smart keyword matching against college database.
    Tries multiple matching strategies before returning None.
    
    Returns: Answer string if matched, else None (AI will handle it).
    """
    try:
        query_lower = query.lower().strip()
        query_words = set(query_lower.replace("?", "").replace(".", "").split())

        # Auto-detect Telugu query
        if _is_telugu(query):
            lang = "te"

        data = college_info_te if lang == "te" else college_info_en

        # ── Strategy 1: Exact key match ────────────────────────────
        for key, value in data.items():
            if key.lower() in query_lower:
                return value

        # ── Strategy 2: All words of a key appear in query ─────────
        # e.g. query="what is the fee for bsc computers" matches key="bsc computers fee"
        best_match = None
        best_score = 0

        for key, value in data.items():
            key_words = set(key.lower().split())
            common = key_words & query_words
            score = len(common) / max(len(key_words), 1)

            if score > best_score and score >= 0.6:
                best_score = score
                best_match = value

        if best_match:
            return best_match

        # ── Strategy 3: Any single word of query matches a key ──────
        for key, value in data.items():
            key_lower = key.lower()
            for word in query_words:
                if len(word) >= 4 and word in key_lower:
                    return value

        return None

    except Exception as e:
        print(f"[College Service Error] {e}")
        return None


def _is_telugu(text: str) -> bool:
    """Return True if text contains Telugu Unicode characters."""
    return any('\u0C00' <= ch <= '\u0C7F' for ch in text)


def get_college_summary() -> dict:
    """
    Returns structured college summary for the sidebar info panel.
    """
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


def get_college_context_prompt() -> str:
    """
    Returns the full college context for AI system prompt.
    Used when database match is not found — AI answers using this context.
    """
    return COLLEGE_CONTEXT
