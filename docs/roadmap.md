# VizMind Project Roadmap

This document outlines the multi-phase engineering roadmap for building VizMind into an AI-powered data analyst platform.

---

## Phase 1 — Project Foundation & System Infrastructure [COMPLETED]
- React + Vite Frontend application shell
- FastAPI Backend with versioned routing (`/api/v1`)
- PostgreSQL database integration & Alembic migrations
- UUID `Dataset` database model schema
- Middleware (`X-Request-ID`), centralized logging, exception handling
- Docker Compose development infrastructure
- Health verification APIs (`/health` and `/health/db`)

---

## Phase 2 — Dataset Ingestion & Secure File Management [COMPLETED]
- Multi-format file upload APIs (`POST /api/v1/datasets`) supporting `.csv`, `.xlsx`, `.xls`
- File validation layer (`FileValidationService` for size limits 50MB, empty files, extension check, structural check)
- Security path traversal protection (`validate_path_safety`)
- Storage abstraction (`StorageService` for safe chunked streaming to `storage/datasets/<uuid>/` + SHA-256 calculation)
- Alembic migration (`002_add_checksum_to_datasets`)
- Dataset CRUD APIs (`GET /api/v1/datasets`, `GET /api/v1/datasets/{id}`, `DELETE`)
- Frontend Ingestion Workspace (UploadZone drag & drop, DatasetList table, DatasetMetadataModal)

---

## Phase 3 — Data Profiling & Quality Engine [COMPLETED]
- Read-only streaming dataset loader (`DatasetLoader`) for CSV and Excel files.
- Automated column semantic type inference engine (`numeric`, `categorical`, `datetime`, `boolean`, `text`).
- Type-aware statistical metric computation (Min, Max, Mean, Median, StdDev, Q25, Q75, Skewness, Top categories, Text length metrics).
- Transparent 0–100 Data Quality Score formula based on normalized component penalties (Missingness, Duplicates, Invalid Values, Constant Columns, Type Consistency, High Cardinality).
- Data quality issue evaluator with severity classification (`critical`, `warning`, `info`).
- Database ORM entities (`DatasetProfile` & `DatasetColumnProfile`) and Alembic migration (`003_add_profiling_tables`).
- Profile REST APIs (`POST /api/v1/datasets/{id}/profile` and `GET /api/v1/datasets/{id}/profile`).
- Interactive Frontend UI (`DatasetProfileView` dashboard).
- Source data integrity guarantee (SHA-256 remains identical pre- and post-profiling).

---

## Phase 4 — Automated Data Preprocessing Engine [COMPLETED]
- Deterministic preprocessing planner (`PreprocessingPlanner`) evaluating dataset structure and Phase 3 profiles.
- Pure transformation suite (`PreprocessingTransformers`) supporting missing numeric median imputation, categorical/text "Unknown" imputation, duplicate removal, empty/constant column removal, text whitespace normalization, and one-hot encoding for low/medium cardinality ($\le 20$ categories).
- Source immutability guarantee: Original dataset files remain 100% untouched (`source_checksum_before == source_checksum_after`).
- Versioned derived dataset creation (`dataset_kind="PROCESSED"`, `parent_dataset_id=<source_id>`) stored in isolated disk storage (`storage/processed/<id>/`).
- Step-by-step audit logging of transformations (`PreprocessingJob` & `PreprocessingTransformation` database entities).
- Alembic migration `004_add_preprocessing_tables`.
- Preprocessing REST APIs (`POST /api/v1/datasets/{id}/preprocess` and `GET /api/v1/datasets/{id}/preprocessing`).
- Interactive Frontend UI (`PreprocessingView` dashboard).

---

## Phase 5 — Smart Visualization Intelligence Engine [COMPLETED]
- Deterministic column-role classification (`NUMERIC_MEASURE`, `CATEGORICAL_DIMENSION`, `DATETIME_DIMENSION`, `BOOLEAN_DIMENSION`).
- Multi-chart candidate planner supporting Histogram, Bar, Count Bar, Line, Scatter Plot, and Box Plot.
- Global recommendation cap (12 max), per-chart type limits, and candidate deduplication.
- Pre-aggregated server-side chart data payload generation with deterministic scatter plot sampling and time-series aggregation.
- Recommendation persistence (`VisualizationRun` & `VisualizationRecommendation`), Alembic migration `005_add_visualization_tables`, and REST APIs.
- Frontend Recharts & custom BoxPlot dashboard rendering.

---

## Phase 6 — Pattern Discovery Intelligence Engine [COMPLETED]
- Deterministic statistical engine supporting Pearson correlation, Welch's t-test / One-way ANOVA, Chi-square test of independence & Cramér's V, historical linear trend detection, and descriptive distribution summaries.
- Benjamini-Hochberg False Discovery Rate (FDR) multiple-testing correction returning both `raw_p_value` and `adjusted_p_value`.
- Strict separation of statistical significance (`adjusted_p_value < 0.05`) and pattern strength (`WEAK`, `MODERATE`, `STRONG` based on effect magnitude).
- Deterministic candidate planning with cap enforcement and identifier/unsuitable column exclusion.
- Bounded 0–100 relevance scoring, canonical pair deduplication, and 5-tier deterministic ranking up to 30 top patterns.
- Version integrity validator enforcing dataset, profile, processed dataset SHA-256 checksum matching before and after analysis.
- Database persistence (`PatternDiscoveryRun` & `PatternResult` entities) with PostgreSQL `ON DELETE CASCADE` constraints and Alembic migration `006_add_pattern_discovery_tables`.
- Pattern Discovery REST APIs (`POST /api/v1/datasets/{id}/patterns`, `GET /api/v1/datasets/{id}/patterns`, `GET /api/v1/datasets/{id}/patterns/{pattern_id}`).
- Interactive Frontend UI (`PatternDiscoveryView`, `PatternSummary`, `PatternCard`, `PatternStatistics` modal) with mathematical disclaimers.

---

## Phase 7 — Anomaly Detection & Predictive Analytics [NEXT]
- Machine learning anomaly detection (Isolation Forest)
- Automated predictive baseline models (Regression & Classification via XGBoost / LightGBM)


---

## Phase 8 — AI Insight Engine (LLM Integration)
- LLM Provider Integration (Gemini / OpenAI API)
- Prompt template engineering for statistical context summary
- Natural language "Data Story" generator

---

## Phase 9 — Natural Language Analyst (Conversational Query Engine)
- Text-to-SQL / Text-to-Pandas query translator
- Conversational data exploration workspace

---

## Phase 10 — Final Production Dashboard & Integration
- Interactive multi-widget dashboard builder
- Export workspace reports to PDF / HTML / Markdown
- Production deployment optimization
