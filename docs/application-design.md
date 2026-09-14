# Document Management System — Application Design

## 1. Purpose

This application is a cloud-based Document Management System (DMS) designed for a fictional company that needs a centralized way to store, organize, retrieve, and manage internal business documents.

The application will first be deployed to Amazon Web Services (AWS) and will later be migrated to Microsoft Azure as part of a cross-cloud migration project.

The application is intentionally designed to use both structured and unstructured data so the migration demonstrates database migration, object storage migration, application migration, container migration, and cloud service reconfiguration.

---

## 2. Business Scenario

A fictional company currently operates its internal Document Management System in AWS.

Employees from departments such as Finance, Human Resources, Sales, and Operations use the system to upload and manage business documents.

The company has decided to migrate the application and its data from AWS to Microsoft Azure.

The migration must preserve:

- Application functionality
- Document metadata
- Uploaded document files
- Database records
- File integrity
- Storage relationships
- Application availability after cutover

The completed Azure environment should provide the same core functionality as the original AWS environment.

---

## 3. Application Users

The initial version represents an internal company application used by employees.

Example departments include:

- Finance
- Human Resources
- Sales
- Operations
- Information Technology

User authentication and advanced role-based application authorization are outside the initial application scope. Cloud infrastructure access will still follow IAM and Azure RBAC security practices.

---

## 4. Core Application Features

The application will allow users to:

1. View all documents.
2. Upload a new document.
3. Enter metadata describing the document.
4. View detailed information about an individual document.
5. Download a stored document.
6. Delete a document.
7. Search or filter documents by useful metadata.
8. View application health status.

---

## 5. Document Metadata

Each uploaded document will have structured metadata stored in PostgreSQL.

Planned metadata includes:

- Document ID
- Original filename
- Stored object key
- Document title
- Description
- Department
- Uploaded by
- Upload timestamp
- File type
- File size
- Storage provider
- Storage location
- Checksum

The database will store information about the document while object storage will contain the actual file.

---

## 6. Supported Test Documents

The project will use synthetic, non-sensitive documents representing realistic company data.

Example document categories include:

### Finance
- Monthly expense report
- Department budget
- Invoice summary

### Human Resources
- Employee handbook
- Benefits guide
- Training policy

### Sales
- Quarterly sales report
- Product pricing sheet
- Sales presentation

### Operations
- Operating procedure
- Inventory report
- Vendor information

No real confidential, customer, employee, financial, or personally identifiable information will be used.

---

## 7. Application Architecture

The application will use a layered design.

### Presentation Layer

HTML templates and CSS will provide the user interface.

### Application Layer

Python Flask will handle:

- HTTP requests
- Application routes
- Input validation
- Business logic
- Error handling
- Logging
- Health checks

### Database Layer

PostgreSQL will store structured document metadata.

### Storage Layer

The application will use a storage abstraction layer so the underlying object-storage provider can change without rewriting the application's main business logic.

Supported storage backends will include:

- Local storage for development
- Amazon S3 for the AWS deployment
- Azure Blob Storage for the Azure deployment

---

## 8. Storage Abstraction

The application will not directly hard-code Amazon S3 or Azure Blob Storage operations throughout the main application.

Instead, storage operations will be handled through a dedicated storage module.

The application will use common operations such as:

- upload_file()
- download_file()
- delete_file()
- file_exists()

The storage module will determine which backend to use based on environment configuration.

Example:

Local development:

STORAGE_PROVIDER=local

AWS:

STORAGE_PROVIDER=s3

Azure:

STORAGE_PROVIDER=azure

This design allows the same application codebase to operate across multiple environments.

---

## 9. Database Design Approach

PostgreSQL will be used in all major environments to reduce unnecessary application-level differences during migration.

Planned environments:

Local Development:
PostgreSQL

AWS:
Amazon RDS for PostgreSQL

Azure:
Azure Database for PostgreSQL Flexible Server

Database connection information will be supplied through environment variables rather than hard-coded credentials.

---

## 10. Application Configuration

Environment-specific configuration will be supplied using environment variables.

Examples include:

- DATABASE_URL
- STORAGE_PROVIDER
- AWS_REGION
- S3_BUCKET_NAME
- AZURE_STORAGE_ACCOUNT
- AZURE_STORAGE_CONTAINER
- MAX_UPLOAD_SIZE
- FLASK_ENV

Sensitive credentials will not be committed to GitHub.

A `.env.example` file will document required configuration variables without containing real secrets.

---

## 11. Validation and Security Requirements

The application will include basic security and validation controls.

Planned controls include:

- Allowed file-type validation
- Maximum upload size
- Filename sanitization
- Required metadata validation
- Parameterized database queries
- Environment-based secrets
- Error handling
- File existence checks
- Duplicate or conflicting file handling
- Checksum generation for migration validation

Cloud access will use AWS IAM and Azure identity/RBAC controls where appropriate.

---

## 12. Observability

The application will produce useful logs for major operations.

Examples include:

- Application startup
- Successful document upload
- Failed upload
- Database connection error
- Storage error
- Document deletion
- Health-check failure

The application will also expose a health endpoint:

`/health`

The health endpoint will help verify that the application is running during local testing, AWS deployment, Azure deployment, migration validation, and cutover.

---

## 13. Migration Requirements

The application must support migration from AWS to Azure without changing its core business functionality.

### AWS Source

Application Runtime:
Amazon ECS with AWS Fargate

Container Registry:
Amazon ECR

Database:
Amazon RDS for PostgreSQL

Object Storage:
Amazon S3

### Azure Target

Application Runtime:
Azure Container Apps

Container Registry:
Azure Container Registry

Database:
Azure Database for PostgreSQL Flexible Server

Object Storage:
Azure Blob Storage

---

## 14. Migration Validation Requirements

The migration will be considered successful when:

- Expected database records exist in Azure PostgreSQL.
- Expected document files exist in Azure Blob Storage.
- Document counts match the AWS source.
- Database record counts match the AWS source.
- File checksums match between source and destination.
- Document metadata remains associated with the correct file.
- Documents can be downloaded from the Azure application.
- New documents can be uploaded after cutover.
- Documents can be deleted after cutover.
- The application health endpoint reports a healthy state.
- Core application workflows operate successfully in Azure.

---

## 15. Application Data Flow

### Upload Workflow

User
→ Flask Application
→ Validate File and Metadata
→ Object Storage
→ PostgreSQL Metadata Record
→ Success Response

### View Workflow

User
→ Flask Application
→ PostgreSQL
→ Retrieve Document Metadata
→ Display Document Information

### Download Workflow

User
→ Flask Application
→ PostgreSQL Metadata Lookup
→ Object Storage
→ Return File to User

### Delete Workflow

User
→ Flask Application
→ PostgreSQL Metadata Lookup
→ Delete Object from Storage
→ Delete Metadata Record
→ Success Response

---

## 16. Migration Data Flow

AWS Source:

ECS/Fargate
→ RDS PostgreSQL
→ Amazon S3

Migration:

RDS PostgreSQL
→ pg_dump
→ pg_restore
→ Azure Database for PostgreSQL

Amazon S3
→ AzCopy
→ Azure Blob Storage

Application Container
→ Azure Container Registry
→ Azure Container Apps

Azure Target:

Azure Container Apps
→ Azure Database for PostgreSQL
→ Azure Blob Storage

---

## 17. Design Goals

The application should be:

- Portable between cloud environments
- Containerized
- Configuration-driven
- Secure enough for a portfolio demonstration
- Easy to test
- Easy to migrate
- Observable
- Documented
- Reproducible
- Suitable for demonstrating cloud migration concepts

---

## 18. Out of Scope

The initial project will not attempt to implement:

- Enterprise Single Sign-On
- Multi-factor authentication inside the application
- Complex application-level RBAC
- Document editing
- Real customer data
- Real employee data
- Production-scale disaster recovery
- Multi-region deployment
- Enterprise-grade high availability

These features could be identified as future improvements without unnecessarily expanding the migration project's primary scope.


## 19. Initial Document Data Model

The primary application entity will be a document record.

Each document record will contain:

- id
- original_filename
- object_key
- title
- description
- department
- uploaded_by
- uploaded_at
- file_type
- file_size
- storage_provider
- storage_location
- checksum

### Field Purpose

`id`
Unique database identifier for the document record.

`original_filename`
The filename provided by the user at upload time.

`object_key`
The internal storage identifier used by local storage, Amazon S3, or Azure Blob Storage.

`title`
A human-readable document title.

`description`
A short explanation of the document's purpose or contents.

`department`
The business department associated with the document.

`uploaded_by`
The employee or test user responsible for uploading the document.

`uploaded_at`
The timestamp when the document was added to the system.

`file_type`
The detected or supplied document type.

`file_size`
The document size in bytes.

`storage_provider`
The active storage backend, such as local, s3, or azure.

`storage_location`
The bucket, container, or logical storage location containing the file.

`checksum`
A SHA-256 checksum used to verify file integrity before and after migration.

---

## 20. Department Values

The initial application will use a controlled department list:

- Finance
- Human Resources
- Sales
- Operations
- Information Technology

Using a controlled list keeps the test data consistent and makes filtering and migration validation easier.

---

## 21. Initial File Types

The initial application will support common business-document formats such as:

- PDF
- DOCX
- XLSX
- CSV
- TXT
- PNG
- JPG / JPEG

The exact allowed extensions will be enforced in application configuration so they can be changed without rewriting core application logic.

---

## 22. Core Business Workflows

### Upload a Document

1. User opens the upload page.
2. User selects a file.
3. User enters document metadata.
4. Application validates required fields.
5. Application validates file type.
6. Application validates file size.
7. Application sanitizes the filename.
8. Application generates a unique storage object key.
9. Application calculates a SHA-256 checksum.
10. Application uploads the file to the configured storage backend.
11. Application inserts the metadata record into PostgreSQL.
12. Application confirms successful upload.

If the database operation fails after the storage upload succeeds, the application should attempt to remove the uploaded object to avoid leaving orphaned files.

### View Documents

1. User opens the document listing page.
2. Application retrieves document records from PostgreSQL.
3. Application displays useful metadata.
4. User can open an individual document detail page.

### Download a Document

1. User selects Download.
2. Application looks up the metadata record.
3. Application verifies the object exists.
4. Application retrieves the file from object storage.
5. Application returns the file to the user.

### Delete a Document

1. User selects Delete.
2. Application retrieves the document record.
3. Application removes the object from storage.
4. Application removes the PostgreSQL metadata record.
5. Application reports success or failure.

### Search and Filter

Users will be able to filter or search documents using fields such as:

- title
- filename
- department
- uploader
- file type

---

## 23. Error Handling Expectations

The application should handle common failure conditions without exposing internal stack traces to the user.

Examples include:

- Missing required metadata
- Unsupported file type
- File exceeding maximum upload size
- Database unavailable
- Storage backend unavailable
- Requested document not found
- Stored object missing
- Upload failure
- Download failure
- Delete failure

Errors should be logged with enough technical context to support troubleshooting.

---

## 24. Data Quality Requirements

Synthetic project data should resemble realistic internal company records.

The dataset should include:

- Multiple departments
- Multiple document types
- Multiple uploaders
- Different file sizes
- Different upload dates
- At least several dozen document records by the AWS migration stage

The data should be varied enough to support meaningful migration validation instead of testing with only one or two files.

---

## 25. Migration Validation Metrics

The migration process should compare source and destination values including:

- Total document record count
- Document count by department
- Document count by file type
- Total stored object count
- Total file size
- Individual file checksums
- Missing object count
- Missing database record count
- Application health status
- Upload test after cutover
- Download test after cutover
- Delete test after cutover

These metrics will provide objective evidence that the migration was completed successfully.