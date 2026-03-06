"""
mock_service.py — Mock data loading and auto-detection of mock mode.
"""

import json
import logging
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

# Paths to mock JSON fixtures
_MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")


def is_mock_mode() -> bool:
    """
    Returns True if mock mode should be used:
    1. MOCK_MODE=true in environment, OR
    2. No AWS credentials available (no key, no profile, no instance metadata)
    """
    if os.environ.get("MOCK_MODE", "false").lower() == "true":
        return True

    # If keys are explicitly set, use live mode
    if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
        return False

    # Try a cheap STS call to detect instance role / SSO credentials
    try:
        boto3.client("sts", region_name="us-east-1").get_caller_identity()
        return False
    except (NoCredentialsError, ClientError):
        logger.info('"No AWS credentials detected — switching to mock mode"')
        return True


def load_mock(filename: str) -> dict:
    """Load and return mock JSON fixture from tests/fixtures/<filename>."""
    path = os.path.join(_MOCK_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Mock fixture not found: {path}")
    with open(path) as f:
        return json.load(f)
