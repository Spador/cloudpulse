"""
test_resources.py — Tests for GET /api/resources
"""


def test_resources_returns_200(client):
    response = client.get("/api/resources")
    assert response.status_code == 200


def test_resources_response_shape(client):
    data = client.get("/api/resources").get_json()
    assert "ec2" in data
    assert "s3" in data
    assert "lambda" in data
    assert "source" in data
    assert "fetched_at" in data


def test_resources_ec2_shape(client):
    data = client.get("/api/resources?mock=true").get_json()
    ec2 = data["ec2"]
    assert "total" in ec2
    assert "by_state" in ec2
    assert "instances" in ec2
    assert isinstance(ec2["instances"], list)


def test_resources_s3_shape(client):
    data = client.get("/api/resources?mock=true").get_json()
    s3 = data["s3"]
    assert "total_buckets" in s3
    assert "buckets" in s3


def test_resources_lambda_shape(client):
    data = client.get("/api/resources?mock=true").get_json()
    lam = data["lambda"]
    assert "total_functions" in lam
    assert "functions" in lam


def test_resources_mock_source(client):
    data = client.get("/api/resources?mock=true").get_json()
    assert data["source"] in ("mock", "mock_fallback")


def test_resources_instance_state_values(client):
    data = client.get("/api/resources?mock=true").get_json()
    valid_states = {"running", "stopped", "terminated", "pending", "shutting-down", "stopped"}
    for inst in data["ec2"]["instances"]:
        assert inst["state"] in valid_states
