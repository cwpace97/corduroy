output "ecr_resort_scraper_repository_url" {
  description = "URL of the resort scraper ECR repository"
  value       = aws_ecr_repository.resort_scraper.repository_url
}

output "ecr_snotel_repository_url" {
  description = "URL of the SNOTEL scraper ECR repository"
  value       = aws_ecr_repository.snotel.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "resort_scraper_task_definition_arn" {
  description = "ARN of the resort scraper task definition"
  value       = aws_ecs_task_definition.resort_scraper.arn
}

output "snotel_scraper_task_definition_arn" {
  description = "ARN of the SNOTEL scraper task definition"
  value       = aws_ecs_task_definition.snotel.arn
}

output "eventbridge_resort_rule_arn" {
  description = "ARN of the EventBridge rule for resort scraper"
  value       = aws_cloudwatch_event_rule.resort_scraper.arn
}

output "eventbridge_snotel_rule_arn" {
  description = "ARN of the EventBridge rule for SNOTEL scraper"
  value       = aws_cloudwatch_event_rule.snotel.arn
}

output "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

