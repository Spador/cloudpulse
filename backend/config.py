"""
config.py — Application configuration loaded from environment variables.
"""

import os


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")
    DEBUG = os.environ.get("FLASK_ENV", "production") == "development"

    # AWS
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    # DynamoDB
    DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "cloudpulse-costs")
    DYNAMODB_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")  # None = real AWS

    # App behaviour
    MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"
    ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "0.20"))
    COST_SNAPSHOT_DAYS = int(os.environ.get("COST_SNAPSHOT_DAYS", "90"))

    # Version
    VERSION = "1.0.0"


class TestConfig(Config):
    TESTING = True
    MOCK_MODE = True
    DYNAMODB_TABLE_NAME = "cloudpulse-costs-test"
