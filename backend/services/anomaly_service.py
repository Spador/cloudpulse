"""
anomaly_service.py — Cost anomaly detection logic.
Detects day-over-day cost spikes above a configurable threshold.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from services.dynamo_service import get_costs_for_period
from services.mock_service import is_mock_mode, load_mock

logger = logging.getLogger(__name__)


def _classify_severity(pct_change: float) -> str:
    """Classify anomaly severity based on percentage change (as decimal)."""
    if pct_change >= 1.0:
        return "critical"
    elif pct_change >= 0.50:
        return "high"
    else:
        return "medium"


def detect_anomalies(
    cost_records: list[dict],
    threshold: float = 0.20,
    days: int = 7,
) -> list[dict]:
    """
    Core detection logic. Pure function — no I/O.

    Args:
        cost_records: List of { service, date, cost, currency } dicts.
        threshold: Fractional spike threshold (0.20 = 20%).
        days: Number of consecutive days to analyse.

    Returns:
        List of anomaly dicts sorted by pct_change descending.
    """
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    date_range = [str(start + timedelta(days=i)) for i in range(days + 1)]

    # Build { service: { date: cost } }
    matrix: dict[str, dict[str, float]] = defaultdict(dict)
    for record in cost_records:
        matrix[record["service"]][record["date"]] = float(record["cost"])

    anomalies = []

    for service, costs_by_date in matrix.items():
        for i in range(1, len(date_range)):
            prev_date = date_range[i - 1]
            curr_date = date_range[i]

            prev_cost = costs_by_date.get(prev_date, 0.0)
            curr_cost = costs_by_date.get(curr_date, 0.0)

            # Skip: no baseline or no credits to compare
            if prev_cost <= 0 or curr_cost <= 0:
                continue

            pct_change = (curr_cost - prev_cost) / prev_cost

            if pct_change >= threshold:
                anomalies.append({
                    "service": service,
                    "date": curr_date,
                    "previous_cost": round(prev_cost, 4),
                    "current_cost": round(curr_cost, 4),
                    "pct_change": round(pct_change * 100, 2),
                    "severity": _classify_severity(pct_change),
                    "currency": "USD",
                })

    # Sort by pct_change descending (biggest spikes first)
    anomalies.sort(key=lambda x: x["pct_change"], reverse=True)
    return anomalies


def get_anomalies(days: int = 7, threshold: float = 0.20, mock: bool = False) -> dict:
    """
    Main entry point for the anomalies API route.
    """
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    if mock or is_mock_mode():
        logger.info('"Returning mock anomaly data"')
        data = load_mock("anomalies.json")
        data["source"] = "mock"
        return data

    try:
        records = get_costs_for_period(days=days)
        anomalies = detect_anomalies(records, threshold=threshold, days=days)

        return {
            "anomalies": anomalies,
            "threshold_used": threshold,
            "period_scanned": {"start": str(start), "end": str(end)},
            "total_anomalies": len(anomalies),
            "source": "live",
        }
    except Exception as e:
        logger.warning(f'"Failed to fetch live data, falling back to mock: {e}"')
        data = load_mock("anomalies.json")
        data["source"] = "mock_fallback"
        return data
