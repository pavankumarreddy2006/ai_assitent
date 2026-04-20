"""
Ideal College AI - Flask App (Fixed for Render Deployment)
"""
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from core.router import route_message
from services.college_service import get_college_summary
from services.media_service import get_college_images, get_college_video
from services.news_service import fetch_news

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ideal-ai.api")

app = Flask(__name__, 
            template_folder="templates", 
            static_folder="static", 
            static_url_path="/static")

CORS(app, resources={r"/*": {"origins": "*"}})

# ====================== MAIN ROUTE (This was missing!) ======================
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    """Serve the frontend"""
    return render_template("index.html")

# ====================== API ROUTES ======================
@app.route("/api/chat", methods=["POST"])
@app.route("/assistant-api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        history = data.get("conversationHistory", [])

        if not message:
            return jsonify({"error": "Message is required"}), 400

        response = route_message(message, history)
        return jsonify(response)

    except Exception as e:
        logger.exception("Chat error")
        return jsonify({
            "reply": "Sorry, something went wrong. Please try again.",
            "intent": "general"
        }), 500

@app.route("/api/college-info")
def college_info():
    return jsonify(get_college_summary())

@app.route("/api/news")
def news():
    query = request.args.get("query", "education India")
    return jsonify({"articles": fetch_news(query)})

@app.route("/api/media/images")
def media_images():
    return jsonify(get_college_images())

@app.route("/api/media/video")
def media_video():
    return jsonify({"video_url": get_college_video()})

@app.route("/api/healthz")
def health():
    return jsonify({"status": "ok"})

# Serve static files explicitly (helps on Render)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)