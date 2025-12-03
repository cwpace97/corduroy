# EventBridge Rule for Resort Scraper (5 AM MT = 12:00 UTC daily)
resource "aws_cloudwatch_event_rule" "resort_scraper" {
  name                = "${var.project_name}-resort-scraper-schedule"
  description         = "Trigger resort scraper daily at 5 AM MT (12:00 UTC)"
  schedule_expression = "cron(0 12 * * ? *)" # 12:00 UTC = 5:00 AM MT (during standard time)

  tags = {
    Name = "${var.project_name}-resort-scraper-schedule"
  }
}

# EventBridge Target for Resort Scraper (ECS Task)
resource "aws_cloudwatch_event_target" "resort_scraper" {
  rule      = aws_cloudwatch_event_rule.resort_scraper.name
  target_id = "${var.project_name}-resort-scraper-target"
  arn       = aws_ecs_cluster.main.arn
  role_arn  = aws_iam_role.eventbridge_ecs.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.resort_scraper.arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [aws_security_group.ecs_tasks.id]
      assign_public_ip = var.assign_public_ip
    }
  }
}

# EventBridge Rule for SNOTEL Scraper (once daily at 6 AM MT = 13:00 UTC)
resource "aws_cloudwatch_event_rule" "snotel" {
  name                = "${var.project_name}-snotel-schedule"
  description         = "Trigger SNOTEL scraper daily at 6 AM MT (13:00 UTC)"
  schedule_expression = "cron(0 13 * * ? *)" # 13:00 UTC = 6:00 AM MT (during standard time)

  tags = {
    Name = "${var.project_name}-snotel-schedule"
  }
}

# EventBridge Target for SNOTEL Scraper
resource "aws_cloudwatch_event_target" "snotel" {
  rule      = aws_cloudwatch_event_rule.snotel.name
  target_id = "${var.project_name}-snotel-target"
  arn       = aws_lambda_function.snotel.arn
}

# EventBridge Rule for Forecast Scraper (every 6 hours)
resource "aws_cloudwatch_event_rule" "forecast" {
  name                = "${var.project_name}-forecast-schedule"
  description         = "Trigger forecast scraper every 6 hours"
  schedule_expression = "cron(0 0/6 * * ? *)" # Every 6 hours at minute 0 (0, 6, 12, 18 UTC)

  tags = {
    Name = "${var.project_name}-forecast-schedule"
  }
}

# EventBridge Target for Forecast Scraper
resource "aws_cloudwatch_event_target" "forecast" {
  rule      = aws_cloudwatch_event_rule.forecast.name
  target_id = "${var.project_name}-forecast-target"
  arn       = aws_lambda_function.forecast.arn
}

# IAM Role for EventBridge to run ECS tasks
resource "aws_iam_role" "eventbridge_ecs" {
  name = "${var.project_name}-eventbridge-ecs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-eventbridge-ecs-role"
  }
}

# IAM Policy for EventBridge to run ECS tasks
resource "aws_iam_role_policy" "eventbridge_ecs" {
  name = "${var.project_name}-eventbridge-ecs-policy"
  role = aws_iam_role.eventbridge_ecs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = [
          aws_ecs_task_definition.resort_scraper.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_task_execution.arn,
          aws_iam_role.ecs_task.arn
        ]
      }
    ]
  })
}

# IAM Permission for EventBridge to invoke Lambda functions
resource "aws_lambda_permission" "snotel_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.snotel.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.snotel.arn
}

resource "aws_lambda_permission" "forecast_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.forecast.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.forecast.arn
}

# EventBridge Rule for Historical Weather (once daily at 6 AM MT = 13:00 UTC)
resource "aws_cloudwatch_event_rule" "historical_weather" {
  name                = "${var.project_name}-historical-weather-schedule"
  description         = "Trigger historical weather scraper daily at 6 AM MT (13:00 UTC)"
  schedule_expression = "cron(0 13 * * ? *)" # 13:00 UTC = 6:00 AM MT (during standard time)

  tags = {
    Name = "${var.project_name}-historical-weather-schedule"
  }
}

# EventBridge Target for Historical Weather
resource "aws_cloudwatch_event_target" "historical_weather" {
  rule      = aws_cloudwatch_event_rule.historical_weather.name
  target_id = "${var.project_name}-historical-weather-target"
  arn       = aws_lambda_function.historical_weather.arn
}

resource "aws_lambda_permission" "historical_weather_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.historical_weather.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.historical_weather.arn
}
