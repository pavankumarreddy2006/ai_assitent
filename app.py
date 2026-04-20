import os
from flask import Flask, request, jsonify, render_template, send_from_directory

# Correct Imports
from config.config import COLLEGE_SYSTEM_PROMPT, TELUGU_SYSTEM_PROMPT, IMAGE_PATHS, VIDEO_PATH
from services.college_service import get_college_answer, get_college_context, COLLEGE_KEYWORDS
from core.router import handle_chat_request

app = Flask(__name__, template_folder="templates", static_folder="static")

# ENV
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
GNEWS_API       = os.getenv("GNEWS_API", "")
NEWS_API_KEY    = os.getenv("NEWS_API_KEY", "")
NEWS_DATA_API   = os.getenv("NEWS_DATA_API", "")

GROQ_MODEL        = "llama3-8b-8192"
OPENROUTER_MODEL  = "openai/gpt-3.5-turbo"

# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/media/<path:filename>")
def serve_media(filename):
    return send_from_directory("static/media", filename)


@app.route("/api/chat", methods=["POST"])
def chat():
    return handle_chat_request(request)


@app.route("/api/news")
def api_news():
    from services.news_service import fetch_news
    return jsonify(fetch_news())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)