terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # S3 backend for state management
  # Uncomment and configure after creating S3 bucket
  backend "s3" {
    bucket         = "corduroy-terraform-state"
    key            = "ecs-scheduled-tasks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  # Profile is set via AWS_PROFILE env var or terraform.tfvars
  # Terraform will automatically use AWS_PROFILE env var if profile is empty
  profile = var.aws_profile != "" ? var.aws_profile : null

  default_tags {
    tags = {
      Project     = "corduroy"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

