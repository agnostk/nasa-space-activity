resource "aws_glue_catalog_database" "nasa_bronze_catalog" {
  name        = "nasa_bronze_catalog"
  description = "Bronze layer for NASA data"
}

resource "aws_glue_crawler" "nasa_bronze_apod_crawler" {
  name          = "nasa_bronze_apod_crawler"
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
  name          = "nasa_bronze_neo_crawler"
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
  name          = "nasa_bronze_mars_crawler"
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