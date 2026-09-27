# VIZMIND — PHASE 7 IMPLEMENTATION PROMPT

## Phase 7: Anomaly Detection + Prediction Intelligence Engine

You are continuing development of **VizMind — An AI-Powered Data Analyst for Automated Visualization, Pattern Discovery, and Explainable Insights**.

Phase 1–6 are already implemented.

Your task is to implement **ONLY Phase 7**:

> **Anomaly Detection Intelligence + Prediction/Forecasting Intelligence**

Do not redesign previous phases.

Do not skip architecture inspection.

Do not implement Phase 8 or Phase 9.

---

# 1. FIRST: INSPECT THE EXISTING PROJECT

Before changing anything, inspect the current repository and understand the actual implementation.

Review:

```text
backend/app/
backend/tests/
backend/alembic/
frontend/src/
README.md
docs/
```

Especially inspect the existing Phase 1–6 implementation:

### Phase 2

* Dataset model
* Dataset storage
* Dataset checksum
* Dataset APIs

### Phase 3

* DatasetProfile
* DatasetColumnProfile
* semantic types
* data loader
* profile validation

### Phase 4

* processed dataset
* preprocessing jobs
* source/processed relationships
* processed dataset checksum

### Phase 5

* visualization services
* identifier detection
* temporal handling
* visualization data utilities

### Phase 6

* PatternDiscoveryRun
* PatternResult
* pattern statistics
* pattern planner
* pattern validator
* pattern scoring
* processed dataset version validation
* repository patterns
* API patterns
* frontend PatternDiscoveryView

Reuse existing infrastructure whenever possible.

Do NOT duplicate functionality already present.

---

# 2. PHASE 7 OBJECTIVE

Build:

```text
                 PHASE 7
                     │
        ┌────────────┴────────────┐
        ↓                         ↓
Anomaly Detection           Prediction Engine
        ↓                         ↓
Outlier Identification     Historical Modeling
        ↓                         ↓
Evidence & Severity        Validation & Metrics
        ↓                         ↓
Anomaly Results            Predictions / Forecast
        └────────────┬────────────┘
                     ↓
             Unified API Layer
                     ↓
             Phase 7 Dashboard
```

The engine must answer two different questions:

### Anomaly Detection

> "Which observations or groups of observations look unusually different from the expected data distribution?"

### Prediction

> "Given historical data, what values can a validated statistical/ML model estimate for future or held-out observations?"

These must remain separate analytical workflows.

---

# 3. STRICT PHASE 7 BOUNDARY

## IMPLEMENT

### Anomaly Detection

* univariate numerical anomaly detection
* IQR-based detection
* robust z-score detection
* configurable anomaly thresholds
* anomaly severity
* anomaly counts
* anomaly percentages
* anomaly evidence
* deterministic anomaly results
* optional time-aware anomaly detection for suitable time-series data

### Prediction

* supervised numerical prediction
* supervised categorical prediction where appropriate
* time-series forecasting for suitable temporal datasets
* train/validation/test separation
* baseline models
* model evaluation
* prediction metrics
* feature selection based only on information available at prediction time
* future/held-out predictions
* prediction intervals where statistically appropriate
* model metadata
* deterministic model execution
* model/version integrity

### Infrastructure

* persistence
* APIs
* frontend dashboard
* validation
* logging
* tests
* documentation

---

# 4. STRICTLY DO NOT IMPLEMENT

Do NOT implement Phase 8:

```text
LLM
Gemini
OpenAI
Claude
AI-generated explanations
AI insight generation
generative summaries
```

Do NOT implement Phase 9:

```text
natural-language analyst
natural-language querying
chat-based data analysis
```

Do NOT implement:

```text
clustering
PCA
dimensionality reduction
reinforcement learning
deep learning
neural networks
automated feature engineering
AutoML
hyperparameter search
ensemble model optimization
real-time streaming prediction
online learning
```

Do not turn Phase 7 into a generic ML platform.

Keep the implementation bounded and explainable.

---

# 5. IMPORTANT ARCHITECTURE PRINCIPLE

The statistical/modeling layer performs all calculations.

The future LLM layer will only explain results.

Therefore:

```text
Python
Pandas
NumPy
SciPy
Scikit-learn
```

perform the actual analytical work.

No LLM should make:

* anomaly decisions
* model predictions
* statistical calculations
* metric calculations
* threshold decisions

---

# 6. TECHNOLOGY

Use:

* Python
* Pandas
* NumPy
* SciPy
* Scikit-learn
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic
* pytest

Use existing project versions where possible.

Do not introduce unnecessary dependencies.

---

# 7. DATA VERSION INTEGRITY

Phase 7 MUST operate on the exact Phase 4 processed dataset.

The flow is:

```text
Source Dataset
      ↓
Phase 3 Profile
      ↓
Phase 4 Processed Dataset
      ↓
Phase 7
```

Before analysis:

1. Verify dataset exists.
2. Verify profile exists.
3. Verify preprocessing exists.
4. Resolve the processed dataset.
5. Verify processed dataset exists.
6. Calculate SHA-256 checksum.
7. Compare with the stored checksum.
8. Load the processed dataset.

If checksum differs:

```text
PREDICTION_DATASET_VERSION_MISMATCH
```

or:

```text
ANOMALY_DATASET_VERSION_MISMATCH
```

Use a shared version validation utility where possible.

Do not analyze a different dataset version silently.

After analysis, verify the checksum again.

The source and processed datasets must never be modified by Phase 7.

---

# 8. PHASE 7 DATABASE DESIGN

Create separate run models.

Recommended:

```text
AnomalyDetectionRun
AnomalyResult

PredictionRun
PredictionResult
```

Do not store everything in one generic JSON blob.

Use structured relational metadata plus JSONB for model-specific statistics/configuration.

---

# 9. ANOMALY DETECTION RUN

Create:

```text
anomaly_detection_runs
```

Fields:

```text
id
dataset_id
processed_dataset_id
profile_id
processed_checksum
method
status
started_at
completed_at
anomaly_count
total_observations
anomaly_percentage
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

Methods may include:

```text
IQR
ROBUST_ZSCORE
TIME_SERIES_RESIDUAL
```

Only implement methods that are actually supported.

---

# 10. ANOMALY RESULT

Create:

```text
anomaly_results
```

Fields:

```text
id
run_id
dataset_id
processed_dataset_id
row_reference
column_name
value
expected_range
anomaly_score
severity
method
evidence
statistics
created_at
updated_at
```

IMPORTANT:

Do not expose entire raw rows.

`row_reference` must be a safe deterministic reference such as the processed DataFrame row index or generated observation identifier.

Do not persist unnecessary sensitive raw data.

---

# 11. ANOMALY METHODS

Implement at least:

## Method 1 — IQR

For numerical columns:

```text
Q1
Q3
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
```

Values outside the bounds are candidate anomalies.

Do not run IQR on:

* identifiers
* constant columns
* all-null columns
* unsuitable semantic types

---

# 12. ROBUST Z-SCORE

Implement robust z-score using median and MAD.

```text
MAD = median(|x - median(x)|)

robust_z =
0.6745 * (x - median) / MAD
```

Use configurable threshold:

```text
ROBUST_Z_THRESHOLD = 3.5
```

If MAD is zero:

* do not divide by zero
* skip the method for that column
* record the reason

Do not silently generate invalid values.

---

# 13. ANOMALY SEVERITY

Do not classify anomaly severity using arbitrary intuition.

Use deterministic thresholds.

Example:

```text
NORMAL
LOW
MEDIUM
HIGH
```

Severity should be based on distance from the expected distribution.

For example, for robust z-score:

```text
|z| < 3.5       NORMAL
3.5–5           LOW
5–7              MEDIUM
>7               HIGH
```

For IQR, use normalized distance beyond the applicable bound.

Document the exact formula.

Keep thresholds configurable.

---

# 14. ANOMALY SCORE

Generate a deterministic normalized anomaly score:

```text
0–100
```

The score should represent unusualness.

It must NOT represent:

* business risk
* fraud probability
* causality
* importance

unless explicitly calculated from supported data.

A high anomaly score means:

> "This observation is statistically unusual under the selected detection method."

Nothing more.

---

# 15. MULTIPLE ANOMALY METHODS

If an observation is detected by more than one method:

Example:

```text
IQR
+
Robust Z-score
```

combine the evidence deterministically.

Store:

```text
methods_detected
```

and avoid creating duplicate anomaly cards for the same observation/column.

---

# 16. ANOMALY OUTPUT LIMITS

Do not return millions of anomaly records.

Use configuration:

```text
MAX_ANOMALY_COLUMNS = 30
MAX_ANOMALY_RESULTS = 500
MAX_ANOMALY_RESULTS_PER_COLUMN = 100
```

If more anomalies exist:

* calculate full counts
* persist only bounded detailed results
* indicate truncation in the run summary

Example:

```text
total_anomalies = 1842
returned_anomalies = 500
results_truncated = true
```

---

# 17. TIME-SERIES ANOMALIES

Only implement time-aware anomaly detection for datasets that contain:

* a valid datetime column
* an appropriate numerical measure
* sufficient chronological observations

Do not treat every numeric column as a time series.

For Phase 7, keep the time-series anomaly approach simple and explainable.

A suitable approach:

```text
time ordering
↓
historical rolling baseline
↓
residual
↓
robust threshold
↓
anomaly
```

Avoid complex forecasting-based anomaly detection.

Do not duplicate the forecasting engine.

---

# 18. ANOMALY SERVICE ARCHITECTURE

Create:

```text
backend/app/services/anomaly_detection_service.py
backend/app/services/anomaly_detection_planner.py
backend/app/services/anomaly_statistics.py
backend/app/services/anomaly_scoring.py
backend/app/services/anomaly_validator.py
backend/app/db/repositories/anomaly_detection_repository.py
```

Keep pure statistical functions separate from orchestration.

---

# 19. PREDICTION ENGINE

Create:

```text
backend/app/services/prediction_service.py
backend/app/services/prediction_planner.py
backend/app/services/prediction_models.py
backend/app/services/prediction_validation.py
backend/app/services/prediction_scoring.py
backend/app/db/repositories/prediction_repository.py
```

The prediction engine must select from a small controlled set of models.

Do NOT build AutoML.

---

# 20. PREDICTION PROBLEM TYPES

Support:

```text
REGRESSION
CLASSIFICATION
FORECASTING
```

But only run a problem type when the dataset satisfies eligibility rules.

---

# 21. REGRESSION

Use a simple baseline model first.

Recommended:

```text
LinearRegression
```

Optional:

```text
RandomForestRegressor
```

Do not automatically use both unless there is a deterministic model comparison rule.

The target must be numeric.

---

# 22. CLASSIFICATION

Use:

```text
LogisticRegression
```

as the primary baseline.

Optional:

```text
RandomForestClassifier
```

Target must be categorical/binary/multiclass and have sufficient samples per class.

Do not attempt classification on:

* IDs
* nearly unique values
* free text
* extremely sparse targets

---

# 23. FORECASTING

Forecasting must be treated separately from ordinary regression.

A dataset qualifies only if it has:

```text
datetime column
+
numeric target
+
sufficient chronological observations
```

Start with a simple baseline:

```text
historical naive forecast
```

and optionally a simple statistical model if justified.

Do NOT use deep learning.

Do NOT use LSTM.

Do NOT use Transformer forecasting.

Do NOT use neural networks.

---

# 24. TIME ORDER MUST BE PRESERVED

For forecasting:

NEVER randomly shuffle the data.

Use:

```text
past → training
later → validation
latest → test
```

The future must never leak into the training set.

This is mandatory.

---

# 25. REGRESSION / CLASSIFICATION SPLIT

For non-temporal supervised learning:

Use deterministic train/test splitting.

Recommended:

```text
TEST_SIZE = 0.20
RANDOM_STATE = 42
```

For classification use stratification when possible.

For temporal datasets where time ordering is meaningful, prefer time-aware splitting.

Do not randomly split temporal data when it would cause leakage.

---

# 26. FEATURE ELIGIBILITY

Features may include:

* numeric columns
* low-cardinality categorical columns
* boolean columns
* appropriately transformed datetime components if already supported

Exclude:

```text
IDs
row identifiers
target column
free text
constant columns
columns with extreme missingness
post-outcome columns
```

Do not use the target itself as a feature.

---

# 27. DATA LEAKAGE PROTECTION

This is mandatory.

The engine must ensure:

```text
target
future values
post-outcome fields
future timestamps
derived target information
```

are not accidentally used as predictors.

All preprocessing required for modeling must be fit ONLY on the training data.

Do not fit scalers/encoders on the complete dataset before train/test splitting.

Use scikit-learn Pipelines / ColumnTransformer where appropriate.

---

# 28. MODEL PREPROCESSING

For numerical features:

* imputation if needed
* scaling where required by the model

For categorical features:

* imputation
* OneHotEncoder with safe unknown handling

Use:

```text
ColumnTransformer
Pipeline
```

where appropriate.

Do not modify the stored Phase 4 processed dataset.

Model preprocessing exists only in the prediction pipeline.

---

# 29. REGRESSION METRICS

Calculate:

```text
MAE
RMSE
R²
```

Where meaningful, also report:

```text
MAPE
```

but avoid MAPE when actual values contain or approach zero.

Do not use MAPE blindly.

Store all metrics in structured JSONB.

---

# 30. CLASSIFICATION METRICS

Calculate:

```text
accuracy
precision
recall
F1
```

For imbalanced datasets, also calculate:

```text
balanced_accuracy
```

when appropriate.

For binary classification, optionally calculate:

```text
ROC-AUC
```

only when both classes are present in the evaluation set.

Do not report metrics that cannot be validly calculated.

---

# 31. FORECASTING METRICS

Use:

```text
MAE
RMSE
```

Optionally:

```text
MAPE
```

only when valid.

Compare against the naive baseline.

Do not claim the model is useful simply because it has a non-zero prediction.

---

# 32. BASELINE COMPARISON

Every prediction workflow must have a baseline.

For regression:

```text
mean predictor
```

For classification:

```text
majority-class baseline
```

For forecasting:

```text
naive previous-value baseline
```

Compare model performance against the baseline.

Persist:

```text
baseline_metrics
model_metrics
improvement
```

Do not describe a model as "better" unless the selected metric objectively supports that comparison.

---

# 33. MODEL SELECTION

Do NOT use arbitrary model selection.

If multiple models are implemented, use a deterministic comparison metric.

Example:

Regression:

```text
lowest validation MAE
```

Classification:

```text
highest validation F1
```

Forecasting:

```text
lowest validation MAE
```

Tie-break:

```text
simpler model first
```

Then:

```text
model_name ascending
```

Do not optimize on the test set.

---

# 34. PREDICTION RUN MODEL

Create:

```text
prediction_runs
```

Fields:

```text
id
dataset_id
processed_dataset_id
profile_id
processed_checksum
problem_type
target_column
model_name
status
started_at
completed_at
training_rows
validation_rows
test_rows
metrics
baseline_metrics
feature_columns
model_parameters
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

---

# 35. PREDICTION RESULT MODEL

Create:

```text
prediction_results
```

Fields:

```text
id
run_id
observation_reference
actual_value
predicted_value
prediction_error
lower_bound
upper_bound
split
created_at
updated_at
```

Only store bounded prediction results.

Do not persist entire raw rows.

---

# 36. FORECAST RESULT HANDLING

For forecasting, prediction results should clearly distinguish:

```text
HISTORICAL_TEST
FUTURE_FORECAST
```

If future forecasting is implemented, clearly mark future values as predictions rather than actual observations.

Do not invent actual future outcomes.

---

# 37. PREDICTION CONFIDENCE / INTERVALS

Do not create fake confidence scores.

If prediction intervals are not statistically supported by the selected model:

Do not display:

```text
confidence = 95%
```

simply because it sounds useful.

Only provide intervals when the implementation has a valid method.

Otherwise:

```text
prediction_interval_available = false
```

---

# 38. MODEL REPRODUCIBILITY

Use deterministic random seeds where applicable:

```text
RANDOM_STATE = 42
```

Store:

```text
model_name
model_parameters
feature_columns
random_state
training_rows
test_rows
processed_checksum
```

For unchanged input data, model evaluation should be reproducible.

---

# 39. MODEL SAFETY / VALIDATION

Create:

```text
prediction_validation.py
```

Validate:

* target exists
* target is not an identifier
* sufficient samples
* sufficient class counts
* valid numeric values
* no NaN/inf in final model inputs
* feature/target separation
* train/test separation
* temporal ordering where applicable
* metric validity
* processed checksum
* model output dimensions

Do not run a model when minimum data requirements are not satisfied.

Return a clear structured reason.

---

# 40. MINIMUM DATA REQUIREMENTS

Centralize configuration.

Suggested:

```text
MIN_PREDICTION_ROWS = 50
MIN_CLASS_COUNT = 10
MIN_FORECAST_POINTS = 30
TEST_SIZE = 0.20
VALIDATION_SIZE = 0.20
RANDOM_STATE = 42
MAX_FEATURES = 30
MAX_CATEGORICAL_CARDINALITY = 20
```

These are initial defaults and must be configurable.

Do not run expensive modeling on arbitrarily large feature spaces.

---

# 41. PREDICTION SCORING / MODEL QUALITY

Do not create a fake "AI score."

Instead provide transparent quality indicators based on:

* performance versus baseline
* evaluation metric
* test sample size
* validation stability
* model type

If a normalized model quality score is implemented, document its formula and keep it separate from raw metrics.

---

# 42. API DESIGN

Create:

```text
backend/app/api/routes/anomalies.py
backend/app/api/routes/predictions.py
```

## Anomaly API

### Run anomaly detection

```http
POST /api/v1/datasets/{dataset_id}/anomalies
```

### Get latest anomaly run

```http
GET /api/v1/datasets/{dataset_id}/anomalies
```

### Get anomaly details

```http
GET /api/v1/datasets/{dataset_id}/anomalies/{anomaly_id}
```

Optional filters:

```text
column
severity
method
```

---

# 43. PREDICTION API

### Run prediction analysis

```http
POST /api/v1/datasets/{dataset_id}/predictions
```

Request may optionally specify:

```text
target_column
problem_type
```

If omitted, the planner may determine eligible targets using deterministic rules.

Do not use an LLM to determine the target.

### Get latest prediction run

```http
GET /api/v1/datasets/{dataset_id}/predictions
```

### Get prediction run

```http
GET /api/v1/datasets/{dataset_id}/predictions/{run_id}
```

### Get prediction results

```http
GET /api/v1/datasets/{dataset_id}/predictions/{run_id}/results
```

Support pagination.

---

# 44. API ERROR CODES

Use structured errors such as:

```text
PREPROCESSING_REQUIRED
ANOMALY_DATASET_VERSION_MISMATCH
PREDICTION_DATASET_VERSION_MISMATCH
TARGET_COLUMN_REQUIRED
TARGET_COLUMN_INVALID
INSUFFICIENT_DATA
INSUFFICIENT_CLASS_SAMPLES
UNSUPPORTED_PROBLEM_TYPE
MODEL_TRAINING_FAILED
INVALID_MODEL_INPUT
PREDICTION_RUN_NOT_FOUND
ANOMALY_RUN_NOT_FOUND
```

Do not expose Python stack traces.

---

# 45. FRONTEND — PHASE 7

Create:

```text
frontend/src/components/AnomalyDetectionView.jsx
frontend/src/components/AnomalySummary.jsx
frontend/src/components/AnomalyCard.jsx

frontend/src/components/PredictionView.jsx
frontend/src/components/PredictionSummary.jsx
frontend/src/components/PredictionMetrics.jsx
frontend/src/components/PredictionResults.jsx
```

Reuse existing dashboard styles.

Do not redesign the entire application.

---

# 46. ANOMALY DASHBOARD

Display:

```text
Total observations
Anomalies detected
Anomaly percentage
High severity
Medium severity
Low severity
Detection method
```

Provide:

```text
Column filter
Severity filter
Method filter
```

Each anomaly card should show:

```text
Column
Observation reference
Observed value
Expected range
Anomaly score
Severity
Detection method
Evidence
```

Do not display unnecessary raw row information.

---

# 47. ANOMALY VISUALIZATION

Where useful, provide simple visual context.

Examples:

* box plot
* distribution marker
* time-series anomaly markers

Reuse Phase 5 visualization infrastructure where appropriate.

Do not duplicate the chart-generation engine.

Do not create a new visualization architecture.

---

# 48. PREDICTION DASHBOARD

Display:

```text
Problem type
Target
Model
Training rows
Validation rows
Test rows
```

Then show metrics.

### Regression

```text
MAE
RMSE
R²
Baseline comparison
```

### Classification

```text
Accuracy
Precision
Recall
F1
Balanced Accuracy
Baseline comparison
```

### Forecasting

```text
MAE
RMSE
Baseline comparison
```

---

# 49. PREDICTION CHARTS

Use existing visualization components where possible.

Regression:

```text
Actual vs Predicted
```

Classification:

```text
Prediction distribution / confusion matrix
```

Forecasting:

```text
Historical values + test predictions + future forecast if available
```

Do not imply forecast certainty.

---

# 50. FRONTEND STATES

Handle:

```text
Not Analyzed
Analyzing
Completed
Failed
Insufficient Data
No Eligible Columns
No Anomalies Found
No Valid Prediction Target
```

Never display stack traces.

---

# 51. TESTING — ANOMALY DETECTION

Create:

```text
tests/test_anomaly_statistics.py
tests/test_anomaly_planner.py
tests/test_anomaly_scoring.py
tests/test_anomaly_validator.py
tests/test_anomaly_persistence.py
tests/test_anomaly_api.py
```

Test:

### IQR

* obvious anomaly
* no anomaly
* constant column
* all-null column
* NaN
* infinite values

### Robust Z-score

* obvious anomaly
* MAD zero
* insufficient observations
* deterministic result

### Severity

* threshold boundaries
* deterministic classification

### Deduplication

* same observation detected by multiple methods

### Limits

* maximum results
* maximum per-column results
* truncation metadata

---

# 52. TESTING — PREDICTION

Create:

```text
tests/test_prediction_planner.py
tests/test_prediction_models.py
tests/test_prediction_validation.py
tests/test_prediction_service.py
tests/test_prediction_persistence.py
tests/test_prediction_api.py
```

Test:

### Regression

* valid target
* invalid target
* numeric prediction
* metrics
* baseline
* deterministic split

### Classification

* binary classification
* multiclass classification
* insufficient class samples
* metric validity

### Forecasting

* chronological ordering
* no shuffle
* baseline
* future/held-out separation

### Leakage

Explicitly test that:

* target is not included as a feature
* future values are not used in training
* preprocessing is fitted only on training data
* test data does not influence model selection

---

# 53. MODEL DETERMINISM TEST

Run the same prediction twice on the same unchanged dataset.

Verify:

```text
same feature set
same model
same parameters
same metrics
same predictions
```

Allow only database IDs and timestamps to differ.

---

# 54. VERSION INTEGRITY TESTS

Explicitly verify:

```text
source checksum unchanged
processed checksum unchanged
```

before and after:

* anomaly detection
* regression
* classification
* forecasting

Simulate a checksum mismatch and ensure the operation fails safely.

---

# 55. DATABASE TESTS

Test:

* run creation
* run status
* result persistence
* foreign keys
* ON DELETE CASCADE
* multiple runs
* latest completed run
* failed runs
* no orphan records
* dataset deletion cleanup

If PostgreSQL is unavailable:

```text
SKIPPED
```

must remain clearly distinguished from:

```text
PASSED
```

Do not report skipped integration tests as passing.

---

# 56. END-TO-END TEST

Mandatory workflow:

```text
Upload Dataset
      ↓
Profile
      ↓
Preprocess
      ↓
Visualize
      ↓
Discover Patterns
      ↓
Run Anomaly Detection
      ↓
Run Prediction
      ↓
View Results
      ↓
Verify Source Checksum
      ↓
Verify Processed Checksum
      ↓
Verify Phase 3 Profile
      ↓
Verify Phase 5 Visualization
      ↓
Verify Phase 6 Patterns
```

Then test dataset deletion and verify dependent Phase 7 records are removed appropriately.

---

# 57. REGRESSION TESTING

Phase 7 must NOT break:

```text
GET /api/v1/health
GET /api/v1/health/db

Dataset upload
Dataset listing
Dataset retrieval
Dataset deletion

Profile creation
Profile retrieval

Preprocessing

Visualization generation
Visualization retrieval

Pattern discovery
Pattern retrieval
```

Run the complete existing test suite.

---

# 58. LOGGING

Add structured events.

Anomaly:

```text
anomaly_detection_started
anomaly_candidates_generated
anomaly_detection_completed
anomaly_detection_failed
```

Prediction:

```text
prediction_started
prediction_data_validated
prediction_model_trained
prediction_model_evaluated
prediction_completed
prediction_failed
```

Include:

```text
request_id
dataset_id
processed_dataset_id
run_id
target_column where applicable
problem_type where applicable
duration
```

Never log:

* raw rows
* sensitive values
* filesystem paths
* model input datasets

---

# 59. DOCUMENTATION

Update:

```text
README.md
docs/architecture.md
docs/api.md
docs/development.md
docs/roadmap.md
```

Document:

### Anomaly detection

* IQR
* robust z-score
* thresholds
* severity
* limitations
* anomaly ≠ error
* anomaly ≠ fraud
* anomaly ≠ causation

### Prediction

* supported problem types
* supported models
* train/test strategy
* temporal splitting
* leakage prevention
* metrics
* baselines
* model selection
* reproducibility
* limitations

Clearly state:

> Prediction results are estimates produced from historical data and should not be interpreted as guaranteed outcomes.

---

# 60. IMPORTANT STATISTICAL DISCLAIMERS

The UI and documentation must distinguish:

```text
Anomaly
≠
Error

Anomaly
≠
Fraud

Correlation
≠
Causation

Prediction
≠
Certainty

Historical trend
≠
Guaranteed future outcome
```

Do not use exaggerated claims such as:

```text
"AI knows what will happen"
"Guaranteed prediction"
"Detected fraud"
"Certain anomaly"
```

---

# 61. PERFORMANCE SAFETY

Phase 7 must be bounded.

Do not automatically train models on:

* hundreds of thousands of features
* thousands of categorical columns
* unrestricted target candidates
* extremely high-cardinality categorical features

Use:

```text
MAX_FEATURES = 30
MAX_CATEGORICAL_CARDINALITY = 20
MAX_ANOMALY_COLUMNS = 30
MAX_ANOMALY_RESULTS = 500
```

All limits must be configurable.

---

# 62. SECURITY AND PRIVACY

Never expose:

* absolute filesystem paths
* raw dataset dumps
* unnecessary raw rows
* sensitive feature values
* model training data through API responses

Prediction APIs should return only:

* model metadata
* metrics
* bounded prediction results
* safe observation references

---

# 63. ALEMBIC MIGRATION

Create the next migration after migration `006`.

Expected:

```text
007_add_phase7_anomaly_prediction_tables.py
```

Before creating it:

```bash
alembic current
alembic heads
```

Ensure the migration chain remains linear unless the existing project intentionally uses branches.

Run:

```bash
alembic upgrade head
alembic current
```

---

# 64. IMPLEMENTATION ORDER

Implement in this order:

## Step 1

Inspect existing Phase 1–6 implementation.

## Step 2

Add Phase 7 configuration and dependencies.

## Step 3

Implement anomaly statistical functions.

## Step 4

Implement anomaly planner.

## Step 5

Implement anomaly validator/scoring.

## Step 6

Implement anomaly database models/repository.

## Step 7

Implement anomaly service.

## Step 8

Implement anomaly API.

## Step 9

Implement anomaly frontend.

## Step 10

Implement prediction planner.

## Step 11

Implement prediction preprocessing pipeline.

## Step 12

Implement regression baseline/model.

## Step 13

Implement classification baseline/model.

## Step 14

Implement forecasting baseline.

## Step 15

Implement prediction validation and metrics.

## Step 16

Implement prediction persistence.

## Step 17

Implement prediction API.

## Step 18

Implement prediction frontend.

## Step 19

Run unit tests.

## Step 20

Run integration tests.

## Step 21

Run frontend build.

## Step 22

Run full regression suite.

## Step 23

Run end-to-end workflow.

## Step 24

Update documentation.

## Step 25

Inspect all changed files and fix regressions.

---

# 65. FINAL VERIFICATION COMMANDS

Run:

```bash
cd backend
python -m pytest tests/ -v
```

Then:

```bash
cd frontend
npm run build
```

Then:

```bash
cd backend
alembic upgrade head
alembic current
```

If Docker PostgreSQL is required, use the existing VizMind PostgreSQL environment.

Do NOT switch to the unrelated WSL/Kafka/PostgreSQL environment from other projects.

---

# 66. FINAL ACCEPTANCE CRITERIA

Phase 7 is complete only when:

## Anomaly Detection

* IQR implemented
* robust z-score implemented
* configurable thresholds
* deterministic severity
* anomaly scoring
* duplicate detection handling
* result limits
* time-aware anomalies if implemented
* persistence
* API
* frontend
* tests

## Prediction

* regression supported
* classification supported
* forecasting baseline supported
* proper train/test separation
* temporal split where required
* baseline comparison
* metrics
* leakage protection
* deterministic model execution
* persistence
* API
* frontend
* tests

## Integrity

* source unchanged
* processed dataset unchanged
* checksums verified
* no raw dataset modification
* no orphan records

## Regression

All Phase 1–6 functionality remains operational.

## Testing

Clearly report:

```text
PASSED
FAILED
SKIPPED
```

Do NOT count skipped PostgreSQL integration tests as passed.

---

# 67. PHASE 7 BOUNDARY CHECK

Before declaring completion, verify that the following have NOT been implemented:

```text
LLM
Gemini
OpenAI
Claude
AI-generated insights
Natural-language analyst
Chat interface
Clustering
PCA
Deep learning
Neural networks
AutoML
Hyperparameter optimization
Real-time streaming ML
```

These belong to later phases or are intentionally outside the project scope.

---

# 68. STRICT STOP CONDITION

After completing Phase 7:

STOP.

Do not implement Phase 8.

Do not implement:

```text
AI Insight Engine
LLM explanations
Natural-language analyst
Chat interface
```

Wait for the next explicit instruction.

---

# FINAL RESPONSE REQUIRED FROM ANTIGRAVITY

After implementation, provide a concise completion report containing:

1. Files created
2. Files modified
3. Database migrations
4. Anomaly detection methods implemented
5. Prediction models implemented
6. Metrics implemented
7. Leakage protections
8. API endpoints
9. Frontend components
10. Tests passed
11. Tests skipped
12. Tests failed, if any
13. Frontend build result
14. Alembic migration result
15. End-to-end verification result
16. Any known limitations

Do not claim a test passed if it was skipped.

Do not claim Phase 7 is complete if any critical acceptance criterion failed.

Then STOP.
