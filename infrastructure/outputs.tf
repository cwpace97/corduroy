# ECR Repository URLs
output "ecr_resort_scraper_repository_url" {
  description = "URL of the resort scraper ECR repository"
  value       = aws_ecr_repository.resort_scraper.repository_url
}

output "ecr_snotel_repository_url" {
  description = "URL of the SNOTEL scraper ECR repository"
  value       = aws_ecr_repository.snotel.repository_url
}

output "ecr_forecast_repository_url" {
  description = "URL of the forecast scraper ECR repository"
  value       = aws_ecr_repository.forecast.repository_url
}

# ECS Resources
output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_resort_scraper_task_definition_arn" {
  description = "ARN of the resort scraper ECS task definition"
  value       = aws_ecs_task_definition.resort_scraper.arn
}

# Lambda Function ARNs
output "snotel_function_arn" {
  description = "ARN of the SNOTEL Lambda function"
  value       = aws_lambda_function.snotel.arn
}

output "forecast_function_arn" {
  description = "ARN of the forecast Lambda function"
  value       = aws_lambda_function.forecast.arn
}

# EventBridge Rule ARNs
output "eventbridge_resort_scraper_rule_arn" {
  description = "ARN of the EventBridge rule for resort scraper"
  value       = aws_cloudwatch_event_rule.resort_scraper.arn
}

output "eventbridge_snotel_rule_arn" {
  description = "ARN of the EventBridge rule for SNOTEL scraper"
  value       = aws_cloudwatch_event_rule.snotel.arn
}

output "eventbridge_forecast_rule_arn" {
  description = "ARN of the EventBridge rule for forecast scraper"
  value       = aws_cloudwatch_event_rule.forecast.arn
}

# Security Groups
output "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}
