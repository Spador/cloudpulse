# Directive 01 — Terraform Infrastructure

## Objective
Provision all AWS infrastructure required by CloudPulse using Terraform 1.7+. All resources must be idempotent, use remote state, and follow least-privilege IAM.

---

## Inputs
- `AWS_REGION` — target region (default: `us-east-1`)
- `TF_STATE_BUCKET` — pre-existing S3 bucket name for remote state
- `TF_STATE_KEY` — S3 object key (default: `cloudpulse/terraform.tfstate`)
- `terraform.tfvars` — populated from `terraform.tfvars.example`

---

## Resources to Provision

### Module: `/modules/iam`
| Resource | Name | Purpose |
|----------|------|---------|
| `aws_iam_role` | `cloudpulse-app-role` | Assumed by Lambda and EC2 |
| `aws_iam_policy` | `cloudpulse-least-privilege` | Read-only CE, EC2, S3, Lambda + DynamoDB R/W |
| `aws_iam_role_policy_attachment` | - | Attach policy to role |
| `aws_iam_role` | `cloudpulse-lambda-exec` | Lambda execution role (also attaches AWSLambdaBasicExecutionRole) |

### Module: `/modules/storage`
| Resource | Name | Purpose |
|----------|------|---------|
| `aws_dynamodb_table` | `cloudpulse-costs` | Cost snapshots, pk=service sk=date |
| `aws_s3_bucket` | `cloudpulse-lambda-<random>` | Lambda deployment package storage |
| `aws_s3_bucket_versioning` | - | Enable versioning on Lambda bucket |

### Module: `/modules/compute`
| Resource | Name | Purpose |
|----------|------|---------|
| `aws_lambda_function` | `cloudpulse-poller` | Runs snapshot_costs.py every 60 min |
| `aws_cloudwatch_event_rule` | `cloudpulse-hourly` | Cron: `rate(1 hour)` |
| `aws_cloudwatch_event_target` | - | Points rule at Lambda |
| `aws_lambda_permission` | - | Allows CloudWatch Events to invoke Lambda |
| `aws_cloudwatch_log_group` | `/cloudpulse/poller` | Lambda logs, 30-day retention |

---

## Execution Scripts to Call

### 1. Bootstrap state bucket (one-time, manual)
```bash
aws s3 mb s3://<TF_STATE_BUCKET> --region <AWS_REGION>
aws s3api put-bucket-versioning \
  --bucket <TF_STATE_BUCKET> \
  --versioning-configuration Status=Enabled
```

### 2. Validate and plan
```bash
python execution/validate_terraform.py
```
This script runs `terraform validate`, then `terraform plan`, and prints a human-readable summary.

### 3. Apply
```bash
cd infra && terraform apply
```

---

## Expected Outputs
After `terraform apply` completes:

| Output | Description |
|--------|-------------|
| `lambda_arn` | ARN of the poller Lambda |
| `dynamodb_table_name` | Name of the cost snapshots table |
| `iam_role_arn` | ARN of the app IAM role |
| `lambda_bucket_name` | S3 bucket for Lambda packages |

---

## Edge Cases and Known Constraints

- **State bucket must exist before `terraform init`**: `validate_terraform.py` checks for this and prints bootstrap instructions if missing.
- **DynamoDB GSI cannot be modified after creation**: If schema changes are needed, destroy and recreate (acceptable in dev; use DynamoDB streams in prod for zero-downtime migration).
- **Lambda package must exist in S3 before apply**: The compute module references an S3 object. Upload a placeholder zip before first apply, then update with `aws lambda update-function-code`.
- **Cost Explorer is only available in `us-east-1` endpoint**: boto3 CE client must always use `us-east-1` regardless of the app's primary region.
- **Terraform destroy caution**: `terraform destroy` will delete the DynamoDB table and all cost history. Always take a backup first.
- **IAM propagation delay**: After role creation, Lambda may fail for ~10 seconds while IAM propagates. Retry logic is built into `snapshot_costs.py`.

---

## Verification Steps
1. `terraform validate` exits with code 0
2. `terraform plan` shows expected resources (no unexpected deletes)
3. `aws dynamodb describe-table --table-name cloudpulse-costs` returns table description
4. `aws lambda get-function --function-name cloudpulse-poller` returns function config
5. `aws iam get-role --role-name cloudpulse-app-role` returns role ARN

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
