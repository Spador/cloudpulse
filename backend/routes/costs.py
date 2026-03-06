"""
routes/costs.py — GET /api/costs
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from services.cost_service import get_costs

logger = logging.getLogger(__name__)
costs_bp = Blueprint("costs", __name__)


def _parse_days(raw) -> tuple[int, str | None]:
    """Parse and validate `days` query param. Returns (value, error_message)."""
    if raw is None:
        return 30, None
    try:
        days = int(raw)
    except (ValueError, TypeError):
        return 0, "'days' must be an integer"
    if not (1 <= days <= 90):
        return 0, "'days' must be an integer between 1 and 90"
    return days, None


def _parse_mock(raw) -> bool:
    if raw is None:
        return False
    return raw.lower() in ("true", "1", "yes")


@costs_bp.route("/api/costs", methods=["GET"])
def costs():
    days, err = _parse_days(request.args.get("days"))
    if err:
        return jsonify({"error": "invalid_param", "message": err, "param": "days"}), 400

    mock = _parse_mock(request.args.get("mock"))

    logger.info(f'"GET /api/costs days={days} mock={mock}"')

    try:
        data = get_costs(days=days, mock=mock)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f'"Error in GET /api/costs: {e}"')
        return jsonify({"error": "internal_error", "message": "Failed to retrieve cost data"}), 500
