# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks"
  description = "Security group for ECS Fargate tasks"
  vpc_id      = var.vpc_id

  # Outbound: Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-tasks"
  }
}

# Security Group Rule: Allow ECS tasks to connect to EC2 PostgreSQL
resource "aws_security_group_rule" "ecs_to_ec2_postgres" {
  type                     = "egress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = var.ec2_security_group_id
  security_group_id        = aws_security_group.ecs_tasks.id
  description              = "Allow ECS tasks to connect to EC2 PostgreSQL"
}

# Security Group Rule: Allow EC2 to accept connections from ECS tasks
resource "aws_security_group_rule" "ec2_from_ecs_postgres" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.ecs_tasks.id
  security_group_id        = var.ec2_security_group_id
  description              = "Allow EC2 PostgreSQL to accept connections from ECS tasks"
}

