# AWS Source Migration Readiness

## Source Environment

- Application platform: Amazon ECS with AWS Fargate
- Database: Amazon RDS for PostgreSQL
- Object storage: Amazon S3
- Application document count: 50
- Database metadata record count: 50

## Database Migration Artifact

The AWS RDS source database was exported into:

`migration/database/backups/aws-rds-data.sql`

The export contains 50 document metadata records.

A SHA-256 checksum was generated and successfully verified:

`migration/database/backups/aws-rds-data.sql.sha256`

## Object Storage Migration Baseline

The AWS S3 source contains 50 application documents across:

- finance/
- human-resources/
- information-technology/
- operations/
- sales/

The following prefix is excluded from the application-document migration inventory:

`migration-artifacts/`

The finalized S3 source inventory is:

`migration/storage/aws-s3-pre-migration-inventory.json`

Its SHA-256 checksum was generated and successfully verified.

## Reconciliation Target

After migration to Azure, validation should confirm:

- Azure PostgreSQL contains 50 metadata records.
- Azure Blob Storage contains 50 application documents.
- Source and destination document inventories reconcile.
- Migrated application data remains accessible through the application.
