resource "aws_s3_bucket" "nasa_bronze_bucket" {
  bucket = "${local.name-prefix}-bronze"
}

resource "aws_s3_bucket" "nasa_silver_bucket" {
  bucket = "${local.name-prefix}-silver"
}