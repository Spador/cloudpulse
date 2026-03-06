variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name prefix, used for resource naming"
  type        = string
  default     = "cloudpulse"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be one of: dev, staging, production"
  }
}

variable "dynamodb_ttl_days" {
  description = "Number of days before DynamoDB cost records expire (TTL)"
  type        = number
  default     = 90

  validation {
    condition     = var.dynamodb_ttl_days >= 30 && var.dynamodb_ttl_days <= 365
    error_message = "dynamodb_ttl_days must be between 30 and 365"
  }
}

variable "lambda_log_retention_days" {
  description = "CloudWatch log retention in days for the Lambda poller"
  type        = number
  default     = 30
}

variable "cost_snapshot_days" {
  description = "Number of past days the Lambda poller fetches from Cost Explorer"
  type        = number
  default     = 90
}

variable "anomaly_threshold" {
  description = "Fractional cost spike threshold for anomaly detection (0.20 = 20%)"
  type        = string
  default     = "0.20"
}
