"""
resource_service.py — Fetches EC2, S3, and Lambda resource inventory
from AWS, with automatic fallback to mock data.
"""

import logging
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from config import Config
from services.mock_service import is_mock_mode, load_mock

logger = logging.getLogger(__name__)


def _get_ec2_inventory() -> dict:
    ec2 = boto3.client("ec2", region_name=Config.AWS_REGION)
    response = ec2.describe_instances()

    instances = []
    state_counts = {}

    for reservation in response.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            state = inst["State"]["Name"]
            state_counts[state] = state_counts.get(state, 0) + 1

            name = next(
                (tag["Value"] for tag in inst.get("Tags", []) if tag["Key"] == "Name"),
                inst["InstanceId"],
            )
            instances.append({
                "id": inst["InstanceId"],
                "type": inst.get("InstanceType", "unknown"),
                "state": state,
                "region": Config.AWS_REGION,
                "name": name,
            })

    return {
        "total": len(instances),
        "by_state": state_counts,
        "instances": instances,
    }


def _get_s3_inventory() -> dict:
    s3 = boto3.client("s3", region_name=Config.AWS_REGION)
    response = s3.list_buckets()
    buckets = []

    for bucket in response.get("Buckets", []):
        try:
            loc = s3.get_bucket_location(Bucket=bucket["Name"])
            region = loc.get("LocationConstraint") or "us-east-1"
        except ClientError:
            region = "unknown"

        buckets.append({
            "name": bucket["Name"],
            "region": region,
            "creation_date": bucket["CreationDate"].isoformat(),
        })

    return {"total_buckets": len(buckets), "buckets": buckets}


def _get_lambda_inventory() -> dict:
    lam = boto3.client("lambda", region_name=Config.AWS_REGION)
    functions = []
    marker = None

    while True:
        kwargs = {"MaxItems": 50}
        if marker:
            kwargs["Marker"] = marker
        response = lam.list_functions(**kwargs)

        for fn in response.get("Functions", []):
            functions.append({
                "name": fn["FunctionName"],
                "runtime": fn.get("Runtime", "unknown"),
                "region": Config.AWS_REGION,
                "last_modified": fn.get("LastModified", ""),
            })

        marker = response.get("NextMarker")
        if not marker:
            break

    return {"total_functions": len(functions), "functions": functions}


def get_resources(mock: bool = False) -> dict:
    """
    Main entry point. Returns resource inventory from live AWS or mock fixture.
    Falls back to mock if AWS credentials are not available.
    """
    if mock or is_mock_mode():
        logger.info('"Returning mock resource data"')
        data = load_mock("resources.json")
        data["source"] = "mock"
        return data

    try:
        logger.info('"Fetching live resource data from AWS"')
        ec2 = _get_ec2_inventory()
        s3 = _get_s3_inventory()
        lam = _get_lambda_inventory()

        return {
            "ec2": ec2,
            "s3": s3,
            "lambda": lam,
            "source": "live",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except (NoCredentialsError, ClientError) as e:
        logger.warning(f'"AWS call failed, falling back to mock: {e}"')
        data = load_mock("resources.json")
        data["source"] = "mock_fallback"
        return data
