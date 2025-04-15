terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.81.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  profile = "agnostk"

  default_tags {
    tags = {
      Project = "nasa-space-activity"
    }
  }
}

