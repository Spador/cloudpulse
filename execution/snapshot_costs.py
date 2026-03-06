"""
snapshot_costs.py
-----------------
Polls AWS Cost Explorer for the past N days and writes daily cost snapshots
to DynamoDB. Designed to run as a Lambda function (triggered hourly by
CloudWatch Events) or as a standalone CLI script.

Usage:
    python execution/snapshot_costs.py [--days 90] [--dry-run]

Environment variables required:
    AWS_REGION            - AWS region
    DYNAMODB_TABLE_NAME   - DynamoDB table name (default: cloudpulse-costs)
    COST_SNAPSHOT_DAYS    - Days to look back (default: 90, overridden by --days)
    AWS_ENDPOINT_URL      - Optional: for local DynamoDB (http://localhost:8000)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "snapshot_costs", "message": %(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("snapshot_costs")

# ─── Configuration ────────────────────────────────────────────────────────────

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "cloudpulse-costs")
SNAPSHOT_DAYS = int(os.environ.get("COST_SNAPSHOT_DAYS", "90"))
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")  # None = real AWS

# Cost Explorer must always use us-east-1 endpoint
CE_REGION = "us-east-1"

TTL_DAYS = 90  # Items expire after 90 days


# ─── AWS Clients ──────────────────────────────────────────────────────────────

def get_ce_client():
    """Cost Explorer client — always us-east-1."""
    kwargs = {"region_name": CE_REGION}
    if ENDPOINT_URL:
        kwargs["endpoint_url"] = ENDPOINT_URL
    return boto3.client("ce", **kwargs)


def get_dynamodb_resource():
    """DynamoDB resource."""
    kwargs = {"region_name": AWS_REGION}
    if ENDPOINT_URL:
        kwargs["endpoint_url"] = ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


# ─── Cost Explorer ────────────────────────────────────────────────────────────

def fetch_costs(days: int) -> list[dict]:
    """
    Fetch daily cost per AWS service for the past `days` days.
    Fetches last 3 days on overlap to catch CE data lag.

    Returns list of dicts: { date, service, cost, currency }
    """
    # CE has up to 48h lag — always fetch last 3 days to catch delayed records
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    logger.info(f'"Fetching cost data from {start} to {end}"')

    ce = get_ce_client()
    records = []
    next_token = None

    while True:
        kwargs = {
            "TimePeriod": {"Start": str(start), "End": str(end)},
            "Granularity": "DAILY",
            "Metrics": ["UnblendedCost"],
            "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],
        }
        if next_token:
            kwargs["NextPageToken"] = next_token

        response = ce.get_cost_and_usage(**kwargs)

        for result_by_time in response.get("ResultsByTime", []):
            date_str = result_by_time["TimePeriod"]["Start"]
            for group in result_by_time.get("Groups", []):
                service = group["Keys"][0]
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                currency = group["Metrics"]["UnblendedCost"]["Unit"]
                if amount > 0:  # Skip $0 entries to save DynamoDB space
                    records.append({
                        "date": date_str,
                        "service": service,
                        "cost": amount,
                        "currency": currency,
                    })

        next_token = response.get("NextPageToken")
        if not next_token:
            break

    logger.info(f'"Fetched {len(records)} cost records"')
    return records


# ─── DynamoDB Write ───────────────────────────────────────────────────────────

def write_to_dynamodb(records: list[dict], dry_run: bool = False) -> int:
    """
    Batch-write cost records to DynamoDB.
    Returns number of items written.
    """
    if dry_run:
        logger.info(f'"DRY RUN: would write {len(records)} items to {TABLE_NAME}"')
        for r in records[:5]:
            print(json.dumps(r, indent=2))
        return 0

    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(TABLE_NAME)
    now_epoch = int(time.time())
    ttl_epoch = now_epoch + (TTL_DAYS * 86400)
    snapshot_at = datetime.now(timezone.utc).isoformat()

    written = 0
    # DynamoDB batch_writer handles 25-item batches automatically
    with table.batch_writer() as batch:
        for record in records:
            item = {
                "pk": f"SERVICE#{record['service']}",
                "sk": f"DATE#{record['date']}",
                "service": record["service"],
                "date": record["date"],
                "cost": str(record["cost"]),  # DynamoDB Decimal-safe
                "currency": record["currency"],
                "source": "cost_explorer",
                "ttl": ttl_epoch,
                "snapshot_at": snapshot_at,
            }
            batch.put_item(Item=item)
            written += 1

    logger.info(f'"Wrote {written} items to DynamoDB table {TABLE_NAME}"')
    return written


# ─── Entry Points ─────────────────────────────────────────────────────────────

def run(days: int = SNAPSHOT_DAYS, dry_run: bool = False) -> dict:
    """Main logic. Returns summary dict."""
    try:
        records = fetch_costs(days)
        written = write_to_dynamodb(records, dry_run=dry_run)
        return {"status": "success", "records_fetched": len(records), "records_written": written}
    except NoCredentialsError:
        logger.error('"No AWS credentials found. Set AWS_ACCESS_KEY_ID or configure an IAM role."')
        return {"status": "error", "error": "no_credentials"}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg = e.response["Error"]["Message"]
        logger.error(f'"AWS ClientError: {code} — {msg}"')
        return {"status": "error", "error": code, "message": msg}
    except Exception as e:
        logger.exception(f'"Unexpected error: {e}"')
        return {"status": "error", "error": str(e)}


def lambda_handler(event, context):
    """AWS Lambda entry point."""
    result = run()
    logger.info(f'"Lambda execution complete: {json.dumps(result)}"')
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapshot AWS costs to DynamoDB")
    parser.add_argument("--days", type=int, default=SNAPSHOT_DAYS, help="Days to look back")
    parser.add_argument("--dry-run", action="store_true", help="Print records without writing")
    args = parser.parse_args()

    result = run(days=args.days, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "success" else 1)
