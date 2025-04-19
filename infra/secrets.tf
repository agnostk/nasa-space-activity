resource "aws_secretsmanager_secret" "nasa_api_key" {
  name        = "${local.name-prefix}-nasa-api-key"
  description = "NASA API Key for accessing NASA's APIs"
}

resource "aws_secretsmanager_secret_version" "nasa_api_key_value" {
  secret_id     = aws_secretsmanager_secret.nasa_api_key.id
  secret_string = var.nasa_api_key
}

resource "aws_secretsmanager_secret" "postgresql_password" {
  name        = "${local.name-prefix}-postgresql-password"
  description = "PostgreSQL password for the RDS instance"
}

resource "aws_secretsmanager_secret_version" "postgresql_password_value" {
  secret_id     = aws_secretsmanager_secret.postgresql_password.id
  secret_string = var.db_password
}