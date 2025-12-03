# ECR Repository for Resort Scraper
resource "aws_ecr_repository" "resort_scraper" {
  name                 = "${var.project_name}-resort-scraper"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

# ECR Lifecycle Policy for Resort Scraper
resource "aws_ecr_lifecycle_policy" "resort_scraper" {
  repository = aws_ecr_repository.resort_scraper.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Repository for SNOTEL Scraper
resource "aws_ecr_repository" "snotel" {
  name                 = "${var.project_name}-snotel"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

# ECR Lifecycle Policy for SNOTEL Scraper
resource "aws_ecr_lifecycle_policy" "snotel" {
  repository = aws_ecr_repository.snotel.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "any"
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

