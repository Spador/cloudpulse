provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cloudpulse"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ─── IAM Module ──────────────────────────────────────────────────────────────

module "iam" {
  source = "./modules/iam"

  app_name             = var.app_name
  environment          = var.environment
  dynamodb_table_arn   = module.storage.dynamodb_table_arn
}

# ─── Storage Module ───────────────────────────────────────────────────────────

module "storage" {
  source = "./modules/storage"

  app_name          = var.app_name
  environment       = var.environment
  dynamodb_ttl_days = var.dynamodb_ttl_days
}

# ─── Compute Module ───────────────────────────────────────────────────────────

module "compute" {
  source = "./modules/compute"

  app_name                  = var.app_name
  environment               = var.environment
  lambda_role_arn           = module.iam.lambda_role_arn
  lambda_bucket             = module.storage.lambda_bucket_name
  dynamodb_table_name       = module.storage.dynamodb_table_name
  aws_region                = var.aws_region
  cost_snapshot_days        = var.cost_snapshot_days
  anomaly_threshold         = var.anomaly_threshold
  log_retention_days        = var.lambda_log_retention_days

  depends_on = [module.iam, module.storage]
}
