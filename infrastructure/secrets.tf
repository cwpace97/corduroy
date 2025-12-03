# Data source to reference existing secret
# Since the secret already exists, we'll reference it instead of creating it
data "aws_secretsmanager_secret" "database_url" {
  name = var.database_url_secret_name
}

# If you need to create the secret instead, uncomment this and comment out the data source above
# resource "aws_secretsmanager_secret" "database_url" {
#   name        = var.database_url_secret_name
#   description = "PostgreSQL database connection URL for Corduroy application"
# 
#   recovery_window_in_days = 0
# 
#   tags = {
#     Name = "${var.project_name}-database-url"
#   }
# }

# Use the data source (existing secret) or resource (new secret)
locals {
  database_secret_id  = data.aws_secretsmanager_secret.database_url.id
  database_secret_arn = data.aws_secretsmanager_secret.database_url.arn
}

