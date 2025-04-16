variable "project" {
  default = "nasa-space-activity"
}

variable "env" {
  default = "dev"
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