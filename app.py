"""
app.py — Main entry point for College AI Flask application.
Run with: python app.py  (dev)  or  gunicorn app:app  (prod/Render)
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config.config import SESSION_SECRET
from core.router import route_message
from services.college_service import get_college_summary
from services.news_service import fetch_news

app = Flask(__name__)
app.secret_key = SESSION_SECRET
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"].strip()
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    conversation_history = data.get("conversationHistory", [])
    response = route_message(message, conversation_history)
    return jsonify(response)


@app.route("/api/college-info", methods=["GET"])
def college_info():
    return jsonify(get_college_summary())


@app.route("/api/news", methods=["GET"])
def news():
    query = request.args.get("query")
    articles = fetch_news(query)
    return jsonify({"articles": articles})


@app.route("/api/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

