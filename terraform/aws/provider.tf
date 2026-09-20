provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "AWS-Azure-Document-Migration"
      Environment = "source"
      ManagedBy   = "Terraform"
    }
  }
}