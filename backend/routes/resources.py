"""
routes/resources.py — GET /api/resources
"""

import logging

from flask import Blueprint, jsonify, request

from services.resource_service import get_resources

logger = logging.getLogger(__name__)
resources_bp = Blueprint("resources", __name__)


@resources_bp.route("/api/resources", methods=["GET"])
def resources():
    mock_raw = request.args.get("mock")
    mock = mock_raw is not None and mock_raw.lower() in ("true", "1", "yes")

    logger.info(f'"GET /api/resources mock={mock}"')

    try:
        data = get_resources(mock=mock)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f'"Error in GET /api/resources: {e}"')
        return jsonify({"error": "internal_error", "message": "Failed to retrieve resource data"}), 500
