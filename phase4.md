# VIZMIND — PHASE 4 IMPLEMENTATION PROMPT

## Automated Data Preprocessing & Data Preparation Engine

You are implementing **Phase 4 of VizMind: Intelligent Data Visualization and Pattern Discovery**.

Phase 1, Phase 2, and Phase 3 are already implemented.

Phase 3 currently provides:

* Read-only dataset loading
* CSV / XLSX / XLS support
* Semantic type inference
* Dataset profiling
* Column profiling
* Missingness analysis
* Duplicate detection
* Constant-column detection
* High-cardinality detection
* Numeric statistics
* Categorical statistics
* Text statistics
* Datetime statistics
* Boolean statistics
* Data quality scoring
* Data quality findings
* Profile persistence
* Profile APIs
* Dataset profile UI
* SHA-256 source integrity verification

Phase 4 must now implement:

> **Automated Data Preprocessing & Data Preparation**

The goal is to transform a raw dataset into a **derived analysis-ready dataset** while preserving the original source dataset completely unchanged.

---

# 1. CORE OBJECTIVE

Build a deterministic preprocessing engine that can take:

```text
Original Uploaded Dataset
        ↓
Phase 3 Profile
        ↓
Preprocessing Decision Engine
        ↓
Preprocessing Pipeline
        ↓
Processed / Analysis-Ready Dataset
        ↓
Preprocessing Report
```

VizMind should automatically identify and safely handle common preparation problems such as:

* missing values
* duplicate rows
* incorrect or inconsistent data types
* malformed datetime values
* unusable columns
* constant columns
* excessive missingness
* categorical encoding
* numerical scaling where appropriate
* basic text normalization where justified
* feature preparation

However:

> Every transformation must be deterministic, explainable, configurable, and recorded.

---

# 2. MOST IMPORTANT DATA-INTEGRITY RULE

## NEVER MODIFY THE ORIGINAL DATASET

The Phase 2 uploaded file is the immutable source dataset.

Phase 4 must NEVER:

* overwrite the original file
* modify the original file
* change the original Dataset record's source checksum
* silently replace the original dataset
* delete the original dataset
* write processed data over the source path

Instead:

```text
Original Dataset
       ↓
Read
       ↓
Transform in memory
       ↓
Save a NEW derived/processed dataset
```

The original checksum must remain unchanged.

---

# 3. STRICT PHASE BOUNDARY

Phase 4 includes:

### Allowed

* missing-value handling
* duplicate handling
* type normalization
* datetime normalization
* constant/empty-column handling
* high-missingness handling
* categorical encoding
* numerical scaling
* deterministic text normalization
* basic feature preparation
* preprocessing pipeline
* preprocessing report
* transformation history
* processed dataset storage
* processed dataset metadata
* preview of changes

### DO NOT IMPLEMENT YET

Do NOT implement:

* automatic visualization recommendations
* chart generation
* pattern discovery
* correlation intelligence
* anomaly detection
* clustering
* PCA
* machine learning models
* prediction
* forecasting
* LLM
* AI-generated insights
* natural-language analyst
* chatbot
* advanced feature selection based on predictive modeling

Those belong to later phases.

---

# 4. FIRST ACTION — INSPECT EXISTING IMPLEMENTATION

Before writing code, inspect the complete existing project.

Inspect:

```text
backend/app/
backend/tests/
backend/alembic/
frontend/src/
docs/
```

Especially inspect the actual Phase 3 implementation:

```text
dataset_loader.py
profiling_service.py
data_quality_service.py
profile_repository.py
dataset_profile.py
dataset_column_profile.py
profiles.py
DatasetProfileView.jsx
DatasetList.jsx
DashboardPlaceholder.jsx
```

Also inspect:

* Dataset model
* Dataset repository
* Storage service
* File validation service
* API error handling
* database session management
* logging
* configuration
* Alembic migrations
* existing API service
* existing frontend components
* existing tests

Do NOT duplicate existing functionality.

Reuse Phase 2 and Phase 3 services wherever appropriate.

---

# 5. TARGET ARCHITECTURE

Implement this pipeline:

```text
Original Dataset
      ↓
Dataset Loader
      ↓
Phase 3 Profile
      ↓
Preprocessing Planner
      ↓
Transformation Plan
      ↓
Preprocessing Executor
      ↓
Processed DataFrame
      ↓
Processed Dataset Storage
      ↓
Preprocessing Report
      ↓
PostgreSQL
      ↓
Frontend Preprocessing View
```

Conceptually:

```text
RAW DATA
   ↓
UNDERSTAND
   ↓
PLAN
   ↓
TRANSFORM
   ↓
VALIDATE
   ↓
SAVE DERIVED DATA
   ↓
REPORT CHANGES
```

---

# 6. NEW BACKEND COMPONENTS

Create components following the existing architecture.

Recommended:

```text
backend/app/services/preprocessing_service.py
backend/app/services/preprocessing_planner.py
backend/app/services/preprocessing_transformers.py
backend/app/db/models/preprocessing_job.py
backend/app/db/models/preprocessing_transformation.py
backend/app/db/repositories/preprocessing_repository.py
backend/app/api/routes/preprocessing.py
```

Do not blindly create every file if the existing architecture suggests a better structure.

Reuse existing services.

---

# 7. PREPROCESSING JOB MODEL

Create a database entity representing a preprocessing run.

Recommended fields:

```text
id
dataset_id
source_profile_id
status
started_at
completed_at
rows_before
rows_after
columns_before
columns_after
output_dataset_id
error_message
created_at
updated_at
```

Status:

```text
PENDING
RUNNING
COMPLETED
FAILED
```

The job should reference:

```text
source dataset
Phase 3 profile
processed dataset
```

where applicable.

---

# 8. PROCESSED DATASET MODEL

Do NOT overload the original Dataset record.

A processed dataset must be represented separately.

Recommended approach:

Create a derived dataset record containing:

```text
id
parent_dataset_id
name
original_filename
file_type
file_size
storage_path
checksum
status
dataset_kind
created_at
updated_at
```

Where:

```text
dataset_kind:
SOURCE
PROCESSED
```

If the existing Dataset architecture can represent derived datasets cleanly, extend it rather than creating a completely separate duplicate dataset system.

Important:

```text
processed_dataset.parent_dataset_id
```

must reference the original source dataset.

This creates:

```text
Source Dataset
      ↓
Processed Dataset
```

---

# 9. PROCESSED FILE STORAGE

Use the existing Phase 2 StorageService.

Do NOT create a second storage mechanism.

Processed datasets must be stored separately from source datasets.

Example conceptual structure:

```text
storage/
    datasets/
        <source-id>/
            original.csv

    processed/
        <processed-id>/
            processed.csv
```

The exact physical structure should follow the existing StorageService architecture.

Never expose physical filesystem paths through the API.

---

# 10. PREPROCESSING TRANSFORMATION MODEL

Every transformation must be recorded.

Create a transformation table such as:

```text
PreprocessingTransformation
```

Fields:

```text
id
job_id
step_order
transformation_type
column_name
parameters
rows_affected
values_affected
description
created_at
```

Example:

```json
{
  "step_order": 1,
  "transformation_type": "MISSING_VALUE_IMPUTATION",
  "column_name": "age",
  "parameters": {
    "strategy": "median"
  },
  "values_affected": 43,
  "description": "Missing numeric values replaced with column median."
}
```

Do not store raw dataset contents.

---

# 11. PREPROCESSING PLAN

Create a preprocessing planner.

Recommended:

```text
backend/app/services/preprocessing_planner.py
```

The planner receives:

```text
DataFrame
+
Phase 3 profile
```

and produces:

```text
PreprocessingPlan
```

Example:

```json
{
  "steps": [
    {
      "type": "REMOVE_DUPLICATES",
      "reason": "Duplicate rows detected",
      "enabled": true
    },
    {
      "type": "IMPUTE_MISSING_NUMERIC",
      "column": "age",
      "strategy": "median",
      "enabled": true
    }
  ]
}
```

The planner must be deterministic.

Do NOT use an LLM.

Do NOT make arbitrary decisions.

---

# 12. CONFIGURATION

Preprocessing thresholds and strategies must be configurable.

Do not hard-code dozens of magic numbers throughout the code.

Create centralized configuration/constants for values such as:

```text
HIGH_MISSINGNESS_THRESHOLD
HIGH_CARDINALITY_THRESHOLD
NUMERIC_IMPUTATION_STRATEGY
CATEGORICAL_IMPUTATION_STRATEGY
MAX_CATEGORICAL_CARDINALITY_FOR_ONE_HOT
OUTLIER_THRESHOLD
```

Use sensible defaults.

Document the defaults.

---

# 13. MISSING-VALUE HANDLING

Implement deterministic missing-value strategies.

## Numeric columns

Default:

```text
median imputation
```

Why:

Median is more robust to skew and extreme values than mean.

However, this is an implementation rule, not an ML decision.

Record:

```text
strategy = median
```

Example:

```text
Age:
10 missing values
median = 25
10 values replaced with 25
```

---

# 14. CATEGORICAL MISSING VALUES

For categorical columns use:

```text
most_frequent
```

or:

```text
"Unknown"
```

Choose ONE default strategy and document it.

Recommended:

```text
"Unknown"
```

because it avoids pretending that a missing category belongs to the most common existing category.

Record:

```text
strategy = constant
value = Unknown
```

---

# 15. TEXT MISSING VALUES

For text columns:

Use an explicit empty/missing marker such as:

```text
""
```

or:

```text
"Unknown"
```

Choose a deterministic strategy.

Do not convert missing text into arbitrary information.

Record the transformation.

---

# 16. DATETIME HANDLING

Datetime preprocessing must be conservative.

For datetime columns:

1. Parse valid datetime values.
2. Identify invalid datetime values.
3. Convert invalid values to missing/null.
4. Apply the configured missing-value strategy if appropriate.

Do NOT invent dates.

Do NOT infer dates from unrelated columns.

Do NOT silently change ambiguous date formats without documentation.

Record:

```text
original inferred type
normalized type
invalid values
conversion strategy
```

---

# 17. BOOLEAN HANDLING

Preserve boolean semantics.

Normalize obvious boolean representations only when deterministic.

Examples:

```text
True / False
true / false
1 / 0
```

Do not automatically interpret arbitrary values such as:

```text
"maybe"
"unknown"
"yes"
"no"
```

unless the rule is explicitly configured.

Invalid boolean values should be reported rather than guessed.

---

# 18. DUPLICATE HANDLING

Phase 3 only detected duplicates.

Phase 4 may remove exact duplicate rows.

Default behavior:

```text
REMOVE_DUPLICATES
```

Use:

```python
df.drop_duplicates()
```

Record:

```text
rows_before
rows_after
duplicates_removed
```

Do not alter the source file.

---

# 19. EMPTY COLUMNS

If a column contains 100% missing values:

Do not attempt meaningless imputation.

Default behavior:

```text
DROP_EMPTY_COLUMN
```

Record:

```text
column
reason = 100% missing
action = dropped
```

This must be clearly visible in the preprocessing report.

---

# 20. CONSTANT COLUMNS

If a column has only one meaningful value:

Default behavior:

```text
DROP_CONSTANT_COLUMN
```

Reason:

Constant columns provide no variation for downstream analysis.

Record:

```text
column
constant_value
action
```

Do not modify the original dataset.

---

# 21. HIGH-MISSINGNESS COLUMNS

High missingness requires conservative handling.

Do NOT automatically drop every high-missingness column.

Use a configurable threshold.

Example:

```text
>= 80% missing
```

may be considered a candidate for removal.

But the preprocessing planner must distinguish:

```text
100% missing
very high missingness
moderate missingness
```

Recommended default:

```text
100% missing → drop
>= 80% missing → drop candidate
< 80% → impute where appropriate
```

Every decision must be recorded.

---

# 22. HIGH CARDINALITY

Do NOT blindly one-hot encode every categorical column.

Example:

```text
customer_id
transaction_id
email
```

may have extremely high cardinality.

One-hot encoding these columns can explode dimensionality.

Default behavior:

* detect high-cardinality columns
* do not one-hot encode them automatically
* preserve them unless they are clearly unusable
* record them as `HIGH_CARDINALITY_SKIPPED`

Later ML/feature-selection phases can determine whether such columns should be used.

---

# 23. CATEGORICAL ENCODING

Implement deterministic categorical encoding for suitable low-cardinality categorical columns.

Recommended default:

```text
One-Hot Encoding
```

Only apply when cardinality is below a configurable threshold.

Example:

```text
<= 20 unique categories
```

Create columns such as:

```text
city_Bangalore
city_Mumbai
city_Delhi
```

Important:

The original categorical column must not be modified in the source dataset.

The processed dataset may contain encoded columns.

Record:

```text
original_column
encoding = one_hot
categories
generated_columns
```

Avoid creating an enormous number of columns.

---

# 24. NUMERIC SCALING

Phase 4 may prepare numeric columns for future ML/analysis.

Implement an optional deterministic scaling step.

Recommended default:

```text
Standard Scaling
```

Formula:

```text
z = (x - mean) / standard_deviation
```

However:

### IMPORTANT

Do NOT automatically scale every numeric column.

Do not scale:

* identifier columns
* obvious count columns where preserving magnitude is useful
* binary numeric columns
* target-like columns unless explicitly configured

The planner should have a conservative default.

If scaling is enabled, record:

```text
mean
standard_deviation
columns_scaled
```

Do not use future prediction knowledge.

---

# 25. OUTLIERS — LIMITED PHASE 4 SCOPE

Phase 4 may implement basic outlier handling only if explicitly defined as preprocessing.

Use a deterministic statistical method such as:

```text
IQR
```

or:

```text
winsorization
```

But do NOT automatically delete valuable observations.

Recommended default:

```text
DETECT ONLY
```

rather than remove.

If actual outlier treatment is implemented, it must be:

* configurable
* deterministic
* explicitly reported
* reversible through the transformation log

Do not implement sophisticated anomaly detection.

That belongs to Phase 7.

---

# 26. TEXT NORMALIZATION

Implement only basic deterministic normalization.

Possible operations:

```text
strip leading/trailing whitespace
normalize repeated whitespace
```

Optional:

```text
lowercase
```

BUT do not lowercase every text field automatically because names, IDs, codes, and case-sensitive values may be meaningful.

Use conservative defaults.

Record each text normalization.

---

# 27. TYPE CORRECTION

Phase 4 may correct obvious type problems.

Examples:

```text
"100"
"200"
"300"
```

→ numeric

or:

```text
"2026-01-01"
"2026-01-02"
```

→ datetime

But type correction must only happen when the conversion is highly reliable.

Do not force ambiguous columns.

If conversion confidence is low:

```text
leave unchanged
report as unresolved type issue
```

Never silently coerce arbitrary data.

---

# 28. PREPROCESSING EXECUTOR

Create:

```text
backend/app/services/preprocessing_service.py
```

The executor should:

1. Load original dataset.
2. Retrieve Phase 3 profile.
3. Generate preprocessing plan.
4. Execute steps in deterministic order.
5. Track each transformation.
6. Validate resulting DataFrame.
7. Save processed dataset.
8. Create processed dataset metadata.
9. Save transformation history.
10. Update preprocessing job.
11. Return preprocessing report.

Recommended execution order:

```text
1. Type normalization
2. Invalid-value normalization
3. Duplicate removal
4. Empty-column removal
5. Constant-column removal
6. Missing-value handling
7. Conservative text normalization
8. Categorical encoding
9. Optional numeric scaling
10. Validation
11. Save processed dataset
```

The exact order may be adjusted if technically necessary, but it must be deterministic and documented.

---

# 29. PREPROCESSING VALIDATION

After transformations, validate the processed DataFrame.

Check:

```text
no unexpected nulls
no invalid numeric values
no duplicate rows where duplicates were configured for removal
valid column names
valid dtypes
row count
column count
```

Do not claim the dataset is "perfect."

The report should clearly state remaining issues.

---

# 30. PROCESSED DATASET CHECKSUM

After writing the processed dataset:

Calculate a SHA-256 checksum.

Store it in the processed Dataset record.

The source Dataset checksum must remain unchanged.

Mandatory validation:

```text
source_checksum_before
==
source_checksum_after
```

---

# 31. PREPROCESSING REPORT

Create a structured report.

Example:

```json
{
  "source_dataset_id": "...",
  "processed_dataset_id": "...",
  "rows_before": 10000,
  "rows_after": 9820,
  "columns_before": 20,
  "columns_after": 27,
  "transformations": [
    {
      "type": "REMOVE_DUPLICATES",
      "rows_affected": 180
    },
    {
      "type": "IMPUTE_MISSING_NUMERIC",
      "column": "age",
      "strategy": "median",
      "values_affected": 42
    },
    {
      "type": "ONE_HOT_ENCODING",
      "column": "city",
      "generated_columns": 8
    }
  ]
}
```

The report must explain:

* what changed
* why it changed
* how many values/rows/columns were affected
* what strategy was used

---

# 32. PREPROCESSING API

Create:

```text
POST /api/v1/datasets/{dataset_id}/preprocess
```

Purpose:

Run preprocessing and create a derived dataset.

Also create:

```text
GET /api/v1/datasets/{dataset_id}/preprocessing
```

Purpose:

Return the latest preprocessing job/report for the source dataset.

Optionally:

```text
GET /api/v1/preprocessing/{job_id}
```

if consistent with the existing architecture.

---

# 33. API BEHAVIOR

POST:

```text
Validate source dataset
        ↓
Verify profile exists
        ↓
Create preprocessing job
        ↓
Generate plan
        ↓
Execute
        ↓
Validate
        ↓
Create processed dataset
        ↓
Persist transformation history
        ↓
Complete job
        ↓
Return report
```

If Phase 3 profile does not exist:

Return:

```text
400/409
PROFILE_REQUIRED
```

Do NOT silently profile inside preprocessing unless the existing architecture explicitly requires it.

The intended flow is:

```text
Upload
 ↓
Profile
 ↓
Preprocess
```

---

# 34. FRONTEND API

Update:

```text
frontend/src/services/api.js
```

Add:

```text
preprocessDataset(datasetId)
getPreprocessingReport(datasetId)
```

---

# 35. FRONTEND DATASET UI

Extend the existing DatasetList/Profile UI.

After a dataset has been profiled:

show:

```text
Preprocess
```

button.

Recommended flow:

```text
Upload
 ↓
Profile
 ↓
View Profile
 ↓
Preprocess
 ↓
View Preprocessing Report
```

Do not automatically preprocess immediately after upload.

---

# 36. PREPROCESSING VIEW

Create:

```text
PreprocessingView.jsx
```

Display:

### Before

```text
Rows
Columns
Missing values
Duplicates
Quality score
```

### After

```text
Rows
Columns
Remaining missing values
Remaining duplicates
```

### Changes

Display transformation cards/table:

```text
Transformation
Column
Reason
Strategy
Values affected
Rows affected
```

Examples:

```text
Removed 180 duplicate rows
Imputed 42 missing age values using median
Removed 2 empty columns
Encoded city into 8 one-hot columns
```

---

# 37. PREPROCESSING STATUS

Support:

```text
Not Preprocessed
Preprocessing
Completed
Failed
```

During execution:

* disable duplicate requests
* show progress/loading state
* show meaningful error messages

Do not show stack traces.

---

# 38. PROCESSED DATASET UI

After successful preprocessing:

Display:

```text
Processed Dataset Created
```

Show:

* processed dataset name
* rows
* columns
* file size
* processing date
* source dataset
* transformation count

Provide a way to access the processed dataset through the existing application architecture.

Do not expose physical filesystem paths.

---

# 39. DATABASE TRANSACTION SAFETY

The preprocessing workflow must not leave inconsistent records.

Important:

If preprocessing fails before the processed file is successfully persisted:

```text
job = FAILED
```

and no incomplete processed dataset record should remain.

If database persistence fails after a processed file is created:

clean up the newly created processed file using the existing storage service.

Do not claim a true atomic transaction across PostgreSQL and the filesystem.

Implement coordinated failure cleanup.

---

# 40. TESTING

Create comprehensive tests.

### test_preprocessing_planner.py

Test:

* numeric missing strategy
* categorical missing strategy
* duplicate handling
* empty-column handling
* constant-column handling
* high-cardinality behavior
* encoding threshold
* scaling configuration
* type correction
* conservative decisions

---

### test_preprocessing_service.py

Test:

* preprocessing succeeds
* source remains unchanged
* processed dataset created
* transformations recorded
* row counts
* column counts
* missing values handled
* duplicate rows removed
* constant columns removed
* empty columns removed
* categorical encoding
* text normalization
* datetime handling
* invalid values
* validation

---

### test_preprocessing_api.py

Test:

```text
POST preprocess
GET preprocessing report
profile required
invalid dataset
reprocessing
failed preprocessing
```

---

### test_preprocessing_persistence.py

Verify:

* preprocessing job stored
* transformation records stored
* processed dataset stored
* parent-child dataset relationship
* no orphan transformation records

---

# 41. SOURCE INTEGRITY TEST

This is mandatory.

Before preprocessing:

```text
source checksum = X
```

After preprocessing:

```text
source checksum = X
```

Assert:

```text
before == after
```

Also verify:

* source file still exists
* source Dataset record unchanged
* source file size unchanged
* source checksum unchanged

---

# 42. PROCESSED DATASET TEST

Verify:

```text
processed dataset exists
processed checksum exists
processed file exists
processed file is different from source when transformations occurred
processed dataset references source dataset
```

If no transformation is required, handle the case explicitly rather than creating meaningless duplicate data.

---

# 43. IDEMPOTENCY / REPROCESSING

Running preprocessing multiple times must not modify the source dataset.

Define behavior clearly.

Recommended:

```text
Every preprocessing run creates a new preprocessing job.
```

If the resulting processed dataset is identical, do not silently overwrite previous results.

Store the relationship:

```text
source dataset
    ↓
preprocessing job 1
    ↓
processed dataset 1

source dataset
    ↓
preprocessing job 2
    ↓
processed dataset 2
```

Alternatively, if the existing architecture supports versioning, implement versioned processed datasets.

Do NOT create ambiguous "latest" records without documentation.

---

# 44. SECURITY / PRIVACY

Never:

* expose raw dataset rows through preprocessing API
* expose physical file paths
* log raw values
* store full text columns in transformation logs
* store all categorical values in reports
* expose database internals

Transformation logs should contain metadata and statistics only.

---

# 45. LOGGING

Use existing centralized logging.

Events:

```text
preprocessing_started
preprocessing_plan_created
preprocessing_step_completed
processed_dataset_created
preprocessing_completed
preprocessing_failed
```

Include:

```text
request_id
dataset_id
job_id
processed_dataset_id
```

Do not log raw dataset content.

---

# 46. DOCUMENTATION

Update:

```text
README.md
docs/architecture.md
docs/api.md
docs/development.md
docs/roadmap.md
```

Document:

* preprocessing architecture
* transformation rules
* default strategies
* thresholds
* processed dataset concept
* source/derived dataset relationship
* transformation history
* API endpoints
* error behavior
* source integrity guarantee

Update roadmap:

```text
Phase 1 — Complete
Phase 2 — Complete
Phase 3 — Complete
Phase 4 — Complete
Phase 5 — Next
```

Only mark Phase 4 complete after all acceptance criteria pass.

---

# 47. REGRESSION REQUIREMENT

All previous phases must continue working.

Run:

```bash
pytest
```

Verify:

### Phase 1

* health endpoint
* database health
* configuration
* database connection

### Phase 2

* upload
* validation
* storage
* list datasets
* retrieve dataset
* delete dataset

### Phase 3

* profile dataset
* retrieve profile
* quality score
* column profiling
* source checksum integrity

Phase 4 must not break any existing behavior.

---

# 48. FRONTEND BUILD

Run:

```bash
npm run build
```

The build must complete successfully.

No:

* compilation errors
* unresolved imports
* broken routes
* console errors caused by Phase 4

---

# 49. DATABASE MIGRATION

Create a new Alembic migration.

Do NOT modify previous migrations.

Run:

```bash
alembic upgrade head
```

Then:

```bash
alembic current
```

Verify the migration is applied.

---

# 50. REAL END-TO-END TEST

Perform a real workflow:

```text
1. Upload dataset
        ↓
2. Verify source dataset exists
        ↓
3. Profile dataset
        ↓
4. Verify profile
        ↓
5. Record source checksum
        ↓
6. Start preprocessing
        ↓
7. Verify preprocessing job
        ↓
8. Verify transformations
        ↓
9. Verify processed dataset
        ↓
10. Verify processed file
        ↓
11. Verify processed checksum
        ↓
12. Verify source checksum unchanged
        ↓
13. View preprocessing report
        ↓
14. Verify source dataset still accessible
        ↓
15. Verify Phase 3 profile still accessible
```

---

# 51. ACCEPTANCE CRITERIA

Phase 4 is complete only when ALL are satisfied.

## Backend

* [ ] Preprocessing planner
* [ ] Preprocessing executor
* [ ] Transformation tracking
* [ ] Missing-value handling
* [ ] Duplicate removal
* [ ] Empty-column handling
* [ ] Constant-column handling
* [ ] Conservative high-cardinality handling
* [ ] Categorical encoding
* [ ] Type normalization
* [ ] Datetime normalization
* [ ] Boolean normalization
* [ ] Basic text normalization
* [ ] Optional numerical scaling
* [ ] Post-processing validation
* [ ] Processed dataset creation

## Database

* [ ] Preprocessing job model
* [ ] Transformation model
* [ ] Processed/derived dataset support
* [ ] Foreign keys
* [ ] Indexes
* [ ] Migration
* [ ] No orphan records

## API

* [ ] POST preprocessing
* [ ] GET preprocessing report
* [ ] PROFILE_REQUIRED handling
* [ ] Structured errors
* [ ] No raw data exposure
* [ ] No filesystem path exposure

## Frontend

* [ ] Preprocess action
* [ ] Processing state
* [ ] Preprocessing report
* [ ] Before/after statistics
* [ ] Transformation history
* [ ] Processed dataset information
* [ ] Error state

## Integrity

* [ ] Source checksum unchanged
* [ ] Source file unchanged
* [ ] Source dataset remains accessible
* [ ] Processed dataset stored separately
* [ ] Failed jobs cleaned up correctly

## Testing

* [ ] Planner tests
* [ ] Transformation tests
* [ ] Service tests
* [ ] API tests
* [ ] Persistence tests
* [ ] Source integrity tests
* [ ] Regression tests
* [ ] E2E test

## Verification

* [ ] All pytest tests pass
* [ ] Frontend build passes
* [ ] Alembic migration succeeds
* [ ] Real preprocessing flow succeeds
* [ ] Phase 1 still works
* [ ] Phase 2 still works
* [ ] Phase 3 still works

---

# 52. IMPORTANT DESIGN PRINCIPLES

Throughout Phase 4:

### Principle 1 — Preserve the source

```text
RAW DATA = IMMUTABLE
```

### Principle 2 — Every transformation must be explainable

Never silently modify data.

### Principle 3 — Deterministic behavior

Same input + same configuration:

```text
→ same preprocessing result
```

### Principle 4 — Conservative automation

When uncertain:

```text
DO NOT GUESS
```

Instead:

```text
preserve + report
```

### Principle 5 — No LLM

Phase 4 must not depend on an LLM.

### Principle 6 — No ML

Phase 4 is preparation, not modeling.

### Principle 7 — Transformation history is mandatory

Every important change must be recorded.

### Principle 8 — Derived data is separate

Never overwrite the uploaded dataset.

---

# 53. FINAL IMPLEMENTATION REPORT

After implementation, provide:

1. Files created
2. Files modified
3. Database models added/changed
4. Alembic migration
5. Preprocessing planner
6. Preprocessing executor
7. Transformations implemented
8. Processed dataset architecture
9. Transformation history
10. API endpoints
11. Frontend components
12. Tests added
13. Total tests passed
14. Frontend build result
15. Migration result
16. E2E result
17. Source checksum verification
18. Processed dataset verification
19. Known limitations
20. Confirmation Phase 1 works
21. Confirmation Phase 2 works
22. Confirmation Phase 3 works

---

# 54. STRICT STOP CONDITION

After Phase 4 is fully implemented and verified:

**STOP.**

Do NOT start Phase 5.

Do NOT implement:

* automated chart recommendations
* chart generation
* visualization intelligence
* pattern discovery
* anomaly detection
* clustering
* PCA
* prediction
* forecasting
* ML
* LLM
* AI insight generation
* natural-language analyst

Wait for explicit instruction before beginning Phase 5.

# END OF PHASE 4 IMPLEMENTATION PROMPT
