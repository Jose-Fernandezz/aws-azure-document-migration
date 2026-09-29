# Troubleshooting Guide

This document records significant technical issues encountered during the AWS-to-Azure Document Management Migration project, including symptoms, investigation, root causes, resolutions, and lessons learned.

---

## 1. ECS Exec Initially Failed

### Symptom
AWS ECS Exec could not initially establish an interactive session with the running Fargate task.

### Investigation
The ECS service and task configuration were reviewed to determine whether execute-command functionality was enabled and whether the running task had been launched with the updated configuration.

### Root Cause
ECS Exec was not enabled for the existing running task. Enabling execute-command on the service does not retroactively modify an already-running task.

### Fix
Execute-command was enabled on the ECS service and a new deployment was forced so that a replacement Fargate task started with ECS Exec support.

### Lesson / Prevention
When enabling ECS Exec, verify that the service has execute-command enabled and replace existing tasks so the new configuration takes effect.

---

## 2. ECS Task ID Changed After Forced Deployment

### Symptom
Previously captured ECS task IDs stopped working after service deployments.

### Investigation
The running tasks were listed again using the AWS CLI and compared with previously stored task identifiers.

### Root Cause
A forced ECS deployment replaces existing Fargate tasks. The replacement task receives a new task ID.

### Fix
The current running task ARN/ID was retrieved again before executing task-specific commands.

### Lesson / Prevention
Do not assume ECS task IDs are permanent. Dynamically retrieve the current running task after deployments before using ECS Exec or other task-specific operations.

---

## 3. PostgreSQL CLI Tools Missing from Application Container

### Symptom
The `psql` and `pg_dump` commands were unavailable inside the AWS ECS application container.

### Investigation
The running container was inspected and attempts to execute the PostgreSQL CLI utilities confirmed that the binaries were not installed.

### Root Cause
The application image is based on the lightweight `python:3.14-slim` image and did not include PostgreSQL client utilities.

### Fix
Python and the `psycopg` PostgreSQL driver already available to the application were used to query and export database data instead of installing additional CLI tools into the running application container.

### Lesson / Prevention
Minimal container images intentionally exclude many administrative utilities. Migration tooling requirements should be identified before deployment, or database operations can use existing application libraries when appropriate.

---

## 4. Python Application Module Import Failed During ECS Testing

### Symptom
Python commands executed inside the ECS container could not consistently import application modules when commands were launched outside the expected application path.

### Investigation
The container filesystem and Python module path were reviewed to determine where the application package was located.

### Root Cause
The application code was located under `/app`, but Python did not always have the correct application directory available in its module search path for manually executed commands.

### Fix
Commands were executed from the appropriate application context and `PYTHONPATH=/app` was used when necessary so Python could locate the application modules.

### Lesson / Prevention
When running administrative or validation commands inside containers, verify the working directory and Python module search path instead of assuming they match the application's normal startup environment.

---

## 5. Duplicate PostgreSQL Primary Key During Upload Testing

### Symptom
An application upload generated a PostgreSQL `UniqueViolation` error indicating that a document ID already existed.

### Investigation
Container App logs were reviewed and the PostgreSQL `documents` table was checked for record count and ID range.

### Root Cause
Migrated records already occupied the existing ID range, while the PostgreSQL sequence used for new inserts was not aligned with the highest migrated ID.

### Fix
The database state and ID range were validated and the sequence behavior was corrected so new application records would not reuse existing migrated primary keys.

### Lesson / Prevention
After bulk migrations that preserve primary keys, PostgreSQL sequences should be validated and synchronized with the highest existing ID before production writes are enabled.

---

## 6. Direct Database Migration Tools Were Incompatible with Private Connectivity

### Symptom
A straightforward local `pg_dump` and `pg_restore` workflow could not directly reach the private AWS RDS and Azure PostgreSQL environments from the local workstation.

### Investigation
Database network exposure, container tooling, and available migration paths were reviewed.

### Root Cause
The databases were intentionally protected from unrestricted public access, and the lightweight application container did not contain the PostgreSQL command-line migration utilities.

### Fix
A controlled Python/psycopg export-and-import workflow was used. Data was exported into validated migration artifacts, transferred through controlled cloud storage, imported into Azure PostgreSQL, and then reconciled against the AWS source.

### Lesson / Prevention
Migration tooling must account for network boundaries and private database architecture. A migration design should preserve security controls rather than weakening database exposure merely to simplify data transfer.

---

# Project Lessons Learned

## 1. Design Migration Paths Around Security Boundaries
Private databases and storage should remain protected during migration. Migration tooling should adapt to the security architecture instead of temporarily weakening security controls for convenience.

## 2. Validate Data Instead of Assuming Transfer Success
A successful transfer command does not prove a successful migration. Record counts, metadata, object counts, checksums, application health, and source-to-target reconciliation should be independently validated.

## 3. Separate Application Configuration from Application Code
Using environment variables, secrets, storage-provider abstractions, and cloud identities allowed the same application codebase to operate across AWS and Azure without hardcoding cloud-specific credentials.

## 4. Plan Cutover and Rollback Together
A migration is safer when the source environment remains recoverable until the Azure target has been validated. The rollback simulation demonstrated that AWS could be restored if the production cutover failed.

## 5. Infrastructure as Code Improves Repeatability
Terraform provided a documented and reproducible definition of the AWS source and Azure target infrastructure instead of relying entirely on manually created cloud resources.

## 6. Troubleshooting Is Part of Migration Engineering
Container configuration, database sequences, networking, identity, migration tooling, and cloud-specific behavior all required investigation during the project. Recording these issues makes the migration process reproducible and easier to maintain.
