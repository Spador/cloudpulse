variable "app_name" {
  description = "Application name prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "dynamodb_ttl_days" {
  description = "Days before DynamoDB records expire"
  type        = number
  default     = 90
}
