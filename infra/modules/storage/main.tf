locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# ─── DynamoDB Table ───────────────────────────────────────────────────────────

resource "aws_dynamodb_table" "cost_snapshots" {
  name         = "${var.app_name}-costs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "cost"
    type = "N"
  }

  # TTL — items expire after dynamodb_ttl_days
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # GSI: query by date, sorted by cost
  global_secondary_index {
    name            = "DateIndex"
    hash_key        = "date"
    range_key       = "cost"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.app_name}-costs"
    Environment = var.environment
  }
}

# ─── S3 Bucket for Lambda Deployment Packages ─────────────────────────────────

resource "aws_s3_bucket" "lambda_packages" {
  bucket        = "${local.name_prefix}-lambda-${random_id.bucket_suffix.hex}"
  force_destroy = true  # Allow destroy even if bucket contains objects

  tags = {
    Name        = "${local.name_prefix}-lambda-packages"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "lambda_packages" {
  bucket = aws_s3_bucket.lambda_packages.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_packages" {
  bucket = aws_s3_bucket.lambda_packages.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lambda_packages" {
  bucket = aws_s3_bucket.lambda_packages.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
