output "lambda_arn" {
  description = "ARN of the CloudPulse poller Lambda function"
  value       = aws_lambda_function.poller.arn
}

output "lambda_function_name" {
  description = "Name of the poller Lambda function"
  value       = aws_lambda_function.poller.function_name
}

output "cloudwatch_rule_arn" {
  description = "ARN of the hourly CloudWatch Events rule"
  value       = aws_cloudwatch_event_rule.hourly.arn
}

output "log_group_name" {
  description = "CloudWatch log group name for the poller"
  value       = aws_cloudwatch_log_group.poller.name
}
