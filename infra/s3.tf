# Store job scripts
resource "aws_s3_bucket" "nasa_pipeline_code" {
  bucket = "${local.name-prefix}-code"
}

# Data layers
resource "aws_s3_bucket" "nasa_bronze_bucket" {
  bucket = "${local.name-prefix}-bronze"
}

resource "aws_s3_bucket_policy" "allow_public_image_access" {
  bucket = aws_s3_bucket.nasa_bronze_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadOnlyForImageFolder"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.nasa_bronze_bucket.arn}/*/image/*"
      }
    ]
  })
}

resource "aws_s3_bucket_cors_configuration" "bronze_cors" {
  bucket = aws_s3_bucket.nasa_bronze_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    expose_headers = []
    max_age_seconds = 3000
  }
}


resource "aws_s3_bucket" "nasa_silver_bucket" {
  bucket = "${local.name-prefix}-silver"
}

resource "aws_s3_bucket" "nasa_gold_bucket" {
  bucket = "${local.name-prefix}-gold"
}

# Extract jobs
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

resource "aws_s3_object" "extract_neo_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/extract_neo.py"
  source = "${path.module}/../etl/extract/neo.py"
  etag = filemd5("${path.module}/../etl/extract/neo.py")
}

# Transform jobs
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

# Enrich jobs
resource "aws_s3_object" "enrich_apod_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/enrich_apod.py"
  source = "${path.module}/../etl/enrich/apod.py"
  etag = filemd5("${path.module}/../etl/enrich/apod.py")
}

resource "aws_s3_object" "enrich_mars_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/enrich_mars.py"
  source = "${path.module}/../etl/enrich/mars.py"
  etag = filemd5("${path.module}/../etl/enrich/mars.py")
}

resource "aws_s3_object" "enrich_neo_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/enrich_neo.py"
  source = "${path.module}/../etl/enrich/neo.py"
  etag = filemd5("${path.module}/../etl/enrich/neo.py")
}

# Load jobs
resource "aws_s3_object" "load_apod_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/load_apod.py"
  source = "${path.module}/../etl/load/apod.py"
  etag = filemd5("${path.module}/../etl/load/apod.py")
}

resource "aws_s3_object" "load_mars_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/load_mars.py"
  source = "${path.module}/../etl/load/mars.py"
  etag = filemd5("${path.module}/../etl/load/mars.py")
}

resource "aws_s3_object" "load_neo_script" {
  bucket = aws_s3_bucket.nasa_pipeline_code.bucket
  key    = "jobs/load_neo.py"
  source = "${path.module}/../etl/load/neo.py"
  etag = filemd5("${path.module}/../etl/load/neo.py")
}