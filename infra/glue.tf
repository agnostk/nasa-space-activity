# Catalogs
resource "aws_glue_catalog_database" "nasa_bronze_catalog" {
  name        = "${local.name-prefix}-bronze-catalog"
  description = "Bronze layer for NASA data"
}

resource "aws_glue_catalog_database" "nasa_silver_catalog" {
  name        = "${local.name-prefix}-silver-catalog"
  description = "Silver layer for NASA data"
}


# Crawlers
# Bronze
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

# Silver
resource "aws_glue_crawler" "nasa_silver_apod_crawler" {
  name          = "${local.name-prefix}-silver-apod-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_silver_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_silver_bucket.id}/apod/"
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

resource "aws_glue_crawler" "nasa_silver_neo_crawler" {
  name          = "${local.name-prefix}-silver-neo-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_silver_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_silver_bucket.id}/neo/"
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

resource "aws_glue_crawler" "nasa_silver_mars_crawler" {
  name          = "${local.name-prefix}-silver-mars-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_silver_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_silver_bucket.id}/mars/"
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

# Jobs
# Extract
resource "aws_glue_job" "extract_apod_job" {
  name              = "${local.name-prefix}-extract-apod-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.extract_apod_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--nasa_secret_key"   = aws_secretsmanager_secret.nasa_api_key.name
    "--bronze_bucket_key" = aws_s3_bucket.nasa_bronze_bucket.id
  }
}

resource "aws_glue_job" "extract_mars_job" {
  name              = "${local.name-prefix}-extract-mars-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.extract_mars_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--nasa_secret_key"   = aws_secretsmanager_secret.nasa_api_key.name
    "--bronze_bucket_key" = aws_s3_bucket.nasa_bronze_bucket.id
  }
}

resource "aws_glue_job" "extract_neo_job" {
  name              = "${local.name-prefix}-extract-neo-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.extract_neo_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--nasa_secret_key"   = aws_secretsmanager_secret.nasa_api_key.name
    "--bronze_bucket_key" = aws_s3_bucket.nasa_bronze_bucket.id
  }
}

# Transform
resource "aws_glue_job" "transform_apod_job" {
  name              = "${local.name-prefix}-transform-apod-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

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
  name              = "${local.name-prefix}-transform-neo-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

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

resource "aws_glue_job" "transform_mars_job" {
  name              = "${local.name-prefix}-transform-mars-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.transform_mars_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_bronze_catalog.name
    "--glue_source_table"    = "nasa_mars"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_silver_bucket.bucket}/mars/"
  }
}

# Enrich
resource "aws_glue_job" "enrich_apod_job" {
  name              = "${local.name-prefix}-enrich-apod-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.enrich_apod_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_silver_catalog.name
    "--glue_source_table"    = "nasa_apod"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_gold_bucket.bucket}/apod/"
    "--enrichment_api_url"   = var.enrichment_service_api_url
    "--enrichment_api_key"   = var.enrichment_service_api_key
  }
}