# AWS to Azure Migration Runbook

## Pre-Migration Baseline

AWS is the authoritative source environment before migration.

### AWS Source
- PostgreSQL documents records: 50
- S3 business documents: 50
- S3 migration artifacts are excluded from the business-document count.

### Azure Target
- Azure Blob Storage documents: 0
- Azure PostgreSQL target: provisioned and ready
- Azure Container App: healthy and provisioned
- Azure infrastructure validated with Terraform

## Migration Objective

Migrate the document-management workload from AWS to Azure while preserving:
- PostgreSQL metadata
- Document objects
- Application functionality
- Data integrity

Post-migration validation will compare Azure against this baseline.
