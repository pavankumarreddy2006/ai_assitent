"""
Flask entrypoint for IDEAL AI College Assistant.
Run locally: python app.py
"""

import logging
from typing import Any

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from core.router import route_message
from services.college_service import get_college_summary
from services.media_service import get_college_images, get_college_video
from services.news_service import fetch_news

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ideal-ai.api")

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})


class ChatRequest:
    def __init__(self, data: dict):
        self.message = data.get("message", "").strip()
        self.conversationHistory = data.get("conversationHistory", [])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
@app.route("/assistant-api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        payload = ChatRequest(data)
        message = payload.message

        if not message:
            return jsonify({"error": "Message is required"}), 400

        history = payload.conversationHistory if isinstance(payload.conversationHistory, list) else []

        response = route_message(message, history)
        if not isinstance(response, dict):
            raise ValueError("Invalid router response")

        return jsonify(response)

    except Exception:
        logger.exception("Unhandled chat error")
        return jsonify({
            "reply": "Sorry, something went wrong. Please try again.",
            "intent": "general",
            "show_images": False,
            "images": [],
            "show_video": False,
            "video_url": None,
        }), 500


@app.route("/api/college-info")
@app.route("/assistant-api/college-info")
def college_info():
    return jsonify(get_college_summary())


@app.route("/api/news")
@app.route("/assistant-api/news")
def news():
    query = request.args.get("query")
    try:
        return jsonify({"articles": fetch_news(query)})
    except Exception:
        logger.exception("Unhandled error in news endpoint")
        return jsonify({"articles": []})


@app.route("/api/media/images")
@app.route("/assistant-api/media/images")
def media_images():
    return jsonify(get_college_images())


@app.route("/api/media/video")
@app.route("/assistant-api/media/video")
def media_video():
    return jsonify(get_college_video())   # Returning as JSON for consistency


@app.route("/api/healthz")
@app.route("/assistant-api/healthz")
def health():
    return jsonify({"status": "ok"})


# Optional: Serve static files explicitly (Flask already does this via static_folder)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)