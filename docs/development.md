# Local Development Guide — Phase 2 Update

## Storage Configuration

Phase 2 adds file storage configurations to `backend/.env`:

```env
STORAGE_PATH=./storage/datasets
TEST_STORAGE_PATH=./storage/test_datasets
MAX_UPLOAD_SIZE_MB=50
```

---

## Database Migrations

Apply database migrations using Alembic:

```bash
cd backend
alembic upgrade head
```

To inspect current migration status:
```bash
alembic current
```

---

## Testing File Uploads Locally

### Option 1: Via Frontend Workspace UI
1. Start PostgreSQL (`docker compose up -d db`).
2. Run database migrations (`alembic upgrade head`).
3. Start FastAPI Backend (`uvicorn app.main:app --reload --port 8000`).
4. Start React Frontend (`npm run dev` inside `frontend/`).
5. Navigate to `http://localhost:5173/dashboard`.
6. Upload a dataset file (CSV/Excel).
7. In the registered datasets table, click **Profile** to view quality and column statistics.
8. In the Dataset Profile header, click **Preprocess Dataset** to run the Phase 4 automated preparation pipeline and view the transformation audit log and derived dataset details.

### Option 2: Via cURL / HTTP Client
```bash
# Trigger dataset profiling & evaluation
curl -X POST "http://localhost:8000/api/v1/datasets/<dataset_uuid>/profile"

# Trigger automated preprocessing pipeline
curl -X POST "http://localhost:8000/api/v1/datasets/<dataset_uuid>/preprocess"

# Retrieve latest preprocessing report
curl -X GET "http://localhost:8000/api/v1/datasets/<dataset_uuid>/preprocessing"
```

### Option 3: Via Automated Test Suite
```bash
cd backend
pytest tests/ -v
```
The automated test suite runs in-memory and isolated test storage checks covering:
- Dataset file loading (`test_dataset_loader.py`)
- Quality score calculation formula (`test_data_quality_service.py`)
- Profiling computation and persistence (`test_profiling_service.py`)
- Preprocessing planner rules (`test_preprocessing_planner.py`)
- Preprocessing transformers (`test_preprocessing_transformers.py`)
- Preprocessing execution and derived dataset persistence (`test_preprocessing_service.py`)
- Preprocessing API endpoints (`test_preprocessing_api.py`)
- Source dataset file integrity checks (`test_source_integrity.py`)
- Cascade deletion behavior (`test_dataset_delete_cascade.py`)


