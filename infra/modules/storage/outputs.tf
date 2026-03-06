output "dynamodb_table_name" {
  description = "Name of the DynamoDB cost snapshots table"
  value       = aws_dynamodb_table.cost_snapshots.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB cost snapshots table"
  value       = aws_dynamodb_table.cost_snapshots.arn
}

output "lambda_bucket_name" {
  description = "S3 bucket name for Lambda deployment packages"
  value       = aws_s3_bucket.lambda_packages.bucket
}

output "lambda_bucket_arn" {
  description = "S3 bucket ARN for Lambda deployment packages"
  value       = aws_s3_bucket.lambda_packages.arn
}
