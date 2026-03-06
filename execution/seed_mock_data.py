"""
seed_mock_data.py
-----------------
Seeds a local (or remote) DynamoDB table with mock cost data for development.
Creates the table if it doesn't exist.

Usage:
    # Local DynamoDB (Docker):
    docker run -p 8000:8000 amazon/dynamodb-local
    AWS_ENDPOINT_URL=http://localhost:8000 python execution/seed_mock_data.py

    # Real DynamoDB (dev account):
    python execution/seed_mock_data.py

Environment variables:
    AWS_REGION            - AWS region (default: us-east-1)
    DYNAMODB_TABLE_NAME   - Table name (default: cloudpulse-costs)
    AWS_ENDPOINT_URL      - Optional: for local DynamoDB
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level="INFO", format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_mock_data")

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "cloudpulse-costs")
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")

# ─── Mock Data Definition ─────────────────────────────────────────────────────

SERVICES = [
    "Amazon EC2",
    "Amazon S3",
    "AWS Lambda",
    "Amazon RDS",
    "Amazon CloudFront",
    "Amazon Route 53",
    "AWS Data Transfer",
]

# Base daily costs per service (USD)
BASE_COSTS = {
    "Amazon EC2": 12.50,
    "Amazon S3": 1.20,
    "AWS Lambda": 0.15,
    "Amazon RDS": 8.50,
    "Amazon CloudFront": 0.45,
    "Amazon Route 53": 0.10,
    "AWS Data Transfer": 0.30,
}

# Anomaly injections: (service, days_ago, multiplier)
ANOMALIES = [
    ("Amazon EC2", 1, 2.30),   # Yesterday: critical spike
    ("Amazon RDS", 2, 1.65),   # 2 days ago: high spike
    ("Amazon S3", 3, 1.30),    # 3 days ago: medium spike
]


def generate_mock_records(days: int = 90) -> list[dict]:
    """Generate realistic mock cost records for the past `days` days."""
    import random
    random.seed(42)  # Deterministic output

    end = datetime.now(timezone.utc).date()
    records = []
    anomaly_map = {(svc, days_ago): mult for svc, days_ago, mult in ANOMALIES}

    for day_offset in range(days, -1, -1):
        date = end - timedelta(days=day_offset)
        date_str = str(date)

        for service in SERVICES:
            base = BASE_COSTS[service]
            # Add ±10% random variance
            variance = random.uniform(0.90, 1.10)
            cost = base * variance

            # Apply anomaly multiplier if applicable
            anomaly_key = (service, day_offset)
            if anomaly_key in anomaly_map:
                cost *= anomaly_map[anomaly_key]

            records.append({
                "pk": f"SERVICE#{service}",
                "sk": f"DATE#{date_str}",
                "service": service,
                "date": date_str,
                "cost": str(round(cost, 4)),
                "currency": "USD",
                "source": "mock",
                "ttl": int(time.time()) + (90 * 86400),
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Generated {len(records)} mock records")
    return records


# ─── DynamoDB Setup ───────────────────────────────────────────────────────────

def get_dynamodb_client():
    kwargs = {"region_name": AWS_REGION}
    if ENDPOINT_URL:
        kwargs["endpoint_url"] = ENDPOINT_URL
    return boto3.client("dynamodb", **kwargs)


def get_dynamodb_resource():
    kwargs = {"region_name": AWS_REGION}
    if ENDPOINT_URL:
        kwargs["endpoint_url"] = ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def ensure_table_exists():
    """Create the DynamoDB table if it doesn't exist."""
    client = get_dynamodb_client()

    try:
        client.describe_table(TableName=TABLE_NAME)
        logger.info(f"Table '{TABLE_NAME}' already exists")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    logger.info(f"Creating table '{TABLE_NAME}'...")
    client.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "date", "AttributeType": "S"},
            {"AttributeName": "cost", "AttributeType": "N"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "DateIndex",
                "KeySchema": [
                    {"AttributeName": "date", "KeyType": "HASH"},
                    {"AttributeName": "cost", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    # Wait for table to be active
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=TABLE_NAME)
    logger.info(f"Table '{TABLE_NAME}' created successfully")

    # Enable TTL
    client.update_time_to_live(
        TableName=TABLE_NAME,
        TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"},
    )
    logger.info("TTL enabled on 'ttl' attribute")


def seed_records(records: list[dict]) -> int:
    """Batch-write records to DynamoDB. Returns count written."""
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)

    written = 0
    with table.batch_writer() as batch:
        for item in records:
            batch.put_item(Item=item)
            written += 1

    return written


def main():
    logger.info(f"Seeding mock data into '{TABLE_NAME}' at {ENDPOINT_URL or 'real AWS'}...")

    ensure_table_exists()
    records = generate_mock_records(days=90)
    written = seed_records(records)

    logger.info(f"Done. Seeded {written} records into '{TABLE_NAME}'.")
    print(json.dumps({"status": "success", "records_written": written, "table": TABLE_NAME}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
