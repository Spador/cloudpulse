variable "app_name" {
  description = "Application name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "lambda_role_arn" {
  description = "IAM role ARN for the Lambda function"
  type        = string
}

variable "lambda_bucket" {
  description = "S3 bucket containing the Lambda deployment package"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for cost snapshots"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "cost_snapshot_days" {
  description = "Days back to fetch from Cost Explorer"
  type        = number
  default     = 90
}

variable "anomaly_threshold" {
  description = "Fractional spike threshold"
  type        = string
  default     = "0.20"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}
