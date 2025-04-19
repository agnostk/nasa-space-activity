resource "aws_s3_bucket" "nasa_pipeline_code" {
  bucket = "${local.name-prefix}-code"
}

resource "aws_s3_bucket" "nasa_bronze_bucket" {
  bucket = "${local.name-prefix}-bronze"
}

resource "aws_s3_bucket" "nasa_silver_bucket" {
  bucket = "${local.name-prefix}-silver"
}

resource "aws_s3_object" "extract_apod_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/extract_apod.py"
  source = "${path.module}/../etl/extract/apod.py"
  etag = filemd5("${path.module}/../etl/extract/apod.py")
}

resource "aws_s3_object" "extract_mars_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/extract_mars.py"
  source = "${path.module}/../etl/extract/mars.py"
  etag = filemd5("${path.module}/../etl/extract/mars.py")
}

resource "aws_s3_object" "transform_apod_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/transform_apod.py"
  source = "${path.module}/../etl/transform/apod.py"
  etag = filemd5("${path.module}/../etl/transform/apod.py")
}

resource "aws_s3_object" "transform_neo_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/transform_neo.py"
  source = "${path.module}/../etl/transform/neo.py"
  etag = filemd5("${path.module}/../etl/transform/neo.py")
}

resource "aws_s3_object" "transform_mars_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/transform_mars.py"
  source = "${path.module}/../etl/transform/mars.py"
  etag = filemd5("${path.module}/../etl/transform/mars.py")
}