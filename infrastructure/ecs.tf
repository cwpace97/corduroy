# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-cluster"
  }
}

# CloudWatch Log Group for Resort Scraper
resource "aws_cloudwatch_log_group" "resort_scraper_ecs" {
  name              = "/ecs/${var.project_name}/resort-scraper"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-resort-scraper-logs"
  }
}

# ECS Task Definition for Resort Scraper
resource "aws_ecs_task_definition" "resort_scraper" {
  family                   = "${var.project_name}-resort-scraper"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.resort_scraper_cpu
  memory                   = var.resort_scraper_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "resort-scraper"
      image = "${aws_ecr_repository.resort_scraper.repository_url}:latest"

      essential = true

      environment = [
        {
          name  = "SELENIUM_HOST"
          value = "local"
        }
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = local.database_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.resort_scraper_ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-resort-scraper-task"
  }
}

