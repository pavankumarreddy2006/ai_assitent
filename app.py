# app.py
import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder="templates", 
            static_folder="static")

# Enable CORS for frontend requests
CORS(app)

# ====================== ENVIRONMENT VARIABLES ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
GNEWS_API = os.getenv("GNEWS_API", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_DATA_API = os.getenv("NEWS_DATA_API", "")

GROQ_MODEL = "llama3-8b-8192"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

# ====================== SAFE IMPORTS ======================
try:
    from config.config import COLLEGE_SYSTEM_PROMPT, TELUGU_SYSTEM_PROMPT, IMAGE_PATHS, VIDEO_PATH
    from services.college_service import get_college_answer, get_college_context, COLLEGE_KEYWORDS
    from core.router import handle_chat_request
    logger.info("✅ All core modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    # Create fallback functions to prevent total crash
    COLLEGE_SYSTEM_PROMPT = "Default college assistant prompt"
    TELUGU_SYSTEM_PROMPT = "Default Telugu prompt"
    
    def get_college_answer(*args, **kwargs):
        return "College service is currently unavailable."
    
    def get_college_context(*args, **kwargs):
        return ""
    
    COLLEGE_KEYWORDS = []
    
    def handle_chat_request(req):
        return jsonify({"error": "Chat service not available", "message": str(e)}), 503

# ====================== ROUTES ======================
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Template error: {e}")
        return "Welcome to Ideal College AI Assistant", 200


@app.route("/static/media/<path:filename>")
def serve_media(filename):
    try:
        return send_from_directory("static/media", filename)
    except FileNotFoundError:
        logger.warning(f"Media file not found: {filename}")
        return "File not found", 404


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        # FIXED: Pass request object to match function signature
        return handle_chat_request(request)
    except Exception as e:
        logger.error(f"Chat route error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": "Unable to process your request at the moment."
        }), 500


@app.route("/api/news")
def api_news():
    try:
        from services.news_service import fetch_news
        return jsonify(fetch_news())
    except ImportError:
        logger.warning("news_service not found")
        return jsonify({"error": "News service not available"}), 503
    except Exception as e:
        logger.error(f"News route error: {e}")
        return jsonify({"error": "Failed to fetch news"}), 500


# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "message": "Ideal College AI Assistant is running"
    })


# ====================== PRODUCTION ENTRY POINT ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)