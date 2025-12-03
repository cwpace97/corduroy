variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile to use (optional, defaults to default profile or AWS_PROFILE env var)"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Environment name (e.g., prod, staging)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "corduroy"
}

variable "vpc_id" {
  description = "VPC ID where EC2 instance is located"
  type        = string
}

variable "ec2_security_group_id" {
  description = "Security group ID of the EC2 instance running PostgreSQL"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks (can be public or private)"
  type        = list(string)
}

variable "database_url_secret_name" {
  description = "Name of the Secrets Manager secret containing DATABASE_URL"
  type        = string
  default     = "corduroy/database-url"
}

variable "resort_scraper_cpu" {
  description = "CPU units for resort scraper task (1024 = 1 vCPU)"
  type        = number
  default     = 1024 # 2 vCPU
}

variable "resort_scraper_memory" {
  description = "Memory in MB for resort scraper task"
  type        = number
  default     = 2048 # 4 GB
}

variable "snotel_scraper_cpu" {
  description = "CPU units for SNOTEL scraper task (1024 = 1 vCPU)"
  type        = number
  default     = 256 # 0.25 vCPU
}

variable "snotel_scraper_memory" {
  description = "Memory in MB for SNOTEL scraper task"
  type        = number
  default     = 512 # 512 MB
}

variable "assign_public_ip" {
  description = "Whether to assign public IP to ECS tasks (needed if using public subnets without NAT)"
  type        = bool
  default     = true
}

variable "forecast_scraper_cpu" {
  description = "CPU units for forecast scraper task (1024 = 1 vCPU)"
  type        = number
  default     = 256 # 0.25 vCPU
}

variable "forecast_scraper_memory" {
  description = "Memory in MB for forecast scraper task"
  type        = number
  default     = 512 # 512 MB
}

