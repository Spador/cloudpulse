"""
test_health.py — Tests for GET /api/health
"""


def test_health_returns_200(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_response_shape(client):
    data = client.get("/api/health").get_json()
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "aws" in data
    assert "dynamodb" in data
    assert "timestamp" in data


def test_health_status_is_string(client):
    data = client.get("/api/health").get_json()
    assert isinstance(data["status"], str)
    assert data["status"] in ("ok", "degraded")


def test_health_version_present(client):
    data = client.get("/api/health").get_json()
    assert data["version"] == "1.0.0"
