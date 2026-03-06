"""
routes/health.py — GET /api/health
"""

import os
import time
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from flask import Blueprint, current_app, jsonify

from config import Config

health_bp = Blueprint("health", __name__)

_START_TIME = time.time()


def _check_aws_connectivity() -> dict:
    try:
        sts = boto3.client("sts", region_name=Config.AWS_REGION)
        identity = sts.get_caller_identity()
        return {
            "connected": True,
            "region": Config.AWS_REGION,
            "account_id": identity.get("Account", "unknown"),
        }
    except (NoCredentialsError, ClientError):
        return {"connected": False, "region": Config.AWS_REGION, "account_id": None}


def _check_dynamodb() -> dict:
    table_name = Config.DYNAMODB_TABLE_NAME
    try:
        kwargs = {"region_name": Config.AWS_REGION}
        if Config.DYNAMODB_ENDPOINT_URL:
            kwargs["endpoint_url"] = Config.DYNAMODB_ENDPOINT_URL
        client = boto3.client("dynamodb", **kwargs)
        client.describe_table(TableName=table_name)
        return {"connected": True, "table": table_name}
    except (NoCredentialsError, ClientError):
        return {"connected": False, "table": table_name}


@health_bp.route("/api/health", methods=["GET"])
def health():
    uptime = int(time.time() - _START_TIME)
    aws = _check_aws_connectivity()
    dynamo = _check_dynamodb()

    status = "ok" if aws["connected"] else "degraded"

    return jsonify({
        "status": status,
        "version": Config.VERSION,
        "uptime_seconds": uptime,
        "mock_mode": Config.MOCK_MODE or not aws["connected"],
        "aws": aws,
        "dynamodb": dynamo,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200
