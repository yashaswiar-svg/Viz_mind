# VIZMIND — PHASE 3 IMPLEMENTATION

## Data Profiling & Data Quality Intelligence

---

# ROLE

Act as a senior Data Scientist, Python backend engineer, FastAPI architect, statistical analyst, and data-quality engineer.

You are continuing development of the existing **VizMind — AI-Powered Data Analyst** project.

Phase 1 and Phase 2 have already been implemented and verified.

Your task is to implement **ONLY Phase 3: Data Profiling & Data Quality Intelligence**.

Do not rebuild the application.

Do not replace working Phase 1 or Phase 2 architecture.

Inspect the existing implementation first and extend it cleanly.

---

# 1. CURRENT SYSTEM

The project currently supports:

```text
React Frontend
      ↓
FastAPI Backend
      ↓
PostgreSQL
      ↓
Dataset Metadata
      ↓
Secure Local File Storage
```

Phase 2 supports:

```text
CSV
XLSX
XLS
```

Dataset files are stored using:

```text
storage/datasets/<dataset_uuid>/
```

Dataset metadata includes:

```text
id
name
original_filename
file_type
file_size
storage_path
checksum
status
created_at
updated_at
```

Phase 2 has already implemented:

```text
POST /api/v1/datasets
GET /api/v1/datasets
GET /api/v1/datasets/{dataset_id}
DELETE /api/v1/datasets/{dataset_id}
```

Do not break these APIs.

---

# 2. PHASE 3 OBJECTIVE

Implement an automated **Data Profiling Engine**.

When a user uploads a dataset, VizMind should be able to analyze the dataset and answer:

```text
What is this dataset?
How large is it?
What columns does it contain?
What are the data types?
How much data is missing?
Are there duplicate records?
What are the unique-value characteristics?
What are the basic numerical statistics?
What are the categorical characteristics?
How clean is the dataset?
What potential data-quality issues exist?
```

The high-level pipeline becomes:

```text
Uploaded Dataset
       ↓
Dataset Loader
       ↓
Data Profiling Engine
       ↓
Data Quality Engine
       ↓
Profile Result
       ↓
PostgreSQL
       ↓
Frontend Profile Dashboard
```

---

# 3. VERY IMPORTANT — PHASE 3 BOUNDARY

Phase 3 is ONLY:

> **Dataset Profiling + Data Quality Assessment**

Do NOT implement:

* automatic data cleaning
* missing-value imputation
* outlier removal
* encoding
* feature engineering
* visualization recommendation
* chart generation
* pattern discovery
* anomaly detection
* clustering
* PCA
* prediction
* forecasting
* machine learning models
* LLM integration
* natural-language querying
* AI-generated business insights

Those belong to later phases.

Phase 3 may **detect and report** issues.

It must NOT automatically modify the original dataset.

---

# 4. CORE PRINCIPLE

The uploaded source dataset must remain unchanged.

Profiling is read-only.

```text
Original Dataset
      │
      ├── Read
      │
      ▼
Profiling Engine
      │
      ├── Analyze
      ├── Calculate statistics
      ├── Detect quality issues
      │
      ▼
Profile Result
```

Never overwrite the original uploaded file during profiling.

---

# 5. TECHNOLOGY

Use:

```text
Python
Pandas
NumPy
FastAPI
SQLAlchemy
PostgreSQL
Pytest
```

Use appropriate Excel readers already supported by the project.

Do NOT add machine-learning libraries in Phase 3.

Do NOT add LLM libraries.

---

# 6. FIRST — INSPECT EXISTING PROJECT

Before modifying anything:

Inspect:

```text
backend/app/
backend/tests/
backend/alembic/
frontend/src/
docs/
```

Especially inspect:

```text
Dataset model
Dataset repository
Dataset service
Storage service
File validation service
Configuration
API routes
schemas
database
existing tests
```

Verify how the physical storage path is currently represented.

Reuse existing storage logic.

Do not duplicate file-location logic.

---

# 7. DATASET LOADER

Create a dedicated dataset-loading abstraction.

Recommended:

```text
backend/app/services/dataset_loader.py
```

Responsibilities:

```text
load_csv()
load_xlsx()
load_xls()
load_dataset()
```

The loader should:

1. Retrieve dataset metadata.
2. Resolve the safe internal storage path.
3. Verify the file exists.
4. Determine format.
5. Load it into a Pandas DataFrame.
6. Return the DataFrame for profiling.

Do not expose physical paths to the frontend.

---

# 8. SUPPORTED FORMATS

Continue supporting:

```text
.csv
.xlsx
.xls
```

Do not introduce additional formats in Phase 3.

---

# 9. LOADING SAFETY

Before profiling:

Verify:

```text
Dataset exists in database
        ↓
Physical file exists
        ↓
Path is inside configured storage root
        ↓
File format matches metadata
        ↓
File can be loaded
```

If any condition fails, return a meaningful error.

Do not profile an invalid/missing file.

---

# 10. CSV LOADING

Use Pandas appropriately for CSV files.

Handle common CSV characteristics where practical:

* UTF-8
* delimiter detection where safe
* encoding issues
* header row

Do not build a complicated automatic CSV parser.

If loading fails, return:

```text
INVALID_DATASET
```

with a useful message.

Do not modify the source file.

---

# 11. EXCEL LOADING

For `.xlsx` and `.xls`:

Load the workbook using Pandas.

For Phase 3, establish a clear sheet-selection policy.

Recommended:

* inspect workbook sheets
* use the first non-empty sheet as the default dataset
* record which sheet was profiled

If the workbook has no usable sheet:

Return an appropriate error.

Do NOT profile every sheet in Phase 3 unless the existing architecture already supports multi-sheet datasets.

Document this behavior.

---

# 12. PROFILE EXECUTION API

Create:

```text
POST /api/v1/datasets/{dataset_id}/profile
```

This endpoint triggers profiling for a specific dataset.

It should:

```text
Find Dataset
      ↓
Load File
      ↓
Profile Data
      ↓
Calculate Quality
      ↓
Persist Profile
      ↓
Return Profile
```

If a profile already exists, decide whether to:

* recompute it
* replace the previous profile

Recommended behavior:

> Recompute and replace the previous profile.

The endpoint should be idempotent in terms of the final stored profile.

---

# 13. PROFILE RETRIEVAL API

Create:

```text
GET /api/v1/datasets/{dataset_id}/profile
```

This returns the latest stored profile.

If no profile exists:

```text
404 PROFILE_NOT_FOUND
```

Do not silently profile the dataset on a GET request.

Profiling should happen explicitly through the POST endpoint.

---

# 14. PROFILE DATABASE DESIGN

Create dedicated database tables for profiling.

Do NOT store the entire profile as an unstructured blob only.

Use structured relational data for important fields.

Recommended architecture:

```text
Dataset
   │
   └── DatasetProfile
           │
           └── DatasetColumnProfile
```

---

# 15. DATASET PROFILE MODEL

Create:

```text
DatasetProfile
```

Suggested fields:

```text
id
dataset_id
row_count
column_count
duplicate_row_count
duplicate_row_percentage
missing_cell_count
missing_cell_percentage
memory_usage_bytes
quality_score
profiled_at
created_at
updated_at
```

Use appropriate numeric types.

Use foreign key:

```text
dataset_id → datasets.id
```

Ensure one current profile per dataset.

A unique constraint on:

```text
dataset_id
```

is recommended if storing only the latest profile.

---

# 16. COLUMN PROFILE MODEL

Create:

```text
DatasetColumnProfile
```

Suggested fields:

```text
id
profile_id
column_name
column_index
inferred_type
pandas_dtype
null_count
null_percentage
non_null_count
unique_count
unique_percentage
is_constant
min_value
max_value
mean_value
median_value
std_value
q1_value
q3_value
```

Do not force numerical statistics into inappropriate columns.

For categorical/date/text fields, irrelevant numerical statistics should be `NULL`.

---

# 17. DATA TYPES

Infer useful semantic categories.

At minimum classify columns as:

```text
numeric
categorical
datetime
boolean
text
```

Do not build a sophisticated ML semantic type detector.

Use deterministic Pandas-based rules.

---

# 18. NUMERIC COLUMN PROFILING

For numerical columns calculate:

```text
count
missing_count
missing_percentage
unique_count
min
max
mean
median
standard_deviation
Q1
Q3
```

Where applicable.

Use robust handling for:

* NaN
* infinite values
* empty columns

Do not modify the source data.

---

# 19. CATEGORICAL COLUMN PROFILING

For categorical columns calculate:

```text
non_null_count
missing_count
missing_percentage
unique_count
unique_percentage
```

Also calculate the most frequent values.

Recommended:

```text
top_values
```

with:

```text
value
count
percentage
```

Limit top values to a reasonable number such as:

```text
Top 10
```

Do not store unlimited category values.

---

# 20. TEXT COLUMN PROFILING

For text columns calculate:

```text
missing_count
missing_percentage
unique_count
unique_percentage
minimum_length
maximum_length
average_length
```

Do not store the entire contents of text columns in PostgreSQL.

Do not expose potentially sensitive dataset contents in profile responses.

---

# 21. DATETIME COLUMN PROFILING

For datetime columns calculate:

```text
missing_count
missing_percentage
unique_count
minimum_datetime
maximum_datetime
```

Where practical.

Handle invalid/null datetime values safely.

Do not automatically modify the source dataset.

---

# 22. BOOLEAN COLUMN PROFILING

For boolean columns calculate:

```text
missing_count
missing_percentage
unique_count
```

and value distribution:

```text
true_count
false_count
```

where applicable.

---

# 23. DUPLICATE DETECTION

Detect complete duplicate rows.

Calculate:

```text
duplicate_row_count
duplicate_row_percentage
```

Use:

```python
df.duplicated()
```

or equivalent.

Do NOT remove duplicates.

Do NOT modify the dataset.

---

# 24. MISSING VALUE ANALYSIS

Calculate:

```text
total_cells
missing_cells
missing_percentage
```

At dataset level.

For each column:

```text
null_count
null_percentage
```

Identify columns with significant missingness.

Do not automatically clean them.

---

# 25. CONSTANT COLUMNS

Detect columns where all non-null values are the same.

For example:

```text
is_constant = true
```

These should be reported as a potential quality issue.

Do not remove the column.

---

# 26. HIGH-CARDINALITY DETECTION

Calculate:

```text
unique_count
unique_percentage
```

for each column.

Flag potential high-cardinality columns using a transparent deterministic rule.

Example:

```text
unique_percentage >= 95%
```

But do not assume every high-cardinality column is a problem.

Label it as:

```text
high_cardinality
```

rather than automatically calling it "bad data."

---

# 27. DATA QUALITY ENGINE

Create a dedicated service:

```text
backend/app/services/data_quality_service.py
```

It should assess:

```text
Missingness
Duplicates
Constant columns
Invalid/unusable values
High cardinality
Potential type issues
```

Keep data-quality calculation separate from raw profiling.

Architecture:

```text
Dataset
   ↓
Dataset Loader
   ↓
Profiling Engine
   ↓
Data Quality Engine
   ↓
Profile + Quality Report
```

---

# 28. DATA QUALITY SCORE

Create a transparent quality score from:

```text
0–100
```

The score must NOT be arbitrary.

Document the calculation.

A reasonable initial model:

```text
Missingness          → 30%
Duplicates           → 20%
Invalid values       → 20%
Constant columns     → 10%
High-cardinality     → 10%
Type consistency     → 10%
```

However, if one category cannot be reliably measured for a dataset, do not fabricate a penalty.

Design the scoring system so the weights can be configured later.

The response should explain the score components.

---

# 29. QUALITY LEVEL

Map the score to a descriptive quality level.

Example:

```text
90–100 → Excellent
75–89  → Good
50–74  → Fair
0–49   → Poor
```

This is a descriptive data-quality classification, not a machine-learning prediction.

Store both:

```text
quality_score
quality_level
```

---

# 30. QUALITY ISSUES

Generate structured quality issues.

Example:

```json
{
  "code": "HIGH_MISSINGNESS",
  "severity": "warning",
  "column": "income",
  "message": "Column contains a high percentage of missing values.",
  "value": 34.5
}
```

Possible issue codes:

```text
HIGH_MISSINGNESS
DUPLICATE_ROWS
CONSTANT_COLUMN
HIGH_CARDINALITY
INVALID_VALUES
TYPE_INCONSISTENCY
EMPTY_COLUMN
```

Do not generate vague AI explanations.

These are deterministic rule-based findings.

---

# 31. SEVERITY LEVELS

Use:

```text
info
warning
critical
```

Do not exaggerate quality issues.

Example:

A column with 96% unique values should not automatically be marked as "critical."

---

# 32. PROFILE SCHEMA

Create Pydantic response schemas.

Recommended:

```text
DatasetProfileResponse
DatasetColumnProfileResponse
DataQualityIssueResponse
```

Structure approximately:

```json
{
  "dataset_id": "...",
  "profiled_at": "...",
  "overview": {
    "rows": 10000,
    "columns": 12,
    "duplicate_rows": 25,
    "missing_cells": 430
  },
  "quality": {
    "score": 86.5,
    "level": "Good",
    "issues": []
  },
  "columns": []
}
```

Keep the API response clean and frontend-friendly.

---

# 33. PROFILE PERSISTENCE

After profiling:

```text
Calculate
   ↓
Validate result
   ↓
Database transaction
   ↓
Save DatasetProfile
   ↓
Save ColumnProfiles
   ↓
Commit
```

If persistence fails:

```text
Rollback
```

Do not leave partially saved profiles.

---

# 34. PROFILE REPLACEMENT

When re-profiling:

```text
Old Profile
     ↓
New Profile
```

Do not leave multiple conflicting "current" profiles.

Recommended:

```text
Delete/replace existing current profile
```

inside a transaction.

Do not delete the original dataset.

---

# 35. LARGE DATASET SAFETY

Phase 3 should work reasonably for the Phase 2 maximum upload size of 50 MB.

Avoid unnecessary copies of the DataFrame.

Do not duplicate the entire dataset multiple times in memory.

Use efficient Pandas operations.

Do not introduce distributed processing in Phase 3.

---

# 36. PROFILE CACHE / RECOMPUTATION

Do not add Redis or external caching.

Persist the profile in PostgreSQL.

The stored profile should be returned by:

```text
GET /api/v1/datasets/{dataset_id}/profile
```

A new profile is generated only when:

```text
POST /api/v1/datasets/{dataset_id}/profile
```

is called.

---

# 37. FRONTEND — PROFILE ACTION

Extend the dataset list.

Add:

```text
Profile Dataset
```

or:

```text
Analyze Dataset
```

button.

When clicked:

```text
POST /api/v1/datasets/{id}/profile
```

Then show the profile.

---

# 38. FRONTEND PROFILE PAGE

Create a dedicated profile view.

Recommended:

```text
Dataset Profile
────────────────────────

Dataset Name

Rows       Columns
10,000     12

Data Quality
86.5 / 100
Good

Missing Data
430 cells

Duplicate Rows
25

────────────────────────

Column Overview

Column | Type | Missing | Unique | Statistics

────────────────────────

Quality Issues

⚠ High Missingness
⚠ Duplicate Rows
ℹ High Cardinality
```

Keep the UI clean and understandable.

---

# 39. COLUMN PROFILE TABLE

Show:

```text
Column Name
Data Type
Missing %
Unique %
Min
Max
Mean
Median
```

Only display statistics applicable to that column.

Do not show meaningless `N/A` values everywhere.

---

# 40. FRONTEND API SERVICE

Extend:

```text
frontend/src/services/api.js
```

with:

```text
profileDataset(id)
getDatasetProfile(id)
```

Keep API communication centralized.

---

# 41. PROFILE LOADING STATES

Support:

```text
Not Profiled
Profiling
Profile Ready
Profile Failed
```

Show clear UI feedback.

Do not make the user think the system is frozen during profiling.

---

# 42. PROFILE ERRORS

Handle:

```text
Dataset not found
File missing
Invalid dataset
Profile generation failed
Database failure
```

Display useful user-facing messages.

Do not expose stack traces.

---

# 43. TESTS — DATA LOADER

Create:

```text
test_dataset_loader.py
```

Test:

```text
CSV loading
XLSX loading
XLS loading
missing file
invalid file
unsupported format
```

---

# 44. TESTS — PROFILING ENGINE

Create:

```text
test_profiling_service.py
```

Test:

```text
row count
column count
numeric statistics
categorical statistics
text statistics
datetime statistics
boolean statistics
missing values
duplicates
constant columns
unique counts
```

Use deterministic test datasets.

---

# 45. TESTS — QUALITY ENGINE

Create:

```text
test_data_quality_service.py
```

Test:

```text
missingness scoring
duplicate scoring
constant column detection
high cardinality detection
quality score
quality level
issue generation
```

Verify calculations manually.

Do not only test that "a score exists."

---

# 46. TESTS — API

Create:

```text
test_profile_api.py
```

Test:

```text
POST /api/v1/datasets/{id}/profile
GET /api/v1/datasets/{id}/profile
```

Test:

```text
successful profiling
profile retrieval
dataset not found
profile not found
invalid dataset
reprofiling
```

---

# 47. TEST PROFILE PERSISTENCE

Verify:

```text
DatasetProfile
DatasetColumnProfile
```

records are actually persisted.

Verify relationships.

Verify a profile can be retrieved after restarting the backend.

---

# 48. TEST SOURCE DATA INTEGRITY

After profiling:

Verify the original dataset file:

```text
has not changed
```

Verify the SHA-256 checksum remains identical.

This is an important Phase 3 acceptance criterion.

---

# 49. TEST PHASE 2 REGRESSION

Run the complete Phase 1 + Phase 2 test suite.

Verify:

```text
Upload still works
List still works
Get still works
Delete still works
Health works
Database health works
```

Do not break existing APIs.

---

# 50. DATABASE MIGRATION

Create new Alembic migration(s) for:

```text
dataset_profiles
dataset_column_profiles
```

Do not modify old applied migrations.

Use foreign keys and appropriate indexes.

Recommended indexes:

```text
dataset_profiles.dataset_id
dataset_column_profiles.profile_id
```

Use cascading behavior carefully.

Deleting a Dataset should not leave orphan profile records.

---

# 51. DATA DELETION INTEGRITY

When Phase 2 deletes a dataset:

```text
Dataset
   ↓
Profile
   ↓
Column Profiles
```

All associated profiling records must also be removed.

Update the existing delete workflow appropriately.

Ensure this does not break Phase 2 deletion tests.

---

# 52. DATABASE TRANSACTIONS

Profile persistence must use a transaction.

Do not save:

```text
DatasetProfile
```

successfully while only half of the column profiles are stored.

If any persistence operation fails:

```text
Rollback everything
```

---

# 53. SECURITY / PRIVACY

Do not store entire raw column values.

Do not return complete dataset contents.

For top categorical values:

Only store a limited number of values.

Be careful with potentially sensitive datasets.

Profile results should contain statistics, not the entire dataset.

---

# 54. LOGGING

Use existing centralized logging.

Log:

```text
profile_started
dataset_loaded
profile_completed
profile_failed
profile_persisted
```

Include:

```text
request_id
dataset_id
```

Do not log full dataset contents.

---

# 55. DOCUMENTATION

Update:

```text
README.md
docs/architecture.md
docs/api.md
docs/development.md
docs/roadmap.md
```

Document:

### Phase 3

```text
Data Profiling & Data Quality
```

Include:

* profile architecture
* supported formats
* profiling metrics
* quality scoring
* API endpoints
* database models
* testing

Update roadmap:

```text
Phase 1 — Foundation           COMPLETE
Phase 2 — Dataset Ingestion    COMPLETE
Phase 3 — Data Profiling       COMPLETE
Phase 4 — Automated Preprocessing   NEXT
```

Only mark Phase 3 complete if all acceptance criteria pass.

---

# 56. API DOCUMENTATION

Document:

```text
POST /api/v1/datasets/{dataset_id}/profile
GET /api/v1/datasets/{dataset_id}/profile
```

Document:

* request
* response
* error codes
* profiling behavior
* quality score

---

# 57. NO MACHINE LEARNING

Do not install or implement:

```text
scikit-learn
xgboost
tensorflow
pytorch
```

unless an existing dependency absolutely requires them.

Phase 3 is deterministic statistical profiling.

---

# 58. NO LLM

Do not implement:

```text
OpenAI
Gemini
Claude
LangChain
RAG
LLM agents
```

Phase 3 findings must be generated by deterministic code.

AI explanations belong to Phase 8.

---

# 59. PERFORMANCE REQUIREMENT

For datasets within the Phase 2 50 MB limit:

The profile operation should complete without unnecessary memory duplication.

Use Pandas efficiently.

Do not create multiple full DataFrame copies.

Do not perform expensive operations repeatedly.

---

# 60. ACCEPTANCE CRITERIA

Phase 3 is complete only when all of the following work.

## Dataset loading

```text
CSV → DataFrame
XLSX → DataFrame
XLS → DataFrame
```

## Dataset overview

The profile provides:

```text
rows
columns
duplicate rows
missing cells
```

## Column profiling

Each column provides appropriate:

```text
type
missing count
missing %
unique count
unique %
```

plus relevant statistics.

## Numerical

```text
min
max
mean
median
std
Q1
Q3
```

## Categorical

```text
top values
counts
percentages
```

## Text

```text
length statistics
```

## Datetime

```text
minimum
maximum
missingness
```

## Boolean

```text
true/false distribution
```

## Quality

The system calculates:

```text
quality score
quality level
quality issues
```

## Persistence

Profile and column profiles are persisted in PostgreSQL.

## API

These work:

```text
POST /api/v1/datasets/{id}/profile
GET /api/v1/datasets/{id}/profile
```

## Frontend

User can:

```text
Upload dataset
     ↓
See dataset
     ↓
Click Profile/Analyze
     ↓
Wait for profiling
     ↓
See quality score
     ↓
See dataset overview
     ↓
See column profiles
     ↓
See quality issues
```

## Integrity

Original dataset checksum remains unchanged.

## Regression

All previous tests continue passing.

---

# 61. FINAL VERIFICATION COMMANDS

Run the complete backend tests:

```bash
pytest
```

Build the frontend:

```bash
npm run build
```

Apply migrations:

```bash
alembic upgrade head
```

Verify migration state:

```bash
alembic current
```

If Docker is part of the existing workflow:

```bash
docker compose up --build
```

Then perform a real end-to-end test:

```text
Upload CSV
    ↓
Profile
    ↓
Retrieve Profile
    ↓
View Profile in UI
    ↓
Delete Dataset
    ↓
Verify profile records are also removed
```

---

# 62. FINAL REPORT

At the end provide a concise implementation report containing:

1. Files created
2. Files modified
3. Database models added
4. Alembic migrations created
5. Dataset loader implementation
6. Profiling engine implementation
7. Data quality engine implementation
8. API endpoints
9. Frontend implementation
10. Test files added
11. Total tests passed
12. Frontend build result
13. Migration result
14. End-to-end verification result
15. Any known issues
16. Confirmation that Phase 1 still works
17. Confirmation that Phase 2 still works
18. Confirmation that Phase 4 was NOT started

If any test fails:

**Fix it before declaring Phase 3 complete.**

Do not hide failures.

Do not claim success when known issues remain.

---

# 63. STRICT STOP CONDITION

After completing Phase 3:

**STOP.**

Do not automatically implement Phase 4.

Do not implement:

* missing-value imputation
* outlier treatment
* encoding
* type correction
* feature engineering
* automated cleaning

Those belong to:

# PHASE 4 — AUTOMATED DATA PREPROCESSING

The final architecture after Phase 3 should be:

```text
                    VIZMIND

                  User
                    │
                    ▼
             React Dashboard
                    │
                    ▼
              FastAPI API
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Dataset APIs        Profile APIs
          │                   │
          ▼                   ▼
   Dataset Service      Profiling Service
          │                   │
          ▼                   ▼
   Storage Service      Quality Engine
          │                   │
          ▼                   ▼
      File System       PostgreSQL
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              DatasetProfile     ColumnProfiles
```

Phase 3 should make VizMind capable of saying:

> **"I understand the structure and quality of this dataset."**

It should NOT yet try to say:

> **"I cleaned it."**

or:

> **"This is the best chart."**

or:

> **"Here is the hidden pattern."**

Those are the responsibilities of Phases 4–6.
