# Architecture Diagrams

This document represents the source AWS architecture, target Azure architecture, and cross-cloud migration path implemented in the AWS-to-Azure Document Management Migration project.

---

## 1. AWS Source Architecture

```mermaid
flowchart TB

    USER["User / Internet"]

    subgraph AWS["AWS Source Environment — us-east-1"]

        IGW["Internet Gateway"]

        subgraph VPC["VPC — 10.0.0.0/16"]

            subgraph PUBLIC["Public Subnet — 10.0.1.0/24"]
                ECS["Amazon ECS Fargate<br/>Flask Application<br/>Docker Container<br/>Port 5001"]
            end

            subgraph PRIVATE1["Private Subnet — 10.0.10.0/24"]
                RDS["Amazon RDS PostgreSQL<br/>Document Metadata<br/>Private Database"]
            end

            subgraph PRIVATE2["Private Subnet — 10.0.20.0/24"]
                RDSAZ["RDS DB Subnet Group<br/>Second-AZ Coverage"]
            end
        end

        S3["Amazon S3<br/>Business Documents<br/>Private + Encrypted"]
        ECR["Amazon ECR<br/>Docker Image Registry"]
        SECRETS["AWS Secrets Manager<br/>DATABASE_URL"]
        IAM["AWS IAM<br/>Execution Role + Task Role"]
        CW["Amazon CloudWatch<br/>Application Logs"]
    end

    USER -->|"HTTP :5001"| IGW
    IGW --> ECS

    ECR -->|"Container Image"| ECS
    SECRETS -->|"Database Secret"| ECS
    IAM -->|"Runtime Permissions"| ECS

    ECS -->|"PostgreSQL :5432"| RDS
    ECS -->|"Document Upload / Download"| S3
    ECS -->|"Application Logs"| CW

    RDS --- RDSAZ

---

## 2. Azure Target Architecture

```mermaid
flowchart TB

    USER["User / Internet"]

    subgraph AZURE["Azure Target Environment"]

        subgraph CAE["Azure Container Apps Environment"]
            ACA["Azure Container App<br/>Flask Application<br/>Docker Container"]
        end

        ACR["Azure Container Registry<br/>Application Container Image"]

        PG["Azure Database for PostgreSQL<br/>Flexible Server<br/>Document Metadata<br/>Private Database"]

        BLOB["Azure Blob Storage<br/>documents Container<br/>Business Documents<br/>Private Storage"]

        MI["Azure Managed Identity<br/>System + User Assigned"]

        RBAC["Azure RBAC<br/>Storage Blob Data Contributor"]

    end

    USER -->|"HTTPS"| ACA

    ACR -->|"Container Image"| ACA

    ACA -->|"PostgreSQL Connection"| PG

    ACA -->|"Upload / Download Documents"| BLOB

    MI -->|"Runtime Identity"| ACA

    RBAC -->|"Authorizes Blob Access"| MI

    MI -->|"Credential-Free Authentication"| BLOB

---

## 3. AWS to Azure Cross-Cloud Migration Flow

```mermaid
flowchart LR

    subgraph AWS["AWS Source Environment"]
        ECS["ECS Fargate<br/>Flask Application"]
        RDS["RDS PostgreSQL<br/>50 Metadata Records"]
        S3["Amazon S3<br/>50 Business Documents"]
        ECR["Amazon ECR<br/>Docker Image"]
    end

    subgraph MIGRATION["Migration Process"]
        DBMIG["Database Migration<br/>Python + psycopg<br/>Validated CSV Export / Import"]
        OBJMIG["Object Migration<br/>AzCopy"]
        APPMIG["Application Re-platforming<br/>Docker Image Deployment"]
        VALIDATE["Validation + Reconciliation<br/>Record Counts<br/>Object Counts<br/>Metadata + Checksums<br/>Health Tests"]
    end

    subgraph AZURE["Azure Target Environment"]
        ACA["Azure Container Apps<br/>Flask Application"]
        AZPG["Azure Database for PostgreSQL<br/>50 Metadata Records"]
        BLOB["Azure Blob Storage<br/>50 Business Documents"]
        ACR["Azure Container Registry<br/>Docker Image"]
    end

    RDS --> DBMIG --> AZPG
    S3 --> OBJMIG --> BLOB
    ECR --> APPMIG --> ACR
    ACR --> ACA

    AZPG --> VALIDATE
    BLOB --> VALIDATE
    ACA --> VALIDATE

    VALIDATE -->|"PASS"| CUTOVER["Production Cutover<br/>Azure Becomes Active"]

    CUTOVER -.->|"Rollback Path Tested"| ECS
