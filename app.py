from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging
import os

from core.router import route_message
from services.college_service import get_college_summary
from services.media_service import get_college_images, get_college_video

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger("ideal-ai.api")

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/static")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        message = (data.get("message") or "").strip()
        history = data.get("conversationHistory", [])

        if not message:
            return jsonify({"reply": "దయచేసి ఒక మెసేజ్ టైప్ చేయండి.", "intent": "general"}), 400

        logger.info(f"Received message: {message}")
        response = route_message(message, history)
        
        logger.info(f"Response sent: {response.get('reply')[:100]}...")
        return jsonify(response)

    except Exception as e:
        logger.exception("Chat API Exception: %s", str(e))
        return jsonify({
            "reply": "క్షమించండి, సర్వర్ లో సమస్య వచ్చింది. మళ్లీ ప్రయత్నించండి.",
            "intent": "general"
        }), 500

@app.route("/api/college-info")
def college_info():
    return jsonify(get_college_summary())

@app.route("/api/media/images")
def media_images():
    return jsonify(get_college_images())

@app.route("/api/media/video")
def media_video():
    return jsonify({"video_url": get_college_video()})

@app.route("/api/healthz")
def health():
    return jsonify({"status": "ok", "env_keys_present": bool(os.getenv("GROQ_API_KEY"))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)