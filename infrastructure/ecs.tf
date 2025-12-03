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
resource "aws_cloudwatch_log_group" "resort_scraper" {
  name              = "/ecs/${var.project_name}/resort-scraper"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-resort-scraper-logs"
  }
}

# CloudWatch Log Group for SNOTEL Scraper
resource "aws_cloudwatch_log_group" "snotel" {
  name              = "/ecs/${var.project_name}/snotel"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-snotel-logs"
  }
}

# CloudWatch Log Group for Forecast Scraper
resource "aws_cloudwatch_log_group" "forecast" {
  name              = "/ecs/${var.project_name}/forecast"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-forecast-logs"
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
          "awslogs-group"         = aws_cloudwatch_log_group.resort_scraper.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      # Health check is optional for one-time tasks
      # But we can add it for monitoring
    }
  ])

  tags = {
    Name = "${var.project_name}-resort-scraper-task"
  }
}

# ECS Task Definition for SNOTEL Scraper
resource "aws_ecs_task_definition" "snotel" {
  family                   = "${var.project_name}-snotel"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.snotel_scraper_cpu
  memory                   = var.snotel_scraper_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "snotel-scraper"
      image = "${aws_ecr_repository.snotel.repository_url}:latest"

      essential = true

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = local.database_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.snotel.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-snotel-task"
  }
}

# ECS Task Definition for Forecast Scraper
resource "aws_ecs_task_definition" "forecast" {
  family                   = "${var.project_name}-forecast"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.forecast_scraper_cpu
  memory                   = var.forecast_scraper_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "forecast-scraper"
      image = "${aws_ecr_repository.forecast.repository_url}:latest"

      essential = true

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = local.database_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.forecast.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-forecast-task"
  }
}

