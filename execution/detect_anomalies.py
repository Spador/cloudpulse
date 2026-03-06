"""
detect_anomalies.py
-------------------
Standalone script to detect cost anomalies from DynamoDB data.
Prints a JSON report and a human-readable summary table to stderr.

Usage:
    python execution/detect_anomalies.py [--days 7] [--threshold 0.20] [--mock]

Environment variables:
    AWS_REGION            - AWS region
    DYNAMODB_TABLE_NAME   - DynamoDB table name
    ANOMALY_THRESHOLD     - Default spike threshold (0.20 = 20%)
    AWS_ENDPOINT_URL      - Optional: for local DynamoDB
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
logger = logging.getLogger("detect_anomalies")

THRESHOLD_DEFAULT = float(os.environ.get("ANOMALY_THRESHOLD", "0.20"))
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "cloudpulse-costs")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")


def load_mock_data() -> list[dict]:
    """Load mock cost data from the frontend mock file."""
    mock_path = os.path.join(
        os.path.dirname(__file__), "..", "frontend", "src", "mock", "costs.json"
    )
    if not os.path.exists(mock_path):
        # Inline minimal mock data if frontend not yet built
        return [
            {"date": "2024-03-01", "service": "Amazon EC2", "cost": 10.0, "currency": "USD"},
            {"date": "2024-03-02", "service": "Amazon EC2", "cost": 10.5, "currency": "USD"},
            {"date": "2024-03-03", "service": "Amazon EC2", "cost": 10.0, "currency": "USD"},
            {"date": "2024-03-04", "service": "Amazon EC2", "cost": 23.0, "currency": "USD"},
            {"date": "2024-03-01", "service": "Amazon RDS", "cost": 8.0, "currency": "USD"},
            {"date": "2024-03-02", "service": "Amazon RDS", "cost": 8.0, "currency": "USD"},
            {"date": "2024-03-03", "service": "Amazon RDS", "cost": 8.0, "currency": "USD"},
            {"date": "2024-03-04", "service": "Amazon RDS", "cost": 13.2, "currency": "USD"},
        ]

    with open(mock_path) as f:
        data = json.load(f)

    records = []
    for day in data.get("daily", []):
        for svc in day.get("services", []):
            records.append({
                "date": day["date"],
                "service": svc["service"],
                "cost": float(svc["cost"]),
                "currency": svc.get("currency", "USD"),
            })
    return records


def fetch_from_dynamodb(days: int) -> list[dict]:
    """Scan DynamoDB for cost records in the last `days` days."""
    import boto3
    from boto3.dynamodb.conditions import Key

    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    kwargs = {"region_name": AWS_REGION}
    if ENDPOINT_URL:
        kwargs["endpoint_url"] = ENDPOINT_URL

    dynamodb = boto3.resource("dynamodb", **kwargs)
    table = dynamodb.Table(TABLE_NAME)

    # Scan with filter — acceptable at this data volume
    response = table.scan(
        FilterExpression="#dt BETWEEN :start AND :end",
        ExpressionAttributeNames={"#dt": "date"},
        ExpressionAttributeValues={":start": str(start), ":end": str(end)},
    )

    records = []
    for item in response.get("Items", []):
        records.append({
            "date": item["date"],
            "service": item["service"],
            "cost": float(item["cost"]),
            "currency": item.get("currency", "USD"),
        })
    return records


def build_cost_matrix(records: list[dict]) -> dict:
    """
    Convert flat records into: { service: { date: cost } }
    """
    matrix = {}
    for r in records:
        svc = r["service"]
        if svc not in matrix:
            matrix[svc] = {}
        matrix[svc][r["date"]] = r["cost"]
    return matrix


def classify_severity(pct_change: float) -> str:
    if pct_change >= 1.0:
        return "critical"
    elif pct_change >= 0.50:
        return "high"
    else:
        return "medium"


def detect_anomalies(records: list[dict], threshold: float, days: int) -> list[dict]:
    """
    Core anomaly detection logic.
    Returns list of anomaly dicts sorted by pct_change descending.
    """
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)

    # Build sorted date list for the window
    date_range = [str(start + timedelta(days=i)) for i in range(days + 1)]

    matrix = build_cost_matrix(records)
    anomalies = []

    for service, costs_by_date in matrix.items():
        for i in range(1, len(date_range)):
            prev_date = date_range[i - 1]
            curr_date = date_range[i]

            prev_cost = costs_by_date.get(prev_date, 0.0)
            curr_cost = costs_by_date.get(curr_date, 0.0)

            # Skip: no baseline (new service or zero previous)
            if prev_cost <= 0:
                continue

            # Skip: no current cost (service had no charges that day)
            if curr_cost <= 0:
                continue

            pct_change = (curr_cost - prev_cost) / prev_cost

            if pct_change >= threshold:
                anomalies.append({
                    "service": service,
                    "date": curr_date,
                    "previous_cost": round(prev_cost, 4),
                    "current_cost": round(curr_cost, 4),
                    "pct_change": round(pct_change * 100, 2),
                    "severity": classify_severity(pct_change),
                    "currency": "USD",
                })

    # Sort by pct_change descending (biggest spikes first)
    anomalies.sort(key=lambda x: x["pct_change"], reverse=True)
    return anomalies


def print_summary_table(anomalies: list[dict], file=sys.stderr):
    """Print human-readable summary to stderr."""
    if not anomalies:
        print("\nNo anomalies detected — costs look healthy!\n", file=file)
        return

    print(f"\nFound {len(anomalies)} anomaly(ies):\n", file=file)
    header = f"{'Service':<30} {'Date':<12} {'Prev $':>8} {'Curr $':>8} {'Change':>8} {'Severity':<10}"
    print(header, file=file)
    print("-" * len(header), file=file)
    for a in anomalies:
        print(
            f"{a['service']:<30} {a['date']:<12} "
            f"${a['previous_cost']:>7.2f} ${a['current_cost']:>7.2f} "
            f"+{a['pct_change']:>6.1f}% {a['severity']:<10}",
            file=file,
        )
    print("", file=file)


def main():
    parser = argparse.ArgumentParser(description="Detect AWS cost anomalies")
    parser.add_argument("--days", type=int, default=7, help="Window of days to scan")
    parser.add_argument(
        "--threshold", type=float, default=THRESHOLD_DEFAULT,
        help="Fractional spike threshold (default: 0.20 = 20%%)"
    )
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of DynamoDB")
    args = parser.parse_args()

    if args.mock:
        records = load_mock_data()
        source = "mock"
    else:
        try:
            records = fetch_from_dynamodb(args.days)
            source = "live"
        except Exception as e:
            print(f"Failed to fetch from DynamoDB: {e}. Falling back to mock data.", file=sys.stderr)
            records = load_mock_data()
            source = "mock_fallback"

    anomalies = detect_anomalies(records, threshold=args.threshold, days=args.days)
    print_summary_table(anomalies)

    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=args.days)

    report = {
        "anomalies": anomalies,
        "threshold_used": args.threshold,
        "period_scanned": {"start": str(start_date), "end": str(end_date)},
        "total_anomalies": len(anomalies),
        "source": source,
    }
    print(json.dumps(report, indent=2))
    return 0 if True else 1  # Always exit 0; anomalies are not a script error


if __name__ == "__main__":
    sys.exit(main())
