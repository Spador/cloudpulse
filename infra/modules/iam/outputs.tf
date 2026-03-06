output "role_arn" {
  description = "ARN of the CloudPulse app IAM role"
  value       = aws_iam_role.app_role.arn
}

output "role_name" {
  description = "Name of the CloudPulse app IAM role"
  value       = aws_iam_role.app_role.name
}

output "policy_arn" {
  description = "ARN of the CloudPulse least-privilege IAM policy"
  value       = aws_iam_policy.least_privilege.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_exec.arn
}
