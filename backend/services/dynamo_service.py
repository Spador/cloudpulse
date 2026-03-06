"""
dynamo_service.py — DynamoDB read/write operations.
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from config import Config

logger = logging.getLogger(__name__)


def _get_table():
    kwargs = {"region_name": Config.AWS_REGION}
    if Config.DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = Config.DYNAMODB_ENDPOINT_URL
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(Config.DYNAMODB_TABLE_NAME)


def get_costs_for_period(days: int) -> list[dict]:
    """
    Query DynamoDB for cost records in the past `days` days.
    Returns flat list of { service, date, cost, currency } dicts.
    """
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    table = _get_table()

    # Scan with filter expression — acceptable volume for this use case
    response = table.scan(
        FilterExpression="#dt BETWEEN :start AND :end",
        ExpressionAttributeNames={"#dt": "date"},
        ExpressionAttributeValues={":start": str(start), ":end": str(end)},
    )

    records = []
    for item in response.get("Items", []):
        records.append({
            "service": item["service"],
            "date": item["date"],
            "cost": float(item["cost"]),
            "currency": item.get("currency", "USD"),
        })

    # Handle DynamoDB pagination
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression="#dt BETWEEN :start AND :end",
            ExpressionAttributeNames={"#dt": "date"},
            ExpressionAttributeValues={":start": str(start), ":end": str(end)},
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        for item in response.get("Items", []):
            records.append({
                "service": item["service"],
                "date": item["date"],
                "cost": float(item["cost"]),
                "currency": item.get("currency", "USD"),
            })

    logger.info(f'"Fetched {len(records)} records from DynamoDB for past {days} days"')
    return records


def put_cost_snapshot(service: str, date: str, cost: float, currency: str = "USD"):
    """Write a single cost snapshot to DynamoDB."""
    import time
    table = _get_table()
    ttl = int(time.time()) + (90 * 86400)

    table.put_item(Item={
        "pk": f"SERVICE#{service}",
        "sk": f"DATE#{date}",
        "service": service,
        "date": date,
        "cost": str(cost),
        "currency": currency,
        "source": "cost_explorer",
        "ttl": ttl,
        "snapshot_at": datetime.now(timezone.utc).isoformat(),
    })
