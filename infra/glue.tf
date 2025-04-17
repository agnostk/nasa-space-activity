resource "aws_glue_catalog_database" "nasa_bronze_catalog" {
  name        = "${local.name-prefix}-bronze-catalog"
  description = "Bronze layer for NASA data"
}

resource "aws_glue_crawler" "nasa_bronze_apod_crawler" {
  name          = "${local.name-prefix}-bronze-apod-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_bronze_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_bronze_bucket.id}/apod/"
    exclusions = ["**/image/**", "**/raw/*"]
  }

  configuration = jsonencode({
    "Version" = 1.0
    "CrawlerOutput" = {
      "Partitions" = {
        "AddOrUpdateBehavior" = "InheritFromTable"
      }
    },
    Grouping = {
      "TableGroupingPolicy" = "CombineCompatibleSchemas"
    }
  })

  schema_change_policy {
    update_behavior = "LOG"
    delete_behavior = "LOG"
  }
}

resource "aws_glue_crawler" "nasa_bronze_neo_crawler" {
  name          = "${local.name-prefix}-bronze-neo-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_bronze_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_bronze_bucket.id}/neo/"
  }

  configuration = jsonencode({
    "Version" = 1.0
    "CrawlerOutput" = {
      "Partitions" = {
        "AddOrUpdateBehavior" = "InheritFromTable"
      }
    },
    Grouping = {
      "TableGroupingPolicy" = "CombineCompatibleSchemas"
    }
  })

  schema_change_policy {
    update_behavior = "LOG"
    delete_behavior = "LOG"
  }
}

resource "aws_glue_crawler" "nasa_bronze_mars_crawler" {
  name          = "${local.name-prefix}-bronze-mars-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_bronze_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_bronze_bucket.id}/mars/"
    exclusions = ["**/image/**", "**/raw/*"]
  }

  configuration = jsonencode({
    "Version" = 1.0
    "CrawlerOutput" = {
      "Partitions" = {
        "AddOrUpdateBehavior" = "InheritFromTable"
      }
    },
    Grouping = {
      "TableGroupingPolicy" = "CombineCompatibleSchemas"
    }
  })

  schema_change_policy {
    update_behavior = "LOG"
    delete_behavior = "LOG"
  }
}

resource "aws_glue_job" "transform_apod_job" {
  name         = "${local.name-prefix}-transform-apod-job"
  role_arn     = aws_iam_role.glue_service_role.arn
  glue_version = "5.0"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.transform_apod_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_bronze_catalog.name
    "--glue_source_table"    = "nasa_apod"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_silver_bucket.bucket}/apod/"
  }
}

resource "aws_glue_job" "transform_neo_job" {
  name         = "${local.name-prefix}-transform-neo-job"
  role_arn     = aws_iam_role.glue_service_role.arn
  glue_version = "5.0"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.transform_neo_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_bronze_catalog.name
    "--glue_source_table"    = "nasa_neo"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_silver_bucket.bucket}/neo/"
  }
}