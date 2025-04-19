# Catalogs
resource "aws_glue_catalog_database" "nasa_bronze_catalog" {
  name        = "${local.name-prefix}-bronze-catalog"
  description = "Bronze layer for NASA data"
}

resource "aws_glue_catalog_database" "nasa_silver_catalog" {
  name        = "${local.name-prefix}-silver-catalog"
  description = "Silver layer for NASA data"
}

resource "aws_glue_catalog_database" "nasa_gold_catalog" {
  name        = "${local.name-prefix}-gold-catalog"
  description = "Gold layer for NASA data"
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

# Gold
resource "aws_glue_crawler" "nasa_gold_apod_crawler" {
  name          = "${local.name-prefix}-gold-apod-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_gold_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_gold_bucket.id}/apod/"
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

resource "aws_glue_crawler" "nasa_gold_mars_crawler" {
  name          = "${local.name-prefix}-gold-mars-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_gold_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_gold_bucket.id}/mars/"
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

resource "aws_glue_crawler" "nasa_gold_neo_crawler" {
  name          = "${local.name-prefix}-gold-neo-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.nasa_gold_catalog.name
  table_prefix  = "nasa_"

  s3_target {
    path = "s3://${aws_s3_bucket.nasa_gold_bucket.id}/neo/"
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

resource "aws_glue_job" "enrich_mars_job" {
  name              = "${local.name-prefix}-enrich-mars-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.enrich_mars_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_silver_catalog.name
    "--glue_source_table"    = "nasa_mars"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_gold_bucket.bucket}/mars/"
    "--enrichment_api_url"   = var.enrichment_service_api_url
    "--enrichment_api_key"   = var.enrichment_service_api_key
  }
}

resource "aws_glue_job" "enrich_neo_job" {
  name              = "${local.name-prefix}-enrich-neo-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.enrich_neo_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_silver_catalog.name
    "--glue_source_table"    = "nasa_neo"
    "--s3_target_path"       = "s3://${aws_s3_bucket.nasa_gold_bucket.bucket}/neo/"
    "--enrichment_api_url"   = var.enrichment_service_api_url
    "--enrichment_api_key"   = var.enrichment_service_api_key
  }
}

# Load
resource "aws_glue_job" "load_apod_job" {
  name              = "${local.name-prefix}-load-apod-job"
  role_arn          = aws_iam_role.glue_service_role.arn
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  command {
    script_location = "s3://${aws_s3_bucket.nasa_pipeline_code.bucket}/${aws_s3_object.load_apod_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--glue_source_database" = aws_glue_catalog_database.nasa_gold_catalog.name
    "--glue_source_table"    = "nasa_apod"
    "--db_user"              = var.db_username
    "--db_password_key"      = aws_secretsmanager_secret.postgresql_password_key.name
    "--rds_endpoint"         = aws_db_instance.postgresql.endpoint
  }
}

resource "aws_glue_workflow" "nasa_etl_pipeline" {
  name        = "${local.name-prefix}-etl-workflow"
  description = "Orchestrates the NASA ETL pipeline from extraction to enrichment"
}

# Step 1: Schedule Trigger → Extraction Jobs
resource "aws_glue_trigger" "start_etl" {
  name          = "${local.name-prefix}-start-etl"
  type          = "SCHEDULED"
  schedule      = "cron(0 3 * * ? *)"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  actions {
    job_name = aws_glue_job.extract_apod_job.name
  }
  actions {
    job_name = aws_glue_job.extract_mars_job.name
  }
  actions {
    job_name = aws_glue_job.extract_neo_job.name
  }
}

# Step 2: After Extraction → Bronze Crawlers
resource "aws_glue_trigger" "after_extract_part1" {
  name          = "${local.name-prefix}-after-extract-part1"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.extract_apod_job.name
      state    = "SUCCEEDED"
    }
    conditions {
      job_name = aws_glue_job.extract_mars_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_bronze_apod_crawler.name
  }
  actions {
    crawler_name = aws_glue_crawler.nasa_bronze_mars_crawler.name
  }
}

resource "aws_glue_trigger" "after_extract_part2" {
  name          = "${local.name-prefix}-after-extract-part2"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.extract_neo_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_bronze_neo_crawler.name
  }
}

# Step 3: After Bronze Crawlers → Transformation Jobs
resource "aws_glue_trigger" "after_bronze_crawlers" {
  name          = "${local.name-prefix}-after-bronze-crawlers"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      crawler_name = aws_glue_crawler.nasa_bronze_apod_crawler.name
      crawl_state  = "SUCCEEDED"
    }
    conditions {
      crawler_name = aws_glue_crawler.nasa_bronze_mars_crawler.name
      crawl_state  = "SUCCEEDED"
    }
    conditions {
      crawler_name = aws_glue_crawler.nasa_bronze_neo_crawler.name
      crawl_state  = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.transform_apod_job.name
  }
  actions {
    job_name = aws_glue_job.transform_mars_job.name
  }
  actions {
    job_name = aws_glue_job.transform_neo_job.name
  }
}

# Step 4: After Transformation Jobs → Silver Crawlers
resource "aws_glue_trigger" "after_transformation_part1" {
  name          = "${local.name-prefix}-after_transformation_part1"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.transform_apod_job.name
      state    = "SUCCEEDED"
    }
    conditions {
      job_name = aws_glue_job.transform_mars_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_silver_apod_crawler.name
  }
  actions {
    crawler_name = aws_glue_crawler.nasa_silver_mars_crawler.name
  }
}

resource "aws_glue_trigger" "after_transformation_part2" {
  name          = "${local.name-prefix}-after_transformation_part2"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.transform_neo_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_silver_neo_crawler.name
  }
}

# Step 5: After Silver Crawlers → Enrichment Jobs
resource "aws_glue_trigger" "after_silver_crawlers" {
  name          = "${local.name-prefix}-after-silver-crawlers"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      crawler_name = aws_glue_crawler.nasa_silver_apod_crawler.name
      crawl_state  = "SUCCEEDED"
    }
    conditions {
      crawler_name = aws_glue_crawler.nasa_silver_mars_crawler.name
      crawl_state  = "SUCCEEDED"
    }
    conditions {
      crawler_name = aws_glue_crawler.nasa_silver_neo_crawler.name
      crawl_state  = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.enrich_apod_job.name
  }
  actions {
    job_name = aws_glue_job.enrich_mars_job.name
  }
  actions {
    job_name = aws_glue_job.enrich_neo_job.name
  }
}

# Step 6: After Enrichment Jobs → Gold Crawlers
resource "aws_glue_trigger" "after_enrichment_part1" {
  name          = "${local.name-prefix}-after_enrichment_part1"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.enrich_apod_job.name
      state    = "SUCCEEDED"
    }
    conditions {
      job_name = aws_glue_job.enrich_mars_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_gold_apod_crawler.name
  }
  actions {
    crawler_name = aws_glue_crawler.nasa_gold_mars_crawler.name
  }
}

resource "aws_glue_trigger" "after_enrichment_part2" {
  name          = "${local.name-prefix}-after_enrichment_part2"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.nasa_etl_pipeline.name

  predicate {
    conditions {
      job_name = aws_glue_job.enrich_neo_job.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.nasa_gold_neo_crawler.name
  }
}