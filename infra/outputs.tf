output "lambda_arn" {
  description = "ARN of the CloudPulse poller Lambda function"
  value       = module.compute.lambda_arn
}

output "lambda_function_name" {
  description = "Name of the CloudPulse poller Lambda function"
  value       = module.compute.lambda_function_name
}

output "dynamodb_table_name" {
  description = "Name of the CloudPulse DynamoDB cost snapshots table"
  value       = module.storage.dynamodb_table_name
}

output "dynamodb_table_arn" {
  description = "ARN of the CloudPulse DynamoDB table"
  value       = module.storage.dynamodb_table_arn
}

output "iam_role_arn" {
  description = "ARN of the CloudPulse IAM application role"
  value       = module.iam.role_arn
}

output "lambda_bucket_name" {
  description = "S3 bucket used for Lambda deployment packages"
  value       = module.storage.lambda_bucket_name
}

output "log_group_name" {
  description = "CloudWatch log group for the poller Lambda"
  value       = module.compute.log_group_name
}
