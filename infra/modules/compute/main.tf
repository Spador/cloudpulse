locals {
  name_prefix      = "${var.app_name}-${var.environment}"
  lambda_zip_key   = "cloudpulse-poller.zip"
  function_name    = "${var.app_name}-poller"
}

# ─── CloudWatch Log Group ─────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "poller" {
  name              = "/cloudpulse/poller"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "/cloudpulse/poller"
    Environment = var.environment
  }
}

# ─── Lambda Function ──────────────────────────────────────────────────────────

resource "aws_lambda_function" "poller" {
  function_name = local.function_name
  description   = "CloudPulse hourly cost snapshot poller"
  role          = var.lambda_role_arn
  runtime       = "python3.11"
  handler       = "snapshot_costs.lambda_handler"
  timeout       = 300  # 5 minutes max
  memory_size   = 256

  # Package must be uploaded to S3 before first apply
  # CI/CD handles this via: aws lambda update-function-code
  s3_bucket = var.lambda_bucket
  s3_key    = local.lambda_zip_key

  environment {
    variables = {
      AWS_REGION            = var.aws_region
      DYNAMODB_TABLE_NAME   = var.dynamodb_table_name
      COST_SNAPSHOT_DAYS    = tostring(var.cost_snapshot_days)
      ANOMALY_THRESHOLD     = var.anomaly_threshold
      LOG_LEVEL             = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.poller]

  tags = {
    Name        = local.function_name
    Environment = var.environment
  }
}

# ─── CloudWatch Events Rule (hourly trigger) ──────────────────────────────────

resource "aws_cloudwatch_event_rule" "hourly" {
  name                = "${local.name_prefix}-hourly-cost-snapshot"
  description         = "Triggers CloudPulse cost snapshot Lambda every hour"
  schedule_expression = "rate(1 hour)"
  state               = "ENABLED"

  tags = {
    Name        = "${local.name_prefix}-hourly"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "poller" {
  rule      = aws_cloudwatch_event_rule.hourly.name
  target_id = "CloudPulsePollerTarget"
  arn       = aws_lambda_function.poller.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.poller.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly.arn
}
