# VizMind API Reference — Phase 2 Update

All VizMind APIs are versioned under the prefix `/api/v1`.

---

## 1. System Health Endpoints

### `GET /api/v1/health`
- **Summary**: Retrieve general application health status.
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "service": "VizMind",
    "version": "0.2.0"
  }
  ```

### `GET /api/v1/health/db`
- **Summary**: Performs a `SELECT 1` query execution against PostgreSQL DB.
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```

---

## 2. Dataset Endpoints (`/api/v1/datasets`)

### `POST /api/v1/datasets`
- **Summary**: Upload dataset file (`multipart/form-data`).
- **Form Fields**:
  - `file` *(Required)*: File payload (`.csv`, `.xlsx`, `.xls`). Max size: 50 MB.
  - `name` *(Optional)*: Custom dataset display name.
- **Response**: `201 Created`
  ```json
  {
    "id": "9a7b744d-4467-4e6c-9c76-f87c2b3e5124",
    "name": "Sales 2026",
    "original_filename": "sales_2026.csv",
    "file_type": "csv",
    "file_size": 1048576,
    "storage_path": "datasets/9a7b744d-4467-4e6c-9c76-f87c2b3e5124/dataset_4c91a0b3.csv",
    "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "status": "ready",
    "created_at": "2026-09-22T16:30:00Z",
    "updated_at": "2026-09-22T16:30:00Z"
  }
  ```

---

### `GET /api/v1/datasets`
- **Summary**: Retrieve paginated list of uploaded datasets metadata.
- **Query Parameters**:
  - `page` (default: 1)
  - `page_size` (default: 20, max: 100)
- **Response**: `200 OK`
  ```json
  {
    "items": [ ... ],
    "page": 1,
    "page_size": 20,
    "total": 1
  }
  ```

---

### `GET /api/v1/datasets/{dataset_id}`
- **Summary**: Retrieve dataset metadata by UUID.
- **Response**: `200 OK`
- **Error Response**: `404 Not Found` (`DATASET_NOT_FOUND`)

---

### `DELETE /api/v1/datasets/{dataset_id}`
- **Summary**: Delete dataset metadata record, associated profiling records & remove physical file directory from disk.
- **Response**: `204 No Content`
- **Error Response**: `404 Not Found` (`DATASET_NOT_FOUND`)

---

## 3. Dataset Profiling Endpoints (`/api/v1/datasets/{dataset_id}/profile`)

### `POST /api/v1/datasets/{dataset_id}/profile`
- **Summary**: Trigger or recompute read-only profiling analysis and quality score evaluation.
- **Response**: `200 OK`
  ```json
  {
    "id": "e3b0c442-98fc-4e6c-9c76-f87c2b3e5124",
    "dataset_id": "9a7b744d-4467-4e6c-9c76-f87c2b3e5124",
    "overview": {
      "rows": 1000,
      "columns": 5,
      "sheet_name": null,
      "memory_bytes": 45000,
      "missing_cells": 12,
      "missing_cell_percentage": 0.24,
      "duplicate_rows": 0,
      "duplicate_row_percentage": 0.0
    },
    "quality": {
      "score": 94,
      "level": "Excellent",
      "issues": [
        {
          "code": "HIGH_CARDINALITY_TEXT",
          "severity": "warning",
          "message": "Column 'customer_id' has high unique ratio (100.0%)",
          "column": "customer_id"
        }
      ]
    },
    "columns": [
      {
        "id": "a1b2c3d4-4467-4e6c-9c76-f87c2b3e5124",
        "column_name": "age",
        "column_index": 0,
        "inferred_type": "numeric",
        "total_count": 1000,
        "null_count": 5,
        "null_percentage": 0.5,
        "unique_count": 65,
        "unique_percentage": 6.5,
        "min_value": 18,
        "max_value": 85,
        "mean_value": 42.5,
        "median_value": 41.0,
        "std_dev": 12.3,
        "q25": 31.0,
        "q75": 53.0
      }
    ],
    "created_at": "2026-09-22T17:00:00Z",
    "updated_at": "2026-09-22T17:00:00Z"
  }
  ```

---

### `GET /api/v1/datasets/{dataset_id}/profile`
- **Summary**: Retrieve previously computed saved profile and data quality report for a dataset.
- **Response**: `200 OK` (Same schema as `POST`)
- **Error Response**: `404 Not Found` (`PROFILE_NOT_FOUND`)

---

## 4. Dataset Preprocessing Endpoints (`/api/v1/datasets/{dataset_id}/preprocess`)

### `POST /api/v1/datasets/{dataset_id}/preprocess`
- **Summary**: Trigger automated preprocessing pipeline for source dataset, creating a derived analysis-ready dataset.
- **Response**: `200 OK`
  ```json
  {
    "job": {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d4e5",
      "dataset_id": "9a7b744d-4467-4e6c-9c76-f87c2b3e5124",
      "source_profile_id": "e3b0c442-98fc-4e6c-9c76-f87c2b3e5124",
      "output_dataset_id": "c1a2b3c4-58cc-4372-a567-0e02b2c3d4e5",
      "status": "COMPLETED",
      "started_at": "2026-09-22T17:30:00Z",
      "completed_at": "2026-09-22T17:30:02Z",
      "rows_before": 1000,
      "rows_after": 980,
      "columns_before": 5,
      "columns_after": 7,
      "missing_cells_before": 42,
      "missing_cells_after": 0,
      "duplicate_rows_before": 20,
      "duplicate_rows_after": 0,
      "source_checksum_before": "e3b0c442...",
      "source_checksum_after": "e3b0c442...",
      "processed_checksum": "a1b2c3d4..."
    },
    "processed_dataset": {
      "id": "c1a2b3c4-58cc-4372-a567-0e02b2c3d4e5",
      "parent_dataset_id": "9a7b744d-4467-4e6c-9c76-f87c2b3e5124",
      "dataset_kind": "PROCESSED",
      "name": "Sales 2026 (Processed)",
      "file_type": "csv",
      "file_size": 95000,
      "checksum": "a1b2c3d4...",
      "status": "ready"
    },
    "transformations": [
      {
        "step_order": 1,
        "transformation_type": "REMOVE_DUPLICATES",
        "column_name": null,
        "parameters": { "duplicate_rows_removed": 20 },
        "rows_affected": 20,
        "values_affected": 20,
        "description": "Removed 20 exact duplicate rows."
      }
    ]
  }
  ```

---

### `GET /api/v1/datasets/{dataset_id}/preprocessing`
- **Summary**: Retrieve latest preprocessing report and transformation audit log for a dataset.
- **Response**: `200 OK` (Same schema as `POST`)
- **Error Response**: `404 Not Found` (`PREPROCESSING_NOT_FOUND`)

---

## Standard Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

### System, Profiling & Preprocessing Error Codes:
- `FILE_REQUIRED` (400)
- `EMPTY_FILE` (400)
- `FILE_TOO_LARGE` (400)
- `UNSUPPORTED_FILE_TYPE` (400)
- `INVALID_FILE` (400)
- `INVALID_FILENAME` (400)
- `PROFILE_REQUIRED` (400)
- `DATASET_NOT_FOUND` (404)
- `PROFILE_NOT_FOUND` (404)
- `PREPROCESSING_NOT_FOUND` (404)
- `PROFILING_FAILED` (500)
- `PREPROCESSING_FAILED` (500)
- `STORAGE_ERROR` (500)
- `DATABASE_ERROR` (500)


