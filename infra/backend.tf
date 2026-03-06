# Remote state — S3 backend.
# The bucket must exist before running `terraform init`.
# See execution/validate_terraform.py for bootstrap instructions.

terraform {
  backend "s3" {
    # These values are passed via -backend-config flags in CI/CD
    # or via terraform init -backend-config=...
    # bucket = var.tf_state_bucket  <-- not allowed here; use -backend-config
    key    = "cloudpulse/terraform.tfstate"
    region = "us-east-1"

    # Enable state locking via DynamoDB (optional but recommended)
    # dynamodb_table = "cloudpulse-tf-lock"
    encrypt = true
  }
}
