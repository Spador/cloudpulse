"""
conftest.py — Shared pytest fixtures.
"""

import os

import pytest

# Force mock mode for all tests — no real AWS calls
os.environ["MOCK_MODE"] = "true"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["DYNAMODB_TABLE_NAME"] = "cloudpulse-costs-test"


@pytest.fixture
def app():
    from config import TestConfig
    from app import create_app

    application = create_app(config=TestConfig)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_cost_records():
    """Flat cost records for anomaly detection tests."""
    from datetime import datetime, timedelta, timezone
    base = datetime.now(timezone.utc).date()

    records = []
    for day_offset in range(8, -1, -1):
        date = str(base - timedelta(days=day_offset))
        records.append({"service": "Amazon EC2", "date": date, "cost": 10.0, "currency": "USD"})
        records.append({"service": "Amazon S3", "date": date, "cost": 1.0, "currency": "USD"})

    return records
