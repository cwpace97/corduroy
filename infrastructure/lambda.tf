# CloudWatch Log Groups for Lambda Functions
resource "aws_cloudwatch_log_group" "snotel" {
  name              = "/aws/lambda/${var.project_name}-snotel"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-snotel-logs"
  }
}

resource "aws_cloudwatch_log_group" "forecast" {
  name              = "/aws/lambda/${var.project_name}-forecast"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-forecast-logs"
  }
}

resource "aws_cloudwatch_log_group" "historical_weather" {
  name              = "/aws/lambda/${var.project_name}-historical-weather"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-historical-weather-logs"
  }
}

# IAM Role for Lambda Execution (used by all Lambda functions)
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-execution-role"
  }
}

# IAM Policy for Lambda basic execution (CloudWatch Logs)
resource "aws_iam_role_policy" "lambda_basic_execution" {
  name = "${var.project_name}-lambda-basic-execution"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          aws_cloudwatch_log_group.snotel.arn,
          "${aws_cloudwatch_log_group.snotel.arn}:*",
          aws_cloudwatch_log_group.forecast.arn,
          "${aws_cloudwatch_log_group.forecast.arn}:*",
          aws_cloudwatch_log_group.historical_weather.arn,
          "${aws_cloudwatch_log_group.historical_weather.arn}:*"
        ]
      }
    ]
  })
}

# IAM Policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_secrets_access" {
  name = "${var.project_name}-lambda-secrets-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          local.database_secret_arn
        ]
      }
    ]
  })
}

# IAM Policy for ECR access (for Lambda to pull container images)
resource "aws_iam_role_policy" "lambda_ecr_access" {
  name = "${var.project_name}-lambda-ecr-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = [
          aws_ecr_repository.snotel.arn,
          aws_ecr_repository.forecast.arn,
          aws_ecr_repository.historical_weather.arn
        ]
      }
    ]
  })
}

# Lambda Function: SNOTEL
resource "aws_lambda_function" "snotel" {
  function_name = "${var.project_name}-snotel"
  role          = aws_iam_role.lambda_execution.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.snotel.repository_url}:latest"

  timeout     = var.snotel_timeout
  memory_size = var.snotel_memory

  environment {
    variables = {
      DATABASE_URL_SECRET_NAME = var.database_url_secret_name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_basic_execution,
    aws_iam_role_policy.lambda_ecr_access,
    aws_iam_role_policy.lambda_secrets_access,
    aws_cloudwatch_log_group.snotel
  ]

  tags = {
    Name = "${var.project_name}-snotel"
  }
}

# Lambda Function: Forecast
resource "aws_lambda_function" "forecast" {
  function_name = "${var.project_name}-forecast"
  role          = aws_iam_role.lambda_execution.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.forecast.repository_url}:latest"

  timeout     = var.forecast_timeout
  memory_size = var.forecast_memory

  environment {
    variables = {
      DATABASE_URL_SECRET_NAME = var.database_url_secret_name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_basic_execution,
    aws_iam_role_policy.lambda_ecr_access,
    aws_iam_role_policy.lambda_secrets_access,
    aws_cloudwatch_log_group.forecast
  ]

  tags = {
    Name = "${var.project_name}-forecast"
  }
}

# Lambda Function: Historical Weather
resource "aws_lambda_function" "historical_weather" {
  function_name = "${var.project_name}-historical-weather"
  role          = aws_iam_role.lambda_execution.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.historical_weather.repository_url}:latest"

  timeout     = var.historical_weather_timeout
  memory_size = var.historical_weather_memory

  environment {
    variables = {
      DATABASE_URL_SECRET_NAME = var.database_url_secret_name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_basic_execution,
    aws_iam_role_policy.lambda_ecr_access,
    aws_iam_role_policy.lambda_secrets_access,
    aws_cloudwatch_log_group.historical_weather
  ]

  tags = {
    Name = "${var.project_name}-historical-weather"
  }
}

