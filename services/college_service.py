# services/college_service.py
"""
College Service Wrapper
This file imports college data and functions so that app.py and router.py can use them easily.
"""

from data.college_data import (
    COLLEGE_KEYWORDS,
    get_college_answer,
    get_college_context
)

# Exporting for compatibility with app.py and router.py
__all__ = [
    "COLLEGE_KEYWORDS",
    "get_college_answer",
    "get_college_context"
]

# Optional: Print confirmation during startup (helpful for debugging on Render)
print("✓ College Service loaded successfully from data.college_data")