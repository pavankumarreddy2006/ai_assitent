import os
from dotenv import load_dotenv

# =====================================================
# Load .env file (SAFE PATH)
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "config", ".env")

load_dotenv(ENV_PATH)

# =====================================================
# API KEYS
# =====================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_DATA_API = os.getenv("NEWS_DATA_API", "")
GNEWS_API = os.getenv("GNEWS_API", "")

# =====================================================
# SECURITY
# =====================================================

SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-in-production")

# =====================================================
# AI MODELS
# =====================================================

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct:free"
)

# =====================================================
# COLLEGE INFO (STATIC CONFIG)
# =====================================================

COLLEGE_NAME = os.getenv(
    "COLLEGE_NAME",
    "Ideal College of Arts and Sciences, Kakinada"
)

COLLEGE_PHONE = os.getenv(
    "COLLEGE_PHONE",
    "0884-2384382 / 0884-2384381"
)

COLLEGE_EMAIL = os.getenv(
    "COLLEGE_EMAIL",
    "idealcolleges@gmail.com"
)

COLLEGE_WEBSITE = os.getenv(
    "COLLEGE_WEBSITE",
    "https://idealcollege.edu.in"
)

COLLEGE_LOCATION = os.getenv(
    "COLLEGE_LOCATION",
    "Vidyuth Nagar, Kakinada, Andhra Pradesh"
)

# =====================================================
# DEBUG (OPTIONAL)
# =====================================================

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 10000))