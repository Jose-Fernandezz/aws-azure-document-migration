# ------------------------------------------------------------
# ECS TASK EXECUTION ROLE
# Used by ECS/Fargate itself to start the container.
# ------------------------------------------------------------

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ecs-task-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# ------------------------------------------------------------
# ECS TASK ROLE
# Used by the Flask application while the container is running.
# ------------------------------------------------------------

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ecs-task-role"
  }
}


# ------------------------------------------------------------
# S3 DOCUMENT ACCESS POLICY
# Gives the application access only to its document bucket.
# ------------------------------------------------------------

resource "aws_iam_policy" "s3_documents" {
  name        = "${var.project_name}-s3-documents-policy"
  description = "Allows the document management application to access its S3 document bucket"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ListDocumentBucket"
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = aws_s3_bucket.documents.arn
      },
      {
        Sid    = "ManageDocumentObjects"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = "${aws_s3_bucket.documents.arn}/*"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-s3-documents-policy"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.s3_documents.arn
}


# ------------------------------------------------------------
# SECRETS MANAGER ACCESS
# Allows ECS to retrieve the RDS DATABASE_URL secret.
# ------------------------------------------------------------

resource "aws_iam_policy" "ecs_secrets_access" {
  name        = "${var.project_name}-ecs-secrets-access"
  description = "Allow ECS task execution role to retrieve the application database URL"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue"
        ]

        Resource = [
          aws_secretsmanager_secret.database_url.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_access" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_secrets_access.arn
}


# ------------------------------------------------------------
# ECS EXEC / SSM MESSAGES ACCESS
# Allows ECS Exec to establish an interactive shell session
# with the running Fargate container.
# ------------------------------------------------------------

resource "aws_iam_role_policy" "ecs_exec" {
  name = "${var.project_name}-ecs-exec-policy"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]

        Resource = "*"
      }
    ]
  })
}