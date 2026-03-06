"""
app.py — Flask application factory.
"""

import logging
import os
import time
from datetime import datetime, timezone

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes import register_blueprints
from services.mock_service import is_mock_mode

# App start time for uptime reporting
_START_TIME = time.time()


def setup_logging(app: Flask):
    """Configure structured JSON logging."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": %(message)s}'
        ),
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))


def create_app(config=None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config or Config)

    # CORS — restrict origins in production via ALLOWED_ORIGINS env var
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
    CORS(app, resources={r"/api/*": {"origins": allowed_origins.split(",")}})

    setup_logging(app)
    register_blueprints(app)

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad_request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found", "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'"Internal server error: {e}"')
        return jsonify({"error": "internal_error", "message": "An unexpected error occurred"}), 500

    app.logger.info(f'"CloudPulse starting — mock_mode={is_mock_mode()}"')
    return app


# Expose for Lambda / gunicorn / flask run
app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=int(os.environ.get("PORT", 5000)))
