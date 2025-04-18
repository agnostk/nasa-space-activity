terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.81.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}

provider "aws" {
  region = local.region

  default_tags {
    tags = {
      Project = "nasa-space-activity"
    }
  }
}

locals {
  name-prefix = "${var.project}-${var.env}-${data.aws_caller_identity.current.account_id}-${random_id.suffix.hex}"
  region      = "ap-northeast-1"
  # enrichment_zip_md5 = filemd5("${path.module}/../enrichment-service/build/enrichment_service.zip")
}

