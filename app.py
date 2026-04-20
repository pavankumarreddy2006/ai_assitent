from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging

# Import only what we need
from core.router import route_message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        message = (data.get("message") or "").strip()

        if not message:
            return jsonify({"reply": "Please say something.", "intent": "general"})

        logger.info(f"User: {message}")

        response = route_message(message)

        logger.info(f"AI Reply: {response.get('reply', '')[:100]}")
        return jsonify(response)

    except Exception as e:
        logger.exception("Backend Error")
        return jsonify({
            "reply": "Something went wrong. Please try again.",
            "intent": "general"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)