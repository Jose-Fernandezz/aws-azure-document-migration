resource "aws_secretsmanager_secret" "database_url" {
  name        = "${var.project_name}/database-url"
  description = "PostgreSQL connection URL for the document management application"

  tags = {
    Name = "${var.project_name}-database-url"
  }
}