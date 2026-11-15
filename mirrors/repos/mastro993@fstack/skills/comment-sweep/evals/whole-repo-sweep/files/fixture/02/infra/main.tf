terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }

  backend "s3" {
    bucket = "northwind-tfstate"
    key    = "wxdata/terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = var.region
}

locals {
  name = "${var.env}-wxdata"
  tags = {
    service     = "wxdata"
    environment = var.env
    owner       = "data-platform"
  }
}

// Create the bucket
resource "aws_s3_bucket" "reports" {
  bucket = "${local.name}-reports"
  tags   = local.tags
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "expire-old-reports"
    status = "Enabled"

    filter {
      prefix = "daily/"
    }

    expiration {
      days = var.report_retention_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_db_subnet_group" "readings" {
  name       = "${local.name}-db"
  subnet_ids = var.private_subnet_ids
  tags       = local.tags
}

resource "aws_db_instance" "readings" {
  identifier = "${local.name}-readings"
  engine     = "postgres"
  # Postgres version
  engine_version = "16.3"
  /* Changed from db.t3.small to db.t3.medium last week */
  instance_class              = "db.t3.medium"
  allocated_storage           = 100
  max_allocated_storage       = 500
  db_name                     = "wxdata"
  username                    = "wx"
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.readings.name
  backup_retention_period     = 14
  deletion_protection         = true
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${local.name}-readings-final"
  tags                        = local.tags
}

output "reports_bucket" {
  value = aws_s3_bucket.reports.bucket
}

output "database_endpoint" {
  value = aws_db_instance.readings.endpoint
}
