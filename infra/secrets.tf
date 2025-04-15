resource "aws_secretsmanager_secret" "nasa_api_key" {
  name        = "nasa_API_key"
  description = "NASA API Key for accessing NASA's APIs"
}

resource "aws_secretsmanager_secret_version" "nasa_api_key_value" {
  secret_id     = aws_secretsmanager_secret.nasa_api_key.id
  secret_string = var.nasa_api_key
}