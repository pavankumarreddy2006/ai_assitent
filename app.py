"""
app.py - Main entry point for College AI Flask application.
Run with: python app.py  (dev)  or  gunicorn app:app  (prod)
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config.config import SESSION_SECRET
from core.router import route_message
from services.college_service import get_college_summary
from services.news_service import fetch_news
from services.media_service import get_college_images, get_college_video

app = Flask(__name__)
app.secret_key = SESSION_SECRET
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
@app.route("/assistant-api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    conversation_history = data.get("conversationHistory", [])
    if not isinstance(conversation_history, list):
        conversation_history = []

    response = route_message(message, conversation_history)
    return jsonify(response)


@app.route("/api/college-info", methods=["GET"])
@app.route("/assistant-api/college-info", methods=["GET"])
def college_info():
    return jsonify(get_college_summary())


@app.route("/api/news", methods=["GET"])
@app.route("/assistant-api/news", methods=["GET"])
def news():
    query = request.args.get("query")
    articles = fetch_news(query)
    return jsonify({"articles": articles})


@app.route("/api/media/images", methods=["GET"])
@app.route("/assistant-api/media/images", methods=["GET"])
def media_images():
    return jsonify(get_college_images())


@app.route("/api/media/video", methods=["GET"])
@app.route("/assistant-api/media/video", methods=["GET"])
def media_video():
    return jsonify(get_college_video())


@app.route("/api/healthz", methods=["GET"])
@app.route("/assistant-api/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)