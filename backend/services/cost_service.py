"""
cost_service.py — Fetches cost data from AWS Cost Explorer or DynamoDB,
with automatic fallback to mock data.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from services.mock_service import is_mock_mode, load_mock

logger = logging.getLogger(__name__)

# Cost Explorer must always use us-east-1
CE_REGION = "us-east-1"


def _get_ce_client():
    return boto3.client("ce", region_name=CE_REGION)


def _fetch_from_cost_explorer(days: int) -> dict:
    """Call AWS Cost Explorer and return shaped response."""
    ce = _get_ce_client()
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    records_by_date = defaultdict(list)
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

        for result in response.get("ResultsByTime", []):
            date_str = result["TimePeriod"]["Start"]
            for group in result.get("Groups", []):
                service = group["Keys"][0]
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                currency = group["Metrics"]["UnblendedCost"]["Unit"]
                if amount > 0:
                    records_by_date[date_str].append({
                        "service": service,
                        "cost": round(amount, 4),
                        "currency": currency,
                    })

        next_token = response.get("NextPageToken")
        if not next_token:
            break

    return _shape_cost_response(records_by_date, start, end, source="live")


def _shape_cost_response(records_by_date: dict, start, end, source: str) -> dict:
    """Convert raw records into the API response shape."""
    daily = []
    service_totals = defaultdict(float)

    for date_str in sorted(records_by_date.keys()):
        services = records_by_date[date_str]
        day_total = sum(s["cost"] for s in services)
        daily.append({
            "date": date_str,
            "services": sorted(services, key=lambda x: x["cost"], reverse=True),
            "total": round(day_total, 4),
        })
        for s in services:
            service_totals[s["service"]] += s["cost"]

    monthly_summary = [
        {"service": svc, "total_cost": round(total, 4), "currency": "USD"}
        for svc, total in sorted(service_totals.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "period": {"start": str(start), "end": str(end)},
        "daily": daily,
        "monthly_summary": monthly_summary,
        "grand_total": round(sum(service_totals.values()), 4),
        "currency": "USD",
        "source": source,
    }


def get_costs(days: int = 30, mock: bool = False) -> dict:
    """
    Main entry point. Returns cost data from live AWS or mock fixture.
    Falls back to mock if AWS credentials are not available.
    """
    if mock or is_mock_mode():
        logger.info('"Returning mock cost data"')
        data = load_mock("costs.json")
        data["source"] = "mock"
        return data

    try:
        logger.info(f'"Fetching live cost data for {days} days"')
        return _fetch_from_cost_explorer(days)
    except (NoCredentialsError, ClientError) as e:
        logger.warning(f'"AWS call failed, falling back to mock: {e}"')
        data = load_mock("costs.json")
        data["source"] = "mock_fallback"
        return data
