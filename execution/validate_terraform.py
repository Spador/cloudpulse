"""
validate_terraform.py
---------------------
Runs terraform validate and terraform plan in the infra/ directory.
Checks S3 state bucket existence before running.
Used by CI/CD pipeline and developers to validate infra changes.

Usage:
    python execution/validate_terraform.py [--check-state-bucket] [--plan-only]

Environment variables:
    TF_STATE_BUCKET   - S3 bucket name for Terraform remote state
    TF_STATE_REGION   - Region where state bucket lives
    AWS_REGION        - AWS region for Terraform
"""

import argparse
import os
import subprocess
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

TF_STATE_BUCKET = os.environ.get("TF_STATE_BUCKET", "")
TF_STATE_REGION = os.environ.get("TF_STATE_REGION", "us-east-1")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

INFRA_DIR = os.path.join(os.path.dirname(__file__), "..", "infra")


def check_state_bucket() -> bool:
    """Verify S3 state bucket exists and is accessible."""
    if not TF_STATE_BUCKET:
        print("ERROR: TF_STATE_BUCKET environment variable not set.")
        print("\nTo bootstrap the state bucket, run:")
        print(f"  aws s3 mb s3://cloudpulse-tf-state-<account-id> --region {TF_STATE_REGION}")
        print(f"  export TF_STATE_BUCKET=cloudpulse-tf-state-<account-id>")
        return False

    try:
        s3 = boto3.client("s3", region_name=TF_STATE_REGION)
        s3.head_bucket(Bucket=TF_STATE_BUCKET)
        print(f"State bucket '{TF_STATE_BUCKET}' exists and is accessible.")
        return True
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            print(f"ERROR: State bucket '{TF_STATE_BUCKET}' does not exist.")
            print("\nBootstrap it with:")
            print(f"  aws s3 mb s3://{TF_STATE_BUCKET} --region {TF_STATE_REGION}")
            print(f"  aws s3api put-bucket-versioning --bucket {TF_STATE_BUCKET} "
                  f"--versioning-configuration Status=Enabled")
        else:
            print(f"ERROR: Cannot access state bucket: {e}")
        return False
    except NoCredentialsError:
        print("ERROR: No AWS credentials found. Configure credentials before running Terraform.")
        return False


def run_cmd(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a subprocess command. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def terraform_validate() -> bool:
    """Run terraform validate. Returns True if valid."""
    print("\nRunning: terraform validate...")
    code, stdout, stderr = run_cmd(["terraform", "validate"], cwd=INFRA_DIR)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    if code == 0:
        print("terraform validate: PASSED")
        return True
    else:
        print(f"terraform validate: FAILED (exit code {code})")
        return False


def terraform_init() -> bool:
    """Run terraform init with S3 backend config."""
    print("\nRunning: terraform init...")
    cmd = [
        "terraform", "init",
        f"-backend-config=bucket={TF_STATE_BUCKET}",
        f"-backend-config=key=cloudpulse/terraform.tfstate",
        f"-backend-config=region={TF_STATE_REGION}",
        "-input=false",
        "-no-color",
    ]
    code, stdout, stderr = run_cmd(cmd, cwd=INFRA_DIR)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    if code == 0:
        print("terraform init: PASSED")
        return True
    else:
        print(f"terraform init: FAILED (exit code {code})")
        return False


def terraform_plan() -> bool:
    """Run terraform plan. Returns True if plan succeeds (no errors)."""
    print("\nRunning: terraform plan...")
    cmd = [
        "terraform", "plan",
        "-out=tfplan",
        "-no-color",
        "-input=false",
    ]
    code, stdout, stderr = run_cmd(cmd, cwd=INFRA_DIR)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    if code == 0:
        print("terraform plan: PASSED")
        return True
    else:
        print(f"terraform plan: FAILED (exit code {code})")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate and plan Terraform infrastructure")
    parser.add_argument(
        "--check-state-bucket", action="store_true",
        help="Verify S3 state bucket exists before running"
    )
    parser.add_argument(
        "--plan-only", action="store_true",
        help="Skip validate, run plan only"
    )
    parser.add_argument(
        "--skip-init", action="store_true",
        help="Skip terraform init (already initialized)"
    )
    args = parser.parse_args()

    failures = []

    if args.check_state_bucket:
        if not check_state_bucket():
            sys.exit(1)

    if not args.skip_init:
        if not terraform_init():
            failures.append("init")

    if not args.plan_only and "init" not in failures:
        if not terraform_validate():
            failures.append("validate")

    if "init" not in failures:
        if not terraform_plan():
            failures.append("plan")

    if failures:
        print(f"\nFAILED stages: {', '.join(failures)}")
        sys.exit(1)

    print("\nAll Terraform checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
