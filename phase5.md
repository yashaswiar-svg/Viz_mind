# VIZMIND — PHASE 5 IMPLEMENTATION PROMPT

## Smart Visualization Intelligence Engine

You are implementing **Phase 5 of VizMind: Intelligent Data Visualization and Pattern Discovery**.

Before making any changes, inspect the COMPLETE existing Phase 1–4 implementation and preserve all existing functionality.

Phase 4 has been implemented and verified with:

* immutable source datasets
* processed/derived datasets
* dataset profiling
* data-quality analysis
* deterministic preprocessing
* preprocessing audit trail
* source and processed checksums
* preprocessing APIs
* preprocessing frontend
* PostgreSQL persistence
* pytest regression tests
* frontend production build

Do NOT assume files, class names, routes, or schemas that do not exist. Inspect the current codebase first and integrate with the actual implementation.

---

# 1. PHASE 5 OBJECTIVE

Implement:

> **Smart Visualization Intelligence Engine**

The purpose of Phase 5 is to make VizMind automatically determine:

> **"What visualizations are appropriate and useful for this dataset?"**

The user should NOT have to manually decide:

* which columns to select
* which chart type to use
* which variables belong on X/Y axes
* which categorical variables should be compared
* which numerical variables should be distributed
* which time columns should become time-series charts.

VizMind should inspect the dataset structure, Phase 3 profile, and Phase 4 processed dataset and generate **deterministic visualization recommendations**.

The engine must recommend appropriate visualizations based on:

* semantic data types
* column cardinality
* numeric vs categorical relationships
* datetime availability
* missingness
* uniqueness
* identifier-like columns
* dataset size
* valid combinations of columns.

The system must generate actual chart specifications that the frontend can render.

---

# 2. CORE PIPELINE

Implement this pipeline:

```text
Source Dataset
      ↓
Phase 3 Data Profile
      ↓
Phase 4 Processed Dataset
      ↓
Visualization Intelligence Engine
      ↓
Column Eligibility Analysis
      ↓
Visualization Candidate Generation
      ↓
Candidate Validation
      ↓
Deterministic Scoring
      ↓
Ranked Visualization Recommendations
      ↓
Chart Specifications
      ↓
Visualization API
      ↓
Frontend Visualization Dashboard
```

The output of Phase 5 should be a structured set of visualization recommendations.

Example:

```text
Dataset: Sales Data

Recommended Visualizations:

1. Monthly Sales Trend
   Chart: Line
   X: Order Date
   Y: Sales
   Reason: Date + numeric measure detected

2. Sales by Region
   Chart: Bar
   X: Region
   Y: Sales
   Aggregation: Sum
   Reason: Low-cardinality categorical + numeric measure

3. Sales Distribution
   Chart: Histogram
   X: Sales
   Reason: Numeric distribution

4. Profit vs Sales
   Chart: Scatter
   X: Sales
   Y: Profit
   Reason: Two numeric measures
```

Do NOT use an LLM to make these decisions.

The visualization intelligence must be deterministic and explainable.

---

# 3. STRICT PHASE 5 BOUNDARY

## IMPLEMENT ONLY

Phase 5 may implement:

* visualization metadata extraction
* column eligibility detection
* semantic type analysis
* visualization candidate generation
* visualization recommendation scoring
* chart specification generation
* aggregation selection
* axis selection
* categorical cardinality filtering
* numerical distribution recommendations
* time-series recommendations
* categorical comparison recommendations
* numeric relationship recommendations
* visualization recommendation persistence
* visualization APIs
* frontend visualization rendering
* interactive chart controls where appropriate
* visualization recommendation explanations
* visualization validation
* visualization caching/versioning if needed.

---

# 4. ABSOLUTELY DO NOT IMPLEMENT

Do NOT implement any of the following in Phase 5:

### Pattern discovery

* correlation discovery engine
* trend discovery engine
* clusters
* segments
* hidden patterns
* statistical relationship detection
* automatic hypothesis generation.

These belong to **Phase 6**.

### Anomaly detection

* anomaly detection
* outlier detection engine
* isolation forest
* z-score anomaly engine
* forecasting
* prediction.

These belong to **Phase 7**.

### AI/LLM

* Gemini/OpenAI/Claude calls
* LLM-generated insights
* AI explanations
* natural-language analyst
* conversational querying.

These belong to **Phase 8/9**.

### Advanced ML

* clustering
* PCA
* classification
* regression
* feature selection
* feature engineering.

Do NOT add them.

### Automated data modification

Do NOT modify the source or processed dataset during visualization generation.

Visualization generation is strictly **read-only**.

---

# 5. FIRST STEP — INSPECT EXISTING CODEBASE

Before coding, inspect:

```text
backend/app/
backend/tests/
backend/alembic/
frontend/src/
docs/
README.md
```

Specifically inspect and reuse:

### Dataset infrastructure

* Dataset model
* Dataset repository
* Dataset APIs
* StorageService
* dataset loader
* source/processed dataset relationship
* checksum implementation

### Profiling infrastructure

* DatasetProfile
* DatasetColumnProfile
* profiling service
* profile repository
* semantic type inference

### Preprocessing infrastructure

* PreprocessingJob
* PreprocessingTransformation
* PreprocessingService
* processed dataset loading

### Existing frontend

* routing
* dashboard
* DatasetProfileView
* PreprocessingView
* API service
* reusable UI components
* styling conventions.

Do not duplicate existing services.

If Phase 3 already provides a semantic type inference utility, reuse it.

If Phase 4 already provides a reliable processed-dataset loader, reuse it.

---

# 6. DATASET SELECTION

Visualization should preferably operate on the **latest successfully processed dataset**.

Expected behavior:

```text
SOURCE DATASET
      ↓
PROFILE
      ↓
PREPROCESS
      ↓
PROCESSED DATASET
      ↓
VISUALIZATION
```

If a processed dataset exists:

```text
use latest valid processed dataset
```

If no processed dataset exists:

The API may either:

1. return a clear `PREPROCESSING_REQUIRED` response, OR
2. visualize the source dataset only if the existing architecture safely supports it.

Prefer option 1 unless the existing implementation already has a safe reusable path.

Do NOT silently run preprocessing from the visualization endpoint.

Visualization generation must not mutate data.

---

# 7. VISUALIZATION ENGINE ARCHITECTURE

Create a clean service layer.

Suggested structure:

```text
backend/app/services/
    visualization_service.py
    visualization_planner.py
    visualization_scoring.py
    visualization_validator.py
    chart_spec_builder.py
```

Names may be adjusted to match the existing architecture.

Suggested responsibilities:

### visualization_planner.py

Generates candidate visualization plans.

### visualization_scoring.py

Scores and ranks candidates deterministically.

### visualization_validator.py

Validates chart configurations against the actual dataset/profile.

### chart_spec_builder.py

Converts valid candidates into frontend-renderable chart specifications.

### visualization_service.py

Orchestrates:

```text
load profile
↓
load processed dataset
↓
analyze eligible columns
↓
generate candidates
↓
validate candidates
↓
score candidates
↓
rank candidates
↓
build chart specifications
↓
persist/retrieve recommendations
```

---

# 8. COLUMN ELIGIBILITY ANALYSIS

Before generating charts, classify columns into visualization roles.

Possible roles:

```text
NUMERIC_MEASURE
CATEGORICAL_DIMENSION
DATETIME_DIMENSION
BOOLEAN_DIMENSION
TEXT_DIMENSION
IDENTIFIER
UNSUITABLE
```

Use Phase 3 profile information wherever possible.

---

# 9. NUMERIC COLUMN RULES

A numeric column is eligible as a measure when:

* numeric semantic type
* not an obvious identifier
* not completely missing
* not constant
* contains enough valid observations.

Examples:

```text
sales
revenue
profit
age
quantity
temperature
score
```

Potential numeric aggregations:

```text
sum
mean
median
min
max
count
```

Default aggregation should be deterministic.

Suggested rules:

### Additive measures

Names such as:

```text
sales
revenue
amount
quantity
profit
cost
```

may prefer:

```text
SUM
```

### General numeric measures

Default:

```text
MEAN
```

unless the profile or column characteristics indicate another appropriate aggregation.

Do NOT rely solely on column names.

Store the chosen aggregation in the chart specification.

---

# 10. IDENTIFIER DETECTION

Do not generate meaningless visualizations from identifiers.

Examples:

```text
id
customer_id
user_id
transaction_id
order_id
uuid
email
phone
account_number
```

Identifier detection should use:

* column name patterns
* extremely high uniqueness
* data type
* semantic profile
* cardinality.

Do NOT assume every high-cardinality column is an identifier.

High cardinality alone should not automatically disqualify a column.

---

# 11. CATEGORICAL COLUMN RULES

Categorical columns can be used as dimensions.

Recommended limits:

```text
0 < unique_count <= 20
```

for standard category comparison charts.

For larger categories:

```text
20 < unique_count <= 50
```

they may be considered for specialized charts only when appropriate.

For:

```text
unique_count > 50
```

normally exclude from standard categorical visualizations.

Never generate charts with hundreds or thousands of categories.

Use deterministic thresholds stored in configuration.

Example:

```text
MAX_BAR_CATEGORIES = 20
MAX_CATEGORY_CATEGORIES = 10
MAX_SCATTER_CATEGORIES = 10
```

Centralize these settings.

---

# 12. DATETIME DETECTION

Datetime columns should receive high priority because they enable time-series visualization.

Examples:

```text
date
created_at
timestamp
order_date
transaction_date
month
year
```

If a valid datetime column exists and a suitable numeric measure exists, generate:

```text
LINE_CHART
```

with:

```text
X = datetime
Y = numeric measure
Aggregation = appropriate aggregation
```

The chart specification must preserve temporal ordering.

Do not treat dates as ordinary categorical strings.

---

# 13. BOOLEAN COLUMNS

Boolean columns may be used for:

```text
bar chart
count comparison
percentage comparison
```

Example:

```text
Subscribed: True / False
```

Do not generate unnecessary visualizations for every boolean column.

Only generate a boolean chart when it provides a meaningful comparison.

---

# 14. TEXT COLUMNS

Long free-text columns should normally NOT be visualized directly.

Do not generate:

```text
bar(text)
scatter(text)
line(text)
```

unless the text has been semantically classified as categorical.

Use Phase 3 semantic typing.

---

# 15. REQUIRED CHART TYPES

Implement at minimum:

## A. Histogram

Use for:

```text
numeric column
```

Example:

```text
Sales Distribution
```

Specification:

```json
{
  "chart_type": "histogram",
  "x": "sales",
  "bins": 20
}
```

Bin count should be deterministic and configurable.

---

## B. Bar Chart

Use for:

```text
categorical + numeric
```

Example:

```text
Revenue by Region
```

Specification:

```json
{
  "chart_type": "bar",
  "x": "region",
  "y": "revenue",
  "aggregation": "sum",
  "sort": "descending"
}
```

Limit categories.

---

## C. Count Bar Chart

For categorical/boolean distributions:

```text
Customer Count by Region
```

Specification:

```json
{
  "chart_type": "bar",
  "x": "region",
  "aggregation": "count"
}
```

---

## D. Line Chart

Use for:

```text
datetime + numeric
```

Example:

```text
Monthly Revenue Trend
```

Specification:

```json
{
  "chart_type": "line",
  "x": "order_date",
  "y": "revenue",
  "aggregation": "sum",
  "sort": "ascending"
}
```

---

## E. Scatter Plot

Use for:

```text
numeric + numeric
```

Example:

```text
Sales vs Profit
```

Specification:

```json
{
  "chart_type": "scatter",
  "x": "sales",
  "y": "profit"
}
```

Do not generate every possible numeric pair.

Limit the number of candidate pairs using deterministic selection.

---

## F. Box Plot

Use for:

```text
numeric
```

or:

```text
categorical + numeric
```

when the category count is low.

Example:

```text
Profit Distribution by Region
```

Specification:

```json
{
  "chart_type": "boxplot",
  "x": "region",
  "y": "profit"
}
```

Do not interpret the result as anomaly detection.

The box plot is only a visualization.

---

# 16. OPTIONAL CHART TYPES

If the implementation remains clean and deterministic, optionally support:

```text
area
pie/donut
heatmap
```

However:

**Do not add many chart types just for quantity.**

Quality and appropriateness are more important.

Pie/donut should only be considered for very low-cardinality categorical distributions, for example:

```text
2–6 categories
```

Avoid pie charts for high-cardinality data.

---

# 17. REQUIRED RECOMMENDATION RULES

At minimum implement these deterministic rules.

### Rule 1 — Numeric distribution

For each eligible numeric column:

```text
→ Histogram
```

Limit the number of generated histograms.

---

### Rule 2 — Categorical + numeric

For each suitable:

```text
categorical + numeric
```

combination:

```text
→ Bar chart
```

Limit the number of combinations.

---

### Rule 3 — Datetime + numeric

For each suitable:

```text
datetime + numeric
```

combination:

```text
→ Line chart
```

These should receive high recommendation priority.

---

### Rule 4 — Numeric + numeric

For suitable numeric pairs:

```text
→ Scatter plot
```

Limit pairs.

---

### Rule 5 — Categorical distribution

For suitable categorical columns:

```text
→ Count bar chart
```

---

### Rule 6 — Categorical + numeric distribution

For suitable low-cardinality categories:

```text
→ Box plot
```

Limit the number.

---

# 18. CANDIDATE EXPLOSION CONTROL

This is extremely important.

Do NOT create:

```text
100 numeric columns × 100 numeric columns
```

or:

```text
50 categorical × 100 numeric
```

combinations.

Set hard limits.

Suggested configuration:

```text
MAX_TOTAL_RECOMMENDATIONS = 12

MAX_HISTOGRAMS = 3
MAX_BAR_CHARTS = 4
MAX_LINE_CHARTS = 3
MAX_SCATTER_PLOTS = 3
MAX_BOXPLOTS = 2
MAX_COUNT_CHARTS = 2
```

These values must be configurable.

If fewer valid charts exist, return fewer.

Never fabricate charts merely to reach the limit.

---

# 19. VISUALIZATION SCORING

Every visualization candidate must receive a deterministic score.

Example:

```text
0–100
```

Do NOT use an LLM.

Possible scoring factors:

### Relevance

Does the visualization match the semantic types?

### Data quality

Are the columns usable?

### Cardinality

Is the number of categories appropriate?

### Analytical usefulness

Does the combination represent a meaningful common analytical view?

### Redundancy

Penalize duplicate or nearly identical visualizations.

### Identifier penalty

Strongly penalize identifier-like columns.

### Missingness penalty

Penalize columns with significant missing values.

### Constant penalty

Exclude constant columns completely.

The exact formula must be documented.

Example:

```text
base score
+ semantic compatibility
+ temporal priority
+ measure suitability
+ category suitability
- high cardinality penalty
- missingness penalty
- identifier penalty
- redundancy penalty
```

Make the scoring deterministic.

---

# 20. RECOMMENDATION EXPLANATION

Each visualization recommendation must contain a concise machine-generated reason.

Example:

```text
"Recommended because Order Date is a datetime field and Revenue is a numeric measure."
```

Another:

```text
"Recommended because Region has 5 categories and Revenue is a suitable numeric measure."
```

Another:

```text
"Recommended to show the distribution of Sales."
```

These explanations must be template-based.

Do NOT use an LLM.

---

# 21. CHART SPECIFICATION

Create a frontend-neutral chart specification.

Suggested structure:

```json
{
  "id": "uuid",
  "rank": 1,
  "chart_type": "line",
  "title": "Revenue Over Time",
  "description": "Monthly revenue trend",
  "x": {
    "column": "order_date",
    "type": "datetime"
  },
  "y": {
    "column": "revenue",
    "type": "numeric",
    "aggregation": "sum"
  },
  "filters": [],
  "sort": {
    "field": "x",
    "direction": "ascending"
  },
  "score": 92,
  "reason": "Recommended because Order Date is a datetime field and Revenue is a numeric measure."
}
```

Keep the specification independent from a specific frontend chart library.

---

# 22. CHART DATA API

Do NOT send the entire dataset to the frontend if unnecessary.

Create an API capable of returning the aggregated data required for a chart.

For example:

```text
GET /api/v1/datasets/{dataset_id}/visualizations
```

returns recommendations.

Then either:

```text
GET /api/v1/datasets/{dataset_id}/visualizations/{visualization_id}/data
```

or an equivalent architecture can return chart-ready data.

Inspect the existing architecture and choose the cleaner approach.

Important:

* never expose filesystem paths
* never expose database connection information
* validate column names server-side
* validate aggregation names server-side
* prevent arbitrary code execution
* never accept arbitrary Pandas expressions from the frontend.

---

# 23. SECURITY

The frontend must never be allowed to send arbitrary Python/Pandas expressions.

Bad:

```text
expression = "df.groupby(...).apply(...)"
```

Do NOT support this.

Accept only validated structured parameters:

```text
column
chart_type
aggregation
sort
limit
```

Use allowlists.

Allowed chart types:

```text
histogram
bar
line
scatter
boxplot
count
```

Allowed aggregations:

```text
count
sum
mean
median
min
max
```

Reject everything else.

---

# 24. DATABASE PERSISTENCE

Inspect whether visualization recommendations need persistence based on the current architecture.

Preferred approach:

Create:

```text
VisualizationRecommendation
```

with fields such as:

```text
id
dataset_id
processed_dataset_id
profile_id
chart_type
title
description
score
rank
chart_spec JSONB
reason
created_at
```

If appropriate, create:

```text
VisualizationDatasetVersion
```

or use existing dataset/checksum references instead.

Important:

Visualization recommendations must be tied to a specific processed dataset/version.

If preprocessing is rerun and creates a new processed dataset, old recommendations must not silently point to the new data.

Use:

```text
processed_dataset_id
```

and/or:

```text
processed_checksum
```

to maintain integrity.

Create a new migration.

Do NOT modify old migrations.

---

# 25. REGENERATION BEHAVIOR

If the user requests visualization generation again:

Do not create uncontrolled duplicate records.

Implement deterministic behavior such as:

```text
latest recommendations for processed dataset
```

or:

```text
replace recommendations for the same processed dataset
```

Document the behavior.

If a new processed dataset version exists:

```text
new processed dataset
→ new visualization recommendations
```

---

# 26. API ENDPOINTS

Implement:

### Generate visualizations

```http
POST /api/v1/datasets/{dataset_id}/visualizations
```

Behavior:

1. verify dataset exists
2. verify profile exists
3. locate valid processed dataset
4. load processed data
5. generate candidates
6. validate candidates
7. score candidates
8. rank candidates
9. persist recommendations
10. return recommendations.

Do NOT automatically preprocess.

---

### Get recommendations

```http
GET /api/v1/datasets/{dataset_id}/visualizations
```

This endpoint must NOT regenerate automatically.

It should retrieve the latest valid visualization recommendations.

If none exist:

```text
404 / VISUALIZATIONS_NOT_GENERATED
```

or an equivalent structured response.

---

### Get chart data

Implement:

```http
GET /api/v1/datasets/{dataset_id}/visualizations/{visualization_id}/data
```

if this fits the architecture.

Validate that:

* visualization belongs to dataset
* referenced processed dataset exists
* columns still exist
* chart specification is valid
* requested aggregation is allowed.

---

# 27. PYDANTIC SCHEMAS

Create appropriate schemas, for example:

```text
VisualizationRecommendationResponse
VisualizationAxisResponse
VisualizationSpecResponse
VisualizationDataResponse
VisualizationGenerateResponse
```

Use strict validation.

Do not expose internal database fields unnecessarily.

---

# 28. FRONTEND VISUALIZATION DASHBOARD

Implement a proper visualization interface.

Suggested:

```text
VisualizationView.jsx
VisualizationCard.jsx
VisualizationGrid.jsx
VisualizationEmptyState.jsx
```

Use the project's existing frontend architecture and styling.

---

# 29. USER FLOW

The user should experience:

```text
Dataset
   ↓
Profile
   ↓
Preprocess
   ↓
Visualize Dataset
```

Add a:

```text
"Generate Visualizations"
```

button to the appropriate dataset/profile/preprocessing page.

After generation:

```text
Smart Visualizations
```

should display recommended charts.

---

# 30. VISUALIZATION UI

Each visualization card should show:

```text
┌────────────────────────────────────┐
│ Revenue Over Time                  │
│                                    │
│        [Rendered Chart]            │
│                                    │
│ Why this chart?                    │
│ Date + numeric measure detected    │
│                                    │
│ Score: 92                          │
└────────────────────────────────────┘
```

Do NOT make the score look like a model confidence score.

Label it clearly:

```text
Recommendation Score
```

or:

```text
Visualization Relevance
```

The user should understand it is an internal ranking score, not statistical certainty.

---

# 31. FRONTEND CHART LIBRARY

Inspect the current frontend dependencies first.

If no chart library exists, select a lightweight React-compatible charting library appropriate for:

* line
* bar
* histogram
* scatter
* box plot

Prefer a mature library with good React support.

Do not introduce multiple overlapping chart libraries.

Keep the visualization layer modular so the backend chart specification is not tightly coupled to the library.

---

# 32. FRONTEND STATES

Implement:

### Not generated

```text
No visualizations generated yet.

[Generate Visualizations]
```

### Generating

```text
Analyzing dataset...
Selecting appropriate visualizations...
Building charts...
```

### Ready

Display visualization grid.

### Empty

```text
No suitable visualizations were found for this dataset.
```

This is valid.

Do NOT fabricate recommendations.

### Failed

Display a clear error with retry.

---

# 33. RESPONSIVE DESIGN

The visualization dashboard should support:

* desktop
* laptop
* tablet widths.

Use:

```text
responsive grid
```

Avoid unnecessarily huge charts.

---

# 34. PERFORMANCE

Do not load the entire dataset into the frontend.

Backend should:

* load data
* aggregate when required
* limit result sizes
* return chart-ready data.

For example:

```text
bar chart → max 20 categories
histogram → max configured bins
line chart → aggregate by time period when appropriate
scatter → configurable point limit
```

For very large datasets, avoid sending millions of scatter points.

Use deterministic sampling only when necessary, and document it.

If sampling is implemented:

```text
random_state = fixed value
```

so visualization remains reproducible.

Do NOT implement a sophisticated sampling engine in Phase 5.

---

# 35. TIME-SERIES AGGREGATION

If datetime data contains many unique timestamps, avoid producing enormous chart payloads.

Implement basic deterministic temporal aggregation when appropriate:

```text
daily
weekly
monthly
yearly
```

Choose based on dataset date span / cardinality.

Document the rule.

Example:

```text
< 90 points → daily
90–365 → weekly
>365 → monthly
```

These are suggested defaults; centralize them in configuration.

Do not implement forecasting.

---

# 36. HISTOGRAM BINNING

Use a deterministic histogram strategy.

Possible default:

```text
bins = 20
```

with configurable minimum/maximum.

Do not use an ML model.

Do not make bins depend on an LLM.

Record the selected bin count in the chart specification.

---

# 37. DUPLICATE / REDUNDANCY CONTROL

Avoid recommendations such as:

```text
Revenue by Region
Revenue by Region
Revenue by Region
```

Each recommendation must be unique by meaningful specification.

Create deterministic deduplication based on:

```text
chart_type
x column
y column
aggregation
grouping
```

---

# 38. COLUMN NAME COLLISIONS

Handle columns with:

* spaces
* special characters
* duplicate-looking names
* reserved frontend words
* Unicode names.

Do not rename the actual dataset columns.

Use safe internal references while preserving display labels.

Example:

```text
column = "Customer Revenue ($)"
label = "Customer Revenue ($)"
```

The backend must always reference the real column name safely.

---

# 39. NULL HANDLING

Visualization queries must handle missing values safely.

Examples:

* aggregations ignore nulls where appropriate
* categorical charts may exclude null or represent it explicitly according to configuration
* histograms exclude invalid/null values
* scatter plots require both x and y values.

Do not mutate the dataset.

---

# 40. VALIDATION

Before returning a visualization:

Verify:

```text
chart type valid
column exists
column type compatible
aggregation valid
cardinality acceptable
data available
chart spec internally consistent
```

Invalid candidates must be rejected.

Never send invalid chart specifications to the frontend.

---

# 41. LOGGING

Add structured logging.

Recommended events:

```text
visualization_generation_started
visualization_columns_analyzed
visualization_candidates_generated
visualization_candidates_scored
visualization_generation_completed
visualization_generation_failed
visualization_data_requested
```

Include:

```text
request_id
dataset_id
processed_dataset_id
```

Do NOT log:

* raw dataset rows
* sensitive column values
* database credentials
* filesystem absolute paths.

---

# 42. ERROR HANDLING

Use structured application errors consistent with Phases 1–4.

Examples:

```text
DATASET_NOT_FOUND
PROFILE_REQUIRED
PREPROCESSING_REQUIRED
PROCESSED_DATASET_NOT_FOUND
VISUALIZATION_NOT_FOUND
UNSUPPORTED_CHART_TYPE
INVALID_VISUALIZATION_SPEC
INVALID_COLUMN
INVALID_AGGREGATION
VISUALIZATION_GENERATION_FAILED
```

Reuse existing error handling conventions.

Do not create a parallel error system.

---

# 43. TESTING REQUIREMENTS

Add comprehensive Phase 5 tests.

## Planner tests

Test:

```text
numeric column
categorical column
datetime column
boolean column
text column
identifier column
constant column
high-cardinality column
missing-heavy column
```

---

## Candidate generation tests

Verify:

```text
numeric → histogram
categorical + numeric → bar
datetime + numeric → line
numeric + numeric → scatter
categorical → count bar
categorical + numeric → boxplot
```

---

## Scoring tests

Verify:

* deterministic scores
* ranking stability
* identifier penalties
* cardinality penalties
* missingness effects
* temporal priority
* duplicate candidate elimination.

Running the same input twice must produce the same ranking.

---

## Validation tests

Test:

```text
invalid chart type
invalid column
wrong data type
invalid aggregation
missing processed dataset
missing profile
empty dataset
constant dataset
```

---

## API tests

Test:

```text
POST /visualizations
GET /visualizations
GET /visualizations/{id}/data
```

Test success and failure cases.

---

## Persistence tests

Verify:

```text
recommendations stored
chart specification stored
rank stored
score stored
processed dataset reference stored
recommendations retrievable
regeneration behavior works
```

---

## Security tests

Verify frontend/API cannot submit:

```text
arbitrary Python
Pandas expressions
SQL expressions
unsupported aggregation
unsupported chart type
invalid column reference
```

---

## Regression tests

Run ALL existing tests from:

```text
Phase 1
Phase 2
Phase 3
Phase 4
```

Do not allow Phase 5 changes to break:

* dataset upload
* dataset deletion
* profile generation
* preprocessing
* source checksum integrity
* processed dataset persistence
* cascade deletion.

---

# 44. END-TO-END TEST

Perform a real workflow:

```text
Upload CSV/XLSX
      ↓
Profile Dataset
      ↓
Preprocess Dataset
      ↓
Generate Visualizations
      ↓
Retrieve Recommendations
      ↓
Render Charts
      ↓
Retrieve Chart Data
      ↓
Delete Source Dataset
      ↓
Verify derived dataset and visualization records/files are cleaned according to existing cascade rules
```

Also verify:

```text
Source checksum BEFORE visualization
=
Source checksum AFTER visualization
```

Visualization must never mutate the source.

---

# 45. DATABASE MIGRATION

Create a NEW Alembic migration.

Do NOT modify:

```text
001_...
002_...
003_...
004_...
```

unless the existing migration architecture explicitly requires correction.

Expected new migration:

```text
005_add_visualization_recommendations.py
```

Use the actual next revision naming convention after inspecting the repository.

Add:

* primary keys
* foreign keys
* indexes
* timestamps
* JSONB chart specification where appropriate.

Ensure delete behavior is intentional.

No orphan visualization records.

---

# 46. CONFIGURATION

Centralize visualization configuration.

Suggested:

```text
MAX_TOTAL_RECOMMENDATIONS=12

MAX_HISTOGRAMS=3
MAX_BAR_CHARTS=4
MAX_LINE_CHARTS=3
MAX_SCATTER_PLOTS=3
MAX_BOXPLOTS=2
MAX_COUNT_CHARTS=2

MAX_BAR_CATEGORIES=20
MAX_PIE_CATEGORIES=6

HISTOGRAM_DEFAULT_BINS=20
HISTOGRAM_MIN_BINS=5
HISTOGRAM_MAX_BINS=50

MAX_SCATTER_POINTS=5000

TIME_SERIES_DAILY_LIMIT=90
TIME_SERIES_WEEKLY_LIMIT=365
```

Adjust names to the project's existing configuration convention.

Do not hardcode important thresholds throughout the code.

---

# 47. DOCUMENTATION

Update:

```text
README.md
docs/architecture.md
docs/api.md
docs/development.md
docs/roadmap.md
```

Document:

* Phase 5 objective
* visualization pipeline
* supported chart types
* column eligibility
* recommendation rules
* scoring formula
* limits
* aggregation rules
* time-series aggregation
* chart specification
* security
* performance considerations
* regeneration behavior
* limitations.

Clearly state:

> Phase 5 recommends and renders visualizations. It does not perform pattern discovery, anomaly detection, prediction, or AI-generated insight generation.

---

# 48. CODE QUALITY

Follow existing project conventions.

Requirements:

* type hints
* Pydantic validation
* small reusable functions
* service/repository separation
* no business logic inside routes
* no business logic inside React components where avoidable
* no duplicated dataset loading logic
* no duplicated profile logic
* meaningful error handling
* structured logging
* clear naming
* testable deterministic functions.

Do not over-engineer.

---

# 49. IMPORTANT ARCHITECTURAL RULE

Maintain this separation:

```text
Phase 3
Data Understanding
        ↓
Phase 4
Data Preparation
        ↓
Phase 5
Visualization Intelligence
        ↓
Phase 6
Pattern Discovery
        ↓
Phase 7
Anomaly Detection + Prediction
        ↓
Phase 8
AI Insight Engine
        ↓
Phase 9
Natural Language Analyst
        ↓
Phase 10
Production Dashboard
```

Do NOT collapse these phases together.

The most important architectural principle is:

> **Python/statistical/data-processing code determines what the data supports. The LLM, when introduced later, only explains the computed results.**

Phase 5 must contain **zero LLM dependency**.

---

# 50. FINAL VERIFICATION CHECKLIST

Before declaring Phase 5 complete, verify ALL of the following.

### Backend

* [ ] visualization planner implemented
* [ ] visualization scoring implemented
* [ ] visualization validation implemented
* [ ] chart specification builder implemented
* [ ] visualization service implemented
* [ ] existing dataset loader reused
* [ ] Phase 3 profile reused
* [ ] Phase 4 processed dataset reused
* [ ] no source dataset modification
* [ ] deterministic recommendations
* [ ] recommendation limits enforced
* [ ] identifier filtering implemented
* [ ] cardinality filtering implemented
* [ ] aggregation validation implemented
* [ ] chart type validation implemented
* [ ] chart data endpoint implemented if appropriate
* [ ] structured errors implemented
* [ ] structured logging implemented.

### Database

* [ ] new migration created
* [ ] visualization recommendation model created
* [ ] processed dataset relationship stored
* [ ] chart specification stored
* [ ] indexes created
* [ ] delete behavior verified
* [ ] no orphan records.

### Frontend

* [ ] visualization API integrated
* [ ] generate button added
* [ ] visualization dashboard created
* [ ] charts render correctly
* [ ] recommendation explanation shown
* [ ] loading state
* [ ] empty state
* [ ] error state
* [ ] responsive layout
* [ ] no raw dataset dumped to browser unnecessarily.

### Tests

* [ ] planner tests
* [ ] scoring tests
* [ ] validator tests
* [ ] chart specification tests
* [ ] service tests
* [ ] API tests
* [ ] persistence tests
* [ ] security tests
* [ ] edge-case tests
* [ ] Phase 1 regression
* [ ] Phase 2 regression
* [ ] Phase 3 regression
* [ ] Phase 4 regression.

---

# 51. REQUIRED COMMANDS

Run the appropriate project commands after implementation.

Backend:

```bash
cd backend
python -m pytest tests/ -v
```

Frontend:

```bash
cd frontend
npm run build
```

Database:

```bash
alembic upgrade head
alembic current
```

If Docker is part of the existing environment, verify the application against the actual project Docker setup.

Do not switch databases or environments.

---

# 52. FINAL END-TO-END ACCEPTANCE TEST

The implementation is NOT complete until this workflow works:

```text
Upload Dataset
        ↓
Dataset Stored
        ↓
Profile Dataset
        ↓
Profile Stored
        ↓
Preprocess Dataset
        ↓
Processed Dataset Created
        ↓
Generate Visualizations
        ↓
Visualization Candidates Generated
        ↓
Candidates Validated
        ↓
Candidates Deterministically Scored
        ↓
Top Recommendations Stored
        ↓
Frontend Displays Charts
        ↓
Chart Data Retrieved
        ↓
Source Dataset Remains Unchanged
```

Verify source checksum remains identical.

Verify the processed dataset remains unchanged.

Verify visualization generation is repeatable and deterministic.

---

# 53. DO NOT CLAIM SUCCESS WITHOUT VERIFICATION

Do not say:

```text
Phase 5 complete
```

until:

* tests pass
* frontend builds
* migration works
* APIs work
* visualization rendering works
* end-to-end workflow works
* Phase 1–4 regression tests pass.

If something fails:

1. identify the exact failure
2. fix it
3. rerun the relevant tests
4. rerun regression tests.

Do not hide or bypass failures.

---

# 54. FINAL REPORT

After implementation, provide a concise implementation report containing:

### 1. Files created

List every new file.

### 2. Files modified

List every modified file.

### 3. Database changes

Explain migration and tables.

### 4. Visualization rules

List supported chart types and recommendation rules.

### 5. Scoring

Explain the deterministic scoring formula.

### 6. API endpoints

List all Phase 5 endpoints.

### 7. Frontend

Explain the visualization dashboard.

### 8. Tests

Report exact test results.

Example:

```text
X passed, Y skipped
```

### 9. Build

Report exact frontend build result.

### 10. End-to-end verification

Report:

```text
Upload → Profile → Preprocess → Visualize → Render
```

### 11. Known limitations

Clearly list anything intentionally deferred.

---

# 55. STRICT STOP CONDITION

After completing and verifying Phase 5:

**STOP.**

Do NOT implement:

* Phase 6 Pattern Discovery
* Phase 7 Anomaly Detection
* Phase 7 Prediction
* Phase 8 AI Insight Engine
* Phase 9 Natural Language Analyst
* Phase 10 Production Dashboard

Do not add:

* LLM
* Gemini
* OpenAI
* correlation discovery
* anomaly detection
* forecasting
* predictive models
* clustering
* PCA
* natural-language querying.

Phase 5 ends at:

```text
Dataset
   ↓
Profile
   ↓
Preprocess
   ↓
Smart Visualization Recommendations
   ↓
Validated Chart Specifications
   ↓
Rendered Visualizations
```

Once all Phase 5 acceptance criteria are satisfied, update the roadmap/documentation to mark Phase 5 complete and **WAIT for the next instruction.**
