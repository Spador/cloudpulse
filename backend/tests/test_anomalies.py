"""
test_anomalies.py — Tests for anomaly detection logic and GET /api/anomalies
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.anomaly_service import detect_anomalies


def make_records(service_costs: dict) -> list[dict]:
    """
    Helper: build flat cost records from { service: [cost_day0, cost_day1, ...] }
    where index 0 = oldest day.
    """
    base = datetime.now(timezone.utc).date()
    num_days = max(len(v) for v in service_costs.values())
    records = []

    for service, costs in service_costs.items():
        for i, cost in enumerate(costs):
            day_offset = num_days - 1 - i
            date_str = str(base - timedelta(days=day_offset))
            if cost > 0:
                records.append({
                    "service": service,
                    "date": date_str,
                    "cost": cost,
                    "currency": "USD",
                })
    return records


# ─── Core detection logic tests ───────────────────────────────────────────────

def test_spike_detected():
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 18.50]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 1
    assert anomalies[0]["service"] == "Amazon EC2"
    assert anomalies[0]["pct_change"] == 85.0


def test_below_threshold_not_flagged():
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 11.50]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 0


def test_zero_previous_cost_skipped():
    records = make_records({"Amazon EC2": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 0


def test_new_service_single_day_skipped():
    # Only one day of data — no previous to compare
    records = make_records({"NewService": [5.0]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 0


def test_critical_severity():
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 25.0]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 1
    assert anomalies[0]["severity"] == "critical"


def test_high_severity():
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 17.0]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 1
    assert anomalies[0]["severity"] == "high"


def test_medium_severity():
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 13.0]})
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 1
    assert anomalies[0]["severity"] == "medium"


def test_ranking_order():
    records = make_records({
        "Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 25.0],  # 150% — critical
        "Amazon RDS": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 17.0],  # 70% — high
        "Amazon S3":  [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 13.0],  # 30% — medium
    })
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 3
    assert anomalies[0]["pct_change"] >= anomalies[1]["pct_change"]
    assert anomalies[1]["pct_change"] >= anomalies[2]["pct_change"]


def test_custom_threshold():
    # 30% spike, but threshold is 50% — should not be flagged
    records = make_records({"Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 13.0]})
    anomalies = detect_anomalies(records, threshold=0.50, days=7)
    assert len(anomalies) == 0


def test_multiple_services_only_two_flagged():
    records = make_records({
        "Amazon EC2": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 25.0],  # spike
        "Amazon RDS": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 17.0],  # spike
        "Amazon S3":  [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.5],  # no spike
        "AWS Lambda": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.05],        # no spike
        "Amazon CF":  [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.52],        # no spike
    })
    anomalies = detect_anomalies(records, threshold=0.20, days=7)
    assert len(anomalies) == 2


def test_empty_records_returns_empty():
    anomalies = detect_anomalies([], threshold=0.20, days=7)
    assert anomalies == []


# ─── API route tests ───────────────────────────────────────────────────────────

def test_anomalies_route_200(client):
    response = client.get("/api/anomalies")
    assert response.status_code == 200


def test_anomalies_route_shape(client):
    data = client.get("/api/anomalies?mock=true").get_json()
    assert "anomalies" in data
    assert "threshold_used" in data
    assert "period_scanned" in data
    assert "total_anomalies" in data
    assert "source" in data


def test_anomalies_invalid_threshold(client):
    response = client.get("/api/anomalies?threshold=abc")
    assert response.status_code == 400


def test_anomalies_threshold_out_of_range(client):
    response = client.get("/api/anomalies?threshold=10.0")
    assert response.status_code == 400


def test_anomalies_invalid_days(client):
    response = client.get("/api/anomalies?days=abc")
    assert response.status_code == 400


def test_anomalies_days_out_of_range(client):
    response = client.get("/api/anomalies?days=100")
    assert response.status_code == 400
