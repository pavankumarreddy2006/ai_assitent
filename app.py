# app.py
import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS

from core.router import router

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

app.register_blueprint(router)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/media/<path:filename>")
def media(filename: str):
    return send_from_directory("static/media", filename)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ideal-ai"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)