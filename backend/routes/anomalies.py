"""
routes/anomalies.py — GET /api/anomalies
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from services.anomaly_service import get_anomalies

logger = logging.getLogger(__name__)
anomalies_bp = Blueprint("anomalies", __name__)


def _parse_threshold(raw) -> tuple[float, str | None]:
    if raw is None:
        return 0.20, None
    try:
        val = float(raw)
    except (ValueError, TypeError):
        return 0.0, "'threshold' must be a number (e.g. 0.20)"
    if not (0.01 <= val <= 5.0):
        return 0.0, "'threshold' must be between 0.01 and 5.0"
    return val, None


def _parse_days(raw) -> tuple[int, str | None]:
    if raw is None:
        return 7, None
    try:
        days = int(raw)
    except (ValueError, TypeError):
        return 0, "'days' must be an integer"
    if not (1 <= days <= 30):
        return 0, "'days' must be an integer between 1 and 30"
    return days, None


@anomalies_bp.route("/api/anomalies", methods=["GET"])
def anomalies():
    threshold, err = _parse_threshold(request.args.get("threshold"))
    if err:
        return jsonify({"error": "invalid_param", "message": err, "param": "threshold"}), 400

    days, err = _parse_days(request.args.get("days"))
    if err:
        return jsonify({"error": "invalid_param", "message": err, "param": "days"}), 400

    mock_raw = request.args.get("mock")
    mock = mock_raw is not None and mock_raw.lower() in ("true", "1", "yes")

    logger.info(f'"GET /api/anomalies days={days} threshold={threshold} mock={mock}"')

    try:
        data = get_anomalies(days=days, threshold=threshold, mock=mock)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f'"Error in GET /api/anomalies: {e}"')
        return jsonify({"error": "internal_error", "message": "Failed to retrieve anomaly data"}), 500
