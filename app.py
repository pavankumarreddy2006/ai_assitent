from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging

from core.router import route_message
from services.college_service import get_college_summary
from services.media_service import get_college_images, get_college_video

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder="templates", 
            static_folder="static", 
            static_url_path="/static")

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()

        if not message:
            return jsonify({"reply": "Please say something.", "intent": "general"}), 400

        logger.info(f"User asked: {message}")

        response = route_message(message)

        logger.info(f"AI Reply: {response.get('reply')[:100]}...")
        return jsonify(response)

    except Exception as e:
        logger.exception("Chat API Error")
        return jsonify({
            "reply": "Something went wrong. Please try again.",
            "intent": "general"
        }), 500

@app.route("/api/healthz")
def health():
    return jsonify({"status": "ok"})

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)