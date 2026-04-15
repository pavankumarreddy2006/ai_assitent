import os
from dotenv import load_dotenv

# =====================================================
# PATH SETUP (SAFE FOR LOCAL + RENDER)
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "config", ".env")

# Load .env if exists
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # fallback (Render uses env vars directly)

# =====================================================
# HELPER FUNCTION (SAFE ENV GET)
# =====================================================

def get_env(key: str, default: str = "") -> str:
    value = os.getenv(key)
    return value if value not in (None, "", "None") else default


# =====================================================
# API KEYS
# =====================================================

GROQ_API_KEY = get_env("GROQ_API_KEY")
OPEN_ROUTER_API = get_env("OPEN_ROUTER_API")
NEWS_API_KEY = get_env("NEWS_API_KEY")
NEWS_DATA_API = get_env("NEWS_DATA_API")
GNEWS_API = get_env("GNEWS_API")

# =====================================================
# SECURITY
# =====================================================

SESSION_SECRET = get_env("SESSION_SECRET", "change-this-in-production")

# =====================================================
# AI MODELS
# =====================================================

GROQ_MODEL = get_env("GROQ_MODEL", "llama-3.1-8b-instant")
OPENROUTER_MODEL = get_env(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct:free"
)

# =====================================================
# COLLEGE INFO (STATIC CONFIG)
# =====================================================

COLLEGE_NAME = get_env(
    "COLLEGE_NAME",
    "Ideal College of Arts and Sciences, Kakinada"
)

COLLEGE_PHONE = get_env(
    "COLLEGE_PHONE",
    "0884-2384382 / 0884-2384381"
)

COLLEGE_EMAIL = get_env(
    "COLLEGE_EMAIL",
    "idealcolleges@gmail.com"
)

COLLEGE_WEBSITE = get_env(
    "COLLEGE_WEBSITE",
    "https://idealcollege.edu.in"
)

COLLEGE_LOCATION = get_env(
    "COLLEGE_LOCATION",
    "Vidyuth Nagar, Kakinada, Andhra Pradesh"
)

# =====================================================
# DEBUG / SERVER CONFIG
# =====================================================

DEBUG = get_env("DEBUG", "False").lower() == "true"

try:
    PORT = int(get_env("PORT", "10000"))
except ValueError:
    PORT = 10000


# =====================================================
# OPTIONAL LOG (DEBUG MODE ONLY)
# =====================================================

if DEBUG:
    print("⚙️ Config Loaded:")
    print(f"GROQ: {'OK' if GROQ_API_KEY else 'MISSING'}")
    print(f"NEWS API: {'OK' if NEWS_API_KEY else 'MISSING'}")
    print(f"PORT: {PORT}")