# VizMind Architecture Specification — Phase 2 Update

## 1. Ingestion Pipeline Architecture

Phase 2 introduces the secure Dataset Ingestion Pipeline:

```text
React Upload Zone UI
        ↓
POST /api/v1/datasets (Multipart Form Data)
        ↓
FileValidationService
 ├── Extension Check (.csv, .xlsx, .xls)
 ├── Size Check (>0 B and <= 50 MB)
 ├── Path Traversal Check (relative_to safe base)
 └── Structural Readability Check (decode/parse sample)
        ↓
StorageService
 ├── Dataset Directory Creation (storage/datasets/<uuid>/)
 ├── Server-Side Safe Filename (dataset_<uuid>.<ext>)
 ├── Chunked Stream Storage (1 MB chunks)
 └── SHA-256 Checksum Calculation
        ↓
DatasetRepository & PostgreSQL
 └── Persist Dataset Metadata (Status: 'ready')
```

---

## 2. Updated Data Model

### `datasets` Table Schema (Alembic Migration 002)
```sql
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NULL,
    checksum VARCHAR(64) NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

---

## 3. Physical Storage Abstraction

- Root storage directory configured via `STORAGE_PATH` (default `./storage/datasets`).
- Storage layout:
  ```text
  storage/
  └── datasets/
      └── <dataset_uuid>/
          └── dataset_<generated_uuid>.<ext>
  ```
- Public API responses return logical relative path identifiers (e.g. `datasets/<uuid>/dataset_<uuid>.csv`) rather than absolute server paths.
- Deleting a dataset via `DELETE /api/v1/datasets/{id}` cleanly purges both the database record and the entire dataset physical directory (`storage/datasets/<uuid>/`).

---

## 4. Profiling & Quality Architecture (Phase 3)

Phase 3 introduces read-only in-memory profiling and database persistence:

```text
POST /api/v1/datasets/{id}/profile
        ↓
DatasetLoader Service
  └── Safely reads dataset file into Pandas DataFrame (CSV, XLSX, XLS)
        ↓
ProfilingService
  ├── Row / Column Count & Memory Footprint calculation
  ├── Column Type Inference (numeric, categorical, datetime, boolean, text)
  └── Type-Specific Summary Metrics calculation
        ↓
DataQualityService
  ├── 0–100 Weighted Score evaluation (Missingness 30%, Duplicates 20%, Invalid 20%, Constant 10%, Type Consistency 10%, Cardinality 10%)
  └── Quality Rule Finding generation (critical, warning, info)
        ↓
ProfileRepository (PostgreSQL Database Transaction)
  ├── Cascading Upsert to dataset_profiles table
  └── Atomic Replacement of dataset_column_profiles records
```

---

## 5. Profiling Database Tables Schema (Alembic Migration 003)

### `dataset_profiles` Table Schema
```sql
CREATE TABLE dataset_profiles (
    id UUID PRIMARY KEY,
    dataset_id UUID NOT NULL UNIQUE REFERENCES datasets(id) ON DELETE CASCADE,
    total_rows INTEGER NOT NULL,
    total_columns INTEGER NOT NULL,
    sheet_name VARCHAR(255) NULL,
    memory_bytes BIGINT NOT NULL,
    missing_cells INTEGER NOT NULL,
    missing_cell_percentage DOUBLE PRECISION NOT NULL,
    duplicate_rows INTEGER NOT NULL,
    duplicate_row_percentage DOUBLE PRECISION NOT NULL,
    quality_score INTEGER NOT NULL,
    quality_level VARCHAR(50) NOT NULL,
    quality_issues JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### `dataset_column_profiles` Table Schema
```sql
CREATE TABLE dataset_column_profiles (
    id UUID PRIMARY KEY,
    profile_id UUID NOT NULL REFERENCES dataset_profiles(id) ON DELETE CASCADE,
    column_name VARCHAR(255) NOT NULL,
    column_index INTEGER NOT NULL,
    inferred_type VARCHAR(50) NOT NULL,
    total_count INTEGER NOT NULL,
    null_count INTEGER NOT NULL,
    null_percentage DOUBLE PRECISION NOT NULL,
    unique_count INTEGER NOT NULL,
    unique_percentage DOUBLE PRECISION NOT NULL,
    min_value DOUBLE PRECISION NULL,
    max_value DOUBLE PRECISION NULL,
    mean_value DOUBLE PRECISION NULL,
    median_value DOUBLE PRECISION NULL,
    std_dev DOUBLE PRECISION NULL,
    q25 DOUBLE PRECISION NULL,
    q75 DOUBLE PRECISION NULL,
    skewness DOUBLE PRECISION NULL,
    min_length INTEGER NULL,
    max_length INTEGER NULL,
    avg_length DOUBLE PRECISION NULL,
    true_count INTEGER NULL,
    false_count INTEGER NULL,
    min_datetime TIMESTAMP WITH TIME ZONE NULL,
    max_datetime TIMESTAMP WITH TIME ZONE NULL,
    top_values JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

---

## 6. Preprocessing & Data Preparation Architecture (Phase 4)

Phase 4 introduces deterministic preprocessing, source dataset immutability, and versioned derived dataset creation:

```text
POST /api/v1/datasets/{id}/preprocess
        ↓
DatasetLoader Service
  └── Safely reads source dataset file into Pandas DataFrame
        ↓
PreprocessingPlanner
  ├── Evaluates Phase 3 profile and configuration rules
  └── Generates deterministic PreprocessingPlan steps
        ↓
PreprocessingTransformers
  ├── Missing numeric median imputation
  ├── Missing categorical & text "Unknown" constant imputation
  ├── Duplicate row removal
  ├── Empty & constant column removal
  ├── Text whitespace normalization
  └── One-hot encoding for low/medium cardinality (<= 20 unique categories)
        ↓
PreprocessingService & StorageService
  ├── Verifies source_checksum_before == source_checksum_after
  ├── Saves processed DataFrame to storage/processed/<processed_id>/
  └── Creates derived Dataset entity (dataset_kind="PROCESSED", parent_dataset_id=<source_id>)
        ↓
PreprocessingRepository (PostgreSQL Database Transaction)
  ├── Saves PreprocessingJob record (status: COMPLETED)
  └── Saves ordered PreprocessingTransformation audit steps
```

---

## 7. Preprocessing Database Tables Schema (Alembic Migration 004)

### `preprocessing_jobs` Table Schema
```sql
CREATE TABLE preprocessing_jobs (
    id UUID PRIMARY KEY,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    source_profile_id UUID NULL REFERENCES dataset_profiles(id) ON DELETE SET NULL,
    output_dataset_id UUID NULL REFERENCES datasets(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    rows_before INTEGER NOT NULL,
    rows_after INTEGER NOT NULL,
    columns_before INTEGER NOT NULL,
    columns_after INTEGER NOT NULL,
    missing_cells_before INTEGER NOT NULL,
    missing_cells_after INTEGER NOT NULL,
    duplicate_rows_before INTEGER NOT NULL,
    duplicate_rows_after INTEGER NOT NULL,
    source_checksum_before VARCHAR(64) NULL,
    source_checksum_after VARCHAR(64) NULL,
    processed_checksum VARCHAR(64) NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### `preprocessing_transformations` Table Schema
```sql
CREATE TABLE preprocessing_transformations (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES preprocessing_jobs(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,
    column_name VARCHAR(255) NULL,
    parameters JSONB NULL,
    rows_affected INTEGER NOT NULL DEFAULT 0,
    values_affected INTEGER NOT NULL DEFAULT 0,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

---

## 8. Productionization, Security & Authentication Architecture (Phase 10)

Phase 10 introduces Production-grade Security, User Authentication, Multi-tenant Isolation, and Container Deployment:

```text
                     Nginx Reverse Proxy Container (:80)
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
Static React Web SPA                          FastAPI Backend (:8000)
(Local Storage JWT)                           ├── Security Headers Middleware
                                              ├── Rate Limiter Middleware
                                              ├── Auth Router (/auth)
                                              └── verify_dataset_ownership (Dependency)
                                                         │
                                               PostgreSQL 16 Container
                                              └── users & datasets tables
```

### Authentication & Authorization Schema (Alembic Migration 010)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE datasets ADD COLUMN user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE;
```

---

## 9. Completed Module Ecosystem (Phases 1–10)

- `auth_service.py`: User registration, login, JWT token verification & account deletion [PHASE 10]
- `dataset_service.py`: Dataset ingestion & multi-tenant storage management [PHASE 2 & 10]
- `profiling_service.py`: Data profiling & quality summaries [PHASE 3]
- `preprocessing_service.py`: Cleaning, missing value & categorical encoding [PHASE 4]
- `visualization_service.py`: Smart chart recommendations & Plotly payload generation [PHASE 5]
- `pattern_service.py`: Statistical correlation, clustering & pattern discovery engines [PHASE 6]
- `anomaly_detection_service.py` & `prediction_service.py`: Anomaly detection & machine learning forecasting models [PHASE 7]
- `insight_service.py`: LLM & deterministic natural language data narratives engine [PHASE 8]
- `analyst_service.py`: Natural language dataset query conversational analyst [PHASE 9]



