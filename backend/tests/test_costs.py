"""
test_costs.py — Tests for GET /api/costs
"""

import pytest


def test_costs_returns_200(client):
    response = client.get("/api/costs")
    assert response.status_code == 200


def test_costs_response_shape(client):
    data = client.get("/api/costs").get_json()
    assert "period" in data
    assert "daily" in data
    assert "monthly_summary" in data
    assert "grand_total" in data
    assert "currency" in data
    assert "source" in data


def test_costs_mock_param(client):
    data = client.get("/api/costs?mock=true").get_json()
    assert data["source"] in ("mock", "mock_fallback")


def test_costs_invalid_days_string(client):
    response = client.get("/api/costs?days=abc")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "invalid_param"
    assert data["param"] == "days"


def test_costs_days_too_large(client):
    response = client.get("/api/costs?days=999")
    assert response.status_code == 400


def test_costs_days_too_small(client):
    response = client.get("/api/costs?days=0")
    assert response.status_code == 400


def test_costs_valid_days(client):
    for days in (7, 30, 90):
        response = client.get(f"/api/costs?days={days}")
        assert response.status_code == 200


def test_costs_daily_list_not_empty(client):
    data = client.get("/api/costs?mock=true").get_json()
    assert isinstance(data["daily"], list)
    assert len(data["daily"]) > 0


def test_costs_monthly_summary_sorted(client):
    data = client.get("/api/costs?mock=true").get_json()
    totals = [item["total_cost"] for item in data["monthly_summary"]]
    assert totals == sorted(totals, reverse=True)
