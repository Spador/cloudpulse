locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

# ─── App Role (assumed by EC2 / ECS / manual use) ─────────────────────────────

data "aws_iam_policy_document" "app_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app_role" {
  name               = "${local.name_prefix}-app-role"
  assume_role_policy = data.aws_iam_policy_document.app_assume_role.json

  tags = {
    Name = "${local.name_prefix}-app-role"
  }
}

# ─── Least-Privilege Policy ───────────────────────────────────────────────────

data "aws_iam_policy_document" "least_privilege" {
  statement {
    sid    = "CostExplorerReadOnly"
    effect = "Allow"
    actions = [
      "ce:GetCostAndUsage",
      "ce:GetCostForecast",
      "ce:GetDimensionValues",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "EC2ReadOnly"
    effect = "Allow"
    actions = [
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeRegions",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "S3ListOnly"
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucketLocation",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "LambdaReadOnly"
    effect = "Allow"
    actions = [
      "lambda:ListFunctions",
      "lambda:GetFunction",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "DynamoDBReadWrite"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem",
    ]
    resources = [
      var.dynamodb_table_arn,
      "${var.dynamodb_table_arn}/index/*",
    ]
  }

  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:log-group:/cloudpulse/*"]
  }
}

resource "aws_iam_policy" "least_privilege" {
  name        = "${local.name_prefix}-least-privilege"
  description = "Least-privilege policy for CloudPulse app (Cost Explorer, EC2, S3, Lambda read + DynamoDB R/W)"
  policy      = data.aws_iam_policy_document.least_privilege.json
}

resource "aws_iam_role_policy_attachment" "app_role_attach" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.least_privilege.arn
}

# ─── Lambda Execution Role ────────────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name               = "${local.name_prefix}-lambda-exec"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Name = "${local.name_prefix}-lambda-exec"
  }
}

# Attach the same least-privilege policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_exec_app_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.least_privilege.arn
}

# Allow Lambda to write logs
resource "aws_iam_role_policy_attachment" "lambda_basic_exec" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
