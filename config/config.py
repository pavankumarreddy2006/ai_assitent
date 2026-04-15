import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_DATA_API = os.getenv("NEWS_DATA_API", "")
GNEWS_API = os.getenv("GNEWS_API", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-in-production")

GROQ_MODEL = "llama-3.1-8b-instant"
OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

COLLEGE_NAME = "Ideal College of Arts and Sciences, Kakinada"
COLLEGE_PHONE = "0884-2384382 / 0884-2384381"
COLLEGE_EMAIL = "idealcolleges@gmail.com"
COLLEGE_WEBSITE = "https://idealcollege.edu.in"
COLLEGE_LOCATION = "Vidyuth Nagar, Kakinada, Andhra Pradesh"
