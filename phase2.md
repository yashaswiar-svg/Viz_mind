# VizMind — Phase 2: Dataset Ingestion & Secure File Management

## ROLE

Act as a senior Python/FastAPI backend engineer and full-stack architect working on the existing **VizMind — AI-Powered Data Analyst** project.

Phase 1 has already been implemented and verified.

Your task is to implement **ONLY Phase 2: Dataset Ingestion & Secure File Management** on top of the existing Phase 1 architecture.

Do not redesign the project unnecessarily.

---

# 1. FIRST: INSPECT THE EXISTING PROJECT

Before modifying anything:

1. Inspect the complete existing repository.
2. Read:

   * `README.md`
   * `docs/architecture.md`
   * `docs/development.md`
   * `docs/api.md`
   * `docs/roadmap.md`
   * backend configuration
   * database setup
   * Dataset model
   * Dataset repository
   * Dataset schemas
   * Dataset service
   * Alembic configuration
   * existing tests
   * frontend API service
3. Verify how Phase 1 is currently implemented.
4. Preserve all valid existing functionality.
5. Do NOT recreate the project from scratch.
6. Do NOT overwrite working code unnecessarily.
7. Reuse the existing `Dataset` model, repository, service, configuration, database, error handling, logging, and request-ID infrastructure where appropriate.

If something in Phase 1 is incomplete or broken, fix it only when it is necessary for Phase 2 to work correctly.

---

# 2. PHASE 2 OBJECTIVE

Implement a secure and production-oriented dataset ingestion pipeline:

```text
User
  ↓
React Upload UI
  ↓
FastAPI Upload Endpoint
  ↓
File Validation
  ↓
Secure Filename Generation
  ↓
Safe File Storage
  ↓
Dataset Metadata
  ↓
PostgreSQL
  ↓
Dataset API Response
```

The system should allow a user to upload supported dataset files and have VizMind safely store the file while recording its metadata in PostgreSQL.

---

# 3. PHASE 2 SUPPORTED FILE TYPES

Support these dataset formats:

### CSV

```text
.csv
```

### Excel

```text
.xlsx
.xls
```

Do NOT add additional formats yet.

Do NOT support:

* JSON
* Parquet
* XML
* PDF
* images
* databases
* ZIP archives

These can be considered later.

---

# 4. IMPORTANT PHASE BOUNDARY

Phase 2 is ONLY about ingestion.

DO NOT implement:

* dataset profiling
* row/column analysis
* missing-value analysis
* duplicate detection
* data-type inference
* data cleaning
* preprocessing
* visualization
* chart recommendation
* pattern discovery
* anomaly detection
* machine learning
* forecasting
* LLM integration
* natural-language queries
* AI-generated insights

The uploaded file should be stored and its metadata registered.

The next phase will analyze the dataset.

---

# 5. STORAGE ARCHITECTURE

Introduce a configurable local dataset storage directory.

Use the existing configuration system.

Add:

```text
STORAGE_PATH=./storage/datasets
```

or an equivalent configurable path.

The actual path must come from application configuration.

Do NOT hardcode storage paths throughout the application.

Recommended structure:

```text
storage/
└── datasets/
    ├── <dataset-uuid>/
    │   └── <generated-safe-filename>
    │
    ├── <dataset-uuid>/
    │   └── <generated-safe-filename>
```

Each uploaded dataset should have its own directory.

This prevents filename collisions and makes future dataset lifecycle management easier.

---

# 6. FILE SECURITY

Implement secure file handling.

Never trust:

* original filename
* user-provided path
* file extension
* MIME type
* directory name

The original filename is metadata only.

Generate a server-side safe storage filename.

For example:

```text
dataset_<uuid>.csv
```

or:

```text
dataset_<uuid>.xlsx
```

Do not use the user's filename directly as the stored filename.

---

# 7. PATH TRAVERSAL PROTECTION

Explicitly protect against filenames such as:

```text
../../malicious.csv
..\..\malicious.csv
/etc/passwd
C:\Windows\System32\...
```

The resolved storage path must always remain inside the configured dataset storage directory.

Use safe path resolution and verify the resulting path is a child of the intended storage root.

If the path escapes the storage directory:

Return a validation error.

Never write the file.

---

# 8. FILE SIZE LIMIT

Introduce a configurable maximum upload size.

Add configuration such as:

```text
MAX_UPLOAD_SIZE_MB=50
```

Default:

```text
50 MB
```

The value must be configurable through environment variables.

Reject files larger than the configured limit.

Return a clear API error.

Example:

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "The uploaded file exceeds the maximum allowed size of 50 MB."
  }
}
```

Do not silently truncate files.

---

# 9. FILE TYPE VALIDATION

Validate uploaded files using BOTH:

1. Extension
2. Content/MIME information where practical

Allowed extensions:

```text
.csv
.xlsx
.xls
```

Do not rely only on the filename extension.

Reject unsupported files with a clear error.

Example:

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only CSV and Excel files are supported."
  }
}
```

For Excel files, use appropriate format validation.

For CSV, validate that the file is plausibly a readable text/CSV file without performing full profiling.

---

# 10. FILE UPLOAD ENDPOINT

Create:

```text
POST /api/v1/datasets
```

Use multipart/form-data.

Expected request:

```text
file=<uploaded dataset>
```

Optional metadata can include a user-friendly dataset name if the architecture already supports it.

Do not require users to manually provide:

* UUID
* storage path
* file size
* status
* timestamps

These must be generated by the backend.

---

# 11. UPLOAD RESPONSE

A successful upload should return the registered dataset metadata.

Example:

```json
{
  "id": "uuid",
  "name": "sales_data",
  "original_filename": "sales_data.csv",
  "file_type": "csv",
  "file_size": 245678,
  "storage_path": "...",
  "status": "ready",
  "created_at": "...",
  "updated_at": "..."
}
```

Do not expose unnecessary internal filesystem details to the frontend.

Prefer returning a safe logical storage identifier/path rather than the absolute server filesystem path.

---

# 12. DATASET STATUS

Use the existing Dataset status model.

Recommended lifecycle:

```text
pending
   ↓
ready
```

If ingestion fails:

```text
pending
   ↓
failed
```

The system must avoid leaving misleading `ready` records when the physical file was not successfully stored.

---

# 13. ATOMIC INGESTION BEHAVIOR

The upload process must handle partial failures safely.

Recommended flow:

```text
1. Receive file
2. Validate request
3. Validate file type
4. Validate file size
5. Generate dataset UUID
6. Create dataset storage directory
7. Write file safely
8. Verify file was written
9. Create/update database metadata
10. Mark dataset ready
11. Return response
```

If file storage fails:

* do not create a misleading `ready` database record
* clean up partially written files where possible

If database persistence fails after file storage:

* attempt to delete the stored file
* return an appropriate server error

Do not leave uncontrolled orphan files whenever reasonably preventable.

---

# 14. FILE WRITING

Avoid loading the entire uploaded file into memory unnecessarily.

Use streaming/chunked writing where appropriate.

This is especially important because future datasets may be significantly larger.

Do not assume all datasets will be small.

---

# 15. DATASET SERVICE

Extend the existing:

```text
dataset_service.py
```

with ingestion-related operations.

Responsibilities should include:

* validation coordination
* storage coordination
* dataset metadata creation
* lifecycle/status handling
* cleanup on failure

Do not put all ingestion logic directly inside the API route.

The desired architecture is:

```text
API Route
    ↓
Dataset Service
    ↓
File Validation / Storage Utilities
    ↓
Dataset Repository
    ↓
PostgreSQL
```

---

# 16. FILE STORAGE SERVICE

Create a dedicated storage abstraction if appropriate.

For example:

```text
backend/app/services/storage_service.py
```

Responsibilities:

* create dataset directory
* generate safe filename
* save uploaded file
* verify file
* delete file
* resolve safe storage path

Keep filesystem operations separate from database operations.

This abstraction will make it easier to replace local storage with cloud/object storage in a future phase.

---

# 17. FILE VALIDATION SERVICE

Create a reusable validation layer if appropriate.

For example:

```text
backend/app/services/file_validation_service.py
```

Responsibilities:

* extension validation
* MIME/content validation
* size validation
* filename safety checks
* supported format detection

Do not put all validation inside the FastAPI route.

---

# 18. DATASET API ENDPOINTS

Implement the following endpoints.

### Upload

```text
POST /api/v1/datasets
```

### Get dataset

```text
GET /api/v1/datasets/{dataset_id}
```

### List datasets

```text
GET /api/v1/datasets
```

### Delete dataset

```text
DELETE /api/v1/datasets/{dataset_id}
```

Deletion must remove:

1. Database metadata
2. Associated physical file/storage directory

Handle failures carefully.

If the dataset does not exist:

Return an appropriate 404 response.

---

# 19. LIST DATASETS

The list endpoint should support basic pagination.

Example:

```text
GET /api/v1/datasets?page=1&page_size=20
```

Reasonable limits:

```text
page >= 1
1 <= page_size <= 100
```

Do not implement advanced search/filtering yet unless already supported by the existing architecture.

Return useful pagination metadata.

Example:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

---

# 20. GET DATASET

Implement:

```text
GET /api/v1/datasets/{dataset_id}
```

Return metadata only.

Do NOT return the dataset contents.

Do NOT expose the physical file directly through this endpoint.

---

# 21. DELETE DATASET

Implement:

```text
DELETE /api/v1/datasets/{dataset_id}
```

Expected behavior:

```text
Find Dataset
      ↓
Locate associated storage
      ↓
Delete physical file/directory
      ↓
Delete database record
```

If the dataset does not exist:

```text
404
```

Use the existing standardized error response.

---

# 22. DUPLICATE FILES

Do not implement sophisticated deduplication in Phase 2.

However, calculate/store a file checksum only if it can be added cleanly without unnecessarily changing the current architecture.

If adding checksum support:

```text
SHA-256
```

should be used.

Do NOT reject duplicate files automatically unless explicitly designed and tested.

Duplicate handling can be expanded later.

---

# 23. EMPTY FILES

Reject empty uploads.

For example:

```text
0 bytes
```

should return:

```text
400 Bad Request
```

with an appropriate error code such as:

```text
EMPTY_FILE
```

Do not create a database record for an empty file.

---

# 24. CORRUPTED FILES

Reject obviously invalid Excel files.

For `.xlsx` and `.xls`, perform basic readability/format validation sufficient to determine whether the file is structurally valid.

Do not perform dataset profiling.

For CSV, perform only basic file validity checks.

Do not calculate:

* columns
* rows
* missing values
* distributions
* correlations

Those belong to Phase 3.

---

# 25. DATASET NAME

If no explicit dataset name is supplied, derive a safe logical name from the original filename without the extension.

Example:

```text
sales_data.csv
```

becomes:

```text
sales_data
```

Do not use the original filename as the physical storage filename.

---

# 26. DATABASE CHANGES

Review the existing Dataset model before modifying it.

Only add fields that are genuinely required for Phase 2.

Potential fields:

```text
id
name
original_filename
file_type
file_size
storage_path
status
created_at
updated_at
```

If checksum is implemented:

```text
checksum
```

Do not unnecessarily redesign the existing schema.

If changes are required:

1. Modify SQLAlchemy model
2. Create a new Alembic migration
3. Run migration
4. Verify existing data remains valid

Never edit an already-applied migration merely to avoid creating a new migration.

---

# 27. DATABASE TRANSACTION SAFETY

Use proper SQLAlchemy transactions.

Do not leave half-created dataset records.

The service must coordinate:

```text
Filesystem
+
Database
```

as safely as possible.

Remember that filesystem and PostgreSQL transactions cannot be truly atomic together.

Therefore implement explicit cleanup/rollback behavior.

---

# 28. ERROR CODES

Use consistent error codes.

At minimum:

```text
FILE_REQUIRED
EMPTY_FILE
UNSUPPORTED_FILE_TYPE
FILE_TOO_LARGE
INVALID_FILE
INVALID_FILENAME
DATASET_NOT_FOUND
STORAGE_ERROR
DATABASE_ERROR
```

Keep the existing standardized error response structure.

---

# 29. LOGGING

Use the existing centralized logger.

Log important ingestion events:

```text
upload_started
upload_validated
file_stored
dataset_created
upload_completed
upload_failed
dataset_deleted
```

Include:

* request ID
* dataset ID where available
* filename where appropriate

Do NOT log:

* file contents
* credentials
* secrets
* API keys

---

# 30. FRONTEND — DATASET UPLOAD UI

Extend the existing Dashboard Placeholder into a basic dataset ingestion interface.

Create a clean upload area.

It should allow:

* selecting a file
* showing selected filename
* showing file size
* uploading
* displaying upload progress/status
* displaying validation errors
* displaying successful dataset metadata

Supported formats should be clearly displayed:

```text
CSV, XLSX, XLS
```

Maximum size should be communicated as:

```text
Maximum file size: 50 MB
```

But read the actual configured limit from a suitable backend/API configuration mechanism if practical rather than hardcoding contradictory values.

---

# 31. FRONTEND DATASET LIST

After successful upload, display the dataset in a dataset list/table.

Show:

```text
Dataset Name
Original Filename
File Type
File Size
Status
Created At
Actions
```

Actions:

```text
View
Delete
```

The "View" action should display metadata only.

Do NOT display dataset analysis yet.

---

# 32. FRONTEND API SERVICE

Extend:

```text
frontend/src/services/api.js
```

with centralized functions for:

```text
uploadDataset()
getDataset()
listDatasets()
deleteDataset()
```

Do not put API calls directly inside UI components.

Handle API errors consistently.

---

# 33. UX REQUIREMENTS

The upload UI should have clear states:

```text
Idle
 ↓
File Selected
 ↓
Uploading
 ↓
Success
```

and failure:

```text
Uploading
 ↓
Error
```

Prevent accidental duplicate submissions while an upload is in progress.

Disable the upload button while uploading.

Show meaningful error messages.

---

# 34. BACKEND TESTS

Add comprehensive Phase 2 tests.

At minimum test:

### Successful uploads

* CSV upload
* XLSX upload

### Validation

* unsupported extension
* empty file
* oversized file
* malformed/invalid Excel
* invalid filename/path traversal attempt

### Dataset APIs

* create/upload
* get by ID
* list
* pagination
* delete
* 404 for unknown dataset

### Database

Verify metadata persistence.

Verify:

```text
id
name
original_filename
file_type
file_size
storage_path
status
timestamps
```

### Filesystem

Verify:

* physical file exists after successful upload
* generated filename is safe
* file is stored inside configured storage root
* physical file is deleted after dataset deletion

### Failure handling

Simulate storage/database failures where practical and verify cleanup behavior.

---

# 35. TEST ISOLATION

All Phase 2 tests must use:

```text
DATABASE_TEST_URL
```

and a dedicated test storage directory.

NEVER use the real development storage directory during tests.

For example:

```text
storage/test-datasets/
```

or a pytest temporary directory.

Tests must clean up after themselves.

Do not leave uploaded test files behind.

---

# 36. SECURITY TESTS

Explicitly test malicious filenames such as:

```text
../../evil.csv
..\..\evil.csv
../../../tmp/test.csv
C:\Windows\System32\test.csv
```

The application must never write outside the configured storage directory.

Also test unsupported formats such as:

```text
.exe
.zip
.py
.html
```

and ensure they are rejected.

---

# 37. API DOCUMENTATION

FastAPI's generated OpenAPI documentation should correctly show:

```text
POST /api/v1/datasets
GET /api/v1/datasets
GET /api/v1/datasets/{dataset_id}
DELETE /api/v1/datasets/{dataset_id}
```

Document:

* accepted file types
* maximum file size
* response structures
* possible errors

---

# 38. DOCUMENTATION UPDATES

Update:

### README.md

Add:

* dataset upload functionality
* supported formats
* maximum file size
* storage configuration
* API examples

### docs/api.md

Document all Phase 2 dataset endpoints.

### docs/architecture.md

Update architecture to include:

```text
Upload
 ↓
Validation
 ↓
Storage Service
 ↓
Dataset Service
 ↓
Repository
 ↓
PostgreSQL
```

### docs/development.md

Document:

* storage directory
* environment configuration
* testing
* running uploads locally

### docs/roadmap.md

Mark Phase 2 as implemented and Phase 3 as the next planned phase.

---

# 39. DOCKER CONSIDERATIONS

Ensure dataset storage works correctly when running through Docker.

The storage directory must be persistent during development.

Configure an appropriate volume if required.

For example:

```text
host storage
      ↓
container /app/storage
```

Do not store uploaded datasets only inside a disposable container layer.

---

# 40. PERFORMANCE CONSIDERATIONS

Do not unnecessarily load complete files into memory.

Use streaming/chunked upload handling where appropriate.

Keep the API responsive for reasonably sized files up to the configured 50 MB limit.

Do not introduce background workers, Celery, Kafka, or Redis in Phase 2.

They are unnecessary at this stage.

---

# 41. REGRESSION TESTING

Before declaring Phase 2 complete:

Run ALL existing Phase 1 tests.

Then run all new Phase 2 tests.

Verify:

```text
Phase 1 tests → PASS
Phase 2 tests → PASS
Frontend build → PASS
Alembic migrations → PASS
Docker environment → PASS
```

Do not break existing health endpoints.

Verify:

```text
GET /api/v1/health
GET /api/v1/health/db
```

still work.

---

# 42. ACCEPTANCE CRITERIA

Phase 2 is complete only when all of the following are true:

### Upload

```text
POST /api/v1/datasets
```

successfully accepts valid:

```text
.csv
.xlsx
.xls
```

files.

### Validation

The system rejects:

* unsupported formats
* empty files
* oversized files
* invalid/corrupted supported files
* malicious path traversal attempts

### Storage

Files are:

* safely stored
* uniquely named
* stored inside configured storage root
* associated with a Dataset UUID

### Database

Metadata is persisted correctly.

### Retrieval

```text
GET /api/v1/datasets/{id}
```

works.

### Listing

```text
GET /api/v1/datasets
```

works with pagination.

### Deletion

```text
DELETE /api/v1/datasets/{id}
```

removes both metadata and physical storage.

### Frontend

User can:

```text
Select file
   ↓
Upload
   ↓
See progress/status
   ↓
See dataset metadata
   ↓
See dataset in list
   ↓
Delete dataset
```

### Testing

All tests pass.

### Security

No uploaded file can escape the configured storage directory.

### Regression

Phase 1 remains fully functional.

---

# 43. STRICT PHASE 2 BOUNDARY

After completing the above:

STOP.

Do NOT start Phase 3.

Specifically do NOT implement:

* row count analysis
* column count analysis
* data type detection
* missing value analysis
* duplicate detection
* cardinality analysis
* data quality scoring
* statistical summaries
* distributions
* profiling
* preprocessing

Those belong to:

# PHASE 3 — DATA PROFILING & DATA QUALITY

---

# 44. FINAL VERIFICATION

Before declaring Phase 2 complete, run and verify:

```bash
pytest
```

```bash
npm run build
```

```bash
alembic upgrade head
```

and verify the API endpoints manually or through automated tests.

If Docker is part of the existing development workflow, verify:

```bash
docker compose up --build
```

Then verify:

```text
Frontend
   ↓
FastAPI
   ↓
PostgreSQL
```

and a real dataset upload through the running application.

---

# 45. FINAL REPORT

At the end, provide a concise report containing:

1. Files created
2. Files modified
3. Database changes
4. Alembic migration created
5. Upload endpoint status
6. Dataset CRUD endpoint status
7. File validation status
8. Storage/security status
9. Frontend upload UI status
10. Test results
11. Frontend build result
12. Docker verification
13. Any known issues
14. Confirmation that Phase 3 was NOT started

If anything fails:

**Fix it before declaring Phase 2 complete.**

Do not hide warnings or known failures.

Do not claim Phase 2 is complete if the acceptance criteria are not satisfied.
