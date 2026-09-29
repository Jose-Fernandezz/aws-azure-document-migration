# AWS to Azure Document Management Migration

## Project Overview

This project demonstrates an end-to-end cross-cloud migration of a containerized document management application from Amazon Web Services (AWS) to Microsoft Azure.

The source environment was built on AWS using Amazon ECS with Fargate, Amazon ECR, Amazon RDS for PostgreSQL, Amazon S3, IAM, Secrets Manager, and CloudWatch. The target environment was built on Azure using Azure Container Apps, Azure Container Registry, Azure Database for PostgreSQL Flexible Server, Azure Blob Storage, Managed Identity, and Azure RBAC.

The migration included three major workload components:

- **Application:** A Python Flask application packaged as a Docker container and re-platformed from AWS ECS/Fargate to Azure Container Apps.
- **Database:** 50 document metadata records migrated from Amazon RDS for PostgreSQL to Azure Database for PostgreSQL.
- **Object Storage:** 50 business documents migrated from Amazon S3 to Azure Blob Storage.

The project also includes migration validation, checksum verification, simulated cutover and rollback procedures, security reviews, infrastructure as code, and technical documentation.

## Business Scenario

A fictional organization operates a document management application in AWS. The application stores structured document metadata in PostgreSQL while the actual business documents are stored separately in Amazon S3.

The organization has decided to migrate the workload to Microsoft Azure while maintaining the existing application functionality and preserving the integrity of its data.

The migration requires moving the application runtime, PostgreSQL metadata, and object storage while validating that the Azure environment contains the same records and documents as the AWS source environment.

## Project Goals

The primary goals of this project were to:

- Build a working document management workload in AWS.
- Provision equivalent Azure infrastructure using Terraform.
- Re-platform the containerized Flask application from AWS ECS/Fargate to Azure Container Apps.
- Migrate PostgreSQL metadata from AWS RDS to Azure Database for PostgreSQL.
- Migrate business documents from Amazon S3 to Azure Blob Storage.
- Validate record counts, object counts, metadata, file sizes, and SHA-256 checksums.
- Implement cloud-specific authentication using AWS IAM and Azure Managed Identity/RBAC.
- Perform and document a controlled cutover and rollback test.
- Demonstrate security, cost-awareness, troubleshooting, and migration validation practices.


## Architecture

### AWS Source Architecture

The source environment runs the containerized Flask application on Amazon ECS with AWS Fargate. Amazon RDS for PostgreSQL stores document metadata, while Amazon S3 stores the business documents. Amazon ECR stores the application image, Secrets Manager provides the database connection secret, IAM controls runtime permissions, and CloudWatch captures application logs.

![AWS Source Architecture](docs/diagrams/aws-source-architecture.png)

### Azure Target Architecture

The target environment re-platforms the application to Azure Container Apps. Azure Database for PostgreSQL Flexible Server stores the migrated metadata, while Azure Blob Storage stores the migrated business documents. Azure Container Registry stores the application image, and a system-assigned managed identity with Azure RBAC provides credential-free access to Blob Storage.

![Azure Target Architecture](docs/diagrams/azure-target-architecture.png)

### Cross-Cloud Migration Flow

The migration moves three workload components from AWS to Azure: the Docker application image, PostgreSQL metadata, and business documents. The application is re-platformed to Azure Container Apps, database records are transferred using a controlled Python/psycopg CSV export-import workflow, and object storage is migrated from Amazon S3 to Azure Blob Storage using AzCopy. Validation is performed before production cutover.

![Cross-Cloud Migration Flow](docs/diagrams/cross-cloud-migration.png)

## Migration Dataset

A controlled synthetic dataset was created so the migration could be validated against a known source baseline.

| Dataset | AWS Source | Azure Target | Result |
|---|---:|---:|---|
| PostgreSQL metadata records | 50 | 50 | PASS |
| Business documents | 50 | 50 | PASS |

The 50 business documents represent multiple departments and file formats, including TXT, CSV, DOCX, XLSX, PDF, and PNG files. Each document has a corresponding PostgreSQL metadata record containing information such as its filename, department, uploader, storage location, file size, and checksum.

### Data Integrity Strategy

SHA-256 checksums were generated for the controlled business documents and stored with their metadata. Migration validation compared the AWS source baseline with the Azure target to verify:

- Database record counts
- Object storage counts
- Primary keys and selected metadata
- Object keys and filenames
- File sizes
- SHA-256 checksums
- Department distribution
- Application health after migration

This provided measurable evidence that the structured metadata and business documents remained consistent during the AWS-to-Azure migration.

## Security Architecture

Security was implemented separately for the AWS source and Azure target environments using cloud-native identity and access controls.

### AWS Security

The AWS source environment used:

- IAM execution and task roles for ECS/Fargate.
- AWS Secrets Manager for the PostgreSQL `DATABASE_URL`.
- A private Amazon RDS PostgreSQL database.
- An RDS security group allowing PostgreSQL traffic on port 5432 only from the ECS security group.
- A private Amazon S3 bucket with public access blocked and server-side encryption enabled.
- Separate runtime permissions for the application instead of embedding AWS credentials in the application.

### Azure Security

The Azure target environment used:

- A system-assigned Managed Identity for the Azure Container App.
- Azure RBAC with the Storage Blob Data Contributor role.
- Credential-free application access to Azure Blob Storage.
- Azure Database for PostgreSQL Flexible Server with public network access disabled.
- Private Azure Blob Storage.
- No storage account access keys or connection strings stored in the application.

This design demonstrates the transition from AWS IAM-based application authorization to Azure Managed Identity and RBAC.

## Migration Execution

The migration was performed as three separate workload migrations.

### Application Migration

The Flask application was packaged as a Docker container. The AWS application image was represented through Amazon ECR and the workload was re-platformed from Amazon ECS with Fargate to Azure Container Apps using Azure Container Registry.

### PostgreSQL Metadata Migration

The source Amazon RDS PostgreSQL database contained 50 controlled document metadata records.

Because the RDS database was private and the ECS application image did not contain the `pg_dump` utility, the migration used a controlled Python and psycopg export/import workflow. The source records were exported to a validated CSV migration artifact, transferred to the Azure environment, and imported into Azure Database for PostgreSQL Flexible Server.

Post-migration validation confirmed:

- 50 AWS source records.
- 50 Azure target records.
- Matching primary keys.
- Matching selected metadata.
- Matching object keys.
- Matching stored SHA-256 checksum values.
- Matching department distributions.

### Object Storage Migration

The 50 business documents stored in Amazon S3 were migrated to Azure Blob Storage using AzCopy.

The migration preserved the document object structure and was followed by object-count, file-size, metadata, and checksum validation to confirm that the migrated Azure objects matched the AWS source baseline.

## Migration Implementation

### AWS Source Environment

The source workload was deployed in AWS using infrastructure provisioned with Terraform. The Flask application was containerized with Docker, stored in Amazon ECR, and executed on Amazon ECS with AWS Fargate.

The AWS source environment used:

- Amazon ECS with Fargate for the application runtime
- Amazon ECR for the Docker application image
- Amazon RDS for PostgreSQL for document metadata
- Amazon S3 for business document storage
- AWS Secrets Manager for the database connection secret
- IAM execution and task roles for runtime permissions
- Amazon CloudWatch for application logging
- VPC networking with public and private subnets and security-group controls

The ECS application communicated with the private RDS PostgreSQL database and accessed the private S3 bucket using its assigned IAM permissions.

### Azure Target Environment

Equivalent target infrastructure was provisioned in Microsoft Azure using Terraform. Rather than reproducing the AWS architecture exactly, the workload was re-platformed to Azure managed services.

The Azure target environment used:

- Azure Container Apps for the containerized Flask application
- Azure Container Registry for the Docker image
- Azure Database for PostgreSQL Flexible Server for document metadata
- Azure Blob Storage for business documents
- System-assigned Managed Identity for the application
- Azure RBAC with the Storage Blob Data Contributor role for credential-free Blob Storage access
- Private PostgreSQL connectivity with public database access disabled

### Database Migration

The migration transferred 50 PostgreSQL document metadata records from Amazon RDS to Azure Database for PostgreSQL.

Because the source RDS database was private and the ECS application image did not include `pg_dump`, the project used a controlled Python/psycopg export-import workflow. Source records were exported to a validated CSV migration artifact, transferred to the Azure environment, and imported into the Azure PostgreSQL target.

Post-migration validation confirmed that all 50 source records were present in Azure and that primary keys, selected metadata, object keys, checksums, and department distributions matched the AWS baseline.

### Object Storage Migration

The 50 business documents stored in Amazon S3 were migrated to the Azure Blob Storage `documents` container using AzCopy.

The migration was executed from a controlled migration workstation using temporary AWS credentials and Azure authentication. Temporary AWS credentials were removed from the shell after the transfer.

Post-migration validation compared the AWS source and Azure target for:

- Business document count
- Object names and storage keys
- File sizes
- SHA-256 checksums

All 50 expected business documents were successfully validated in the Azure target.

### Application Re-platforming

The same containerized Flask application was re-platformed from Amazon ECS/Fargate to Azure Container Apps.

The Azure deployment used the application image stored in Azure Container Registry and Azure-specific runtime configuration. The application's storage abstraction allowed the storage backend to change from Amazon S3 to Azure Blob Storage without redesigning the application.

After the database and document migrations were validated, application health and document-management functionality were tested against the Azure target before production cutover.

## Migration Validation

Migration validation was performed before production cutover to verify that the Azure target matched the AWS source environment.

The following checks were completed:

- PostgreSQL record count: 50 AWS records → 50 Azure records — PASS
- Primary keys and selected metadata — PASS
- Object/storage keys — PASS
- Department distribution — PASS
- Business document count: 50 AWS documents → 50 Azure documents — PASS
- File sizes — PASS
- SHA-256 checksum validation — PASS
- Azure application health and document-management functionality — PASS

These checks provided measurable evidence that the structured metadata and business documents remained consistent throughout the migration.

## Cutover and Rollback

After migration validation passed, the Azure environment was treated as the active target environment.

The cutover process verified that:

- The Flask application was running successfully in Azure Container Apps.
- The application connected to Azure Database for PostgreSQL.
- Document upload and download operations used Azure Blob Storage.
- The migrated metadata and business documents were accessible from the Azure workload.
- Application health checks passed after migration.

A rollback path was also maintained so the AWS ECS/Fargate source environment could be used again if validation or post-cutover testing failed.

This approach demonstrates a controlled migration strategy in which validation occurs before the target environment is accepted as the production destination.

## Security

Security controls were implemented across both cloud environments as part of the migration design.

### AWS Source

- Amazon RDS was deployed without public database access.
- The RDS security group allowed PostgreSQL traffic on port 5432 only from the ECS security group.
- Amazon S3 was configured as private storage with public access blocked and encryption enabled.
- AWS Secrets Manager stored the database connection secret used by the ECS workload.
- Separate ECS execution and task roles were used for deployment and runtime permissions.
- IAM permissions were used to control access to AWS resources.

### Azure Target

- Azure Database for PostgreSQL Flexible Server was deployed with public access disabled.
- Azure Blob Storage was configured as private storage.
- The Azure Container App used a system-assigned managed identity.
- Azure RBAC granted the workload the Storage Blob Data Contributor role for Blob Storage access.
- The application accessed Blob Storage without embedding a storage account key or connection string in the application.
- Temporary AWS credentials used during the AzCopy migration were removed from the migration shell after the transfer.

These controls demonstrate the use of private data services, workload identities, least-privilege access patterns, secret management, and credential-free authentication where supported.

## Architecture and Cost Decisions

This project was designed as a portfolio migration environment rather than a production-scale enterprise platform. Several architecture decisions were intentionally made to balance security, migration realism, and cloud cost.

- Amazon ECS with AWS Fargate was used instead of EC2 so the source application demonstrated managed container orchestration.
- Azure Container Apps was selected as the Azure target to demonstrate application re-platforming rather than a simple virtual-machine migration.
- The AWS source used a public ECS task networking design for the lab environment while keeping the PostgreSQL database private.
- A NAT Gateway and Application Load Balancer were not added to the AWS lab architecture in order to avoid unnecessary recurring cost.
- Amazon RDS remained private and accepted PostgreSQL traffic only from the ECS security group.
- Azure Database for PostgreSQL was configured with public access disabled.
- Managed Identity and Azure RBAC were used instead of application-managed Blob Storage credentials.
- The migration dataset was intentionally controlled at 50 metadata records and 50 business documents so record counts, object counts, file sizes, metadata, and checksums could be reconciled precisely.

For a production implementation, the architecture could be extended with additional high-availability, private networking, monitoring, centralized secret management, load-balancing, and disaster-recovery controls.

## Project Results

The AWS-to-Azure migration was completed successfully while preserving the application's data and document-management functionality.

Key results:

- Re-platformed a containerized Flask application from Amazon ECS with Fargate to Azure Container Apps.
- Migrated 50 PostgreSQL metadata records from Amazon RDS to Azure Database for PostgreSQL.
- Migrated 50 business documents from Amazon S3 to Azure Blob Storage using AzCopy.
- Verified database record counts, primary keys, metadata, object counts, file sizes, and SHA-256 checksums.
- Validated application health and document upload/download functionality in Azure before production cutover.
- Implemented a documented rollback path to the AWS source environment.
- Used Terraform to define cloud infrastructure across AWS and Azure.
- Applied AWS IAM, Secrets Manager, Azure Managed Identity, RBAC, private storage, and restricted database connectivity.

## Skills Demonstrated

This project demonstrates hands-on experience with:

- AWS and Microsoft Azure
- Cross-cloud workload migration
- Infrastructure as Code with Terraform
- Docker and containerized applications
- Amazon ECS with AWS Fargate
- Azure Container Apps
- Amazon ECR and Azure Container Registry
- Amazon RDS and Azure Database for PostgreSQL
- Amazon S3 and Azure Blob Storage
- AzCopy
- PostgreSQL data migration
- Python and psycopg
- IAM, Managed Identity, and RBAC
- Secrets management
- Migration validation and data-integrity testing
- Production cutover and rollback planning
- Cloud architecture documentation
