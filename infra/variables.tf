variable "project" {
  default = "nasa-space-activity"
}

variable "env" {
  default = "dev"
}

variable "aws_region" {
  default = "ap-northeast-1"
}

data "aws_caller_identity" "current" {}

resource "random_id" "suffix" {
  byte_length = 4
}

variable "nasa_api_key" {
  description = "NASA API Key for accessing NASA's APIs"
  type        = string
  sensitive   = true
}

variable "enrichment_service_api_url" {
  description = "API URL for the enrichment service"
  type        = string
  default     = "https://enrichment-service.sfdw802c78hbe.ap-northeast-1.cs.amazonlightsail.com"
}

variable "enrichment_service_api_key" {
  description = "API key for the enrichment service"
  type        = string
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "Permanent AWS Access Key ID for the enrichment service"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "Permanent AWS Secret Access Key for the enrichment service"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "RDS Database username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "RDS Database password"
  type        = string
  sensitive   = true
}

variable "alert_email" {
  description = "Email to receive notifications about failed Glue jobs"
  type        = string
  sensitive   = true
}
