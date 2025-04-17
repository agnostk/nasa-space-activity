resource "aws_s3_bucket" "nasa_pipeline_code" {
  bucket = "${local.name-prefix}-code"
}

resource "aws_s3_bucket" "nasa_bronze_bucket" {
  bucket = "${local.name-prefix}-bronze"
}

resource "aws_s3_bucket" "nasa_silver_bucket" {
  bucket = "${local.name-prefix}-silver"
}

resource "aws_s3_object" "transform_apod_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/transform-apod.py"
  source = "${path.module}/../etl/transform/apod.py"
  etag = filemd5("${path.module}/../etl/transform/apod.py")
}